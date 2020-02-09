import time
import logging
import grpc
import cv2
import numpy as np
import platform

from . import jetsonrpc_pb2_grpc
from . import jetsonrpc_pb2
from ..utils.protocol import encode_values
from .keyboard_driver import keyboard_val_gen


def gamepad_val_gen():
    from .gamepad_driver import get_gamepad_values, joyGetPosEx, p_info
    prev_motor_val = 0
    while True:
        # Fetch new joystick data until it returns non-0 (that is, it has been unplugged)
        if joyGetPosEx(0, p_info) != 0:
            print("Gamepad disconnected")
            break
        values = get_gamepad_values()
        motor_val = encode_values(*values)
        if prev_motor_val == motor_val:  # don't seed messages if gamepad value is not changing
            time.sleep(0.01)
            continue
        print(values)
        prev_motor_val = motor_val
        yield jetsonrpc_pb2.MotorCmd(values=motor_val)


def dummy_val_gen():
    import random
    while True:
        left = random.randint(0, 200)  # left
        right = random.randint(0, 200)  # right
        act1 = random.randint(0, 200)  # actuator1
        act2 = random.randint(0, 200)  # actuator2
        ladder = random.randint(0, 200)  # arm
        deposit = random.choice([0, 1, 2])

        print(left, left, right, right, act1, act2, ladder, deposit)
        yield jetsonrpc_pb2.MotorCmd(values=encode_values(
            left, right, act1, act2, ladder, deposit
        ))


HOST = '172.27.39.1'    # The remote host
PORT = 50051        # The same port as used by the server


def run():
    with grpc.insecure_channel("{}:{}".format(HOST, PORT)) as channel:
        stub = jetsonrpc_pb2_grpc.JetsonRPCStub(channel)
        response = stub.SendMotorCmd(keyboard_val_gen())
        print(response)


if __name__ == '__main__':
    logging.basicConfig()
    run()
