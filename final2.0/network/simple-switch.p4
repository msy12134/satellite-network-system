#include <core.p4>
#include <v1model.p4>

const bit<32> controller_ipv4dst=0x0A00050F;
const bit<16> TYPE_IPV4=0x0800;
const bit<8> IP_PROTO_REQUEST=150;
const bit<8> IP_PROTO_RESPONSE=151;
header ethernet_t {
    bit<48> dstAddr;
    bit<48> srcAddr;
    bit<16>   ether_type;
}

header ipv4_t {
    bit<4>    version;
    bit<4>    ihl;
    bit<8>    diffserv;
    bit<16>   totalLen;
    bit<16>   identification;
    bit<3>    flags;
    bit<13>   fragOffset;
    bit<8>    ttl;
    bit<8>    protocol;
    bit<16>   hdrChecksum;
    bit<32> src_addr;
    bit<32> dst_addr;
}

header request_t{
    bit<8> deviceid;
    bit <32> dst_addr;
}

header response_t{
    bit<8> deviceid;
    bit<32> dst_addr;
    bit<9> port;
    bit<48> dst_port_mac;
    bit<7> padding;
}

struct headers{
    ethernet_t         ethernet;
    ipv4_t             ipv4;
    request_t          request;
    response_t         response;
}

struct metadata {
    
}
parser MyParser(
            packet_in pkt,
            out headers hdr,
            inout metadata meta,
            inout standard_metadata_t standard_metadata
){
    state start{
        transition parse_ethernet;
    }

    state parse_ethernet{
        pkt.extract(hdr.ethernet);
        transition parse_ipv4;
    }

    state parse_ipv4{
        pkt.extract(hdr.ipv4);
        transition select(hdr.ipv4.protocol){
            150: parse_request;
            151:parse_response;
            default: accept;
        }
    }

    state parse_request{
        pkt.extract(hdr.request);
        transition accept;
    }

    state parse_response{
        pkt.extract(hdr.response);
        transition accept;
    }
}

control MyVerifyChecksum(inout headers hdr, inout metadata meta) {
    apply {  }
}  

control MyIngress(inout headers hdr,
                  inout metadata meta,
                  inout standard_metadata_t standard_metadata)
{
    action drop(){
        mark_to_drop(standard_metadata);
    }

    action ipv4_forward(bit<48> dst_ethernet, bit<9> port){
        hdr.ethernet.srcAddr=hdr.ethernet.dstAddr;
        hdr.ethernet.dstAddr=dst_ethernet;
        standard_metadata.egress_spec = port;
    }

    action set_deviceid_in_request(bit<8> deviceid){
        hdr.request.deviceid=deviceid;
    }

    action set_cpu_port(bit<9> CPU_PORT){
        standard_metadata.egress_spec=CPU_PORT;
    }

    action set_packet_ipv4dst_to_controllerip(bit<32> controller_ipv4){
        hdr.ipv4.dst_addr=controller_ipv4;
    }

    table table_set_packet_ipv4dst_to_controllerip{
        key={
            hdr.ethernet.ether_type: exact;
        }
        actions={
            set_packet_ipv4dst_to_controllerip;
            NoAction;
        }
        default_action = NoAction();
    }

    table set_cpu_port_for_this_packet{
        key={
            hdr.ethernet.ether_type: exact;
        }
        actions={
            set_cpu_port;
            NoAction;
        }
        default_action = NoAction();
    }

    table set_deviceid{
        key = {
           hdr.ethernet.ether_type: exact;       
        }
        actions = {
            set_deviceid_in_request;
            NoAction;
        }
        default_action = NoAction();
    }

    table ipv4_lpm{
        key={
            hdr.ipv4.dst_addr: exact;
        }
        actions={
            ipv4_forward;
            drop;
        }
        size = 1024;
        default_action = drop;
    }

    table ipv4_dst_memory{
        key={
            hdr.ipv4.dst_addr: exact;
        }
        actions={
            ipv4_forward;
            drop;
        }
        size = 1024;
        default_action = drop;
    }


    table if_the_deviceid_hit{
        key={
            hdr.response.deviceid: exact;
        }
        actions={
            ipv4_forward;
            drop;
        }
        size=1024;
        default_action=drop;
    }

    apply{
        bool use_ipv4_lpm;
        use_ipv4_lpm=false;
       if(ipv4_dst_memory.apply().hit){//这张表的用处就是单纯来查看这个数据包的目的地址是否是已经记录的地址
            if(hdr.ipv4.protocol!=151 && hdr.ipv4.protocol!=150){
                use_ipv4_lpm=true;   //只是记录在的普通数据包，那就转发
            }else{
                if(hdr.ipv4.protocol==150){
                    use_ipv4_lpm=true;
                }else if(hdr.ipv4.protocol==151){
                    if(if_the_deviceid_hit.apply().hit){
                        // standard_metadata.egress_spec=CPU_PORT;
                        set_cpu_port_for_this_packet.apply();
                    }
                    else{
                        use_ipv4_lpm=true;
                    }
                }
            }
       }else{
        hdr.request.setValid();
        set_deviceid.apply();
        hdr.request.dst_addr=hdr.ipv4.dst_addr;
        hdr.ipv4.protocol=150;
        table_set_packet_ipv4dst_to_controllerip.apply();
        use_ipv4_lpm=true;
       }
       if (use_ipv4_lpm){
        ipv4_lpm.apply();
       }
    }
}

control MyEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata){
        apply{}
}

control MyComputeChecksum(inout headers  hdr, inout metadata meta){
    apply{}
}

control MyDeparser(packet_out packet, in headers hdr){
    apply{
        packet.emit(hdr.ethernet);
        packet.emit(hdr.ipv4);
        packet.emit(hdr.request);
        packet.emit(hdr.response);
    }
}

V1Switch(
MyParser(),
MyVerifyChecksum(),
MyIngress(),
MyEgress(),
MyComputeChecksum(),
MyDeparser()
) main;