import socket
import netifaces


def get_broadcast_address(ip):
    net = netifaces.interfaces()
    for eth in net:
        addrs = netifaces.ifaddresses(eth)
        try:
            detials = addrs[netifaces.AF_INET]
            for detial in detials:
                if str(detial["addr"]) == ip:        # 获取的信息与ip地址进行对比
                    broadcast = detial["broadcast"]
                    break
        except:
            pass
    return broadcast


def get_host_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('114.114.114.114', 80))
    local_ip = s.getsockname()[0]
    return local_ip


def main():
    host_ip = get_host_ip()
    print("ip地址是:" + host_ip)
    broadcast_address = get_broadcast_address(host_ip)
    print("广播地址是:" + broadcast_address)
    return broadcast_address


if __name__ == '__main__':
    broadcast_address = main()

