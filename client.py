# Echo client program
import socket

HOST = 'localhost'    # The remote host
PORT = 6666              # The same port as used by the server
seq = [0xff, 0xff, 0, 0, 0, 0, 0]
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(bytes(seq * 2))

    print('Received', repr(s.recv(1024)))
    print('Received', repr(s.recv(1024)))
