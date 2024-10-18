#运行这个文件，在mysql中建立绑定device_id,ipv4_address,switch_name之间的绑定关系
from sqlalchemy import create_engine,Column,BigInteger,String,Integer
from sqlalchemy.orm import sessionmaker,declarative_base
import sys
sys.path.insert(0,"/home/mao/Desktop/systerm-code/final2.0/controller/sdn_controller")
from common import mysql_database_url,topo

engine=create_engine(mysql_database_url)

SessionLocal=sessionmaker(autocommit=False,autoflush=False,bind=engine)

Base=declarative_base()
class DeviceIdMappingIpv4Address(Base):
    __tablename__='device_id_mapping_ipv4_address'
    id=Column(BigInteger,primary_key=True,autoincrement=True,comment='主键')
    device_id=Column(Integer,nullable=False,comment="交换机分配的decice id",unique=True)
    ipv4_address=Column(String(50),nullable=False,comment="交换机所连接终端的ipv4地址",unique=True)
    switch_name=Column(String(30),nullable=False,comment="交换机名称",unique=True)

class DomainIdMappingSwitchName(Base):
    __tablename__='domain_id_mapping_switch_name'
    id=Column(BigInteger,primary_key=True,autoincrement=True,comment='主键')
    domain_id=Column(Integer,nullable=False,comment="交换机分配的domain id")
    switch_name=Column(String(50),nullable=False,comment="交换机的名字",unique=True)

Session=sessionmaker(bind=engine)


if __name__=="__main__":
    Base.metadata.create_all(engine)
    controller_switch_for_domain1='s00303'  #redis_db=0
    controller_switch_for_domain2='s00309'  #redis_db=1
    controller_switch_for_domain3='s00803'  #redis_db=2
    controller_switch_for_domain4='s00809'  #redis_db=3

    controller_switch_name_list=['s00303','s00309','s00803','s00809']

    domian1=['s0'+str(x).zfill(2)+str(y).zfill(2) for x in range(1,6) for y in range(1,7)] #每个domain中有三十个交换机
    domian2=['s0'+str(x).zfill(2)+str(y).zfill(2) for x in range(1,6) for y in range(7,13)]
    domian3=['s0'+str(x).zfill(2)+str(y).zfill(2) for x in range(6,11) for y in range(1,7)]
    domian4=['s0'+str(x).zfill(2)+str(y).zfill(2) for x in range(6,11) for y in range(7,13)]

    
    db=Session()
    switch_name_list=list(topo.get_switches().keys())
    host_name_list=list(topo.get_hosts().keys())
    host_ipv4_list=[topo.get_host_ip(host) for host in host_name_list]
    device_id=1
    for i in zip(switch_name_list,host_ipv4_list):
        item=DeviceIdMappingIpv4Address(device_id=device_id,ipv4_address=i[1],switch_name=i[0])
        device_id+=1
        db.add(item)
    db.commit()
    for i in domian1+domian2+domian3+domian4:
        if i in domian1:
            item=DomainIdMappingSwitchName(domain_id=1,switch_name=i)
            db.add(item)
        if i in domian2:
            item=DomainIdMappingSwitchName(domain_id=2,switch_name=i)
            db.add(item)
        if i in domian3:
            item=DomainIdMappingSwitchName(domain_id=3,switch_name=i)
            db.add(item)
        if i in domian4:
            item=DomainIdMappingSwitchName(domain_id=4,switch_name=i)
            db.add(item)
    db.commit()