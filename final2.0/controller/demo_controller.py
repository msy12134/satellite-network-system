import aioconsole.console
from scapy.all import sniff,Packet
import threading
import deal_packet
from scapy.layers.inet import IP
from scapy.all import sendp
from p4utils.utils.sswitch_thrift_API import SimpleSwitchThriftAPI
from p4utils.utils.topology import NetworkGraph
import requests
class mycontroller:
    def __init__(self,sniff_port:str,controller:SimpleSwitchThriftAPI,deviceid_switchname_dict:dict,topo:NetworkGraph,domainid:int,fake_database=None,hot_switch_ip:str =None,switchname:str =None):
        self.sniff_port=sniff_port
        self.controller=controller
        self.deviceid_switchname_dict=deviceid_switchname_dict
        self.topo=topo
        self.domainid=domainid
        self.fake_database=fake_database
        self.hot_switch_ip=hot_switch_ip
        self.switchname=switchname
    def start_receiving_cpu_packet(self):
        sniff_thread=threading.Thread(target=self.__sniff_packet)
        sniff_thread.start()
        print(f"网络端口{self.sniff_port}开始在后台监听cpu数据包")

    def __sniff_packet(self):
        sniff(iface=self.sniff_port,prn=self.__packet_deal)
        
    def __packet_deal(self,packet:Packet):
        print(f"{self.sniff_port[0:6]}的CPUport收到数据包")
        packet.show()
        if packet[IP].proto==151:  #普通交换机收到response数据包直接插表
            dict=deal_packet.deal_packet_for_simple_switch(packet)
            mac_int=dict["dst_port_mac"] #这时得到的mac地址是一个int类型的
            mac_hex = f'{mac_int:012x}'  # 转换为 12 位的十六进制数
            mac_str = ':'.join(mac_hex[i:i+2] for i in range(0, 12, 2))
            self.controller.table_add("ipv4_lpm",'ipv4_forward',[str(dict["dst_addr"])],[mac_str,str(dict["port"])])
            self.controller.table_add("ipv4_dst_memory",'ipv4_forward',[str(dict["dst_addr"])],[mac_str,str(dict["port"])])
        elif packet[IP].proto==150: #控制交换机收到request数据包解析请求，构造response
            dict=deal_packet.deal_packet_for_controller_switch(packet)
            print(f"解析出的request信息：{dict}")
            switch_name=""
            for i in self.deviceid_switchname_dict:
                if int(self.deviceid_switchname_dict[i])==int(dict["deviceid"]):
                    switch_name=i
                    self.switchname=switch_name
                    break
            print(f"这个deviceid对应的交换机名称是{switch_name}")
            print(f"这个request包的目的地址是:{dict['dst_addr']},对应终端：{self.topo.get_host_name(str(dict['dst_addr']))}")
            if self.hot_switch_ip is None:
                if 's'+self.topo.get_host_name(dict["dst_addr"])[1:] not in self.deviceid_switchname_dict:
                    self.__ask_the_NOCC_for_help(dict)
                else:
                    self.__the_switch_is_domain_owned_make_route_now(switch_name,dict)
            else:
                if self.hot_switch_ip==dict["dst_addr"]:
                    self.__use_the_fakedatabase_info(switch_name,dict)
                else:
                    print(f"预缓存信息虽然有但是用不上")
                    if 's'+self.topo.get_host_name(dict["dst_addr"])[1:] not in self.deviceid_switchname_dict:
                        self.__ask_the_NOCC_for_help(dict)
                    else:
                        self.__the_switch_is_domain_owned_make_route_now(switch_name,dict)

    def __the_switch_is_domain_owned_make_route_now(self,switch_name,dict):#域内可以处理的包就用这个函数，传入请求交换机的名字和解析出来的request包信息
        print(f"这个包的目的地址在自治域内，可以域内解决")
        hostname=self.topo.get_host_name(str(dict["dst_addr"]))
        route=self.topo.get_shortest_paths_between_nodes(switch_name,hostname)[0]#('s1','s2','s3','h1')
        for i in range(len(route)-1):
            port=self.topo.node_to_node_port_num(route[i],route[i+1])
            ipv4dst=self.topo.get_host_ip('h'+route[i][1:])
            mac=self.topo.node_to_node_mac(route[i+1],route[i])
            deviceid=int(self.deviceid_switchname_dict[route[i]])
            dst_addr=str(self.topo.get_host_ip(route[-1]))
            response=deal_packet.make_a_response_packet(int(deviceid),dst_addr,int(port),mac,str(ipv4dst))
            sendp(response,iface=self.sniff_port)
    def __ask_the_NOCC_for_help(self,dict):#域内无法处理的包而且没有预缓存的信息的就向NOCC询问,dict是解析出来的request请求
        print(f"该目的ipv4地址超出了自治域范围,向OCC询问信息")
        response=requests.get(f"http://127.0.0.1:8000/{self.domainid}/from/{dict['deviceid']}/to/{dict['dst_addr']}")
        table_info_for_each_switch=response.json()
        print(f"接收到的OCC响应信息如下：{table_info_for_each_switch}")
        for i in table_info_for_each_switch:
            response_packet=deal_packet.make_a_response_packet(**table_info_for_each_switch[i])
            sendp(response_packet,iface=self.sniff_port)
    def __use_the_fakedatabase_info(self,switch_name,dict):#如果域缓存的信息 用得上就用预缓存的信息,switchname是请求交换机名称，dict是解析出来的相关信息
        print(f"预先缓存的信息可以用得上，使用预缓存的路径信息")
        print(f"预缓存的信息如下:{self.fake_database}")
        for i in self.fake_database:
            if i[0]==switch_name:
                print(f"在预缓存中找到了路径信息：{i}")
                route=i
                break
        for i in range(len(route)-1):
            if route[i] not in self.deviceid_switchname_dict and route[i+1] not in self.deviceid_switchname_dict:
                break
            else:
                port=self.topo.node_to_node_port_num(route[i],route[i+1])
                ipv4dst=self.topo.get_host_ip('h'+route[i][1:])
                mac=self.topo.node_to_node_mac(route[i+1],route[i])
                deviceid=int(self.deviceid_switchname_dict[route[i]])
                dst_addr=str(self.hot_switch_ip)
                response=deal_packet.make_a_response_packet(int(deviceid),dst_addr,int(port),mac,str(ipv4dst))
                sendp(response,iface=self.sniff_port)
            # if self.hot_switch_ip is None:
            #     print(f"没有预缓存的信息")
            #     if 's'+self.topo.get_host_name(dict["dst_addr"])[1:] not in self.deviceid_switchname_dict:
            #         print(f"该目的ipv4地址超出了自治域范围,向OCC询问信息")
            #         """
            #         第一种情况：
            #         如果单纯就是涉及到了跨域的通信，控制器向OCC构造一个请求获取流表信息，控制器将接收到的流表信息推送给对应的交换机，从而实现跨域通信
            #         第二种情况：
            #         预缓存就先不在这里写了，到时候直接写个命令行程序去调后端的服务就行
            #         """
            #         response=requests.get(f"http://127.0.0.1:8000/{self.domainid}/from/{dict['deviceid']}/to/{dict['dst_addr']}")
            #         table_info_for_each_switch=response.json()
            #         print(f"接收到的OCC响应信息如下：{table_info_for_each_switch}")
            #         for i in table_info_for_each_switch:
            #             response_packet=deal_packet.make_a_response_packet(**table_info_for_each_switch[i])
            #             sendp(response_packet,iface=self.sniff_port)
            #     else:
            #         hostname=self.topo.get_host_name(str(dict["dst_addr"]))
            #         route=self.topo.get_shortest_paths_between_nodes(switch_name,hostname)[0]#('s1','s2','s3','h1')
            #         for i in range(len(route)-1):
            #             port=self.topo.node_to_node_port_num(route[i],route[i+1])
            #             ipv4dst=self.topo.get_host_ip('h'+route[i][1:])
            #             mac=self.topo.node_to_node_mac(route[i+1],route[i])
            #             deviceid=int(self.deviceid_switchname_dict[route[i]])
            #             dst_addr=str(self.topo.get_host_ip(route[-1]))
            #             response=deal_packet.make_a_response_packet(int(deviceid),dst_addr,int(port),mac,str(ipv4dst))
            #             sendp(response,iface=self.sniff_port)
            # else:
            #     print(f"已经有了预缓存的信息")
            #     if self.hot_switch_ip!=dict["dst_addr"]:
            #         print(f"这个预缓存的信息用不上")
            #         if 's'+self.topo.get_host_name(dict["dst_addr"])[1:] not in self.deviceid_switchname_dict:
            #             print(f"该目的ipv4地址超出了自治域范围,向OCC询问信息")
            #             """
            #             第一种情况：
            #             如果单纯就是涉及到了跨域的通信，控制器向OCC构造一个请求获取流表信息，控制器将接收到的流表信息推送给对应的交换机，从而实现跨域通信
            #             第二种情况：
            #             预缓存就先不在这里写了，到时候直接写个命令行程序去调后端的服务就行
            #             """
            #             response=requests.get(f"http://127.0.0.1:8000/{self.domainid}/from/{dict['deviceid']}/to/{dict['dst_addr']}")
            #             table_info_for_each_switch=response.json()
            #             print(f"接收到的OCC响应信息如下：{table_info_for_each_switch}")
            #             for i in table_info_for_each_switch:
            #                 response_packet=deal_packet.make_a_response_packet(**table_info_for_each_switch[i])
            #                 sendp(response_packet,iface=self.sniff_port)
            #         else:
            #             hostname=self.topo.get_host_name(str(dict["dst_addr"]))
            #             route=self.topo.get_shortest_paths_between_nodes(switch_name,hostname)[0]#('s1','s2','s3','h1')
            #             for i in range(len(route)-1):
            #                 port=self.topo.node_to_node_port_num(route[i],route[i+1])
            #                 ipv4dst=self.topo.get_host_ip('h'+route[i][1:])
            #                 mac=self.topo.node_to_node_mac(route[i+1],route[i])
            #                 deviceid=int(self.deviceid_switchname_dict[route[i]])
            #                 dst_addr=str(self.topo.get_host_ip(route[-1]))
            #                 response=deal_packet.make_a_response_packet(int(deviceid),dst_addr,int(port),mac,str(ipv4dst))
            #                 sendp(response,iface=self.sniff_port)
            #     else:
            #         print("这个预缓存的信息能用上")
            #         print(self.fake_database)
            #         for i in self.fake_database:
            #             if i[0]==switch_name:
            #                 print(f"在预缓存中找到了路径信息：{i}")
            #                 route=i
            #                 break
            #         for i in range(len(route)-1):
            #             if route[i] not in self.deviceid_switchname_dict and route[i+1] not in self.deviceid_switchname_dict:
            #                 break
            #             else:
            #                 port=self.topo.node_to_node_port_num(route[i],route[i+1])
            #                 ipv4dst=self.topo.get_host_ip('h'+route[i][1:])
            #                 mac=self.topo.node_to_node_mac(route[i+1],route[i])
            #                 deviceid=int(self.deviceid_switchname_dict[route[i]])
            #                 dst_addr=str(self.hot_switch_ip)
            #                 response=deal_packet.make_a_response_packet(int(deviceid),dst_addr,int(port),mac,str(ipv4dst))
            #                 sendp(response,iface=self.sniff_port)


              
    