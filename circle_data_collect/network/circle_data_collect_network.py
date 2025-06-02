from p4utils.mininetlib.network_API import NetworkAPI


net = NetworkAPI()

# Network general options
net.setLogLevel('info')
net.enableCli()

left_region_switches=["L"+str(i) for i in range(1,13)]
right_region_switches=["R"+str(i) for i in range(1,10)]


for i in left_region_switches+right_region_switches:
    if i=="L11" or i=="L12":
        net.addP4Switch(i,cli_input=i+".txt")
    else:
        net.addP4Switch(i)
net.setP4SourceAll('switch.p4')

net.addHost("h12")
net.addHost("h3")
net.addHost("h11")

link_pair_left_region=[(1,2),(2,3),(4,5),(5,6),(7,8),(8,9),(10,11),(11,12),(1,4),(2,5),(3,6),(4,7),(5,8),(6,9),(7,10),(8,11),(9,12)]
link_pair_right_region=[(1,2),(2,3),(4,5),(5,6),(7,8),(8,9),(1,4),(2,5),(3,6),(4,7),(5,8),(6,9)]

for i in link_pair_left_region:
    net.addLink("L"+str(i[0]),"L"+str(i[1]))

for i in link_pair_right_region:
    net.addLink("R"+str(i[0]),"R"+str(i[1]))

net.addLink("L3","R1")
net.addLink("L12","h12")
net.addLink("R3","h3")
net.addLink("h11","L11")
net.mixed()

net.enablePcapDumpAll()
net.enableLogAll()

net.startNetwork()
