import time
from scapy.layers.l2 import Ether
from scapy.layers.inet import IP
from scapy.sendrecv import sendp

# 获取当前时间戳
timestamp = str(time.time())

# 创建以太网头部和IPv4头部，并将时间戳作为载荷

pkt = Ether() / IP(dst="192.168.1.1",proto=155) / timestamp
sendp(pkt,iface="WLAN",count=100)

