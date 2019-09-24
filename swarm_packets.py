#coding:utf-8

from scapy.contrib.openflow3 import *

SWARM_PROTOCOL = 0xFE   #254 in decmial


SWARM_PDUS = {
    1: "swarm_build",
    2: "swarm_join",
    3: "swarm_role",
    4: "swarm_confirm",
    5: "swarm_ack"
}

SWARM_ROLES = {
    1: "peer",
    2: "head",
    3: "node",
    4: "unknown"
}

class MANET_Underlay_Swarm_Build(Packet):
    name = "MANET_Underlay_Swarm_Build"
    fields_desc = [
        ByteEnumField("type", 1, SWARM_PDUS),
        ByteField("value", 0)
    ]

class MANET_Underlay_Swarm_Join(Packet):
    name = "MANET_Underlay_Swarm_Join"
    fields_desc = [
        ByteEnumField("type", 2, SWARM_PDUS),
        ByteField("battery", 0)
    ]

class MANET_Underlay_Swarm_Role(Packet):
    name = "MANET_Underlay_Swarm_Role"
    fields_desc = [
        ByteEnumField("type", 3, SWARM_PDUS),
        ByteEnumField("role", 1, SWARM_ROLES)
    ]

class MANET_Underlay_Swarm_Confirm(Packet):
    name = "MANET_Underlay_Swarm_Confirm"
    fields_desc = [
        ByteEnumField("type", 4, SWARM_PDUS),
        ByteField("value", 0)  # 一个字节
    ]

class MANET_Underlay_Swarm_ACK(Packet):
    name = "MANET_Underlay_Swarm_ACK"
    fields_desc = [
        ByteEnumField("type", 5, SWARM_PDUS),
        ByteField("value", 0)
    ]
