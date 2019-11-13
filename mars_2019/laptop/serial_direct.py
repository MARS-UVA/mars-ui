import socket
import time
from gamepad_driver import get_gamepad_values, joyGetPosEx, p_info
from gamepad_encoder import get_values, send_data
import serial

ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
while True:
    vals = get_values()
    print(vals)
    ser.write(send_data(vals))
    time.sleep(0.01)
