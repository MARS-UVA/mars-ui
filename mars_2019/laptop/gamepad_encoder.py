import time
import logging
import grpc
import cv2
import numpy as np
import platform

from . import jetsonrpc_pb2_grpc
from . import jetsonrpc_pb2

# motor values array
motor_arr = np.zeros(4, "uint8")
# last values
motor_arr_prev = np.zeros(4, "uint8")
# uint32 view of the motor values
motor_ui32v = motor_arr.view("uint32")


def gamepad_val_gen():
    from .gamepad_driver import get_gamepad_values, joyGetPosEx, p_info
    while True:
        # Fetch new joystick data until it returns non-0 (that is, it has been unplugged)
        if joyGetPosEx(0, p_info) != 0:
            print("Gamepad disconnected")
            break
        motor_arr_prev[:] = motor_arr
        get_gamepad_values(motor_arr)
        if np.array_equal(motor_arr, motor_arr_prev): # don't seed messages if gamepad value is not changing
            time.sleep(0.01)
            continue
        print(motor_arr)
        yield jetsonrpc_pb2.MotorCmd(values=motor_ui32v[0])


def dummy_val_gen():
    import random
    while True:
        left = random.randint(0, 200) # left
        right = random.randint(0, 200) # right
        act = random.randint(0, 200) # actuator
        ladder = random.randint(0, 200) # arm
        deposit = random.choice([0, 1, -1])
        
        print(left, left, right, right, deposit * 100 + 100, act, ladder)
        motor_arr[0] = left
        motor_arr[1] = right
        motor_arr[2] = act
        motor_arr[3] = ladder & 0b11111100
        motor_arr[3] |= deposit + 1
        time.sleep(0.5)
        yield jetsonrpc_pb2.MotorCmd(values=motor_ui32v[0])


HOST = 'localhost'    # The remote host
PORT = 50051        # The same port as used by the server


def run():
    with grpc.insecure_channel("{}:{}".format(HOST, PORT)) as channel:
        stub = jetsonrpc_pb2_grpc.JetsonRPCStub(channel)
        response = stub.SendMotorCmd(dummy_val_gen())
        print(response)


if __name__ == '__main__':
    logging.basicConfig()
    run()
