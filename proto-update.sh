#!/bin/sh

mkdir -p protos
cd protos

echo Deleting old protofile...
rm jetsonrpc.proto

echo Fetching new protofile...
wget https://raw.githubusercontent.com/MARS-UVA/mars-ros/master/src/rpc-server/jetsonrpc.proto

echo Generating python files...
cd ..
python3 -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. protos/jetsonrpc.proto

echo Done.
