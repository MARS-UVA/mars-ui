import keyboard

def keyboard_val_gen():
    key_status = {'w': False, 'a': False, 's': False, 'd': False}
    while True:
        event = keyboard.read_event()
        if key_status.get(event.name) is not None:
            if event.event_type == "up":
                key_status[event.name] = False
            else:
                key_status[event.name] = True

        left = 100
        right = 100
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

        left = max(left, 0)
        left = min(left, 200)

        right = max(right, 0)
        right = min(right, 200)

        yield jetsonrpc_pb2.MotorCmd(values=encode_values(
            left, right, 100, 100, 100, 1
        ))
