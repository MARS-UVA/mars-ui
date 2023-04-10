
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

import argparse
import inputs
import math
import time
import multiprocessing

GAMEPAD_LOWER_LIMIT = -1.54
GAMEPAD_UPPER_LIMIT = 1.54

codes = [ # These are listed here just to initialize the state dictionary
    "ABS_X", "ABS_Y", # Left stick
    "ABS_RX", "ABS_RY", # Right stick
    "ABS_Z", "ABS_RZ", # Triggers
    "BTN_NORTH", "BTN_EAST", "BTN_SOUTH", "BTN_WEST", # Letter buttons (some are unused)
    "ABS_HAT0X", "ABS_HAT0Y", # Hat (unused)
]

state_update_process = None
sharedstate = multiprocessing.Array("i", [100, 100, 100, 100, 100, 100, 100])

# maps the input value, a, from the original bounds to the target bounds
def map_to_acceptable_range(a, og_lower_bound, og_upper_bound, target_lower_bound, target_upper_bound):
    fraction_of_range = (a - og_lower_bound) / (og_upper_bound - og_lower_bound)
    return fraction_of_range * (target_upper_bound - target_lower_bound) + target_lower_bound


def apply_eqn(a, l_th=0.1, lower=GAMEPAD_LOWER_LIMIT, upper=GAMEPAD_UPPER_LIMIT):
    # for smoother driving: only return value if it is greater than a lower threshold
    if abs(a) < l_th: 
        return 100 # neutral value
    else:
        og_lower = lower
        og_upper = upper
        # we want the absolute value to increase according to the equation type,
        # but the sign (negative or positive) should stay the same
        multiplier = 1 if a >= 0 else -1
        if arguments.equation_type == 'linear':
            raw_value = a  # y = x
        elif arguments.equation_type == 'quadratic':
            raw_value = multiplier * pow(a, 2)  # y = x^2
            og_lower = (-1 if lower < 0 else 1) * pow(lower, 2)
            og_upper = (-1 if upper < 0 else 1) * pow(upper, 2)
        elif arguments.equation_type == 'exponential':
            raw_value = multiplier * (pow(2, abs(a)) - 1)  # y = 2^|x| - 1 so that we have (0, 0)
            og_lower = (-1 if lower < 0 else 1) * (pow(2, abs(lower)) - 1)
            og_upper = (-1 if upper < 0 else 1) * (pow(2, abs(upper)) - 1)
        else:
            raw_value = multiplier * 1
        return map_to_acceptable_range(raw_value, og_lower, og_upper, 0, 200)  # the target rango is 0 - 200, with 100 being neutral

def format_gamepad_values(state):
        x = (state["ABS_X"])/32768.0
        y = (state["ABS_Y"])/32768.0 * -1
        lt = (state["ABS_Z"])/255.0
        rt = (state["ABS_RZ"])/255.0
        rx = (state["ABS_RX"])/32768.0
        ry = (state["ABS_RY"])/32768.0

        if abs(x) > abs(y):
            y = 0
        else:
            x = 0

        deposit_bin_angle = 100
        if state["BTN_WEST"] == 1: # This should be BTN_NORTH. I don't know why it's switched. Is it controller/computer dependent?
            deposit_bin_angle = 200
        elif state["BTN_SOUTH"] == 1:
            deposit_bin_angle = 0

        conveyor = 100
        if state["BTN_EAST"] == 1:
            conveyor = 200
        elif state["BTN_NORTH"] == 1: # See note above about BTN_WEST and BTN_NORTH being switched
            conveyor = 0

        args = [
            int(apply_eqn(-ry+rx, 0.1)), # left stick mixed
            int(apply_eqn(-ry-rx, 0.1)), # left stick mixed
            int(apply_eqn(x, 0.1)), # right stick x axis
            int(apply_eqn(y, 0.1)), # right stick y axis
            # left trigger is backwards (0), right is forwards (200)
            int(apply_eqn((-(lt + 1) / 2 + (rt + 1) / 2), lower=-2, upper=2)),  # trigger values range from -2 to 2
            deposit_bin_angle,
            conveyor
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
    parser = argparse.ArgumentParser()
    parser.add_argument('--equation-type', choices=['constant', 'linear', 'quadratic', 'exponential'],
                        default='linear',
                        help='Sets the type of equation that maps joystick locations to motor currents')
    arguments = parser.parse_args()
    start()
    try:
        while True:
            print(get_gamepad_values())
            time.sleep(0.05)
    except KeyboardInterrupt:
        print("except KeyboardInterrupt")
        stop()
