# SDN-DDoS
SDN-DDOS simulation using mininet and pox controller. ddos.py is run in pox controller along with l3_learning.py script. 
ddos_printer script is used to generate sync flood when run on one of the host in the mininet topology.

HOW to Run the CODE:
Put the ddos.py and ddos_printer.py in ext folder under POX folder
Run the topology using miniedit i.e open the ddos_test.mn file in miniedit.
Run the controller using this command. 
cd pox
./pox.py forwarding.l3_learning ddos

Open any host terminal in the mininet topology and run the ddos_printer.py script using this command sudo python ddos_printer.py
This will generate random syn flood traffic from random ip addresses. If the number of syn attack from a ip exceeds 50 request per second, that IP will be blocked.

