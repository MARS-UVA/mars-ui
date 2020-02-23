"""
Provides a thread to read data from grpc
"""

from gui_graph import LineGraph

import rpc_client
from protos import jetsonrpc_pb2_grpc
import tkinter as tk
import grpc
import threading
import time
import random
import numpy as np


class DataThread(threading.Thread):
    def __init__(self, name, gen, test=False):
        threading.Thread.__init__(self)
        self.TESTING = test
        self.name = name
        self.gen = gen
        self.recent_data = None

        self.stopped = False

    def run(self):
        # print("starting thread")
        while not self.stopped:
            self.recent_data = next(self.gen)
            # time.sleep(1)

    def get_recent_data(self):
        return self.recent_data

    def stop(self):
        # print("stopping thread")
        self.stopped = True


"""
def animate(tick):
	return dt.get_recent_data()
		
if __name__ == '__main__':
	root_width = 1280
	root_height = 720
	root = tk.Tk()
	root.geometry("{}x{}".format(root_width, root_height))

	dt = DataThread("dt", ___)
	dt.start()

	graph1 = LineGraph(root, animate)
	graph1.pack(side=tk.TOP)

	root.mainloop()

	# stop data thread
	dt.stop()
	dt.join()
"""
