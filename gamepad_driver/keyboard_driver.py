# TODO this file is not compatible with the new system of processing values through the common
# gamepad_encoder file. It looks like using the 'keyboard' package will have the same challenge
# as in gamepad_driver_linux so multiprocessing might be necessary. Alternatively, there might
# be a better keyboard input package out there that would work easier. 


import keyboard
from protos import jetsonrpc_pb2
from utils.protocol import encode_values


key_status = {'w': False, 'a': False, 's': False, 'd': False, 'up': False, 'down': False}

def keyboard_val_gen():
    while True:
        event = keyboard.read_event()
        if key_status.get(event.name) is not None:
            if event.event_type == "up":
                key_status[event.name] = False
            else:
                key_status[event.name] = True

        left = 100
        right = 100
        ladder = 100
        if key_status['s']:
            left += 100
            right += 100
        if key_status['w']:
            left -= 100
            right -= 100
        if key_status['d']:
            left -= 100
            right += 100
        if key_status['a']:
            left += 100
            right -= 100
        if key_status['up']:
            ladder += 100
        if key_status['down']:
            ladder -= 100

        left = max(left, 0)
        left = min(left, 200)

        right = max(right, 0)
        right = min(right, 200)

        ladder = max(ladder, 0)
        ladder = min(ladder, 200)

        yield jetsonrpc_pb2.MotorCmd(values=encode_values(
            left, right, 100, 100, 100, 1
        ))

if __name__ == "__main__":
    while True:
        event = keyboard.read_event()
        print(event.name)