import time
import grpc
import numpy as np
import sys
import rpc_client

from protos import jetsonrpc_pb2_grpc
from protos import jetsonrpc_pb2
from utils.protocol import encode_values
# from keyboard_driver import keyboard_val_gen


def start(stub):
    def g():
        m1 = 125
        m2 = 125
        bucket_ladder_angle = 100
        bucket_ladder_extension = 100
        bucket_ladder_chain = 100
        deposit_angle = 100
        conveyor = 100

        yield jetsonrpc_pb2.DDCommand(values=
            encode_values(m1, m2, bucket_ladder_angle, bucket_ladder_extension, bucket_ladder_chain, deposit_angle, conveyor)
        )
    stub.SendDDCommand(g())

def stop(stub):
    def g():
        m1 = 100
        m2 = 100
        bucket_ladder_angle = 100
        bucket_ladder_extension = 100
        bucket_ladder_chain = 100
        deposit_angle = 100
        conveyor = 100

        yield jetsonrpc_pb2.DDCommand(values=
            encode_values(m1, m2, bucket_ladder_angle, bucket_ladder_extension, bucket_ladder_chain, deposit_angle, conveyor)
        )
    stub.SendDDCommand(g())


if __name__ == '__main__':
    import network_config

    with grpc.insecure_channel("{}:{}".format(network_config.HOST, network_config.PORT)) as channel:
        try:
            stub = jetsonrpc_pb2_grpc.JetsonRPCStub(channel)
            print("Changing to drive state DIRECT_DRIVE...")
            rpc_client.change_drive_state(stub, jetsonrpc_pb2.DriveStateEnum.DIRECT_DRIVE)

            start(stub)
            time.sleep(30)
            stop(stub)

        except KeyboardInterrupt:
            stop(stub)
        finally:
            print("Changing to drive state IDLE...")
            rpc_client.change_drive_state(stub, jetsonrpc_pb2.DriveStateEnum.IDLE)
