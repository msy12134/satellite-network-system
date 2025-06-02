from scapy.all import *
from headers_definition import *
import time
def create_packet():
    # Create a packet with the defined headers
    sr_header=sr_header_t(sr_segment_num=2)
    sr_segments = [
        sr_t(sr_info=100),
        sr_t(sr_info=100)
    ]
    int_header=int_header_t(int_segment_num=0, flag=1, circle_id=1)
    packet=circle_data_collect(
        sr_header=sr_header,
        sr=sr_segments,
        int_header=int_header,
    )
    return packet

if __name__ == "__main__":
    packet = create_packet()
    # Display the packet
    while True:
        sendp(packet, iface="h12-eth0")  # Replace "eth0" with your network interface
        print(packet.show())
        time.sleep(1)
