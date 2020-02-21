# !/usr/bin/python3

"""
The goal is to develop a cross-platform friendly graphical user interface for controlling and monitoring our robot. Recommended framework: Tkinter/PyQt. Recommended graphing tool: Matplotlib/PyQtGraph. The following tasks are not in order
1. Finish the RPC client implementation
2. Graph the angle of the robotic arm using the incoming IMU data
3. Display and graph the current flowing through each of the motors
4. Add some buttons for performing shortcut actions like turning around/digging, etc.
There will be more tasks...
"""

# finish series graph, frame with check boxes for 8 motors, threading for animate (one thread reads fast data and stores the most recent data, slow animate function reads that value)
# python3 -m mars_2019.laptop.gui_test_grpc

from gui_graph import LineGraph

from . import rpc_client
from .protos import jetsonrpc_pb2_grpc
import tkinter as tk
import grpc
import threading
import time
import random
import numpy as np


class DataThread(threading.Thread):
	def __init__(self, threadID, name, test=False):
		threading.Thread.__init__(self)
		self.TESTING = test
		self.threadID = threadID
		self.name = name
		# self.counter = counter

		if not self.TESTING:
			self.channel = grpc.insecure_channel('172.27.39.1:50051')
			self.stub = jetsonrpc_pb2_grpc.JetsonRPCStub(self.channel)
			self.gen = rpc_client.stream_motor_current(self.stub)
		else:
			self.gen = self.fake_generator()

		self.stopped = False
		self.recent_data = None
	
	def run(self):
		# print("starting thread")
		while not self.stopped:
			self.recent_data = next(self.gen)/4
			# time.sleep(1)

	def get_recent_data(self):
		return self.recent_data

	def stop(self):
		# print("stopping thread")
		self.stopped = True
		if not self.TESTING:
			self.channel.close()

	def fake_generator(self):
		while not self.stopped:
			yield np.array([random.randint(0, 8)*4 for i in range(8)])
			time.sleep(0.01)


def animate(tick):
	return dt.get_recent_data()
		
if __name__ == '__main__':
	root_width = 1280
	root_height = 720
	root = tk.Tk()
	root.geometry("{}x{}".format(root_width, root_height))

	dt = DataThread(1, "dt", test=True)
	dt.start()

	graph1 = LineGraph(root, animate)
	graph1.pack(side=tk.TOP)

	root.mainloop()

	# close data thread
	dt.stop()
	dt.join()

