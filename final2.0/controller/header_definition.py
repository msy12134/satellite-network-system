from scapy.all import Packet,IPField,BitField,bind_layers
from scapy.layers.l2 import Ether,MACField
from scapy.layers.inet import IP


class request_t(Packet):
    name="request"
    fields_desc=[
        BitField('deviceid',0,8),
        IPField('dst_addr','0.0.0.0')
    ]

class response_t(Packet):
    name="response"
    fields_desc=[
        BitField('deviceid',0,8),
        IPField('dst_addr','0.0.0.0'),
        BitField('port',0,9),
        BitField('dst_port_mac',0,48),
        BitField('padding',0,7)
    ]

bind_layers(Ether,IP)
bind_layers(IP,request_t,proto=150)
bind_layers(IP,response_t,proto=151)