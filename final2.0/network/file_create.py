from p4utils.utils.helper import load_topo
import os
topo=load_topo("/home/mao/Desktop/systerm-code/final/network/topology.json")
host_pairs_list = [
    ("h0707", "h0809"),  # 已提供
    ("h0108", "h0309"),    # 对应 0108卫星 -> 0309卫星的时间
    ("h0309", "h0512"),    # 对应 0309卫星 -> 0512卫星的时间
    ("h0104", "h0303"),    # 对应 0104卫星 -> 0303卫星的时间
    ("h0303", "h0506"),    # 对应 0303卫星 -> 0506卫星的时间
    ("h0605", "h0803"),    # 对应 0605卫星 -> 0803卫星的时间
    ("h0803", "h1006"),    # 对应 0803卫星 -> 1006卫星的时间
    ("h0811", "h0809"),    # 对应 0811卫星 -> 0809卫星的时间
    ("h0411", "h0309"),    # 对应 0411卫星 -> 0309卫星的时间
    ("h0204", "h0303"),    # 对应 0204卫星 -> 0303卫星的时间
    ("h0703", "h0803"),    # 对应 0703卫星 -> 0803卫星的时间
    ("h0911", "h0809"),    # 对应 0911卫星 -> 0809卫星的时间
    ("h0412", "h0309"),    # 对应 0412卫星 -> 0309卫星的时间
    ("h0103", "h0303"),    # 对应 0103卫星 -> 0303卫星的时间
    ("h0606", "h0803"),    # 对应 0606卫星 -> 0803卫星的时间
    ("h0911", "h0809"),    # 对应 0911卫星 -> 0809卫星的时间 (重复，保留)
    ("h0112", "h0309"),    # 对应 0112卫星 -> 0309卫星的时间
    ("h0103", "h0303"),    # 对应 0103卫星 -> 0303卫星的时间 (重复，保留)
    ("h0602", "h0803"),    # 对应 0602卫星 -> 0803卫星的时间
    ("h0609", "h0809"),    # 对应 0609卫星 -> 0809卫星的时间
    ("h0312", "h0309"),    # 对应 0312卫星 -> 0309卫星的时间
    ("h0202", "h0303"),    # 对应 0202卫星 -> 0303卫星的时间
    ("h0704", "h0803"),    # 对应 0704卫星 -> 0803卫星的时间
    ("h0708", "h0809"),    # 对应 0708卫星 -> 0809卫星的时间
    ("h0109", "h0309"),    # 对应 0109卫星 -> 0309卫星的时间
    ("h0102", "h0303"),    # 对应 0102卫星 -> 0303卫星的时间
    ("h0803", "h0803"),    # 对应 0803卫星 -> 0803卫星的时间
    ("h0807", "h0809"),    # 对应 0807卫星 -> 0809卫星的时间
    ("h0208", "h0309"),    # 对应 0208卫星 -> 0309卫星的时间
    ("h0101", "h0303"),    # 对应 0101卫星 -> 0303卫星的时间
    ("h0901", "h0803"),    # 对应 0901卫星 -> 0803卫星的时间
    ("h0609", "h0809"),    # 对应 0609卫星 -> 0809卫星的时间 (重复，保留)
    ("h0111", "h0309"),    # 对应 0111卫星 -> 0309卫星的时间
    ("h0306", "h0303"),    # 对应 0306卫星 -> 0303卫星的时间
    ("h0806", "h0803"),    # 对应 0806卫星 -> 0803卫星的时间
    ("h0608", "h0809"),    # 对应 0608卫星 -> 0809卫星的时间
    ("h0112", "h0309"),    # 对应 0112卫星 -> 0309卫星的时间 (重复，保留)
    ("h0301", "h0303"),    # 对应 0301卫星 -> 0303卫星的时间
    ("h0605", "h0803")     # 对应 0605卫星 -> 0803卫星的时间 (重复，保留)
]
for i in range(0,len(host_pairs_list)):
    a=host_pairs_list[i][0][0]+"0"+host_pairs_list[i][0][1:]
    b=host_pairs_list[i][1][0]+"0"+host_pairs_list[i][1][1:]
    host_pairs_list[i]=(a,b)
# print(host_pairs_list)
# print(len(host_pairs_list))
model_for_send="""
import time
from scapy.layers.l2 import Ether
from scapy.layers.inet import IP
from scapy.sendrecv import sendp
from scapy.arch import get_if_hwaddr
# 获取当前时间戳
while True:
	timestamp = str(time.time())

	# 创建以太网头部和IPv4头部，并将时间戳作为载荷

	pkt = Ether(src=get_if_hwaddr("{send_iface}"), dst="ff:ff:ff:ff:ff:ff") / IP(dst="{dst_ipv4}",proto=155) / timestamp
	sendp(pkt,iface="{send_iface}",count=1)
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
sniff(prn=packet_callback, filter="ip",count=1000,iface="{receive_iface}")
"""
for i in host_pairs_list:
    folder_name=i[0]+" to "+i[1]
    os.makedirs(folder_name,exist_ok=True)
    with open(os.path.join(folder_name,"send.py"),"w") as file1:
        file_content=model_for_send.format(send_iface=i[0]+"-eth0",dst_ipv4=topo.get_host_ip(i[1]))
        file1.write(file_content)
    with open(os.path.join(folder_name,"receive.py"),"w") as file2:
        file_content=model_for_receive.format(receive_iface=i[1]+"-eth0")
        file2.write(file_content)