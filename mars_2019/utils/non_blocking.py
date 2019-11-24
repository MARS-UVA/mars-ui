import sys
import threading
import multiprocessing as mp
import time

# non blocking input
class NBInput:
    @staticmethod
    def __input__(queue):
        while True:
            queue.put(input())

    def __init__(self):
        super().__init__()
        self.queue = mp.Manager().Queue()
        self.thread = threading.Thread(target=self.__input__, args=(self.queue,))
        self.thread.daemon = True
        self.thread.start()

    def get(self):
        try:
            return self.queue.get_nowait()
        except:
            return ""

if __name__ == "__main__":
    inp = NBInput()
    for i in range(10000):
        ip = inp.get()
        print(ip)
        time.sleep(0.1)