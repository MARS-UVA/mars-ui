#!/bin/bash

mkdir -p mars_2019/laptop/protos
cd mars_2019/laptop/protos
rm jetsonrpc.proto
wget https://github.com/hanzhi713/mars-ros/blob/master/src/rpc-server/jetsonrpc.proto
cd ..
python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. protos/jetsonrpc.proto
