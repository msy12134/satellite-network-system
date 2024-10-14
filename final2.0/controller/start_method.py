from p4utils.utils.helper import load_topo
from p4utils.utils.sswitch_thrift_API import SimpleSwitchThriftAPI
from p4utils.utils.topology import NetworkGraph
from demo_controller import mycontroller 
#为每一个交换机添加一个控制器
def place_controller_for_every_switch(topo:NetworkGraph):
    """为拓扑中的每个交换机设置一个关联的控制器.

    Args:
        topo: load_topo(拓扑json文件的具体路径)方法的返回对象

    Returns:
        dict:字典中的键是每个交换机的名称，字典的值是对应交换机的控制器对象
    """
    switch_name_list=list(topo.get_p4switches().keys())
    switch_thrift_port_list=[topo.get_thrift_port(i) for i in switch_name_list]
    controller_dict={}
    for i in list(zip(switch_name_list,switch_thrift_port_list)):
        controller_dict[i[0]]=SimpleSwitchThriftAPI(int(i[1]))
    return controller_dict
    

#在部署完相应的p4程序添加转发流表，让两个终端自动ping通
def implement_ping_between_two_terminals(host1:str,host2:str,dict:dict,topo:NetworkGraph):
    """使得拓扑中的host1主机和host2主机可以ping通.

    Args:
        host1(str): 终端1的名称
        host2(str): 终端2的名称
        dict(dict): place_controller_for_every_switch方法的返回对象
        topo: load_topo(拓扑json文件的具体路径)方法的返回对象

    Returns:
        None: 
    """
    route=topo.get_shortest_paths_between_nodes(host1,host2)[0]
    print(route)
    host1_ip,host2_ip=topo.get_host_ip(host1),topo.get_host_ip(host2)
    for i in range(1,len(route)-1):
        port_right=topo.node_to_node_port_num(route[i],route[i+1])
        mac_right=topo.node_to_node_mac(route[i+1],route[i])
        mac_left=topo.node_to_node_mac(route[i-1],route[i])
        port_left=topo.node_to_node_port_num(route[i],route[i-1])
        dict[route[i]].table_add('ipv4_lpm','ipv4_forward',[host2_ip],[mac_right,str(port_right)])
        dict[route[i]].table_add('ipv4_lpm','ipv4_forward',[host1_ip],[mac_left,str(port_left)])
        dict[route[i]].table_add('ipv4_dst_memory','ipv4_forward',[host2_ip],[mac_right,str(port_right)])
        dict[route[i]].table_add('ipv4_dst_memory','ipv4_forward',[host1_ip],[mac_right,str(port_left)])
        print(f"交换机{route[i]}的流表初始化完成,可以和域内控制器ping通")


def make_every_switch_knows_its_CPU_PORT(topo:NetworkGraph,dict:dict):
    """使得每个交换机都配置查找cpu port的流表项（每个交换机只有一条）.

    Args:
        topo: load_topo(拓扑json文件的具体路径)方法的返回对象
        dict(dict): place_controller_for_every_switch方法的返回对象
    
    Returns:
        None: 
    """
    switch_name_list=list(topo.get_p4switches().keys())
    switch_cpu_port=[topo.get_cpu_port_index(i) for i in switch_name_list]
    dict_switchname_to_cpuport={i[0]:i[1] for i in list(zip(switch_name_list,switch_cpu_port))}
    result_list=[]
    for i in dict:
        result=dict[i].table_add('set_cpu_port_for_this_packet','set_cpu_port',["0x0800"],[str(dict_switchname_to_cpuport[i])])
        if isinstance(result,int):
            result_list.append(result)
    if len(result_list)==len(switch_name_list):
        print(f"CPU 流表添加成功，总共添加了{len(result_list)}条")
    else:
        print("添加流表过程中出现错误，请仔细检查")

def make_every_switch_knows_its_controller_ipv4(controller_ipv4:str,controller_dict:dict):
    """使得每个交换机都配置查找域内controller的流表项（每个交换机只有一条）.

    Args:
        controller_ipv4(str)：域内控制器的ipv4地址，例如 '10.0.5.15'
        controller_dict(dict): place_controller_for_every_switch方法的返回对象
    
    Returns:
        None: 
    """
    for i in controller_dict:
        controller_dict[i].table_add('table_set_packet_ipv4dst_to_controllerip','set_packet_ipv4dst_to_controllerip',["0x0800"],[controller_ipv4])


def make_every_switch_have_its_own_deviceID(controller_dict:dict):
    """使得每个交换机都配置对应的deviceID信息.

    Args:
        controller_dict(dict): place_controller_for_every_switch方法的返回对象
    
    Returns:
        dict: 字典的键是交换机的名字，对应的值是每个交换机的deviceID 
    """
    deviceID=1
    switchname_to_deveiceID_dict={}
    for i in controller_dict:
        result=controller_dict[i].table_add('set_deviceid','set_deviceid_in_request',["0x0800"],[str(deviceID)])
        controller_dict[i].table_add('if_the_deviceid_hit','ipv4_forward',[str(deviceID)],['00:00:00:00:00:00',"255"])
        switchname_to_deveiceID_dict[i]=deviceID
        deviceID+=1
    return switchname_to_deveiceID_dict


def get_controller_domain(x_from:str,x_to:str,y_from:str,y_to:str):
    """.

    Args:
        
    Returns:
        list[str]: 字典的键是交换机的名字，对应的值是每个交换机的deviceID 
    """
    domain=['s0'+str(x).zfill(2)+str(y).zfill(2) for x in range(int(x_from),int(x_to)+1) for y in range(int(y_from),int(y_to)+1)]
    return domain
# if __name__=='__main__':
#     topo = load_topo('/home/mao/Desktop/systerm-code/final/network/topology.json')
#     controller_dict=place_controller_for_every_switch(topo)
#     print(f"交换机控制器如下：{controller_dict}")
#     make_every_switch_knows_its_CPU_PORT(topo,controller_dict)
#     simple_switch_connect_host_list=[x for x in list(topo.get_hosts().keys()) if x!='h00309']
#     list=[(x,y) for x in ["h00309"] for y in simple_switch_connect_host_list]
#     for i in list:
#         implement_ping_between_two_terminals(i[0],i[1],controller_dict,topo)
#     make_every_switch_knows_its_controller_ipv4(topo.get_host_ip("h00309"),controller_dict)
#     switch_to_deviceID_dict= make_every_switch_have_its_own_deviceID(controller_dict)
#     print(switch_to_deviceID_dict)

#     print("-------------各台交换机流表初始化完毕------------")


#     for i in controller_dict:
#         sniff_port_name=i+"-cpu-eth1"
#         mycontroller(sniff_port_name,controller_dict[i],switch_to_deviceID_dict,topo).start_receiving_cpu_packet()

    

