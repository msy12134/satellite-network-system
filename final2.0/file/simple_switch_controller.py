from p4utils.utils.sswitch_thrift_API import SimpleSwitchThriftAPI
import threading
from scapy.all import sniff,Packet
from scapy.layers.inet import IP
from header_definition import response_t
class SimpleSwitchController:
    def __init__(self,sniff_port:str,bmv2_client:SimpleSwitchThriftAPI,switch_name:str):
        self.sniff_port=sniff_port
        self.bmv2_client=bmv2_client
        self.switch_name=switch_name
    def start_receiving_cpu_packet(self):
        sniff_thread=threading.Thread(target=sniff(iface=self.sniff_port,prn=self.cpu_packet_dealer))
        sniff_thread.start()
        print(f"网络端口{self.sniff_port}开始在后台监听cpu数据包")
    def cpu_packet_dealer(self,packet:Packet):
        print(f"{self.sniff_port[0:6]}的CPUport收到数据包:\n{packet.show()}")
        if packet[IP].proto==151:
            packet_info_dict=self.deal_with_response_cpu_packet(packet)
            mac:str=packet_info_dict["dst_port_mac"] 
            self.bmv2_client.table_add("ipv4_lpm",'ipv4_forward',[str(packet_info_dict["dst_addr"])],[mac,str(packet_info_dict["port"])])
            self.bmv2_client.table_add("ipv4_dst_memory",'ipv4_forward',[str(packet_info_dict["dst_addr"])],[mac,str(packet_info_dict["port"])])
    def deal_with_response_cpu_packet(self,packet:Packet):
        deviceid=packet[response_t].deviceid
        dst_addr=packet[response_t].dst_addr
        port=packet[response_t].port
        dst_port_mac=packet[response_t].dst_port_mac
        return  {"deviceid":deviceid,"dst_addr":dst_addr,"port":port,"dst_port_mac":dst_port_mac}


    