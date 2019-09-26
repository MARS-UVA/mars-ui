# Echo client program
import socket
import random

seq = [0xff, 0xff, 4, 23, 45, 67, 74, 0]
seq[-1] = sum(seq[:-1]) % 256
seq *= 10
HOST = 'localhost'    # The remote host
PORT = 6666              # The same port as used by the server
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    total = 0
    while total < len(seq):
        increment = random.randint(4, 10)
        print("Sending", seq[total:total + increment])
        s.sendall(bytes(seq[total:total + increment]))
        print(s.recv(1024).decode("utf-8"))
        total += increment