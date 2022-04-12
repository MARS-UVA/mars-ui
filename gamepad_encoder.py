import time
import grpc
import numpy as np
import platform
import sys
import rpc_client

from protos import jetsonrpc_pb2_grpc
from protos import jetsonrpc_pb2
from utils.protocol import encode_values
# from keyboard_driver import keyboard_val_gen

gamepad_running = False

detected_platform = None
if sys.platform == "win32" or sys.platform == "cygwin": detected_platform = "WINDOWS"
if sys.platform.startswith("linux"): detected_platform = "LINUX"


def gamepad_val_gen():
    if detected_platform == "WINDOWS":
        print("gamepad_encoder starting windows driver")
        # from gamepad_driver_windows import get_gamepad_values
        from gamepad_driver_windows import get_gamepad_values, joyGetPosEx, p_info
    elif detected_platform == "LINUX":
        print("gamepad_encoder starting linux driver")
        import gamepad_driver_linux
        from gamepad_driver_linux import get_gamepad_values
        gamepad_driver_linux.start()
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
        if prev_encoded_val == encoded_val:  # don't send messages if gamepad value hasn't changed
            # print("skipping, e_v=", encoded_val, "v=", values)
            time.sleep(0.01)
        else:
            print("gamepad_encoder sending motor values:", values)
            prev_encoded_val = encoded_val
            yield jetsonrpc_pb2.DDCommand(values=encoded_val)
    
    if detected_platform == "LINUX": # only linux driver needs a "stop()" command
        gamepad_driver_linux.stop()

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
        yield jetsonrpc_pb2.DDCommand(values=encode_values(
            left, right, act1, act2, ladder, deposit
        ))
        time.sleep(0.1)

def start(host, port, stub):
    print("gamepad_encoder starting...")
    global gamepad_running
    gamepad_running = True
    response = stub.SendDDCommand(gamepad_val_gen())
    # response = stub.SendMotorCmd(dummy_val_gen()) # for sending fake data
    print(response)

def stop():
    print("gamepad_encoder stopping...")
    global gamepad_running
    gamepad_running = False


if __name__ == '__main__':
    host = "localhost"
    port = 50051

    with grpc.insecure_channel("{}:{}".format(host, port)) as channel:
        try:
            stub = jetsonrpc_pb2_grpc.JetsonRPCStub(channel)
            print("Changing to drive state DIRECT_DRIVE...")
            rpc_client.change_drive_state(stub, jetsonrpc_pb2.DriveStateEnum.DIRECT_DRIVE)

            start(host, port, stub)
        except KeyboardInterrupt:
            stop()
        finally:
            print("Changing to drive state IDLE...")
            rpc_client.change_drive_state(stub, jetsonrpc_pb2.DriveStateEnum.IDLE)
