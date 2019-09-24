# coding:utf-8
from scapy.all import *
from scapy.contrib.openflow3 import *
from iot_actions import *
import binascii
import socket
import sys
import time
import getfile
import recv_camera


class IoTController(Automaton):
    ip_address_list = []

    @ATMT.state(initial=1)
    def INIT(self):
        print("******************** STATE: INIT ********************")

    @ATMT.condition(INIT)
    def choose_mode(self):
        choice = input("Please press 1 to  run this  Interactive demo  (CLI).  \n")
        if choice == "1":
            raise self.DEMO()
        else:
            print("No such a choice. Please select again. ")
            raise self.INIT()

    @ATMT.state()
    def DEMO(self):
        print("******************** STATE: DEMO ********************")

    @ATMT.condition(DEMO)
    def choose_demo(self):
        demo = input(
            "Please select a demo: \nPress 1: SDN-controlled Movement.\nPress 2:SDN-controlled Special_Action \n")
        if demo == "1":
            raise self.WAIT_FOR_INSTRUCTION()
        elif demo == "2":
            raise self.WAIT_FOR_Special_Action()
        else:
            print("No such a demo. Please select again. ")
            raise self.DEMO().action_parameters(specify=False)

    @ATMT.action(choose_demo)
    def specify_controlled_nodes(self, specify=True):                    # 输入要被控制节点的IP地址
        if specify:
            ip_addresses = input(
                "Input the IP addresses of the IoT nodes you want to control: \n"
                "use ; to split ip addresses\n"
                "input addresses separated by ; \nPlease input: ")
            self.ip_address_list = self.split_ip_addresses(ip_addresses)
            print(self.ip_address_list)

    @ATMT.state()
    def WAIT_FOR_INSTRUCTION(self):
        print("******************** STATE: WAIT_FOR_INSTRUCTION ********************")
        print(
            "Press W: Forward\nPress S: Backward\nPress A: Left\nPress D: Right\nPress Q:spin_left\n"
            "Press E:spin_right\nPress Z:Speed Up\nPress X:Speed Down\nPress space:STOP\n"
            "Press P:Quit\nInput your direction: ")
        act = None
        instruction = input()  # 这里通过按键控制命令使小车进行对应操作
        if instruction == "p":
            raise self.DEMO()
        elif instruction == "w":
            act = MOVE_ACTION()
            act.setfieldval("action_type", 1)
            act.setfieldval("direction", 1)
        elif instruction == "s":
            act = MOVE_ACTION()
            act.setfieldval("action_type", 1)
            act.setfieldval("direction", 2)
        elif instruction == "a":
            act = MOVE_ACTION()
            act.setfieldval("action_type", 1)
            act.setfieldval("direction", 3)
        elif instruction == "d":
            act = MOVE_ACTION()
            act.setfieldval("action_type", 1)
            act.setfieldval("direction", 4)
        elif instruction == "q":
            act = MOVE_ACTION()
            act.setfieldval("action_type", 1)
            act.setfieldval("direction", 5)
        elif instruction == "e":
            act = MOVE_ACTION()
            act.setfieldval("action_type", 1)
            act.setfieldval("direction", 6)
        elif instruction == "z":
            act = MOVE_ACTION()
            act.setfieldval("action_type", 1)
            act.setfieldval("direction", 7)
        elif instruction == "x":
            act = MOVE_ACTION()
            act.setfieldval("action_type", 1)
            act.setfieldval("direction", 8)
        elif instruction == " ":
            act = MOVE_ACTION()
            act.setfieldval("action_type", 1)
            act.setfieldval("direction", 9)
        else:
            print("No such a move instruction. Please input again. ")
            # act = None
        if act is not None:
            for ip in self.ip_address_list:
                pkt_out = self.build_packet_out(ip, act)
                send(pkt_out)
        # raise self.WAIT_FOR_INSTRUCTION

    @ATMT.state()
    def WAIT_FOR_Special_Action(self):
        print("******************** STATE: WAIT_Special_Action ********************")
        print("Press C: open camara\nPress V: Take picture\nPress F: Follow Light\n"
              "Press B: Temperature and Humidity\nPress N: Get Distance\nPress P:Quit\n"
              "Press: Space to Stop\nInput your direction: ")
        act = None
        instruction = input()  # 这里通过按键控制命令使小车进行对应操作
        if instruction == "c":
            act = SPEICAL_ACTION()
            act.setfieldval("action_type", 2)
            act.setfieldval("operation", 1)
        elif instruction == "v":
            act = SPEICAL_ACTION()
            act.setfieldval("action_type", 2)
            act.setfieldval("operation", 2)
        elif instruction == "f":
            act = SPEICAL_ACTION()
            act.setfieldval("action_type", 2)
            act.setfieldval("operation", 3)
        elif instruction == "b":
            act = SPEICAL_ACTION()
            act.setfieldval("action_type", 2)
            act.setfieldval("operation", 4)
        elif instruction == "n":
            act = SPEICAL_ACTION()
            act.setfieldval("action_type", 2)
            act.setfieldval("operation", 5)
        elif instruction == " ":
            act = SPEICAL_ACTION()
            act.setfieldval("action_type", 2)
            act.setfieldval("operation", 6)
        elif instruction == "p":  # 退出
            raise self.DEMO()
        else:
            print("No such a move instruction. Please input again. ")
            # act = None
        if act is not None:
            for ip in self.ip_address_list:
                pkt_out = self.build_packet_out(ip, act)
                send(pkt_out)
                for exptr in pkt_out.actions:
                    exptr_raw = raw(exptr)
                    if exptr_raw[4] == 0x02:                                              # 对应的传感器进行数据接收
                        if act.operation == 1:
                            print("please wait for a moment")
                            time.sleep(1)
                            try:                             # 接收摄像头数据
                                print("************\nRress ESC to stop this action\n************")
                                time.sleep(2)  # 等待服务器先启动
                                recv_camera.main(ip)
                            except:
                                print("画面传输失败")
                        elif act.operation == 2:
                            try:
                                time.sleep(2)            # 等待服务器先启动
                                getfile.run(ip)
                            except:
                                print("图片传输失败")
                            # 传输结束
                        elif act.operation == 4:
                            try:
                                getfile.run(ip)
                                print("获取数据中")
                                time.sleep(2)
                            except:
                                print("没有获得温度和湿度数据")
                        elif act.operation == 5:
                            try:
                                getfile.run(ip)
                                print("获取数据中")
                                time.sleep(3)
                            except:
                                print("没有获得距离数据")
                    else:
                        pass
        raise self.WAIT_FOR_Special_Action()

    @ATMT.condition(WAIT_FOR_INSTRUCTION)
    def move_finished(self):
        raise self.WAIT_FOR_INSTRUCTION()

    @ATMT.condition(WAIT_FOR_Special_Action)
    def act_finished(self):
        raise self.WAIT_FOR_Special_Action

    def split_ip_addresses(self, ip_str):       # 分开IP地址
        return ip_str.split(";")

    def build_packet_out(self, ip, act):           # 构造数据包
        act_raw = raw(act)
        act_int = int(binascii.b2a_hex(act_raw), 16)
        exptr = OFPATExperimenter()
        exptr.setfieldval("experimenter", act_int)
        pkt_out = IP(dst=ip) / TCP(sport=6653, dport=6653) / OFPTPacketOut()
        action_list = pkt_out[OFPTPacketOut].actions
        action_list.append(exptr)
        print("******************** data_package ********************")
        pkt_out.show()         # 显示构建的数据包
        print("******************** actions ********************")
        print(act)             # 显示要执行命令的actions数字
        return pkt_out

