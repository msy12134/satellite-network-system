import multiprocessing.queues
from fastapi import FastAPI,WebSocket
from ipaddress import IPv4Address
from p4utils.utils.topology import NetworkGraph
from p4utils.utils.helper import load_topo
import uvicorn
from typing import Dict
import multiprocessing
from typing import List
each_switch_and_its_switchid_dict={'s00101': 1, 's00102': 2, 's00103': 3, 's00104': 4, 's00105': 5, 's00106': 6, 's00107': 7, 's00108': 8, 's00109': 9, 's00110': 10, 
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
def get_controller_domain(x_from:str,x_to:str,y_from:str,y_to:str):
    """.

    Args:
        
    Returns:
        list[str]: 字典的键是交换机的名字，对应的值是每个交换机的deviceID 
    """
    domain=['s0'+str(x).zfill(2)+str(y).zfill(2) for x in range(int(x_from),int(x_to)+1) for y in range(int(y_from),int(y_to)+1)]
    return domain
domain_1=get_controller_domain("01","05","07","12")
domain_2=get_controller_domain("06","10","07","12")
domain_3=get_controller_domain("01","05","01","06")
domain_4=get_controller_domain("06","10","01","06")
topo = load_topo('/home/mao/Desktop/systerm-code/final/network/topology.json')
app=FastAPI()
domain_dict={"1":domain_1,"2":domain_2,"3":domain_3,"4":domain_4}


@app.get("/{domainid}/from/{deviceid}/to/{ip_address}")
def query_the_path_info(domainid:str,deviceid:int,ip_address:IPv4Address):
    destination_hostname=topo.get_host_name(str(ip_address))
    reversed_each_switch_and_its_switchid_dict={a:b for b,a in each_switch_and_its_switchid_dict.items()}
    the_query_device_name=reversed_each_switch_and_its_switchid_dict[deviceid]
    print(f"{domainid}想知道其中的{the_query_device_name}交换机去往{destination_hostname}的路径")
    route=topo.get_shortest_paths_between_nodes(the_query_device_name,destination_hostname)[0]
    print(f"OCC找到了最短路径：{route},开始构造路由表信息")
    table_entry_for_each_switch={}
    for i in range(len(route)-1):
        table_entry_info={}
        deviceid=each_switch_and_its_switchid_dict[route[i]]
        dst_addr=topo.get_host_ip(route[-1])
        port=topo.node_to_node_port_num(route[i],route[i+1])
        mac=topo.node_to_node_mac(route[i+1],route[i])
        ipv4dst=topo.get_host_ip("h"+route[i][1:])
        table_entry_info={"deviceid":int(deviceid),"dst_addr":str(dst_addr),"port":int(port),
                          "dst_port_mac":mac,"ipv4":str(ipv4dst)}
        table_entry_for_each_switch[route[i]]=table_entry_info
    print(f"构造的路由信息：{table_entry_for_each_switch}")
    return {key:value for key,value in table_entry_for_each_switch.items() if key in domain_dict[domainid]}


def calculate_other_switch_to_hot_switch(hotswitch:str,other:List[str],q:multiprocessing.Queue): #每个域内计算出到热点交换机的路径，放入队列中
    for i in other:
        q.put(topo.get_shortest_paths_between_nodes(i,hotswitch)[0])


connected_clients: Dict[str, WebSocket] = {}
@app.websocket("/ws/{domainid}")
async def websocket(websocket:WebSocket,domainid:str):
    await websocket.accept()
    connected_clients[domainid] = websocket
    print(connected_clients)
    data=await websocket.receive_text() #data应该就是某个域内交换机的名称
    print(f"receive data :{data} is going to be hot ")
    the_three_remain_domain_dict=domain_dict
    for i in domain_dict:
        if data in domain_dict[i]:
            delete_key=i
            break
    print(f"这个交换机来自域{delete_key}")
    del the_three_remain_domain_dict[delete_key]
    queue_dict:Dict[str,multiprocessing.Queue]={}
    for i in the_three_remain_domain_dict:
        q = multiprocessing.Queue()
        queue_dict[i] = q #每个域的存储结果都会在自己的队列中
    print(queue_dict)
    process=[]
    for i in the_three_remain_domain_dict:
        p=multiprocessing.Process(target=calculate_other_switch_to_hot_switch,args=(data,the_three_remain_domain_dict[i],queue_dict[i]))
        process.append(p)
        p.start()
    for p in process:
        p.join()
    number=0
    for i in queue_dict:
        while not queue_dict[i].empty():
            print(queue_dict[i].get())
            number+=1
    print(number)
if __name__=="__main__":
    uvicorn.run(app)
