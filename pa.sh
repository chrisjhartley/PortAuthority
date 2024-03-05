#bash
#Do something about the occasions when lldp.py takes a while to start up - modify index.html to monitor; preload the image into index.html base64-encoded so that we don't need the server up for the UI to look OK?
#python3 ./lldp.py &
#child=$!
uname -a | grep Darwin && open pa.html || xdg-open pa.html # Yeah, this is not really sufficient, but it'll work in enough cases - and likely, for its intended purpose, it'll only ever be run on Windows :( 
python3 ./lldp.py

#trap "kill $child" EXIT
