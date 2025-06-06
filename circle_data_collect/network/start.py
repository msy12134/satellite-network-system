from scapy.all import *
from headers_definition import *
import time
import json
from init_table import topo
def init_route_dict():
    route_dict={}
    with open("circle.txt","r") as f:
        content=[line[:-1] for line in f.readlines()]
        cur_circle_id=1
        cur_topo=None
        for line in content:
            if route_dict =={}:
                cur_topo=line[1:]
                route_dict[line[1:]]={}
            elif line.startswith("#"):
                cur_topo=line[1:]
                route_dict[line[1:]]={}
            elif not line.startswith("#"):
                route_dict[cur_topo][cur_circle_id]=line
                cur_circle_id+=1
    with open("route_dict.json","w") as f:
        json.dump(route_dict,f,indent=4)
    return route_dict

def extract_sr_info_from_circle_str(circle_str,topo):
    circle_list=circle_str.split("->")
    if circle_str.startswith("12"):
        circle_list=["L"+i for i in circle_list]
    else:
        circle_list=["R"+i for i in circle_list]
    pass

def create_packet(sr_info_list,circle_id):
    # Create a packet with the defined headers
    sr_header=sr_header_t(sr_segment_num=len(sr_info_list))
    sr_segments = [sr_t(sr_info=info) for info in sr_info_list]
    int_header=int_header_t(int_segment_num=0, flag=1, circle_id=circle_id)
    packet=circle_data_collect(
        sr_header=sr_header,
        sr=sr_segments,
        int_header=int_header,
    )
    return packet

if __name__ == "__main__":
    # packet = create_packet()
    # # Display the packet
    # while True:
    #     sendp(packet, iface="h12-eth0")  # Replace "eth0" with your network interface
    #     print(packet.show())
    #     time.sleep(1)
    route_dict=init_route_dict()
    left_packets=[]
    right_packets=[]

