import socket
import struct
import pickle
import os


def get(client):
    filepath = os.path.dirname(os.path.abspath(__file__))
    obj = client.recv(4)
    header_size = struct.unpack('i', obj)[0]
    if header_size == 0:
        pass
    else:
        header_types = client.recv(header_size)
        header = pickle.loads(header_types)
        # print(header)
        file_size = header['file_size']
        file_name = header['file_name']
        with open('%s\\%s' % (filepath, file_name), 'wb') as f:
            recv_size = 0
            while recv_size < file_size:
                res = client.recv(1024)
                f.write(res)
                recv_size += len(res)


def run(ip):
    client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client.connect((ip, 5400))
    msg = "useless"
    client.send(msg.encode('utf-8'))
    get(client)
    client.close()


if __name__ == '__main__':
    ip = input()
    run(ip)
