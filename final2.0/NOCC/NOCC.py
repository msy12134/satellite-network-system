from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import redis
import sys
from loguru import logger
import json
sys.path.insert(0,"/home/mao/Desktop/systerm-code/final2.0")
from controller.sdn_controller.mysql_init import Session,DeviceIdMappingIpv4Address,DomainIdMappingSwitchName
from controller.sdn_controller.common import topo
class PacketInfoDict(BaseModel):
    deviceid:int
    dst_addr:str


app=FastAPI()

@app.post("/route",description="接收控制器发出的请求，计算跨域通信的路径")
def calculate_route(packet_info_dict:PacketInfoDict):
    logger.info(f"接收到的数据为：{packet_info_dict}")
    db=Session()
    switch_from_name=db.query(DeviceIdMappingIpv4Address).filter(DeviceIdMappingIpv4Address.device_id==packet_info_dict.deviceid).first().switch_name
    switch_to_name=db.query(DeviceIdMappingIpv4Address).filter(DeviceIdMappingIpv4Address.ipv4_address==packet_info_dict.dst_addr).first().switch_name
    route=topo.get_shortest_paths_between_nodes(switch_from_name,"h"+switch_to_name[1:])[0]
    list_1,list_2,list_3,list_4=[],[],[],[]
    for i in range(len(route)-1):
        port=topo.node_to_node_port_num(route[i],route[i+1])
        ipv4_dst=topo.get_host_ip('h'+route[i][1:])
        mac=topo.node_to_node_mac(route[i+1],route[i])
        device_id=(db.query(DeviceIdMappingIpv4Address).filter(DeviceIdMappingIpv4Address.ipv4_address==ipv4_dst).first()).device_id
        dst_addr=str(topo.get_host_ip(route[-1]))
        info_dict={"port":port,"ipv4_dst":ipv4_dst,"mac":mac,"deviceid":device_id,"dst_addr":dst_addr}
        if db.query(DomainIdMappingSwitchName).filter(DomainIdMappingSwitchName.switch_name==route[i]).first().domain_id==1:
            list_1.append(info_dict)
        if db.query(DomainIdMappingSwitchName).filter(DomainIdMappingSwitchName.switch_name==route[i]).first().domain_id==2:
            list_2.append(info_dict)
        if db.query(DomainIdMappingSwitchName).filter(DomainIdMappingSwitchName.switch_name==route[i]).first().domain_id==3:
            list_3.append(info_dict)
        if db.query(DomainIdMappingSwitchName).filter(DomainIdMappingSwitchName.switch_name==route[i]).first().domain_id==4:
            list_4.append(info_dict)
    for key,value in {0:list_1,1:list_2,2:list_3,3:list_4}.items():
        if value!=[]:
            r=redis.Redis(db=key,decode_responses=True)
            r.set(str(packet_info_dict.deviceid)+"to"+packet_info_dict.dst_addr,json.dumps(value))
if __name__=="__main__":
    uvicorn.run(app,port=8080)