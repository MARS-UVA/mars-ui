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

        self.event = threading.Event()
        self.paused = False
        self.stopped = False

    def run(self):
        while not self.stopped:
            self.recent_data = next(self.gen)
            if self.paused:
                self.event.wait()
            # time.sleep(1)

    def get_recent_data(self):
        return self.recent_data

    def stopCollection(self):
        self.event.clear()
        self.paused = True

    def resumeCollection(self):
        self.event.set()
        self.paused = False

    def isCollecting(self):
        return (not self.stopped) and (not self.paused)

    def stop(self):
        # self.gen.close() # TODO close the generator?
        self.event.set()
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
