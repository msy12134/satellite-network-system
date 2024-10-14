import time
from scapy.all import sniff
from scapy.layers.inet import IP
# 定义处理接收到的数据包的函数
def packet_callback(pkt):
    if IP in pkt and pkt[IP].proto == 155:
        # 提取载荷，即时间戳
        timestamp_now = time.time()
        timestamp = pkt.load.decode('utf-8')
        print(f"Received timestamp: {(timestamp_now-float(timestamp))*1000}ms")

# 捕获数据包
sniff(prn=packet_callback, filter="ip",count=1000,iface="h00606-eth0")
