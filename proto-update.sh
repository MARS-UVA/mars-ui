#!/bin/bash

mkdir -p protos
cd protos
rm jetsonrpc.proto
wget https://raw.githubusercontent.com/MARS-UVA/mars-ros/master/src/rpc-server/jetsonrpc.proto
cd ..
python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. protos/jetsonrpc.proto
