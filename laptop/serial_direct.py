from utils.protocol import var_len_proto_send, var_len_proto_recv
from utils.non_blocking import NBInput
import struct
import matplotlib.pyplot as plt
import time
import serial
ser = serial.Serial("COM4", 115200)

# import matplotlib
# matplotlib.use("Qt5agg")


# ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)
default_values = [100, 100, 100, 100, 100, 100, 100, 100]
values = default_values.copy()
init_time = time.time()
inp = NBInput()

fig = plt.figure()
plt.show(block=False)
prev_time = []
prev_values = []

MOTOR = 3
MAX_POINTS = 100
LEN_AV = 5  # length of moving average

while True:
    try:
        if not inp.empty():
            values[MOTOR] = int(inp.get())
            ser.write(var_len_proto_send(values))
    except ValueError:
        ser.write(var_len_proto_send(default_values))
    except KeyboardInterrupt:
        break

    raw = ser.read(ser.inWaiting())
    data = var_len_proto_recv(raw)

    now = time.time() - init_time
    new_values = []
    for piece in data:
        unpacked = struct.unpack('8B', piece)
        new_values.append(unpacked[MOTOR] * 0.25)

    if len(new_values):
        prev_len = len(prev_values)
        if prev_len >= LEN_AV:
            new_values.extend(prev_values[prev_len - LEN_AV:prev_len])

        average = sum(new_values) / len(new_values)

        prev_time.append(now)
        prev_values.append(average)
        if len(prev_time) > MAX_POINTS:
            del prev_time[0]
            del prev_values[0]

    plt.clf()
    plt.plot(prev_time, prev_values, c='g')
    plt.ylim([0, 5])
    fig.canvas.draw_idle()
    fig.canvas.start_event_loop(0.001)
    time.sleep(0.001)
