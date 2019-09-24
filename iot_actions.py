# coding:utf-8

from scapy.contrib.openflow3 import *


action_types = {
                1: "Move_Action", 
                2: "Special_Action"
                    }

move_directions = {
                    1: "Move_Forward", 
                    2: "Move_Backward", 
                    3: "Move_Left", 
                    4: "Move_Right",
                    5: "Move_spin_left",
                    6: "Move_spin_right",
                    7: "speed_up",
                    8: "speed_down",
                    9: "Stop"
}

special_operations = {
                    1: "Camera_On",
                    2: "Take_Photo",
                    3: "Follow_Light",
                    4: "temperature and humidity",
                    5: "get_distance",
                    6: "Stop",

}


class MOVE_ACTION(Packet):
    name = "MOVE_ACTION"
    fields_desc = [
                    ByteEnumField("action_type", 1, action_types),
                    ByteEnumField("direction", 1, move_directions),
                    ByteField("step", 5),
                    ByteField("reserve", 0)
    ]


class SPEICAL_ACTION(Packet):
    name = "Special_ACTION"
    fields_desc = [
                    ByteEnumField("action_type", 2, action_types),
                    ByteEnumField("operation", 1, special_operations),
                    ByteField("reserve1", 0),
                    ByteField("reserve2", 0)
    ]