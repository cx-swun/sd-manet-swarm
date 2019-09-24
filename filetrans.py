import socket
import os
import struct
import pickle


def get(file_name, client):
    filepath = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(filepath, file_name)
    if os.path.isfile(file_path):
        header = {
            'file_name': file_name,
            'file_size': os.path.getsize(file_path)
        }
        header_bytes = pickle.dumps(header)
        client.send(struct.pack('i', len(header_bytes)))
        client.send(header_bytes)
        with open(file_path, 'rb') as f:
            for line in f:
                client.send(line)
    else:
        client.send(struct.pack('i', 0))


def run(filename):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 80))
    server_ip = s.getsockname()[0]
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((server_ip, 5400))
    server.listen(5)
    while True:
        client, addr = server.accept()
        print('A new connection from %s' % addr[0])
        while True:
            try:
                request = client.recv(1024).decode('utf-8')
                # print('Send %s to %s' % (request, addr[0]))
                get(filename, client)
            except ConnectionResetError:
                break
            break
        client.close()
        break
    server.close()

