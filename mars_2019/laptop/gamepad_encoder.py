import time
import logging
import grpc
import cv2
import numpy as np

from . import jetsonrpc_pb2_grpc
from . import jetsonrpc_pb2

# motor values array
motor_arr = np.zeros(8, "uint8")
# last values
motor_arr_prev = np.zeros(8, "uint8")
# uint64 view of the motor values
motor_ui64v = motor_arr.view("uint64")


def gamepad_val_gen():
    from .gamepad_driver import get_gamepad_values, joyGetPosEx, p_info
    while True:
        # Fetch new joystick data until it returns non-0 (that is, it has been unplugged)
        if joyGetPosEx(0, p_info) != 0:
            break
        motor_arr_prev[:] = motor_arr
        get_gamepad_values(motor_arr)
        if np.array_equal(motor_arr, motor_arr_prev):
            time.sleep(0.01)
            continue
        print(motor_arr)
        yield jetsonrpc_pb2.MotorCmd(values=motor_ui64v[0])


def dummy_val_gen():
    import random
    while True:
        for i in range(7):
            num = random.randint(0, 255)
            motor_arr[i] = num
        print(motor_arr)
        time.sleep(0.25)
        yield jetsonrpc_pb2.MotorCmd(values=motor_ui64v[0])


HOST = '172.27.39.1'    # The remote host
PORT = 50051        # The same port as used by the server


def run():
    with grpc.insecure_channel("{}:{}".format(HOST, PORT)) as channel:
        stub = jetsonrpc_pb2_grpc.JetsonRPCStub(channel)
        response = stub.SendMotorCmd(gamepad_val_gen())
        print(response)


if __name__ == '__main__':
    logging.basicConfig()
    run()
