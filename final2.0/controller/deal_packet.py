from header_definition import *
from scapy.packet import Raw,Packet

def deal_packet_for_simple_switch(packet:Packet):
    """普通交换机解析域内控制器发过来的response包.

    Args:
        packet: 对应普通交换机的控制平面接收到的response包
    
    Returns:
        dict: 从response包中解析出来的信息
    """
    deviceid=packet[response_t].deviceid
    dst_addr=packet[response_t].dst_addr
    port=packet[response_t].port
    dst_port_mac=packet[response_t].dst_port_mac
    return  {"deviceid":deviceid,"dst_addr":dst_addr,"port":port,"dst_port_mac":dst_port_mac}


def deal_packet_for_controller_switch(packet:Packet):
    """控制交换机解析发过来的request包.

    Args:
        packet: 对应控制交换机的控制平面接收到的request包
    
    Returns:
        dict: 从request包中解析出来的信息
    """
    deviceid=packet[request_t].deviceid
    dst_addr=packet[request_t].dst_addr
    return {"deviceid": deviceid,"dst_addr":dst_addr}


def make_a_response_packet(deviceid:int,dst_addr:str,port:int,dst_port_mac:str,ipv4:str):
    """控制交换机控制平面构造response数据包发送给对应普通交换机.

    Args:
        deviceid(int): response包目的交换机的deviceid
        dst_addr(str): response包的response头部的dst_addr
        port(int): response包的response头部的port
        dst_port_mac(str): response包的response头部的dst_port_mac
        ipv4(str): response包的ipv4头部中的dst_addr
    
    Returns:
        packet: 打包好的完整response包
    """
    mac_address_int_form=int(dst_port_mac.replace(":",""),16)
    
    packet=Ether(type=0x0800)/IP(dst=ipv4,proto=151)/\
    response_t(deviceid=deviceid,dst_addr=dst_addr,port=port,dst_port_mac=mac_address_int_form)
    return packet


