from scapy.all import *

class sr_header_t(Packet):
    name = "sr_header_t"
    fields_desc=[
        BitField("sr_segment_num", 0, 8)  
    ]
class sr_t(Packet):
    name = "sr"
    fields_desc=[
        BitField("sr_info", 0, 8)
    ]
class int_header_t(Packet):
    name = "int_header"
    fields_desc=[
        BitField("int_segment_num", 0, 8),
        BitField("flag", 0, 8),
        BitField("circle_id", 0, 8)
    ]
class int_t(Packet):
    name = "int"
    fields_desc=[
        BitField("switch_id", 0, 8),
        BitField("ingress_port", 0, 8),
        BitField("egress_port", 0, 8),
        BitField("ingress_timestamp", 0, 48),
        BitField("egress_timestamp", 0, 48)
    ]
class circle_data_collect(Packet):
    name = "circle_data_collect"
    fields_desc=[
        PacketField("sr_header", sr_header_t(), sr_header_t),
        PacketListField("sr", [], sr_t, count_from=lambda pkt: pkt.sr_header.sr_segment_num if pkt.sr_header else 0),
        PacketField("int_header", int_header_t(), int_header_t),
        PacketListField("int", [], int_t, count_from=lambda pkt: pkt.int_header.int_segment_num if pkt.int_header else 0)
    ]
