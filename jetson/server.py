import socket
import traceback
import time
import serial
from serial_proto_ethan import var_len_proto_send

if __name__ == "__main__":
    ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 6666))
        s.listen(1)
        try:
            conn, addr = s.accept()
            print("Connected by", addr)

            while True:
                data = conn.recv(1024)
                ser.write(data)
                time.sleep(0.01)

        except KeyboardInterrupt:
            print("Shutting down the socket")
            s.close()  # cleanup socket
