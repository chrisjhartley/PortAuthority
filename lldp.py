# Windows, at least, just to get winpcap easily - you can do it other ways, whatever: install npcap (I dunno, provide link)...
# install python ~3.11
# install scapy: python -m pip install scapy
# install IPython (no, don't, but I did)
# install flask: python -m pip install flask
# install requests: python -m pip install requests
# This all needs to go into an installer or just portauthority.bat, or something.
# Maybe just do all the pip stuff here. import pip; pip.main(['install','Flask']); etc.
# Notes from recent meeting... The switch LLDP must support the following in the LLDP advertisementsPortIDID of the port. Multiple forms depending on the PortIDSubType value.PortIDSubTypeValid subtypes are:1: InterfaceAlias5: InterfaceName7: LocallyAssignedManagement address of the switch IP address formChassisIDThe MAC address of the switch (associated with the management IP address or base switch MAC address)
#v10
interfaceSubTypes = {1: 'InterfaceAlias', 5: 'InterfaceName', 7: 'LocallyAssigned', 3: 'MacAddress', 4: 'Network Address', 2: 'Port component', 6: 'Agent Circuit Name'}

import time

try:
    import pip
except:
    print("Cannot import pip; fail")
    exit(-1)
finally:
    import pip

# Is this workable, maybe?
try: 
    from scapy.all import *
    from scapy.contrib import *
    from scapy.contrib.lldp import *
except:
    import pip
    pip.main(['install','scapy'])
finally:
    from scapy.all import *
    from scapy.contrib import *
    from scapy.contrib.lldp import *



from socket import inet_ntoa # This should already be installed?

import subprocess
import os
import platform

import json

try:
    import flask
except:
    pip.main(["install", "flask"])
finally:
    from flask import Flask
    from flask import request
    from flask import send_file

try: 
   import requests
except:
    import pip
    pip.main(['install','requests'])
finally:
    import requests

app = Flask(__name__)
# TODO: NO! These go in the config file.  Fix this.
api_base_url="https://cmdb.it.ohio-state.edu/"
api_building_path="/api/portmapper_locations"
api_mapping_path="/api/portmapper_data"

PATH=os.path.dirname(os.path.realpath(__file__)) # os.path.expanduser("~")
path_delim = "\\" if platform.system() == "Windows" else "/"
# TODO: set an "editor" variable according to Windows/OS X/Linux/BSD rather than just hard-coding notepad.
#background_image_filename = "osu.png" # Put this in the config file...
fields = ['SystemName','SystemIPAddress','SystemMacAddress','PortMacAddress','InterfaceDescription','building','room','jack', 'MappingMacAddress','MappingIPAddress','PortID','PortIDSubtype']
editor="notepad" if platform.system()=="Windows" else "open" if platform.system() == "Darwin" else "gedit"

def load_config():
    return json.loads("\n".join(list(open(f"{PATH}{path_delim}config.json","r"))))

def write_config_buildings(buildings): # Hopefully we're not updating other types of config items, but maybe. 
    print(f"Writing {PATH}{path_delim}config.json: {len(buildings)} buildings total!")
    with open(f"{PATH}{path_delim}config.json","w") as f:
        config["buildings"] = json.dumps(buildings)
        f.write(json.dumps(config, indent=4))
        f.close()

config=load_config()
background_image_filename = config['logo']

def get_buildings():
    resp = requests.get(f"{api_base_url}/{api_building_path}", headers={'Authorization': f"Bearer {config['Auth-Token']}"})
    buildings = [ {'name': x["name"], "id": x["u_building_number"] } for x in json.loads(resp.content) ]
    write_config_buildings(buildings)

@app.route("/update_buildings")
def update_buildings():
    try:
        get_buildings()
    except:
        return "error", 500
    finally:
        return "success", 200

@app.route('/ping')
def ping():
    #return 'ALIVE', 200
    response = flask.jsonify({'ping': 'true'})
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response

@app.route("/edit_records")
def edit_records():
    # TODO: Make editor a part of the config file, perhaps setting them per-platform so that the config if portable, but flexible?
    subprocess.Popen([f"{editor}", f"{PATH}{path_delim}local_records.txt"])
    return "", 200

@app.route("/edit_config")
def edit_config():
    subprocess.Popen([f"{editor}", f"{PATH}{path_delim}config.json"])
    return "", 200

@app.route("/purge_local")
def purge_local(): # Remove local results...
    try:
        for fname in [f"{PATH}{path_delim}local_records.txt", f"{PATH}{path_delim}uploaded_records.txt"]:
            f = open(f"{PATH}{path_delim}local_records.txt","w")
            f.write('')
            f.close()
        return "", 200
    except:
        return "Error?", 500



@app.route('/index')
def index():
    path = f"{PATH}{path_delim}index.html"
    return send_file(path)

@app.route("/local_records")
def local_records():
    total_records = len(list(open(f"{PATH}{path_delim}local_records.txt","r")))
    unuploaded_records = len(get_new_records()) # We don't need the new records, just their count, here.
    return json.dumps({"total": total_records, "unuploaded": unuploaded_records})

# Yes, this should go up higher in the file.  But it also doesn't matter, and I don't care - but I'll probably fix it later.
def get_new_records():
    uploaded_records = [ x.strip() for x in list(open(f"{PATH}{path_delim}uploaded_records.txt","r")) ]
    local_records = list(open(f"{PATH}{path_delim}local_records.txt","r"))
    local_records = [json.loads(x.strip()) for x in local_records] 
    new_records = [ record for record in local_records if record['id'] not in uploaded_records ]
    print(f"Returning {len(new_records)} new_records")
    return new_records

@app.route("/store_results")
def store_results():
    valid = True;
    for field in fields:
        if len(request.args.get(field)) == 0:
            valid = False
    print("Valid?", valid)
    if valid:
        # HERE
        print("Valid request?...")
        fname = f"{PATH}{path_delim}local_records.txt"
        fd = open(fname,"a")
        
        record = {}
        #[ {field: request.args.get(field)} for field in fields ]
        for field in fields:
            record[field] = request.args.get(field)
        record['id'] = str(uuid.uuid4())

        print(json.dumps(record))
        fd.write(json.dumps(record)+"\n")
        fd.close()
    else:
        print("Not valid...")
        return json.dumps({"Saved": "False", "reason": "Empty field(s)"}), 200 # Add an error, too...

    return json.dumps({"Saved": "True"}),200

def upload_to_server(records):
    """ Receive a record - hash, and use requests module to make HTTP request to .. something - consult config file. """
    data_json = json.dumps( records )
    resp = requests.post(f"{api_base_url}/{api_mapping_path}",headers={'Authorization': f"Bearer {config['Auth-Token']}"}, data=data_json)
    print("response?", resp.content)
    return resp.status_code >= 200 and resp.status_code <= 300

@app.route("/upload")
def upload():
        new_records = get_new_records()
        print(f"Uploading {len(new_records)} records.")
        if upload_to_server(new_records):
            uploaded_ids = [ x["id"] for x in new_records ]
            print("UPLOADED IDS", uploaded_ids)
            with open(f"{PATH}{path_delim}uploaded_records.txt","a") as f:
                f.write("\n".join(uploaded_ids)+"\n")
            return json.dumps({"Uploaded": len(new_records) }), 200
        else:
            print("Error?")
            return json.dumps({"Error": "?"}), 500


@app.route("/interfaces")
def interfaces():
    interfaces = []
    for i in ifaces.data.keys():
        name=ifaces.data[i].name
        ip=ifaces.data[i].ip
        mac=ifaces.data[i].mac
        index = i
        interfaces.append({'name':name, 'ip':ip, 'index':index})
    return json.dumps(interfaces), 200

@app.route("/buildings")
def buildings():
    print(config['buildings'])
    buildings = json.loads(config['buildings'])
    #return str(config['buildings']).replace("'",'"'), 200
    return json.dumps(buildings), 200

@app.route("/bgimage")
def bg_image(): 
    return send_file(f"{PATH}{path_delim}{background_image_filename}")

receivedValidPacket = False
def eligible_packet(pkt):
    global receivedValidPacket, skippedPackets
    if (time.time() - started_capture) > (int(config['lldp_timeout_seconds']) + 1):
        return True # Timeout; not a successful capture.
    elif ("LLDPDUSystemCapabilities" in pkt and pkt["LLDPDUSystemCapabilities"].telephone_available == 0):
        receivedValidPacket = True
        skippedPackets+=1
        return True 
    else:
        print("Ineligible packet:", pkt)
        return False

skippedPackets=0
started_capture = -1  # Ew, mixed variable-naming convention: TODO: FIX.

# Let's add some exception handling here, dude.
@app.route("/capture")
def capture():
    global started_capture
    print("LLDP capture requested")
    interface_name=request.args.get('interface')
    MAC="(error)"
    IP="(error)"
    for i in ifaces.data.keys():
        if ifaces.data[i].name == interface_name:
            MAC=ifaces.data[i].mac
            IP=ifaces.data[i].ip
    started_capture = time.time()   
    # TODO: Add further configuration options to affect the BPF filter and the behavior of eligible_packet(). 
    pkts = sniff(filter="ether proto 0x88cc", stop_filter=eligible_packet, iface=interface_name)
   
    print(f"Skipped {skippedPackets} packets")  
    if len(pkts) == 0:
        return "ERROR", 200
    if not receivedValidPacket:
        return "No LLDP packet captured.", 200
    pkt = pkts[-1]

    print(pkt["LLDPDUSystemCapabilities"].telephone_available)
    if pkt["LLDPDUSystemCapabilities"].telephone_available == 1:
        print("It's a phone!")
    else:
        print("Not a phone!")
    InterfaceDescription = pkt['LLDPDUPortDescription'].description.decode()
    SystemName = pkt['LLDPDUSystemName'].system_name.decode()
    SystemIPAddress = inet_ntoa(pkt['LLDPDUManagementAddress'].management_address)
    SystemMacAddress = pkt["LLDPDUChassisID"].id
    PortID = pkt["LLDPDUPortID"].id.decode() if hasattr(pkt["LLDPDUPortID"].id, "decode") else pkt["LLDPDUPortID"].id
    PortIDSubtype = interfaceSubTypes[pkt["LLDPDUPortID"].subtype] if pkt["LLDPDUPortID"].subtype in interfaceSubTypes else f"INVALID({pkt['LLDPDUPortID'].subtype})"
    PortMacAddress = pkt.src
    return json.dumps({"MappingMacAddress": MAC, "MappingIPAddress": IP,"InterfaceDescription": InterfaceDescription, "SystemName": SystemName, "SystemIPAddress": SystemIPAddress, "SystemMacAddress": SystemMacAddress, "PortMacAddress": PortMacAddress, "PortID": PortID, "PortIDSubtype": PortIDSubtype}), 200

if __name__ == '__main__':
    app.run()

