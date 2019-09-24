#coding:utf-8

from scapy.all import *
from swarm_packets import *
from random import randint
import socket
# from iot_controller import *
# from iot_mediator import *
import time
from get_adress import *


class SwarmPeer(Automaton):
    role = ""
    willing_to_join = True
    join_list = []
    join_list_scores = []
    swarm_list = []
    swarm_head = ""
    hostname = ""
    ip_addr = ""
    broadcast_addr = ""
    battery = 0

    TIMEOUT_WAIT_FOR_BUILD = 10
    TIMEOUT_WAIT_FOR_JOIN = 5
    TIMEOUT_WAIT_FOR_ROLE = 25
    TIMEOUT_WAIT_FOR_CONFIRM = 5
    TIMEOUT_WAIT_FOR_ACK = 5

    def self_info(self):
        print("Host name: ", self.hostname)
        print("IP address: ", self.ip_addr)
        print("Broadcast Address: ", self.broadcast_addr)
        print("Role: ", self.role)
        print("Battery: ", self.battery)


    def swarm_info(self):
        print("swarm head: ", self.swarm_head)
        if self.role == "head":
            print("swarm: ", self.swarm_list)


    # def get_broadcast_addr(self):
    #     # return "255.255.255.255"
    #     # return "172.17.255.255" #要修改！！！！！！！！！！！！！！should be modified
    #     return get_broadcast_address(self.ip_addr)

    def get_broacast_addr_no_routing(self):
        return "255.255.255.255"

    def other_sends_to_me(self, pkt):
        if pkt[IP].src != self.ip_addr:
            if pkt[IP].dst == self.ip_addr:
                return True
            elif pkt[IP].dst == self.broadcast_addr: #self.get_broadcast_addr():
                return True
            elif pkt[IP].dst == self.get_broacast_addr_no_routing():
                return True
            else:
                return False
        else:
            return False


    def master_filter(self, pkt):
        # return (ICMP in pkt)
        # pkt.show()
        return IP in pkt and pkt[IP].proto == SWARM_PROTOCOL

    @ATMT.state(initial=1)
    def INIT(self):

        self.hostname = socket.getfqdn(socket.gethostname())
        self.ip_addr = socket.gethostbyname(self.hostname)
        self.broadcast_addr = get_broadcast_address(self.ip_addr)#self.get_broadcast_addr()



    @ATMT.condition(INIT)
    def build_manet_underlay(self):
        raise self.WAIT_FOR_BUILD()

    @ATMT.state()
    def WAIT_FOR_BUILD(self):
        # print(time.time())
        print("******************** STATE: WAIT_FOR_BUILD ********************")
        self.join_list.clear()
        self.swarm_list.clear()
        self.role = "peer"
        self.join_list.append(self.ip_addr)
        self.swarm_list.append(self.ip_addr)
        self.willing_to_join = True
        self.battery = self.get_battery()
        self.join_list_scores.append(self.battery)
        self.self_info()

    @ATMT.timeout(WAIT_FOR_BUILD, TIMEOUT_WAIT_FOR_BUILD)
    def build_wait_timeout(self):
        print(time.time())
        print("WAIT_FOR_BUILD timed out!")
        raise self.WAIT_FOR_JOIN()

    @ATMT.action(build_wait_timeout)
    def broadcast_swarm_build(self):
        print(time.time())
        print("I will broadcast the swarm_build, since none is received.")
        swarm_build = MANET_Underlay_Swarm_Build()
        pkt_send = IP(dst=self.broadcast_addr, proto=SWARM_PROTOCOL) / swarm_build #note the boradcast address, should be corrected
        pkt_send.show()
        send(pkt_send)

    @ATMT.receive_condition(WAIT_FOR_BUILD)
    def swarm_build_arrived(self, pkt):
        print("I have received swarm_build as follows: ")
        pkt.show()
        raise self.WAIT_FOR_ROLE().action_parameters(pkt)

    @ATMT.action(swarm_build_arrived)
    def send_swarm_join(self, pkt):

        if self.willing_to_join and self.other_sends_to_me(pkt):#pkt[IP].dst == self.ip_addr:

            rcvd_src = pkt[IP].src
            swarm_join = MANET_Underlay_Swarm_Join()
            swarm_join.battery = self.battery
            pkt_send = IP(dst=rcvd_src, proto=SWARM_PROTOCOL) / swarm_join
            print("I will send the swarm_join")
            pkt_send.show()
            send(pkt_send)



    @ATMT.state()
    def WAIT_FOR_JOIN(self):
        print(time.time())
        print("******************** STATE: WAIT_FOR_JOIN ********************")

    @ATMT.receive_condition(WAIT_FOR_JOIN)
    def swarm_join_arrived(self, pkt):
        # print(pkt[ICMP].type)
        print("I have received swarm_join as follows: ")
        pkt.show()
        raise self.WAIT_FOR_JOIN().action_parameters(pkt)


    @ATMT.action(swarm_join_arrived)
    def add_to_join_list(self, pkt):

        raw_pkt = pkt[Raw]
        raw_data = raw(raw_pkt)

        if raw_data[0] == 2:#swarm_join
            src = pkt[IP].src
            swarm_join = MANET_Underlay_Swarm_Join(raw_data)

            if src not in self.join_list:
                self.join_list.append(src)

                batt = swarm_join.battery
                self.join_list_scores.append(batt)

        # print(self.join_list)



    def select_head(self):

        mx = max(self.join_list_scores)
        # print(self.join_list_scores)
        idx = self.join_list_scores.index(mx)

        # idx = randint(1, len(self.join_list)-1)   #这里是随机选择了一个peer作为head, 暂时不选自己，方便观察，should be modified

        head = self.join_list[idx]

        print("I have selected head as: ", head)
        return head





    @ATMT.state()
    def WAIT_FOR_ROLE(self):
        print("******************** STATE: WAIT_FOR_ROLE ********************")


    @ATMT.timeout(WAIT_FOR_ROLE, TIMEOUT_WAIT_FOR_ROLE)
    def role_wait_timeout(self):
        raise self.WAIT_FOR_BUILD()


    @ATMT.receive_condition(WAIT_FOR_ROLE)
    def swarm_role_arrived(self, pkt):

        raw_pkt = pkt[Raw]
        raw_data = raw(raw_pkt)

        if raw_data[0] != 3:
            print("Received wrong PDU type! Ignored!")
            raise self.WAIT_FOR_ROLE()

        if raw_data[0] == 3 and raw_data[1] == 2 and pkt[IP].dst == self.ip_addr:
            print("I am selected as the swarm head.")
            self.role = SWARM_ROLES[2]
            self.swarm_head = self.ip_addr
            self.join_list = self.parse_addresses_from_pkt(pkt)
            self.multicast_as_node()

            raise self.WAIT_FOR_CONFIRM()

        if raw_data[0] == 3 and raw_data[1] == 3 and pkt[IP].dst == self.ip_addr:
            print("I am a swarm node.")
            self.role = SWARM_ROLES[3]
            self.swarm_head = pkt[IP].src
            self.send_swarm_confirm(pkt)

            raise self.WAIT_FOR_ACK()

        raise self.WAIT_FOR_ROLE()



    @ATMT.timeout(WAIT_FOR_JOIN, TIMEOUT_WAIT_FOR_JOIN)
    def join_wait_timeout(self):
        print("WAIT_FOR_JOIN timed out!")
        if len(self.join_list) == 1:
            print("No one joins. I will start over!")
            raise self.WAIT_FOR_BUILD()
        else:
            print("Someone just joined. I will select the swarm head. ")
            head = self.select_head()

            if head != self.ip_addr:
                self.send_as_head(head)
                raise self.WAIT_FOR_ROLE()

            else:
                self.assign_as_head()
                self.multicast_as_node()
                raise self.WAIT_FOR_CONFIRM()

    def assign_as_head(self):
        print("I am selected as the swarm head, by myself.")
        self.role = SWARM_ROLES[2]
        self.swarm_head = self.ip_addr


    def send_as_head(self, head):


        as_head = MANET_Underlay_Swarm_Role(role=SWARM_ROLES[2])
        members = ""
        for addr in self.join_list:
            members += addr + "-"
        members = members[0:len(members) - 1]
        pkt_send = IP(dst=head, proto=SWARM_PROTOCOL) / as_head / members
        print("I will send the following swarm_role: ")
        pkt_send.show()
        send(pkt_send)

    def parse_addresses_from_pkt(self, pkt):
        print(pkt)
        pkt.show()
        raw_pkt = pkt[Raw]
        raw_data = raw(raw_pkt)
        swarm_role = MANET_Underlay_Swarm_Role(raw_data)
        self.role = SWARM_ROLES[swarm_role.role]
        swarm_role.show()
        raw_str = bytes.decode(raw_data[2:])
        members = raw_str.split("-")
        # self.join_list = members
        # print(self.join_list)

        return members


    def multicast_as_node(self):

        print("I will tell everyone in the join_list they should be swarm nodes. ")

        for addr in self.join_list:
            print("iterating...")
            if addr != self.ip_addr:
                as_node = MANET_Underlay_Swarm_Role(role=3)
                pkt_send = IP(dst=addr, proto=SWARM_PROTOCOL) / as_node
                as_node.show()
                send(pkt_send)
                print("just sent to notify everyone")

    # @ATMT.state()
    def send_swarm_confirm(self, pkt):
        # print("******************** STATE: CONFIRMING ********************")
        rcvd_src = pkt[IP].src
        swarm_confirm = MANET_Underlay_Swarm_Confirm()
        # self.role =
        pkt_send = IP(dst=rcvd_src, proto=SWARM_PROTOCOL) / swarm_confirm
        print("I will send the swarm_confirm")
        pkt_send.show()
        send(pkt_send)


    def send_swarm_ack(self, pkt):
        rcvd_src = pkt[IP].src
        swarm_ack = MANET_Underlay_Swarm_ACK()
        pkt_send = IP(dst=rcvd_src, proto=SWARM_PROTOCOL) / swarm_ack
        print("I will send the swarm_ack")
        pkt_send.show()
        send(pkt_send)

    @ATMT.state()
    def WAIT_FOR_CONFIRM(self):
        print("******************** STATE: WAIT_FOR_CONFIRM ********************")

    @ATMT.state()
    def WAIT_FOR_ACK(self):
        print("******************** STATE: WAIT_FOR_ACK ********************")

    @ATMT.state(final=1)
    def BUILT(self):
        print("******************** STATE: BUILT ********************")
        self.self_info()
        self.swarm_info()



    @ATMT.receive_condition(WAIT_FOR_CONFIRM)
    def swarm_confirm_arrived(self, pkt):
        print("I have received a swarm_confirm")
        pkt.show()

        raw_pkt = pkt[Raw]
        raw_data = raw(raw_pkt)

        if raw_data[0] != 4:
            print("Received wrong PDU type! Ignored!")

        if raw_data[0] == 4 and pkt[IP].dst == self.ip_addr:
            print("I have received a REAL swarm_confirm")
            rcvd_src = pkt[IP].src
            self.swarm_list.append(rcvd_src)
            self.send_swarm_ack(pkt)
        print(self.swarm_list)

        raise self.WAIT_FOR_CONFIRM()

    @ATMT.receive_condition(WAIT_FOR_ACK)
    def swarm_ack_arrived(self, pkt):
        print("I have received a swarm_ack")
        pkt.show()

        raw_pkt = pkt[Raw]
        raw_data = raw(raw_pkt)

        if raw_data[0] != 5:
            print("Received wrong PDU type! Ignored!")

        if raw_data[0] == 5 and pkt[IP].dst == self.ip_addr:
            print("I have received a REAL swarm_ack")

            raise self.BUILT()

        raise self.WAIT_FOR_ACK()

    @ATMT.timeout(WAIT_FOR_CONFIRM, TIMEOUT_WAIT_FOR_CONFIRM)
    def confirm_wait_timeout(self):
        if len(self.swarm_list) == 1:
            raise self.WAIT_FOR_BUILD()
        elif len(self.swarm_list) > 1:
            raise self.BUILT()


    def get_battery(self):
        return randint(1, 100)  #randomly generate a number to simulate the remain battery percentage



if __name__ == '__main__':
    sp = SwarmPeer()
    sp.role = "peer"
    print(sp.role)
    sp.run()    #start the manet underlay networking


    # start the sdn overlay controlling
    # mediator = IoTMediator()
    # mediator.run()
    #
    # if sp.role == "head":
    #     controller = IoTController()
    #     controller.run()


