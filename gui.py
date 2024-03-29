import gui_datathread
import gui_graph
import gui_cameraview
import threading
import gamepad_encoder
import network_config
import tkinter as tk
from tkinter import ttk

import numpy as np
import random
import time
from datetime import datetime
import json

import grpc
import rpc_client
from protos import jetsonrpc_pb2_grpc, jetsonrpc_pb2



DEFAULT_RPC_RATE = 1000 # update period, in ms

stub = None


def ratebutton_factory(parent, on_text, off_text, datathread, rpc_function):
    frame = tk.Frame(parent)
    def toggle_command():
        if b['text'] == on_text:
            datathread.stopCollection()
            b['text'] = off_text
        elif b['text'] == off_text:
            datathread.resumeCollection()
            b['text'] = on_text
    b = ttk.Button(
        frame,
        text=on_text,
        command=toggle_command,
        width=28)
    b.pack(side=tk.LEFT, pady=2, padx=2)

    r = tk.Entry(frame, width=6) # Could do validation like this: https://riptutorial.com/tkinter/example/27780/adding-validation-to-an-entry-widget
    r.insert(0, str(DEFAULT_RPC_RATE)) # set the text of the default value - the actual value is set to the default when the datathread is created
    r.pack(side=tk.LEFT, pady=2, padx=2)

    def rate_command():
        rate = DEFAULT_RPC_RATE
        try:
            rate = int(r.get())
        except ValueError:
            r.delete(0, tk.END)
            r.insert(0, str(DEFAULT_RPC_RATE))
        print("updating rate:", rate)
        datathread.updateGenerator(rpc_function(stub, rate=rate))
    c = ttk.Button(frame, text="✓", command=rate_command, width=2)
    c.pack(side=tk.LEFT, pady=2, padx=2)

    return frame

def actionbutton_factory(parent, text, filepath, command):
    def saveText(filepath, txt_edit, newWindow):
        with open(filepath, "w") as output_file:
            filetext = txt_edit.get(1.0, 'end')
            output_file.write(filetext)
            newWindow.destroy()
    def editText(filepath):
        newWindow = Toplevel()
        newWindow.title("Editing command '%s'" % text)
        newWindow.rowconfigure(0, minsize=50, weight=1)
        newWindow.columnconfigure(1, minsize=50, weight=1)
        txt_edit = tk.Text(newWindow)
        txt_edit.grid(row=0, column=0, sticky="nsew")
        txt_edit.delete(1.0, tk.END)
        with open(filepath, "r") as input_file:
            filetext = input_file.read()
            txt_edit.insert(tk.END, filetext)
        newButton = ttk.Button(newWindow, text="Save command '%s'" % text, command=(lambda: saveText(filepath, txt_edit, newWindow)))
        newButton.grid(row=1, column=0, sticky="nsew", padx=5)
    def readText(filepath):
        file = open(filepath, "r")
        text = file.read()
        file.close()
        return text
    frame = tk.Frame(parent)
    b = ttk.Button(frame, text=text, command=lambda: command(readText(filepath)), width=25).pack(side=tk.LEFT, pady=2, padx=2)
    bedit = ttk.Button(frame, text="Edit", command=lambda: editText(filepath), width=5).pack(side=tk.LEFT, pady=2, padx=2)
    return frame 

class MainApplication(tk.Frame):
    def __init__(self, master, *args, **kwargs):
        tk.Frame.__init__(self, master, *args, **kwargs)

        master_pad = 10
        master.title("MARS Robot Interface")
        master.geometry("{0}x{1}+0+0".format(
            master.winfo_screenwidth() - master_pad,
            master.winfo_screenheight() - master_pad))
        master.grid_columnconfigure(0, weight=1)
        master.grid_columnconfigure(1, weight=1)
        master.grid_columnconfigure(2, weight=1)
        master.grid_rowconfigure(0, weight=1)

        master.update()

        self.is_using_gamepad = False
        self.gamepad_thread = None

        self.drive_state = jetsonrpc_pb2.DriveStateEnum.IDLE

        # There are three main frames: Data Panel, Actions Panel, and Graph Panel.
        data_panel = tk.Frame(
            master, bg="#F7F7F7", width=200, height=master.winfo_height() - 10)
        data_panel.grid(row=0, column=0, sticky="nsew")

        # Tells tkinter not to rescale the frame to the size of its components.
        data_panel.pack_propagate(0)

        actions_panel = tk.Frame(
            master, width=200, bg="#F7F7F7", height=master.winfo_height() - 10)
        actions_panel.grid(row=0, column=1, sticky="nsew")
        actions_panel.pack_propagate(0)

        graph_panel = tk.Frame(
            master, width=200, bg="#F7F7F7", height=master.winfo_height() - 10)
        graph_panel.grid(row=0, column=2, sticky="nsew")
        graph_panel.pack_propagate(0)

        # -------------------------------------------------------------------------
        # Data Panel
        #
        # This panel will be used to display raw data in real time. The only
        # tab on this panel that has been implemented as of 3/5/20 is Motor
        # Current.
        # Naming convention: data_<tab name (if any)>_<component name>

        # Title
        data_title = ttk.Label(data_panel, text="Data", style="BW.TLabel")
        data_title.pack(side="top", pady=(50, 25))

        # Notebook and tabs
        data_notebook = ttk.Notebook(data_panel)

        data_feedback_frame = tk.Frame(data_notebook, background="white")  # mc stands for motor current
        # data_cam_frame = tk.Frame(data_notebook, background="white")
        # data_IMU_frame = tk.Frame(data_notebook, background="white")

        data_notebook.add(data_feedback_frame, text="Hero Feedback")
        # data_notebook.add(data_IMU_frame, text="IMU Data")
        # data_notebook.add(data_cam_frame, text="Camera")
        data_notebook.pack(expand=1, fill='both')

        # Hero Feedback tab. All labels are defined as instance variables
        # so they can be accessed by updateDataPanel().
        self.data_feedback_title = tk.Label(
            data_feedback_frame, text="Hero Feedback", font=("Pitch", 25))
        # The .grid function is used to designate where this label is located
        self.data_feedback_title.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)

        self.data_feedback_status = tk.Label(
            data_feedback_frame,
            text="STATUS: Collecting Data",
            font='Pitch 20 bold')
        self.data_feedback_status.grid(row=1, column=0, padx=10, pady=3, sticky=tk.W)

        self.data_feedback_body = tk.Label(
            data_feedback_frame,
            text="NA",
            font=("Pitch", 20),
            justify=tk.LEFT)
        self.data_feedback_body.grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)

        # IMU Data tab. All labels are defined as instance variables
        # so they can be accessed by updateDataPanel().

        # self.data_IMU_title = tk.Label(
        #     data_IMU_frame, text="IMU Data", font=("Pitch", 25))
        # # The .grid function is used to designate where this label is located
        # self.data_IMU_title.grid(
        #     row=0, column=0, padx=10, pady=10, sticky=tk.W)
        # self.data_IMU_status = tk.Label(
        #     data_IMU_frame,
        #     text="STATUS: Collecting Data",
        #     font='Pitch 20 bold')
        # self.data_IMU_status.grid(
        #     row=1, column=0, padx=10, pady=3, sticky=tk.W)
        # self.data_IMU_body = tk.Label(
        #     data_IMU_frame,
        #     text="NA",
        #     font=("Pitch", 20),
        #     justify=tk.LEFT)
        # self.data_IMU_body.grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)

        # -------------------------------------------------------------------------
        # Actions Panel
        #
        # This panel will contain a set of action buttons to control the robot
        # and/or the UI.
        # Naming convention: actions_<component name>

        # Title
        actions_title = ttk.Label(
            actions_panel, text="Actions", style="BW.TLabel")
        actions_title.pack(side="top", pady=(50, 25))

        def gamepadControlOff():
            if not self.is_using_gamepad:
                return
            gamepad_encoder.stop()
            self.gamepad_thread.join()
            self.is_using_gamepad = False

        def gamepadControlOn():
            if self.is_using_gamepad:
                return
            self.gamepad_thread = threading.Thread(target=gamepad_encoder.start, args=(stub,))
            self.gamepad_thread.start()
            self.is_using_gamepad = True

        def changeDriveState(new_state):
            if new_state == self.drive_state:
                return
            self.drive_state = new_state
            rpc_client.change_drive_state(stub, new_state)
            if new_state == jetsonrpc_pb2.DIRECT_DRIVE:
                gamepadControlOn()
                actions_state_label['text'] = "Current state: Direct Drive"
            elif new_state == jetsonrpc_pb2.AUTONOMY:
                gamepadControlOff()
                actions_state_label['text'] = "Current state: Autonomy"
            else: # includes IDLE state
                gamepadControlOff()
                actions_state_label['text'] = "Current state: Idle"

        actions_toggle_hero_feedback = ratebutton_factory(actions_panel, "Pause Feedback Collection", "Resume Feedback Collection", threads["stream_hero_feedback"], rpc_client.stream_hero_feedback)
        actions_toggle_hero_feedback.pack(side=tk.TOP, pady=(20,3), padx=10)

        actions_toggle_camera = ratebutton_factory(actions_panel, "Pause Camera Collection", "Resume Camera Collection", threads["stream_image"], rpc_client.stream_image)
        actions_toggle_camera.pack(side=tk.TOP, pady=10, padx=10)

        # actions_toggle_IMU_data = ttk.Button(
        #     actions_panel,
        #     text="Pause IMU Data Collection",
        #     command=toggleIMUDataThread,
        #     width=35)
        # actions_toggle_IMU_data.pack(side=tk.TOP, pady=10, padx=10)

        # actions_toggle_camera_stream = ttk.Button(
        #     actions_panel,
        #     text="Pause Camera Stream",
        #     command=toggleCamDataThread,
        #     width=35)
        # actions_toggle_camera_stream.pack(side=tk.TOP, pady=10, padx=10)


        # This ttk style makes a pretty red button for e-stop
        style = ttk.Style()
        style.configure('emergency.TButton', foreground='white', background="maroon",)
        actions_toggle_emergency_stop = ttk.Button(
            actions_panel,
            text="EMERGENCY STOP",
            command=lambda: rpc_client.emergency_stop(stub),
            width=35,
            style="emergency.TButton",
        )
        actions_toggle_emergency_stop.pack(side=tk.TOP, pady=(10,50), padx=10)

        # Action buttons (placeholders)

        actions_state_frame = tk.Frame(actions_panel, width=35, pady=10)
        actions_state_frame.pack()
        actions_state_idle = ttk.Button(actions_state_frame, text="State Idle", command=lambda: changeDriveState(jetsonrpc_pb2.DriveStateEnum.IDLE)).pack(side=tk.LEFT, padx=4)
        actions_state_direct_drive = ttk.Button(actions_state_frame, text="State Direct Drive", command=lambda: changeDriveState(jetsonrpc_pb2.DriveStateEnum.DIRECT_DRIVE)).pack(side=tk.LEFT, padx=4)
        actions_state_autonomy = ttk.Button(actions_state_frame, text="State Autonomy", command=lambda: changeDriveState(jetsonrpc_pb2.DriveStateEnum.AUTONOMY)).pack(side=tk.LEFT, padx=4)

        actions_state_label = tk.Label(actions_panel, text="Current state: Idle", font='Pitch 20')
        actions_state_label.pack(side=tk.TOP, pady=10)
 
        def action_wrapper(text):
            # This is used so that the button onclick funtion can read the file from within the factory function
            # There is probably a better way to do this. Especially because this is super weird to understand
            def action(t):
                minified = json.dumps(json.loads(t), separators=(',', ':')) # this eliminates any extra spaces, tabs, and newlines
                print("Sending start_action, text=" + str(minified))
                rpc_client.start_action(stub, text=minified)
            return action(text)
        actionframe1 = actionbutton_factory(actions_panel, "Raise Deposit Bin", "action_config/raise_bin.json", command=action_wrapper)
        actionframe1.pack(side=tk.TOP, pady=(20,3), padx=10)
        actionframe2 = actionbutton_factory(actions_panel, "Lower Deposit Bin", "action_config/lower_bin.json", command=action_wrapper)
        actionframe2.pack(side=tk.TOP, pady=3, padx=10)
        actionframe3 = actionbutton_factory(actions_panel, "Raise Bucket Ladder", "action_config/raise_ladder.json", command=action_wrapper)
        actionframe3.pack(side=tk.TOP, pady=(10,3), padx=10)
        actionframe4 = actionbutton_factory(actions_panel, "Lower Bucket Ladder", "action_config/lower_ladder.json", command=action_wrapper)
        actionframe4.pack(side=tk.TOP, pady=3, padx=10)
        actionframe4 = actionbutton_factory(actions_panel, "Dig", "action_config/dig.json", command=action_wrapper)
        actionframe4.pack(side=tk.TOP, pady=(10,3), padx=10)


        # -------------------------------------------------------------------------
        # Graphs Panel
        #
        # This panel will contain graphs that display data in real time. 
        # Naming convention: graphs_<tab name (if any)>_<component name>

        # Title
        graphs_title = ttk.Label(graph_panel, text="Graphs", style="BW.TLabel")
        graphs_title.pack(side="top", pady=(50, 25))

        # Notebook and Tabs
        graphs_notebook = ttk.Notebook(graph_panel)
        graphs_mc_frame = tk.Frame(graphs_notebook, background="white")
        graphs_line_frame = tk.Frame(graphs_notebook, background="white")
        graphs_image_frame = tk.Frame(graphs_notebook, background="white")

        graphs_notebook.add(graphs_mc_frame, text="Motor currents")
        graphs_notebook.add(graphs_line_frame, text="X vx. Y")
        graphs_notebook.add(graphs_image_frame, text="Camera view")
        graphs_notebook.pack(expand=1, fill='both')

        # Motor Currents graph. Note that mc stands for motor current.
        def mc_update_data():
            d = threads["stream_hero_feedback"].get_recent_data()
            if d is None:
                return None
            return list(d.currents)
        graphs_mc_lineGraph = gui_graph.LineGraph(graphs_mc_frame, get_data_function=mc_update_data)

        # Robotic Arm Length graph.
        graphs_2_ArmGraph = gui_graph.ArmGraph(graphs_line_frame)

        def image_update_data():
            d = threads["stream_image"].get_recent_data()
            if d is None:
                return None
            return d.data
        graphs_3_cameraView = gui_cameraview.CameraView(graphs_image_frame, get_data_function=image_update_data)


def updateDataPanel():
    if threads["stream_hero_feedback"].isCollecting():
        currents = threads["stream_hero_feedback"].get_recent_data()
        app.data_feedback_status['text'] = "STATUS: Collecting Data"
        app.data_feedback_body['text'] = formatHeroFeedback(currents)
    else:
        app.data_feedback_status['text'] = "STATUS: Paused"
        app.data_feedback_body['text'] = "Paused"

    # if threads["stream_IMU_data"].isCollecting():
    #     IMU_data = threads["stream_IMU_data"].get_recent_data() #the recent data is the array of 6 valuess
    #     app.data_IMU_status['text'] = "STATUS: Collecting Data"
    #     app.data_IMU_body['text'] = formatIMUData(IMU_data)
    # else:
    #     app.data_IMU_status['text'] = "STATUS: Paused"
    #     app.data_IMU_body['text'] = "Paused"

    app.after(100, updateDataPanel)


def formatHeroFeedback(fb):
    if fb is None:
        return "None"
    s = ""
    currents = list(fb.currents)
    for i in range(len(currents)):
        s += "Motor {}:{:>6} A\n".format(i, currents[i]) # TODO this right-align formatting doesn't work because the font isn't monospaced

    s += "\nArm Angle L:   {:.2f} °\n".format(fb.bucketLadderAngleL)
    s += "Arm Angle R:   {:.2f} °\n".format(fb.bucketLadderAngleR)
    s += "Deposit bin:   Raised={}, Lowered={}".format(fb.depositBinRaised, fb.depositBinLowered)
    return s


# def formatIMUData(IMU_data):
#     lx, ly, lz, ax, ay, az = IMU_data # assigns these vars to list values
#     s = ""
#     s += "Lin Accel X:     "
#     s += "{:0<6.3f}".format(lx) + " Units\n\n"
#     s += "Lin Accel Y:     "
#     s += "{:0<6.3f}".format(ly) + " Units\n\n"
#     s += "Lin Accel Z:     "
#     s += "{:0<6.3f}".format(lz) + " Units\n\n"
#     s += "Ang Accel X:     "
#     s += "{:0<6.3f}".format(ax) + " Units\n\n"
#     s += "Ang Accel Y:     "
#     s += "{:0<6.3f}".format(ay) + " Units\n\n"
#     s += "Ang Accel Z:     "
#     s += "{:0<6.3f}".format(az) + " Units\n\n"
#     return s


# def fake_generator(columns, max=10):
#     while True:
#         yield np.array([random.randint(0, max) for i in range(columns)])
#         time.sleep(0.1)


if __name__ == '__main__':
    channel = grpc.insecure_channel("{}:{}".format(network_config.HOST, network_config.PORT))
    stub = jetsonrpc_pb2_grpc.JetsonRPCStub(channel)

    threads = {}
    threads["stream_hero_feedback"] = gui_datathread.DataThread("datathread for stream_hero_feedback", rpc_client.stream_hero_feedback(stub, rate=DEFAULT_RPC_RATE))
    threads["stream_hero_feedback"].start()
    threads["stream_image"] = gui_datathread.DataThread("datathread for stream_image", rpc_client.stream_image(stub, rate=DEFAULT_RPC_RATE))
    threads["stream_image"].start()
    # As of now, no IMU data is gathered so the IMU datathread hangs and prevents the program from closing
    # For now, use a local source of fake data instead of the rpc server
    # threads["stream_IMU_data"] = gui_datathread.DataThread("datathread for stream_IMU_data", rpc_client.stream_imu(stub))
    # threads["stream_IMU_data"].start()
    # threads["stream_IMU_data"] = gui_datathread.DataThread("datathread for stream_IMU_data", fake_generator(6, max=10)) # 6 columns of fake data, 3 for linear acceleration, 3 for angular acceleration
    # threads["stream_IMU_data"].start()

    root = tk.Tk()
    style = ttk.Style()
    style.configure("TButton", font="Tahoma 18")
    style.configure("BW.TLabel", foreground="black",
                    background="white", font=("Tahoma 24"))

    app = MainApplication(root)
    app.after(100, updateDataPanel) # time before the first update
    root.mainloop()

    # After UI is closed:
    if gamepad_encoder.gamepad_running:
        gamepad_encoder.stop()
        app.gamepad_thread.join()

    # Set the state to idle on close
    # TODO this should also happen (or maybe estop instead?) if any errors happen in the UI - something like a try/except/finally
    rpc_client.change_drive_state(stub, jetsonrpc_pb2.DriveStateEnum.IDLE)

    for k in threads.keys():
        threads[k].stop()
        threads[k].join()
    channel.close()
