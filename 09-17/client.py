import socket

HOST = '172.27.38.111'    # The remote host
PORT = 6667           # The same port as used by the server


def sendints(*args):
    seq = [] # make your sequence
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(bytes(seq))
        print('Received', repr(s.recv(1024)))


sendints(1, 2, 3, 5)
sendints(127)
sendints(1, 2, 3, 5, 9, 99, 123)

