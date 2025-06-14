from scapy.all import *
from headers_definition import *
import json
def circle_packet_handler(packet):
    """专门用来解析收到的环路数据包"""
    result={"int_segment_num":0,"circle_id":0,"int_info":[]}
    sr_header=sr_header_t(bytes(packet))
    if sr_header.sr_segment_num != 0:
        return
    int_header=int_header_t(bytes(sr_header.payload))
    int_segment_num,circle_id=int_header.int_segment_num, int_header.circle_id
    result["int_segment_num"]=int_segment_num
    result["circle_id"]=circle_id
    for _ in range(int_segment_num):
        int_segment=int_t(bytes(int_header.payload))
        int_info={
            "switch_id":int_segment.switch_id,
            "ingress_port":int_segment.ingress_port,
            "egress_port":int_segment.egress_port,
            "ingress_timestamp":int_segment.ingress_timestamp,
            "egress_timestamp":int_segment.egress_timestamp,
        }
        result["int_info"].append(int_info)
        int_header=int_segment
    print(f"Received INT packet: {result}")
    save_int_info_to_file(result)
    


def save_int_info_to_file(parsed_packet_info):#databases指的是具体的拓扑，table指代具体的环路
    """ 把解析后的环路数据包信息保存到文件中 """
    circle_id= parsed_packet_info["circle_id"]
    with open(f"data/circle_{circle_id}.txt", "a") as f:
        f.write(json.dumps(parsed_packet_info) + "\n")
if __name__ == "__main__":
    sniff(iface="h12-eth0", prn=circle_packet_handler)