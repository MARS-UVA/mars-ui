from concurrent import futures
import logging
import numpy as np
import random
import time
import cv2
import grpc

from protos import jetsonrpc_pb2_grpc, jetsonrpc_pb2


class FakeRPCServer(jetsonrpc_pb2_grpc.JetsonRPC):

    # Receiving data:

    def SendMotorCmd(self, request, context):
        print("received motor command...")
        # Copied from https://github.com/MARS-UVA/mars-ros/blob/master/src/rpc-server/src/grpc-server.cpp function SendMotorCmd
        for cmd in request:
            raw = cmd.values
            motors = [-1]*8
            motors[7] = (raw & 0b11) * 100
            raw >>= 2
            motors[6] = (raw & 0b111111) << 2
            raw >>= 6
            motors[5] = (raw & 0b111111) << 2
            raw >>= 6
            motors[4] = (raw & 0b111111) << 2
            raw >>= 6
            motors[3] = (raw & 0b111111) << 2
            motors[2] = (raw & 0b111111) << 2
            raw >>= 6
            motors[1] = raw << 2
            motors[0] = raw << 2

            print("received motor command:", motors)

        return jetsonrpc_pb2.Void()

    # Sending data:

    def StreamIMU(self, request, context):
        while True:
            time.sleep(1.0/request.rate)
            # 6 values: 3 for linear acc, 3 for angular acc
            # random floats between 0 and 10
            randoms = [random.random() * 10 for i in range(6)]
            yield jetsonrpc_pb2.IMUData(values=randoms)

    def StreamImage(self, request, context):
        cap = cv2.VideoCapture(0)
        while(True):
            time.sleep(1.0/request.rate)
            ret, frame = cap.read()
            ret, data = cv2.imencode(".jpg", frame)
            yield jetsonrpc_pb2.Image(data=data.tobytes())

    def StreamMotorCurrent(self, request, context):
        while True:
            time.sleep(1.0/request.rate)
            randoms = np.array([random.randint(0, 10) for i in range(8)], 'uint8') # 8 motors
            randoms = randoms.view('uint64') # combine into one value, as specified by the proto file
            yield jetsonrpc_pb2.MotorCurrent(values=randoms[0])

    def StreamArmStatus(self, request, context):
        while True:
            time.sleep(1.0/request.rate)
            random_angle = random.random() * 45
            random_translation = random.random() * 2
            yield jetsonrpc_pb2.ArmStatus(angle=random_angle, translation=random_translation)

    def EmergencyStop(self, request, context):
        print("fake_rpc_server received emergency stop!")
        return jetsonrpc_pb2.Void()


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    jetsonrpc_pb2_grpc.add_JetsonRPCServicer_to_server(FakeRPCServer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    print("fake_rpc_server starting...")
    logging.basicConfig()
    serve()
