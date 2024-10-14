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

#运行上述脚本用来清空当前交换机中的关于ipv4转发的所有流表信息
# controller_list[0].table_clear("MyIngress.ipv4_dst_memory")
# print(controller_list[0].table_num_entries("MyIngress.ipv4_dst_memory"))