# CN-assignment-2
This is the solution for computer networks assignment 2 done by Manav Parmar ( 21110120) and Pulkit Gautam ( 21110169)

# How to run the Q1 code:

Prerequisites:
Installed Mininet and python on the system.

Running the topology
1. Save the provided python-script on your system
2. Navigate to the directory where this file is, and in the terminal, write 
sudo python <Saved_name_of_the_provided_code>.py

Exploring Topology
This network consists of three routers (r1,r2 and r3), which can be explored with mininet CLI through
<name of the router > route
example: r1 route

Modifying Default Routes:
The script includes commands to modify the default routes for traffic from hosts h1 to h6. You can observe the changes in the routing tables of the routers before and after modifying the routes.

Exiting the topology:
On minitnet CLI write: 
exit

Packet Capture:
The script starts packet capture on interfaces connected to other routers on r1. The captured packets are stored in /tmp/r1-eth2.pcap and /tmp/r1-eth3.pcap. To stop packet capture:
r1 kill %tcpdump


# How to run Q2 code














