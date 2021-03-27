# MARS 2019

Codebase for the MARS club @ UVA

## Configure RPC Client

First, make sure you have grpc installed

```bash
pip install grpcio grpcio-tools
```

To setup the rpc client, you need to
1. get [jetsonrpc.proto file](https://github.com/hanzhi713/mars-ros/blob/master/src/rpc-server/jetsonrpc.proto)
2. create a folder called `protos` (under the laptop folder)
3. move jetsonrpc.proto into the `protos` folder
4. run the following command

```bash
cd mars_2019/laptop
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. protos/jetsonrpc.proto
```

## Setup Manual Control

Launch the gamepad state interpreter

```bash
python -m mars_2019.laptop.gamepad_encoder
```
