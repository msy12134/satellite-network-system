from scapy.all import *
from headers_definition import *
import time
import json
from typing import List
from init_table import topo
from p4utils.utils.topology import NetworkGraph
import multiprocessing as mp
from scapy.all import sendp
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

def extract_sr_info_from_circle_str(circle_str:str,topo:NetworkGraph,refer_dict) -> List[int]: # type: ignore
    circle_list=circle_str.split("->")
    if circle_str.startswith("12"):
        circle_list=["L"+i for i in circle_list]+["h12"]
    else:
        circle_list=["R"+i for i in circle_list]+["h3"]
    sr_info_list=[]
    for index in range(len(circle_list)-1):
        port=topo.node_to_node_port_num(circle_list[index], circle_list[(index + 1)])
        sr_info_list.append(int(refer_dict[circle_list[index]][str(port)]))
    print(f"Extracted SR info: {sr_info_list}")
    return sr_info_list
def create_packet(sr_info_list:List[int],circle_id:int): # type: ignore
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

def send_packet(packet,iface:str):
    """Send the packet on the specified interface."""
    sendp(packet, iface=iface,count=10000,inter=0.1)  # Replace "eth0" with your network interface


if __name__ == "__main__":
    # packet = create_packet()
    # # Display the packet
    # while True:
    #     sendp(packet, iface="h12-eth0")  # Replace "eth0" with your network interface
    #     print(packet.show())
    #     time.sleep(1)
    with open("refer_dict.json","r") as f:
        refer_dict=json.load(f)
    left_packet_list=[]#h12
    right_packet_list=[]#h3
    route_dict=init_route_dict()
    for topo_name,circle_dict in route_dict.items():
        for circle_id,circle_str in circle_dict.items():
            sr_info=extract_sr_info_from_circle_str(circle_str, topo, refer_dict)
            packet=create_packet(sr_info_list=sr_info,circle_id=int(circle_id))
            if circle_str.startswith("12"):
                left_packet_list.append(packet)
            else:
                right_packet_list.append(packet)
    print(f"Left packet list length: {len(left_packet_list)}")
    print(f"Right packet list length: {len(right_packet_list)}")
    with mp.Pool(processes=len(right_packet_list)) as pool:
        pool.starmap(send_packet, [(packet, "h3-eth0") for packet in right_packet_list])