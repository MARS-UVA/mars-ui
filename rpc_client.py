import grpc
import cv2
import numpy as np

from protos import jetsonrpc_pb2_grpc, jetsonrpc_pb2
import typing
import struct

STUB = jetsonrpc_pb2_grpc.JetsonRPCStub


def stream_image(stub: STUB, rate=30):
    response = stub.StreamImage(jetsonrpc_pb2.Rate(rate=rate))
    for item in response:
        arr = np.frombuffer(item.data, "uint8")
        yield cv2.imdecode(arr, cv2.IMREAD_COLOR)


def stream_imu(stub: STUB, rate=30):
    response = stub.StreamIMU(jetsonrpc_pb2.Rate(rate=rate))
    for item in response:
        yield item.values


def stream_motor_current(stub: STUB, rate=30):
    response = stub.StreamMotorCurrent(jetsonrpc_pb2.Rate(rate=rate))
    arr = np.zeros(1, 'uint64')
    arr_uint8v = arr.view('uint8')
    for item in response:
        arr[0] = item.values
        yield arr_uint8v.astype("float32")


def stream_arm_status(stub: STUB, rate=30):
    response = stub.StreamArmStatus(jetsonrpc_pb2.Rate(rate=rate))
    for item in response:
        yield (item.angle, item.translation)


def send_motor_cmd(stub: STUB, gen):
    return stub.StreamMotorCurrent(gen)


def start_dig(stub: STUB, param=29):
    return stub.StartDig(jetsonrpc_pb2.Params(param=param))


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
