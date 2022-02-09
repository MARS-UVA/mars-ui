import sys
import threading
import queue
import time

# non blocking input


class NBInput:
    @staticmethod
    def __input__(queue):
        while True:
            queue.put(input())

    def __init__(self):
        super().__init__()
        self.queue = queue.Queue()
        self.thread = threading.Thread(target=self.__input__, args=(self.queue,))
        self.thread.daemon = True
        self.thread.start()

    def get(self):
        return self.queue.get_nowait()

    def empty(self):
        return self.queue.empty()


if __name__ == "__main__":
    inp = NBInput()
    for i in range(10000):
        ip = inp.get()
        print(ip)
        time.sleep(0.1)
