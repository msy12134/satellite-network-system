from scapy.all import *
from headers_definition import *
def circle_packet_handler(packet):
    sr_header=sr_header_t(bytes(packet))
    sr_header.show()
    int_header=int_header_t(bytes(sr_header.payload))
    int_header.show()
    
    int_segment=int_t(bytes(int_header.payload))
    int_segment.show()
    int_segment=int_t(bytes(int_segment.payload))
    int_segment.show()
    


def save_int_info_to_database(databases,table,int_segment):#databases指的是具体的拓扑，table指代具体的环路
    """ Save INT segment information to the database."""
    pass
sniff(iface="h11-eth0", prn=circle_packet_handler)