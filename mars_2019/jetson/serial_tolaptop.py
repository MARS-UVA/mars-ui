import socket
import struct
import serial
import random
from ..utils.protocol import var_len_proto_send


def fake_data():
    # simulated current draws from hero, 0-32 amps
    return random.randint(0,32)


if __name__ == "__main__":
    ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
    while True:

        data = fake_data()
        data = struct.pack('1f', [data])
        data = var_len_proto_send(data)
        # print("sending data ", data)

        ser.write(data)
        time.sleep(0.01) # is this needed?