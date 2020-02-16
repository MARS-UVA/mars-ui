# Laptop Package

## RPC Client

First, make sure you have grpc installed

```bash
pip install grpcio grpcio-tools
```

To use the rpc client, copy the [jetsonroc.proto file](https://github.com/hanzhi713/mars-ros/blob/master/src/rpc-server/jetsonrpc.proto) from the mars-ros repository, and then compile the protocol definitions

```bash
cd mars_2019/laptop
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. protos/jetsonrpc.proto
```