# For running rpc-server on the jetson:
# HOST = "172.27.172.34"
# PORT = "50051" # This port should never change


# For running rpc-server in a virtual machine:
# In virtualbox, you can configure ports that map between the host and the guest OS. I chose host port 50052 to exose guest port 50051 (the port ROS uses)
HOST = "localhost"
PORT = "50052"
