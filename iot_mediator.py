# coding:utf-8
# 部署在小车上
import requests
import cv2
import time
from scapy.all import *
from random import *
from scapy.contrib.openflow3 import *
from iot_actions import *
import socket
import multiprocessing
import camera_on
from distance import Getdistance
import temperature_and_humidity
import filetrans
import datetime
import send_camera


class IoTMediator(Automaton):

    def master_filter(self, pkt):
        return (TCP in pkt and pkt[TCP].sport == 6653)

    @ATMT.state(initial=1)
    def INIT(self):
        print("******************** STATE: INIT ********************")

    @ATMT.state()
    def SERVICING(self):
        print("******************** STATE: SERVICING ********************")

    @ATMT.receive_condition(SERVICING)
    def on_packet_out(self, pkt):
        # 两种方法获取packet_out的方法，两种方法用一种即可，需要把另一种注释掉
        # 方法一：直接使用OFPTPacketOut结构从收到的pkt中抓取出来
        # pkt_out = pkt[OFPTPacketOut]

        # 方法二：先得到TCP结构；然后将TCP结构还原为字节流，TCP字节流前二十个字节为TCP首部，
        # 后面就是packet_out字节流，然后将packet_out字节流重构为packet_out分组结构
        pkt_tcp = pkt[TCP]
        pkt_tcp_raw = raw(pkt_tcp)
        pkt_out_raw = pkt_tcp_raw[20:]
        pkt_out = OFPTPacketOut(pkt_out_raw)

        for exptr in pkt_out.actions:
            exptr_raw = raw(exptr)
            exptr.show()
            act = None
            if exptr_raw[4] == 0x01:
                act = MOVE_ACTION(exptr_raw[4:])
                act.show()
                raise self.MOVING(act)

            elif exptr_raw[4] == 0x02:
                act = SPEICAL_ACTION(exptr_raw[4:])
                act.show()
                raise self.HANDLING_Special_Action(act)
            else:
                print("Invalid packet received. Returning back to SERVICING")
                raise self.SERVICING()
        raise self.SERVICING()

    @ATMT.state()
    def MOVING(self, act):
        print("I am moving as per the received packet")
        # print("应该在这里调用前后左右移动的函数")
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]  # 获取本机ip
        if act.direction == 1:
            requests.get('http://' + ip + ':5000/api/car/run')
        elif act.direction == 2:
            requests.get('http://' + ip + ':5000/api/car/back')
        elif act.direction == 3:
            requests.get('http://' + ip + ':5000/api/car/left')
        elif act.direction == 4:
            requests.get('http://' + ip + ':5000/api/car/right')
        elif act.direction == 5:
            requests.get('http://' + ip + ':5000/api/car/spin_left')
        elif act.direction == 6:
            requests.get('http://' + ip + ':5000/api/car/spin_right')
        elif act.direction == 7:
            requests.get('http://' + ip + ':5000/api/speed/up')
        elif act.direction == 8:
            requests.get('http://' + ip + ':5000/api/speed/down')
        elif act.direction == 9:
            requests.get('http://' + ip + ':5000/api/car/stop')

    @ATMT.state()
    def HANDLING_Special_Action(self, act):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        if act.operation == 1:
            try:
                send_camera.run()
            except:
                print("摄像头开启失败")
        elif act.operation == 2:
            try:
                camera_on.take_photo()
            except:
                print("拍照失败")
        elif act.operation == 3:
            requests.get('http://' + ip + ':5000/api/act/findlight')          # 追光寻走
        elif act.operation == 4:
            try:
                the_data = temperature_and_humidity.get_data()
                if the_data is not None:
                    with open("tandh.txt", "a") as th:
                        now_time = datetime.datetime.now()
                        th.write(str(now_time))
                        th.write(the_data+"\n")
                        th.close()
                    file_name = "tandh.txt"
                    filetrans.run(file_name)
                else:
                    print("没有获得数据")
            except:
                pass
        elif act.operation == 5:
            try:
                run = Getdistance()
                the_distance = run.get_thedistance()
                with open("distance.txt", "a") as th:
                    now_time = datetime.datetime.now()
                    th.write(str(now_time))
                    th.write(the_distance+"\n")
                    th.close()
                file_name = "distance.txt"
                filetrans.run(file_name)
            except:
                pass
        elif act.direction == 6:
            requests.get('http://' + ip + ':5000/api/car/stop')              # 停止

    @ATMT.condition(MOVING)
    def moving_finishes(self):
        raise self.SERVICING()

    @ATMT.condition(HANDLING_Special_Action)
    def camera_op_finishes(self):
        raise self.SERVICING()

    @ATMT.condition(INIT)
    def start_service(self):
        raise self.SERVICING()

    @ATMT.state(final=1)
    def FINISH(self):
        print("******************** STATE: FINISH ********************")


