#include <core.p4>
#include <v1model.p4>

#define MAX_PORTS 255

header sr_header_t {
    bit<8> sr_segment_num;//总共还剩几段sr segment
}

header sr_t {
    bit<8> sr_info;//sr路由信息存储在这个地方，会有好几段
}

header int_header_t {
    bit<8>    int_segment_num;//表明总共有几段int
    bit<8>    flag;//标志位，默认设为1,用来作为获取swid 的标志
    bit<8>    circle_id; //环路id，默认设为0
}

header int_t{
    bit<8> switch_id;
    bit<8> ingress_port;
    bit<8> egress_port;
    bit<48> ingress_timestamp;
    bit<48> egress_timestamp;
}


struct headers{
    sr_header_t sr_header;
    sr_t[MAX_PORTS] sr;
    int_header_t int_header;
    int_t[MAX_PORTS] int_data; 
}

struct metadata {
    bit<8> sr_segment_num; 
    bit<8> int_segment_num; //记录int segment的数量
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
        pkt.extract(hdr.sr_header);
        meta.sr_segment_num = hdr.sr_header.sr_segment_num;//记录有后面有几段sr segment要解析
        transition parse_sr_segment;
    }

    state parse_sr_segment{
        pkt.extract(hdr.sr.next);
        meta.sr_segment_num = meta.sr_segment_num - 1;
        transition select(meta.sr_segment_num) {
            0: parse_int_header;
            default: parse_sr_segment;
        }
    }

    state parse_int_header{
        pkt.extract(hdr.int_header);
        meta.int_segment_num = hdr.int_header.int_segment_num; //记录有几段int segment要解析
        transition parse_int_segment;
    }

    state parse_int_segment{
        pkt.extract(hdr.int_data.next);
        meta.int_segment_num = meta.int_segment_num - 1;
        transition select(meta.int_segment_num) {
            0: accept;
            default: parse_int_segment;
        }
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

    action set_swid(bit<8> swid){
        hdr.int_data[hdr.int_header.int_segment_num-1].switch_id=swid;
    }

    action sr_forward(bit<8> port){
        standard_metadata.egress_spec = (bit<9>)port;
    }

    table sr_table{
        key = {
            hdr.sr[0].sr_info: exact;
        }
        actions = {
            sr_forward;
            drop;
        }
        size = 1024; // Adjust size as needed
        default_action = drop();
    }

    table swid {
        key = {
            hdr.int_header.flag: exact;
        }
        actions = {
            set_swid;
            drop;
        }
        size = 1024; // Adjust size as needed
        default_action = drop();
    }
    apply{
        sr_table.apply();
        hdr.sr_header.sr_segment_num = hdr.sr_header.sr_segment_num - 1;
        hdr.sr.pop_front(1);
        hdr.int_header.int_segment_num = hdr.int_header.int_segment_num + 1;
        hdr.int_data[hdr.int_header.int_segment_num-1].setValid();
        swid.apply();
        hdr.int_data[hdr.int_header.int_segment_num-1].ingress_port = (bit<8>)standard_metadata.ingress_port;
        hdr.int_data[hdr.int_header.int_segment_num-1].ingress_timestamp = standard_metadata.ingress_global_timestamp;
    }
}

control MyEgress(inout headers hdr,
                 inout metadata meta,
                 inout standard_metadata_t standard_metadata){
        apply{
            hdr.int_data[hdr.int_header.int_segment_num-1].egress_port = (bit<8>)standard_metadata.egress_port;
            hdr.int_data[hdr.int_header.int_segment_num-1].egress_timestamp = standard_metadata.egress_global_timestamp;
        }
}

control MyComputeChecksum(inout headers  hdr, inout metadata meta) {
     apply {
        }
}

control MyDeparser(packet_out packet, in headers hdr){
    apply{
        packet.emit(hdr.sr_header);
        packet.emit(hdr.sr);
        packet.emit(hdr.int_header);
        packet.emit(hdr.int_data);
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