from simple_switch_controller import SimpleSwitchController,SimpleSwitchThriftAPI
from controller_switch_controller import ControllerSwitchController
from common import topo
import redis
controller_switch_for_domain1='s00303'  #redis_db=0
controller_switch_for_domain2='s00309'  #redis_db=1
controller_switch_for_domain3='s00803'  #redis_db=2
controller_switch_for_domain4='s00809'  #redis_db=3

controller_switch_name_list=['s00303','s00309','s00803','s00809']

domian1=['s0'+str(x).zfill(2)+str(y).zfill(2) for x in range(1,6) for y in range(1,7)] #每个domain中有三十个交换机
domian2=['s0'+str(x).zfill(2)+str(y).zfill(2) for x in range(1,6) for y in range(7,13)]
domian3=['s0'+str(x).zfill(2)+str(y).zfill(2) for x in range(6,11) for y in range(1,7)]
domian4=['s0'+str(x).zfill(2)+str(y).zfill(2) for x in range(6,11) for y in range(7,13)]

if __name__=='__main__':

    switch_name_list=topo.get_switches().keys()
    thrift_port_list=[topo.get_thrift_port(i) for i in switch_name_list]
    sniff_port_list=[topo.get_cpu_port_intf(i)[:-1]+'1'for i in switch_name_list]

    list_controller=[]
    list_simple_switch=[]
    redis_db_number=0
    #for循环启动所有交换机
    for i in zip(switch_name_list,thrift_port_list,sniff_port_list):
        if i[0] in controller_switch_name_list:
            item=ControllerSwitchController(
                sniff_port=i[2],
                bmv2_client=SimpleSwitchThriftAPI(i[1]),
                switch_name=i[0],
                redis_connection=redis.Redis(db=redis_db_number,decode_responses=True)
            )
            item.start_receiving_cpu_packet()
            redis_db_number+=1
            list_controller.append(item)
        else:
            item=SimpleSwitchController(
                    bmv2_client=SimpleSwitchThriftAPI(i[1]),
                    switch_name=i[0],
                    sniff_port=i[2]
                )
            item.start_receiving_cpu_packet()
            list_simple_switch.append(item)
    
        
