# Echo client program
import socket

HOST = '172.27.38.111'    # The remote host
PORT = 6666              # The same port as used by the server


def send4int(a, b, c, d):
    seq = [0xff, 0xff, a, b, c, d, 0]
    checksum = sum(seq[0:6]) % 255
    seq[6] = checksum
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(bytes(seq * 2))  # change here
        print('Received', repr(s.recv(1024)))


send4int(1, 2, 3, 5)
