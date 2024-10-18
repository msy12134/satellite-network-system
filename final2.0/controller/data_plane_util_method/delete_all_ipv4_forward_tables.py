#运行此脚本，删除所有交换机关于ipv4转发的流表信息
from p4utils.utils.sswitch_thrift_API import SimpleSwitchThriftAPI
from typing import List
controller_list:List[SimpleSwitchThriftAPI]=[]
for i in range(9090,9210):
    controller=SimpleSwitchThriftAPI(i)
    controller_list.append(controller)
print(len(controller_list))
for i in controller_list:
    i.table_clear("MyIngress.ipv4_lpm")
    i.table_clear("MyIngress.ipv4_dst_memory")
    if i.table_num_entries("MyIngress.ipv4_lpm")==0 and i.table_num_entries("MyIngress.ipv4_dst_memory"):
        print(f"交换机{i}流表已经清空了")
