import time
from scapy.layers.l2 import Ether
from scapy.layers.inet import IP
from scapy.sendrecv import sendp
from scapy.arch import get_if_hwaddr
# 获取当前时间戳
while True:
	timestamp = str(time.time())

	# 创建以太网头部和IPv4头部，并将时间戳作为载荷

	pkt = Ether(src=get_if_hwaddr("h00707-eth0"), dst="ff:ff:ff:ff:ff:ff") / IP(dst="10.0.3.41",proto=155) / timestamp
	sendp(pkt,iface="h00707-eth0",count=1)
