import time
import grpc
import numpy as np
import platform
import sys

from protos import jetsonrpc_pb2_grpc
from protos import jetsonrpc_pb2
from utils.protocol import encode_values


gamepad_running = False

detected_platform = None
if sys.platform == "win32" or sys.platform == "cygwin": detected_platform = "WINDOWS"
if sys.platform.startswith("linux"): detected_platform = "LINUX"


def gamepad_val_gen():
    if detected_platform == "WINDOWS":
        print("gamepad_encoder starting windows driver")
        from gamepad_driver.gamepad_driver_windows import get_gamepad_values, joyGetPosEx, p_info
    elif detected_platform == "LINUX":
        print("gamepad_encoder starting linux driver")
        from gamepad_driver.gamepad_driver_linux import process_start, process_stop, get_gamepad_values
        process_start()
    else:
        print("Error: gamepad_encoder system platform not recognized! Aborting...")
        return

    prev_encoded_val = None
    while gamepad_running:
        if detected_platform == "WINDOWS" and joyGetPosEx(0, p_info) != 0: 
            # For some reason, this is necessary for the windows code to update the gamepad values
            print("Error: gamepad_encoder gamepad disconnected")
            break

        values = get_gamepad_values()
        encoded_val = encode_values(*values)
        if prev_encoded_val == encoded_val: # don't send messages if gamepad value hasn't changed
            time.sleep(0.01)
        else:
            print("gamepad_encoder sending motor values:", values)
            prev_encoded_val = encoded_val
            yield jetsonrpc_pb2.MotorCmd(values=encoded_val)
    
    if detected_platform == "LINUX": # only linux driver needs a "stop()" command
        process_stop()

def dummy_val_gen():
    import random
    while True:
        left = random.randint(0, 200)  # left
        right = random.randint(0, 200)  # right
        act1 = random.randint(0, 200)  # actuator1
        act2 = random.randint(0, 200)  # actuator2
        ladder = random.randint(0, 200)  # arm
        deposit = random.choice([0, 1, 2])

        print(left, right, act1, act2, ladder, deposit)
        yield jetsonrpc_pb2.MotorCmd(values=encode_values(
            left, right, act1, act2, ladder, deposit
        ))
        time.sleep(0.1)

def start(host, port):
    print("gamepad_encoder starting...")
    global gamepad_running
    gamepad_running = True
    with grpc.insecure_channel("{}:{}".format(host, port)) as channel:
        stub = jetsonrpc_pb2_grpc.JetsonRPCStub(channel)
        response = stub.SendMotorCmd(gamepad_val_gen())
        # response = stub.SendMotorCmd(dummy_val_gen()) # for sending fake data
        print(response)

def stop():
    print("gamepad_encoder stopping...")
    global gamepad_running
    gamepad_running = False


if __name__ == '__main__':
    # host = "10.0.0.60"
    # host = "172.27.172.34"
    host = "127.0.0.1"
    port = 50051

    start(host, port)
