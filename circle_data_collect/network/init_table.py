from p4utils.utils.helper import load_topo
from p4utils.utils.sswitch_thrift_API import SimpleSwitchThriftAPI
import json
topo = load_topo("topology.json")


if __name__ == "__main__":
        
    refer_dict={}#键为交换机的名字，值为字典，端口号对应sr信息

    left_domain=[i for i in  list(topo.get_switches().keys()) if i.startswith("L")]#4x3拓扑
    right_domain=[i for i in  list(topo.get_switches().keys()) if i.startswith("R")]#3x3拓扑
    for switch in left_domain+right_domain:
        refer_dict[switch]={}
        thrift_port=topo.get_thrift_port(switch)
        thrift_ip=topo.get_thrift_ip(switch)
        controller=SimpleSwitchThriftAPI(thrift_port,thrift_ip)
        suffix=switch[1:]
        ports=[topo.interface_to_port(switch,interface) for interface in topo.get_interfaces(switch)]
        controller.table_clear("sr_table")
        controller.table_clear("swid")
        controller.table_add('swid',"set_swid",["1"],[str(suffix)])
        for port in ports:
            controller.table_add("sr_table","sr_forward",[str(suffix)+str(port)],[str(port)])
            refer_dict[switch][port]=str(suffix)+str(port)
    with open("refer_dict.json","w") as f:
        json.dump(refer_dict,f,indent=4)


