from p4utils.utils.sswitch_thrift_API import SimpleSwitchThriftAPI
import threading
from scapy.all import sniff,Packet,sendp
from header_definition import request_t,response_t
from scapy.layers.inet import IP,Ether
import redis
import json
from typing import Dict,List
import requests
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
class ControllerSwitchController:
    __slots__=['sniff_port','bmv2_client','switch_name','redis_connection']
    def __init__(self,sniff_port:str,bmv2_client:SimpleSwitchThriftAPI,switch_name:str,redis_connection:redis.Redis):
        self.sniff_port=sniff_port
        self.bmv2_client=bmv2_client
        self.switch_name=switch_name
        self.redis_connection=redis_connection
    def start_receiving_cpu_packet(self):
        sniff_thread=threading.Thread(target=sniff,kwargs={'iface':self.sniff_port,'prn':self.cpu_packet_dealer})
        sniff_thread.start()
        print(f"网络端口{self.sniff_port}开始在后台监听cpu数据包")
    def cpu_packet_dealer(self,packet:Packet):
        print(f"{self.sniff_port[0:6]}的CPUport收到数据包:")
        if packet[IP].proto==151:
            packet_info_dict=self.deal_with_response_cpu_packet(packet)
            mac=packet_info_dict["dst_port_mac"] 
            self.bmv2_client.table_add("ipv4_lpm",'ipv4_forward',[str(packet_info_dict["dst_addr"])],[mac,str(packet_info_dict["port"])])
            self.bmv2_client.table_add("ipv4_dst_memory",'ipv4_forward',[str(packet_info_dict["dst_addr"])],[mac,str(packet_info_dict["port"])])
        elif packet[IP].proto==150:
            packet_info_dict=self.deal_with_request_cpu_packet(packet)
            print(f"解析出的的request包信息为:{packet_info_dict}")
            value=self.redis_connection.get(f"{packet_info_dict['deviceid']}to{packet_info_dict['dst_addr']}")
            if value:
                self.parse_redis_info_and_send_the_response_packet_to_each_destination(value)
            else:
                #询问NOCC后端服务
                print(f"询问NOCC")
                self.ask_the_nocc_for_help(packet_info_dict)
    def deal_with_response_cpu_packet(self,packet:Packet):
        deviceid=packet[response_t].deviceid
        dst_addr=packet[response_t].dst_addr
        port=packet[response_t].port
        dst_port_mac=packet[response_t].dst_port_mac
        return  {"deviceid":deviceid,"dst_addr":dst_addr,"port":port,"dst_port_mac":dst_port_mac}
    def deal_with_request_cpu_packet(self,packet:Packet):
        deviceid=packet[request_t].deviceid
        dst_addr=packet[request_t].dst_addr
        return {"deviceid": deviceid,"dst_addr":dst_addr}
    def make_a_response_packet(self,deviceid:int,dst_addr:str,port:int,mac:str,ipv4:str):
        packet=Ether(src="00:11:22:33:44:55",dst="00:11:22:33:44:77",type=0x0800)/IP(dst=ipv4,proto=151)/\
        response_t(deviceid=deviceid,dst_addr=dst_addr,port=port,dst_port_mac=mac)
        return packet
    def parse_redis_info_and_send_the_response_packet_to_each_destination(self,value:str):
        start=int(datetime.now().timestamp()*1000)
        packet_list=[]
        parsed_value:List[Dict[str,str]]=json.loads(value)
        for single_packet_info in parsed_value:
            port=single_packet_info["port"]
            ipv4_dst=single_packet_info["ipv4_dst"]#接收这个response包的ipv4地址
            mac=single_packet_info["mac"]
            deviceid=single_packet_info["deviceid"]
            dst_addr=single_packet_info["dst_addr"]
            packet_list.append(self.make_a_response_packet(int(deviceid),str(dst_addr),int(port),str(mac),str(ipv4_dst)))
        with ThreadPoolExecutor(max_workers=30) as executor:
            executor.map(lambda packet: sendp(packet,iface=self.sniff_port),packet_list)
        end=int(datetime.now().timestamp()*1000)
        print(f"控制器{self.switch_name}把response发出去总共用了：{end-start}ms")
        
    def ask_the_nocc_for_help(self,packet_info_dict:Dict):
        start=int(datetime.now().timestamp()*1000)
        response=requests.post('http://127.0.0.1:8080/route',json=packet_info_dict)
        end=int(datetime.now().timestamp()*1000)
        print(f"控制器{self.switch_name}询问NOCC总共用了：{end-start}ms")
        if response.status_code==200:
            print(f"控制器{self.switch_name}请求NOCC服务成功")
            
            
