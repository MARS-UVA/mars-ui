import socket
import time
from test2 import get_gamepad_values, joyGetPosEx, p_info


def thresh(a, th):
    if abs(a) < th:
        return 0
    return a


def get_values():

    if joyGetPosEx(0, p_info) != 0:
        return []

    data = get_gamepad_values()
    rx = data[2]
    ry = data[3]
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
    values.append(int(((1 + thresh(ry-rx, 0.1)) * 100) + 100))
    values.append(int(((1 + thresh(ry-rx, 0.1)) * 100) + 100))
    values.append(int(((1 + thresh(ry+rx, 0.1)) * 100) + 100))
    values.append(int(((1 + thresh(ry+rx, 0.1)) * 100) + 100))
    values.append(int(((1 + y_or_a) * 100) + 100))
    values.append(int(((1 + lb_or_rb) * 100) + 100))
    values.append(int(((1 + thresh(y, 0.1)) * 100) + 100))

    return values

while True:
    print(get_values())

# Dummy values
# rx = -0.6
# ry = 0.2
# y = 0.2
# button_states = {}
# button_states['y'] = True
# button_states['a'] = False
# button_states['tl'] = True
# button_states['tr'] = False

# print(get_values())


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
        s.sendall(send_data(get_values()))
        time.sleep(10)
