import socket
import time
import serial
from ..utils.protocol import var_len_proto_recv
import struct
import queue
import threading


def compress_xf(data):
    return [max(int(item * 8), 255) for item in data]


ser_send_q = queue.Queue()
soc_send_q = queue.Queue()
ser_recv_q = queue.Queue()
soc_recv_q = queue.Queue()


def t_soc_recv_data():
    while True:
        soc_recv_q.put(soc.recv(1024))


def t_ser_recv_data():
    while True:
        ser_recv_q.put(ser.read(ser.inWaiting()))


def t_soc_send_data():
    while True:
        if not soc_send_q.empty():
            soc.send(soc_send_q.get())


def t_ser_send_data():
    while True:
        if not ser_send_q.empty():
            ser.write(ser_send_q.get())


if __name__ == "__main__":
    ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
    soc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soc.bind(('', 6666))
    soc.listen(1)
    conn, addr = soc.accept()
    print("Connected by", addr)
    try:

        t1 = threading.Thread(target=t_ser_send_data).start()
        t2 = threading.Thread(target=t_ser_recv_data).start()
        t3 = threading.Thread(target=t_soc_send_data).start()
        t4 = threading.Thread(target=t_soc_recv_data).start()

        while True:
            # assume 5 motor values
            if not soc_recv_q.empty():
                compressed_data = var_len_proto_recv(soc_recv_q.get())
                real_data = (compressed_data[0:1] * 2) + (compressed_data[1:2] * 2) + compressed_data[3:]
                ser_send_q.put(real_data)
            if not ser_recv_q.empty():
                data = var_len_proto_recv(ser_recv_q.get())
                for piece in data:
                    if len(piece):
                        unpacked = struct.unpack('7f', piece)
                        print(unpacked)
                        compressed = compress_xf(unpacked)
                        soc_send_q.put(compressed)
            time.sleep(0.001)

    except KeyboardInterrupt:
        print("Shutting down the socket")
        soc.close()  # cleanup socket
