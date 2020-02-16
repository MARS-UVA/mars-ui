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
# python3 -m mars_2019.laptop.tkinter_test_class (on branch master)

import tkinter as tk
# from tkinter import *

from gui_graph import LineGraph
# import matplotlib.pyplot as plt
# from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
# import matplotlib.animation as animation
# import numpy as np
# from collections import deque

from . import rpc_client
from .protos import jetsonrpc_pb2_grpc
import grpc
import threading
import time
import random


class DataThread(threading.Thread):
	def __init__(self, threadID, name, counter):
		threading.Thread.__init__(self)
		self.threadID = threadID
		self.name = name
		self.counter = counter

		# self.channel = grpc.insecure_channel('172.27.39.1:50051')
		# self.stub = jetsonrpc_pb2_grpc.JetsonRPCStub(self.channel)
		# self.gen = rpc_client.stream_motor_current(self.stub)

		# self.gen = fake_generator

		self.stopped = False
		self.recent_data = None
	
	def run(self):
		# print("starting thread")
		while not self.stopped:
			# self.recent_data = next(self.gen)
			self.recent_data = next(fake_generator())
			# self.recent_data = int(random.random()*10)
			# time.sleep(1)

	def get_recent_data(self):
		# print(self.recent_data)
		return self.recent_data

	def stop(self):
		# print(stopping thread)
		# self.channel.close()
		self.stopped = True


def animate(tick):
	return dt.get_recent_data()
	# return next(g)

def fake_generator():
	while True:
		yield [int(random.random()*10) for i in range(8)]
		# yield int(random.random()*10)
		
if __name__ == '__main__':

	root_width = 1280
	root_height = 720
	root = tk.Tk()
	root.geometry("{}x{}".format(root_width, root_height)) # https://stackoverflow.com/questions/34276663/tkinter-gui-layout-using-frames-and-grid

	
	#print("Connected to", args.host)
	# stub = jetsonrpc_pb2_grpc.JetsonRPCStub(channel)
	# g = rpc_client.stream_motor_current(stub)

	dt = DataThread(1, "dt1", 1)
	dt.start()



	graph1 = LineGraph(root, animate)
	graph1.pack(side=tk.TOP)

	root.mainloop()

	# close data thread
	dt.stop()
	dt.join()





"""
from tkinter import *

root = Tk()
frame = Frame(root)
frame.pack()

bottomframe = Frame(root)
bottomframe.pack( side = BOTTOM )


redbutton = Button(frame, text = "Red", fg = "red")
redbutton.pack( side = LEFT)

greenbutton = Button(frame, text = "Brown", fg="brown")
greenbutton.pack( side = LEFT )

bluebutton = Button(frame, text = "Blue", fg = "blue")
bluebutton.pack( side = LEFT )

blackbutton = Button(bottomframe, text = "Black", fg = "black")
blackbutton.pack( side = BOTTOM)

root.mainloop()

"""
