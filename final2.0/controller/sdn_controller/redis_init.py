#初始化每个域内控制器的初始redis数据库
import redis
import json
from mysql_init import Session,DeviceIdMappingIpv4Address
from common import topo
from start import domian1,domian2,domian3,domian4
db=Session()
redis_db_number=0
for domain in [domian1,domian2,domian3,domian4]:
    r=redis.Redis(db=redis_db_number,decode_responses=True)
    redis_db_number+=1
    for switch_from in domain:
        for switch_to in domain:
            result:DeviceIdMappingIpv4Address=db.query(DeviceIdMappingIpv4Address).filter(DeviceIdMappingIpv4Address.switch_name==switch_from).first()
            switch_from_device_id=result.device_id
            route=topo.get_shortest_paths_between_nodes(switch_from,'h'+switch_to[1:])[0]  #("s1","s2","s3","h3")
            redis_key=str(switch_from_device_id)+"to"+topo.get_host_ip('h'+switch_to[1:])  #redis_key_example:"1to10.0.0.1"
            redis_value=[]
            for i in range(len(route)-1):
                info_dict={}
                port=topo.node_to_node_port_num(route[i],route[i+1])
                ipv4_dst=topo.get_host_ip('h'+route[i][1:])
                mac=topo.node_to_node_mac(route[i+1],route[i])
                device_id=(db.query(DeviceIdMappingIpv4Address).filter(DeviceIdMappingIpv4Address.ipv4_address==ipv4_dst).first()).device_id
                dst_addr=str(topo.get_host_ip(route[-1]))
                info_dict={"port":port,"ipv4_dst":ipv4_dst,"mac":mac,"deviceid":device_id,"dst_addr":dst_addr}
                redis_value.append(info_dict)
            r.set(redis_key,json.dumps(redis_value))
        




