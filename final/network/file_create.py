from p4utils.utils.helper import load_topo
import os
topo=load_topo("/home/maomao/Desktop/satellite-network-system/final/network/topology.json")
raw_data=[  
            ('0602', '0209'), ('1006', '0508'), ('0206', '0407'), ('0111', '0204'), ('0408', '1008'),
            ('0405', '1002'), ('0110', '0906'), ('0711', '0304'), ('0808', '0211'), ('0310', '0303'),
            ('0502', '1012'), ('0912', '1003'), ('1003', '0502'), ('0810', '0503'), ('0406', '0711'),
            ('1012', '0901'), ('0508', '0611'), ('0603', '0711'), ('0704', '0812'), ('0104', '0806'),
            ('0201', '1002'), ('0103', '0408'), ('0901', '0208'), ('0201', '1009'), ('0408', '0910'),
            ('0103', '0109'), ('0512', '0608'), ('1012', '0503'), ('0805', '0203'), ('0511', '0910')
        ]
model_for_send="""
import time
from scapy.layers.l2 import Ether
from scapy.layers.inet import IP
from scapy.sendrecv import sendp
from scapy.arch import get_if_hwaddr
# 获取当前时间戳
timestamp = str(time.time())

# 创建以太网头部和IPv4头部，并将时间戳作为载荷

pkt = Ether(src=get_if_hwaddr("{send_iface}"), dst="ff:ff:ff:ff:ff:ff") / IP(dst="{dst_ipv4}",proto=155) / timestamp
sendp(pkt,iface="{send_iface}",count=50,realtime=True,inter=0.01)
"""

model_for_receive="""
import time
from scapy.all import sniff
from scapy.layers.inet import IP
# 定义处理接收到的数据包的函数
def packet_callback(pkt):
    if IP in pkt and pkt[IP].proto == 155:
        # 提取载荷，即时间戳
        timestamp_now = time.time()
        timestamp = pkt.load.decode('utf-8')
        print((timestamp_now-float(timestamp))*1000)

# 捕获数据包
sniff(prn=packet_callback, filter="ip",count=1,iface="{receive_iface}")
"""
file_path="/home/maomao/Desktop/satellite-network-system/final/network"
file_path=os.path.join(file_path,"between_domain")
os.makedirs(file_path)
for i in raw_data:
    host_from,host_to="h0"+i[0],"h0"+i[1]
    folder_name=os.path.join(file_path,host_from+"to"+host_to)
    os.makedirs(folder_name,exist_ok=True)
    with open(os.path.join(folder_name,"send.py"),"w") as file1:
        file_content=model_for_send.format(send_iface=host_from+"-eth0",dst_ipv4=topo.get_host_ip(host_to))
        file1.write(file_content)
    with open(os.path.join(folder_name,"receive.py"),"w") as file2:
        file_content=model_for_receive.format(receive_iface=i[1]+"-eth0")
        file2.write(file_content)

