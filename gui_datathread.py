"""
Provides a thread to read data from grpc
"""

import grpc
import threading
import time


class DataThread(threading.Thread):
    def __init__(self, name, gen):
        threading.Thread.__init__(self)
        self.name = name
        self.gen = gen
        self.recent_data = None
        self.message = None

        self.event = threading.Event()
        self.paused = False
        self.stopped = False

    def run(self):
        while not self.stopped:
            try:
                self.recent_data = next(self.gen)
            except:
                self.message = "Error: Server Disconnected"
                print("error: disconnected")
                break
            if self.paused:
                self.event.wait()

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

    def updateRate(self, newRate):
        pass

    def updateGenerator(self, newGen):
        # Used when the data transmission rate is changed
        self.gen = newGen
    
    def get_message(self):
        return self.message
