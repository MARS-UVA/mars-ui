from concurrent import futures
import logging

import grpc

from protos import jetsonrpc_pb2_grpc, jetsonrpc_pb2


class Greeter(helloworld_pb2_grpc.GreeterServicer):

    def MotorCurrent(self, request, context):
        pass



def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    jetsonrpc_pb2_grpc.add_GreeterServicer_to_server(Greeter(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    serve()