
"""
This code is designed to replicate the behavior of gamepad_driver_windows.py

For some reason, this code gives different outputs when running on windows and linux (I think). 
The configuration in get_gamepad_values works only for linux devices right now. Ideally, this 
code should work the same for windows and linux and therefore eliminate the need for 2 files. 
"""


"""
This code uses multiprocessing so that inputs.get_gamepad() can constantly be called to update
the stored state while the gamepad_encoder calls get_gamepad_values(). 

This code uses multiprocessing instead of a traditional thread because inputs.get_gamepad()
cannot be stopped while it is blocking and there is no gentle way to stop it. So 
multiprocess.terminate() is used to forcefully end the blocking. 
"""


import inputs
import math
import time
import multiprocessing

codes = [ # These are listed here just to initialize the state dictionary
    "ABS_X", "ABS_Y", # Left stick
    "ABS_RX", "ABS_RY", # Right stick
    "ABS_Z", "ABS_RZ", # Triggers
    "BTN_NORTH", "BTN_EAST", "BTN_SOUTH", "BTN_WEST", # Letter buttons (some are unused)
    "ABS_HAT0X", "ABS_HAT0Y", # Hat (unused)
]

state_update_process = None
sharedstate = multiprocessing.Array("i", [100, 100, 100, 100, 100, 1])


def thresh(a, l_th=0.1, u_th=1): # Copied from gamepad_driver_windows
    if abs(a) < l_th:
        return 0
    elif abs(a) > u_th:
        return -1 if a < 0 else 1
    return a

def format_gamepad_values(state):
        x = (state["ABS_X"] - 0)/32768.0
        y = (state["ABS_Y"] - 0)/32768.0 * -1
        lt = (state["ABS_Z"])/255.0
        rt = (state["ABS_RZ"])/255.0
        rx = (state["ABS_RX"] - 0)/32768.0
        ry = (state["ABS_RY"] - 0)/32768.0

        if abs(x) > abs(y):
            y = 0
        else:
            x = 0

        dbin = 1
        if state["BTN_WEST"] == 1: # This should be BTN_NORTH. I don't know why it's switched. Is it controller/computer dependent?
            dbin = 2
        if state["BTN_SOUTH"] == 1:
            dbin = 0

        args = [
            int(thresh(ry-rx, 0.1) * 100 + 100), # 0-200, neutral=100 (left stick)
            int(thresh(ry+rx, 0.1) * 100 + 100),
            int(thresh(x, 0.1) * 100 + 100), # 0-200, neutral=100 (right stick)
            int(thresh(y, 0.1) * 100 + 100), # unused for old robot
            int((-(lt + 1) + (rt + 1)) * 100 + 100), # left trigger is backwards, right is forwards
            dbin
        ]
        return args


class InputProcess(multiprocessing.Process):

    def __init__(self, sharedstate):
        multiprocessing.Process.__init__(self)

        self.state = {k:0 for k in codes}
        self.sharedstate = sharedstate

    def run(self):
        while True:
            events = inputs.get_gamepad() # this function call blocks until there is new gamepad input
            for event in events:
                if event.ev_type == "Sync":
                    continue
                # print("e type=" + str(event.ev_type) + ", code=" + str(event.code) + ", state=" + str(event.state))

                self.state[event.code] = event.state
                for i, n in enumerate(format_gamepad_values(self.state)):
                    self.sharedstate[i] = n
    

def start():
    global state_update_process
    state_update_process = InputProcess(sharedstate)
    state_update_process.start()

def stop():
    global state_update_process
    state_update_process.terminate()
    state_update_process.join()

def get_gamepad_values():
    return tuple(sharedstate[:])


if __name__ == "__main__":
    start()
    try:
        while True:
            print(get_gamepad_values())
            time.sleep(0.02)
    except KeyboardInterrupt:
        print("except KeyboardInterrupt")
        stop()
