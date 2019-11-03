import socket
import serial
import time


def var_len_proto_send(data: list):
    count = len(data)
    count = count | 0b11000000

    buffer = [0xff, count]
    buffer.extend(data)
    buffer.append(sum(buffer) % 256)
    return bytes(buffer)


ser = serial.Serial('COM4', 115200, timeout=1)
while True:
    vals = [int(x) for x in input().split(" ")]
    ser.write(var_len_proto_send(vals))
    time.sleep(0.1)
