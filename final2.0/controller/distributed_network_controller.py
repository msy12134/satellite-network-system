from start_method import *
import asyncio
topo = load_topo('/home/mao/Desktop/systerm-code/final/network/topology.json')
domain_1=get_controller_domain("01","05","07","12")
domain_2=get_controller_domain("06","10","07","12")
domain_3=get_controller_domain("01","05","01","06")
domain_4=get_controller_domain("06","10","01","06")
controller_switch_for_domain_1='s00309'
controller_switch_for_domain_2='s00809'
controller_switch_for_domain_3='s00303'
controller_switch_for_domain_4='s00803'

controller_dict=place_controller_for_every_switch(topo)
print(f"交换机控制器数量:{len(controller_dict)}")
make_every_switch_knows_its_CPU_PORT(topo,controller_dict)
switch_to_deviceID_dict=make_every_switch_have_its_own_deviceID(controller_dict)

controller_dict_domain1={}
controller_dict_domain2={}
controller_dict_domain3={}
controller_dict_domain4={}
for i in controller_dict:
    if i in domain_1:
        controller_dict_domain1.update({i:controller_dict[i]})
        implement_ping_between_two_terminals('h'+controller_switch_for_domain_1[1:],'h'+i[1:],controller_dict,topo)
    elif i in domain_2:
        controller_dict_domain2.update({i:controller_dict[i]})
        implement_ping_between_two_terminals('h'+controller_switch_for_domain_2[1:],'h'+i[1:],controller_dict,topo)
    elif i in domain_3:
        controller_dict_domain3.update({i:controller_dict[i]})
        implement_ping_between_two_terminals('h'+controller_switch_for_domain_3[1:],'h'+i[1:],controller_dict,topo)
    elif i in domain_4:
        controller_dict_domain4.update({i:controller_dict[i]})
        implement_ping_between_two_terminals('h'+controller_switch_for_domain_4[1:],'h'+i[1:],controller_dict,topo)
print(f"1:{len(controller_dict_domain1)},2:{len(controller_dict_domain2)},3:{len(controller_dict_domain3)},4:{len(controller_dict_domain4)}")
make_every_switch_knows_its_controller_ipv4(topo.get_host_ip('h'+controller_switch_for_domain_1[1:]),controller_dict_domain1)
make_every_switch_knows_its_controller_ipv4(topo.get_host_ip('h'+controller_switch_for_domain_2[1:]),controller_dict_domain2)
make_every_switch_knows_its_controller_ipv4(topo.get_host_ip('h'+controller_switch_for_domain_3[1:]),controller_dict_domain3)
make_every_switch_knows_its_controller_ipv4(topo.get_host_ip('h'+controller_switch_for_domain_4[1:]),controller_dict_domain4)



print(switch_to_deviceID_dict)
switch_to_deviceID_dict={'s00101': 1, 's00102': 2, 's00103': 3, 's00104': 4, 's00105': 5, 's00106': 6, 's00107': 7, 's00108': 8, 's00109': 9, 's00110': 10, 
                         's00111': 11, 's00112': 12, 's00201': 13, 's00202': 14, 's00203': 15, 's00204': 16, 's00205': 17, 's00206': 18, 's00207': 19, 's00208': 20, 
                         's00209': 21, 's00210': 22, 's00211': 23, 's00212': 24, 's00301': 25, 's00302': 26, 's00303': 27, 's00304': 28, 's00305': 29, 's00306': 30, 
                         's00307': 31, 's00308': 32, 's00309': 33, 's00310': 34, 's00311': 35, 's00312': 36, 's00401': 37, 's00402': 38, 's00403': 39, 's00404': 40, 
                         's00405': 41, 's00406': 42, 's00407': 43, 's00408': 44, 's00409': 45, 's00410': 46, 's00411': 47, 's00412': 48, 's00501': 49, 's00502': 50, 
                         's00503': 51, 's00504': 52, 's00505': 53, 's00506': 54, 's00507': 55, 's00508': 56, 's00509': 57, 's00510': 58, 's00511': 59, 's00512': 60, 
                         's00601': 61, 's00602': 62, 's00603': 63, 's00604': 64, 's00605': 65, 's00606': 66, 's00607': 67, 's00608': 68, 's00609': 69, 's00610': 70, 
                         's00611': 71, 's00612': 72, 's00701': 73, 's00702': 74, 's00703': 75, 's00704': 76, 's00705': 77, 's00706': 78, 's00707': 79, 's00708': 80, 
                         's00709': 81, 's00710': 82, 's00711': 83, 's00712': 84, 's00801': 85, 's00802': 86, 's00803': 87, 's00804': 88, 's00805': 89, 's00806': 90, 
                         's00807': 91, 's00808': 92, 's00809': 93, 's00810': 94, 's00811': 95, 's00812': 96, 's00901': 97, 's00902': 98, 's00903': 99, 's00904': 100, 
                         's00905': 101, 's00906': 102, 's00907': 103, 's00908': 104, 's00909': 105, 's00910': 106, 's00911': 107, 's00912': 108, 's01001': 109, 's01002': 110, 
                         's01003': 111, 's01004': 112, 's01005': 113, 's01006': 114, 's01007': 115, 's01008': 116, 's01009': 117, 's01010': 118, 's01011': 119, 's01012': 120}

switch_to_deviceID_dict_domain_1={}
switch_to_deviceID_dict_domain_2={}
switch_to_deviceID_dict_domain_3={}
switch_to_deviceID_dict_domain_4={}
for i in switch_to_deviceID_dict:
    if i in domain_1:
        switch_to_deviceID_dict_domain_1.update({i:switch_to_deviceID_dict[i]})
    elif i in domain_2:
        switch_to_deviceID_dict_domain_2.update({i:switch_to_deviceID_dict[i]})
    elif i in domain_3:
        switch_to_deviceID_dict_domain_3.update({i:switch_to_deviceID_dict[i]})
    elif i in domain_4:
        switch_to_deviceID_dict_domain_4.update({i:switch_to_deviceID_dict[i]})
for i in controller_dict:
    sniff_port_name=i+"-cpu-eth1"
    if i in domain_1:
        if i=="s00309":
            c1=mycontroller(sniff_port_name,controller_dict[i],switch_to_deviceID_dict_domain_1,topo,1)
            c1.start_receiving_cpu_packet()
        else:
            mycontroller(sniff_port_name,controller_dict[i],switch_to_deviceID_dict_domain_1,topo,1).start_receiving_cpu_packet()
    if i in domain_2:
        if i=="s00809":
            c2=mycontroller(sniff_port_name,controller_dict[i],switch_to_deviceID_dict_domain_2,topo,2)
            c2.start_receiving_cpu_packet()
        else:
            mycontroller(sniff_port_name,controller_dict[i],switch_to_deviceID_dict_domain_2,topo,2).start_receiving_cpu_packet()
    if i in domain_3:
        if i=="s00303":
            c3=mycontroller(sniff_port_name,controller_dict[i],switch_to_deviceID_dict_domain_3,topo,3)
            c3.start_receiving_cpu_packet()
        else:
            mycontroller(sniff_port_name,controller_dict[i],switch_to_deviceID_dict_domain_3,topo,3).start_receiving_cpu_packet()
    if i in domain_4:
        if i=="s00803":
            c4=mycontroller(sniff_port_name,controller_dict[i],switch_to_deviceID_dict_domain_4,topo,4)
            c4.start_receiving_cpu_packet()
        else:
            mycontroller(sniff_port_name,controller_dict[i],switch_to_deviceID_dict_domain_4,topo,4).start_receiving_cpu_packet()
hot_switch_name=input("enter the switch name:")#输入domain1中的某个交换机的名称
#得出其他三个域中的交换机到这个热点交换机的路径
route_list_domain2=[]
for i in domain_2:
    # route2=topo.get_shortest_paths_between_nodes(i,hot_switch_name)[0]
    # route2=list(route2)
    # for j in route2:
    #     if j not in domain_2:
    #         route2.remove(j)
    route_list_domain2.append(topo.get_shortest_paths_between_nodes(i,hot_switch_name)[0])
route_list_domain3=[]
for i in domain_3:
    #route3=topo.get_shortest_paths_between_nodes(i,hot_switch_name)[0]
    # route3=list(route3)
    # for j in route3:
    #     if j not in domain_3:
    #         route3.remove(j)
    route_list_domain3.append(topo.get_shortest_paths_between_nodes(i,hot_switch_name)[0])
route_list_domain4=[]
for i in domain_4:
    #route4=topo.get_shortest_paths_between_nodes(i,hot_switch_name)[0]
    # route4=list(route4)
    # for j in route4:
    #     if j not in domain_4:
    #         route4.remove(j)
    route_list_domain4.append(topo.get_shortest_paths_between_nodes(i,hot_switch_name)[0])
c2.hot_switch_ip=topo.get_host_ip("h"+hot_switch_name[1:])
c3.hot_switch_ip=topo.get_host_ip("h"+hot_switch_name[1:])
c4.hot_switch_ip=topo.get_host_ip("h"+hot_switch_name[1:])
print(c2.hot_switch_ip,c3.hot_switch_ip,c4.hot_switch_ip)
c2.fake_database=route_list_domain2
c3.fake_database=route_list_domain3
c4.fake_database=route_list_domain4

