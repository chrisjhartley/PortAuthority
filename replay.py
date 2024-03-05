from scapy.all import *
from scapy.utils import rdpcap
import time

import sys
if len(sys.argv) > 1:
    pcap_file = sys.argv[1]

#pkts=rdpcap("phonelldp2.pcapng") # Comment left as a reminder when I forget which pcap I want to test against :)
pkts=rdpcap(pcap_file)

print(f"{len(pkts)} packets to send!")
for a in range(0,100):
  for i,pkt in enumerate(pkts):
    if True or i == 5:
        #for a in range(1000):
            print("Sent", pkt)
            sendp(pkt)
            time.sleep(0.2)


