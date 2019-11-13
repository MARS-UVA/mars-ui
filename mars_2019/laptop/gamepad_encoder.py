import socket
import time

from .gamepad_driver import get_gamepad_values, joyGetPosEx, p_info
from ..utils.protocol import var_len_proto_send


def thresh(a, l_th=0.1, u_th=1):
    if abs(a) < l_th:
        return 0
    elif abs(a) > u_th:
        return -1 if a < 0 else 1
    return a


def get_values():

    # Fetch new joystick data until it returns non-0 (that is, it has been unplugged)
    if joyGetPosEx(0, p_info) != 0:
        return []

    data = get_gamepad_values()
    y = data[1]
    ry = -data[2]
    rx = -data[3]
    lt = data[5]
    rt = data[6]
    button_states = data[7]

    y_or_a = 0.0
    if button_states['y']:
        y_or_a = 1.0
    elif button_states['a']:
        y_or_a = -1.0

    values = []
    values.append(int(thresh(ry-rx, 0.1) * 100 + 100))
    values.append(int(thresh(ry-rx, 0.1) * 100 + 100))
    values.append(int(thresh(ry+rx, 0.1) * 100 + 100))
    values.append(int(thresh(ry+rx, 0.1) * 100 + 100))
    values.append(int(y_or_a * 100 + 100))
    values.append(int((-(lt + 1) / 2 + (rt + 1) / 2) * 100 + 100))
    values.append(int(thresh(y, 0.1) * 100 + 100))
    return values


HOST = '172.27.39.176'    # The remote host
PORT = 6666              # The same port as used by the server
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    while True:
        vals = get_values()
        print(vals)
        s.send(var_len_proto_send(vals))
        time.sleep(0.01)
