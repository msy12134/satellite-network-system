#运行这个文件，在mysql中建立绑定device_id,ipv4_address,switch_name之间的绑定关系
from sqlalchemy import create_engine,Column,BigInteger,String,Integer
from sqlalchemy.orm import sessionmaker,declarative_base
from p4utils.utils.topology import NetworkGraph
from p4utils.utils.helper import load_topo
engine=create_engine('mysql+pymysql://maomao:1234@localhost:3306/system')

SessionLocal=sessionmaker(autocommit=False,autoflush=False,bind=engine)

Base=declarative_base()
class DeviceIdMappingIpv4Address(Base):
    __tablename__='device_id_mapping_ipv4_address'
    id=Column(BigInteger,primary_key=True,autoincrement=True,comment='主键')
    device_id=Column(Integer,nullable=False,comment="交换机分配的decice id")
    ipv4_address=Column(String(50),nullable=False,comment="交换机所连接终端的ipv4地址")
    switch_name=Column(String(30),nullable=False,comment="交换机名称")

Session=sessionmaker(bind=engine)


if __name__=="__main__":
    Base.metadata.create_all(engine)
    db=Session()
    topo = load_topo('/home/mao/Desktop/systerm-code/final/network/topology.json')
    switch_name_list=list(topo.get_switches().keys())
    host_name_list=list(topo.get_hosts().keys())
    host_ipv4_list=[topo.get_host_ip(host) for host in host_name_list]
    device_id=1
    for i in zip(switch_name_list,host_ipv4_list):
        item=DeviceIdMappingIpv4Address(device_id=device_id,ipv4_address=i[1],switch_name=i[0])
        device_id+=1
        db.add(item)
    db.commit()
