import socket
import time
import math
from test2 import get_gamepad_values, joyGetPosEx, p_info


def thresh(a, l_th=0.1, u_th=1):
    if abs(a) < l_th:
        return 0
    elif abs(a) > u_th:
        return -1 if a < 0 else 1
    return a


def get_values():

    if joyGetPosEx(0, p_info) != 0:
        return []

    data = get_gamepad_values()
    rx = data[3]
    ry = data[2]
    y = data[1]
    button_states = data[7]

    y_or_a = 0.0
    if button_states['y']:
        y_or_a = 1.0
    elif button_states['a']:
        y_or_a = -1.0

    lb_or_rb = 0.0
    if button_states['tl']:
        lb_or_rb = 1.0
    elif button_states['tr']:
        lb_or_rb = -1.0

    values = []
    values.append(int(((thresh(ry-rx, 0.1)) * 100) + 100))
    values.append(int(((thresh(ry-rx, 0.1)) * 100) + 100))
    values.append(int(((thresh(ry+rx, 0.1)) * 100) + 100))
    values.append(int(((thresh(ry+rx, 0.1)) * 100) + 100))
    values.append(int(((y_or_a) * 100) + 100))
    values.append(int(((lb_or_rb) * 100) + 100))
    values.append(int(((thresh(y, 0.1)) * 100) + 100))

    return values


def send_data(data: list):
    count = len(data) | 0b11000000

    buffer = [0xff, count]
    buffer.extend(data)
    buffer.append(sum(buffer) % 256)
    return bytes(buffer)


HOST = '172.27.39.176'    # The remote host
PORT = 6666              # The same port as used by the server
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    while True:
        vals = get_values()
        print(vals)
        s.send(send_data(vals))
        time.sleep(0.01)