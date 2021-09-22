
"""
This code is designed to replicate the behavior of gamepad_driver_windows.py

For some reason, this code gives different outputs when running on windows and linux (I think). 
The configuration in get_gamepad_values works only for linux devices right now. Ideally, this 
code should work the same for windows and linux and therefore eliminate the need for 2 files. 
"""

import inputs
import math
import time
import threading

codes = [ # These are listed here just to initialize the state dictionary
    "ABS_X", "ABS_Y", # Left stick
    "ABS_RX", "ABS_RY", # Right stick
    "ABS_Z", "ABS_RZ", # Triggers
    "BTN_NORTH", "BTN_EAST", "BTN_SOUTH", "BTN_WEST", # Letter buttons (some are unused)
    "ABS_HAT0X", "ABS_HAT0Y", # Hat (unused)
]
state = {k:0 for k in codes}
running = False
state_update_thread = None

def update_state():
    global state
    while running:
        events = inputs.get_gamepad()
        for event in events:
            if event.ev_type == "Sync":
                continue
            # print("e type=" + str(event.ev_type) + ", code=" + str(event.code) + ", state=" + str(event.state))
            state[event.code] = event.state
        # time.sleep(0.01)

def thresh(a, l_th=0.1, u_th=1): # Copied from gamepad_driver_windows
    if abs(a) < l_th:
        return 0
    elif abs(a) > u_th:
        return -1 if a < 0 else 1
    return a

def get_gamepad_values():

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

    args = (
        int(thresh(ry-rx, 0.1) * 100 + 100), # 0-200, neutral=100 (left stick)
        int(thresh(ry+rx, 0.1) * 100 + 100),
        int(thresh(x, 0.1) * 100 + 100), # 0-200, neutral=100 (right stick)
        int(thresh(y, 0.1) * 100 + 100), # unused for old robot
        int((-(lt + 1) + (rt + 1)) * 100 + 100), # left trigger is backwards, right is forwards
        dbin
    )
    return args

def start():
    global running, state_update_thread
    running = True
    state_update_thread = threading.Thread(target=update_state)
    state_update_thread.start()

def stop():
    global running, state_update_thread
    running = False
    state_update_thread.join()


if __name__ == "__main__":
    start()
    try:
        while True:
            print(get_gamepad_values())
            time.sleep(0.01)
    except KeyboardInterrupt:
        print("except KeyboardInterrupt")
        stop()
