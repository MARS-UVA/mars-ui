# Echo client program
import socket

HOST = '172.27.38.111'    # The remote host
PORT = 6666              # The same port as used by the server


def send4int(a, b, c, d):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(...)  # change here
        print('Received', repr(s.recv(1024)))
