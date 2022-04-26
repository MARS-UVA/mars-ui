import grpc
import cv2
import numpy as np
import typing
import json

from protos import jetsonrpc_pb2_grpc, jetsonrpc_pb2

STUB = jetsonrpc_pb2_grpc.JetsonRPCStub # this is a type


def stream_image(stub: STUB, rate=30):
    response = stub.StreamImage(jetsonrpc_pb2.Rate(rate=rate))
    for item in response:
        arr = np.frombuffer(item.data, "uint8")
        yield cv2.imdecode(arr, cv2.IMREAD_COLOR)


def stream_imu(stub: STUB, rate=30):
    response = stub.StreamIMU(jetsonrpc_pb2.Rate(rate=rate))
    for item in response:
        yield item.values

def stream_hero_feedback(stub: STUB, rate=30):
    return stub.StreamHeroFeedback(jetsonrpc_pb2.Rate(rate=rate))

def send_dd_command(stub: STUB, gen):
    return stub.StreamDDCommand(gen)

def emergency_stop(stub: STUB):
    stub.EmergencyStop(jetsonrpc_pb2.Void())

def change_drive_state(stub: STUB, state):
    stub.ChangeDriveState(jetsonrpc_pb2.DriveState(dse=state))

def start_action(stub: STUB, text):
    stub.StartAction(jetsonrpc_pb2.ActionDescription(text=text))


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("host", type=str, default="localhost")
    args = parser.parse_args()

    with grpc.insecure_channel(args.host + ':50051') as channel:
        print("Connected to", args.host)
        stub = jetsonrpc_pb2_grpc.JetsonRPCStub(channel)

        data1 = stream_arm_status(stub)
        data2 = stream_motor_current(stub)
        counter = 0
        for item1, item2 in zip(data1, data2):
            print(item1, item2)
        #     counter += 1
        #     if counter > 10:
        #         break
        # data.close()
