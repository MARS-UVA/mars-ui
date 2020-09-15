import gui_datathread
import gui_graph
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk
from tkinter import ttk

import numpy as np
import matplotlib.pyplot as plt
import random
import time
from datetime import datetime

import matplotlib
matplotlib.use("TkAgg")

class MainApplication(tk.Frame):
    def __init__(self, master, *args, **kwargs):
        tk.Frame.__init__(self, master, *args, **kwargs)

        master_pad = 10
        master.title("MARS Robot Interface")
        master.geometry("{0}x{1}+0+0".format(
            master.winfo_screenwidth()-master_pad,
            master.winfo_screenheight()-master_pad))
        master.grid_columnconfigure(0, weight=1)
        master.grid_columnconfigure(1, weight=1)
        master.grid_columnconfigure(2, weight=1)
        master.grid_rowconfigure(0, weight=1)

        master.update()

        # There are three main frames: Data Panel, Actions Panel, and Graph Panel.
        data_panel = tk.Frame(
            master, bg="#F7F7F7", width=200, height=master.winfo_height()-10)
        data_panel.grid(row=0, column=0, sticky="nsew")

        # Tells tkinter not to rescale the frame to the size of its components.
        data_panel.pack_propagate(0)

        actions_panel = tk.Frame(
            master, width=200, bg="#F7F7F7", height=master.winfo_height()-10)
        actions_panel.grid(row=0, column=1, sticky="nsew")
        actions_panel.pack_propagate(0)

        graph_panel = tk.Frame(
            master, width=200, bg="#F7F7F7", height=master.winfo_height()-10)
        graph_panel.grid(row=0, column=2, sticky="nsew")
        graph_panel.pack_propagate(0)

        # -------------------------------------------------------------------------
        # Data Panel
        #
        # This panel will be used to display raw data in real time. The only
        # tab on this panel that has been implemented as of 3/5/20 is Motor
        # Current.
        #
        # Naming convention: data_<tab name (if any)>_<component name>

        # Title
        data_title = ttk.Label(data_panel, text="Data", style="BW.TLabel")
        data_title.pack(side="top", pady=(50, 25))

        # Notebook and tabs
        data_notebook = ttk.Notebook(data_panel)

        # mc stands for motor current
        data_mc_frame = tk.Frame(data_notebook, background="white")
        data_2_frame = tk.Frame(data_notebook, background="white") # dummy tab
        data_3_frame = tk.Frame(data_notebook, background="white") # dummy tab

        data_notebook.add(data_mc_frame, text="Motors Currents")
        data_notebook.add(data_2_frame, text="Arm")
        data_notebook.add(data_3_frame, text="Basket")
        data_notebook.pack(expand=1, fill='both')

        # Motor Currents tab. All labels are defined as instance variables
        # so they can be accessed by updateDataPanel().
        self.data_mc_title = tk.Label(
            data_mc_frame, text="Motor Currents", font=("Pitch", 25))
        self.data_mc_title.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W) # The .grid function is used to designate where this label is located

        self.data_mc_status = tk.Label(
            data_mc_frame,
            text="STATUS: Collecting Data",
            font='Pitch 20 bold')
        self.data_mc_status.grid(row=1, column=0, padx=10, pady=3, sticky=tk.W)

        self.data_mc_body = tk.Label(
            data_mc_frame,
            text="Motor 1 Speed: xx rpm",
            font=("Pitch", 20),
            justify=tk.LEFT)
        self.data_mc_body.grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)

        # Arm Status tab. All labels are defined as instance variables
        # so they can be accessed by updateDataPanel().
        self.data_2_title = ttk.Label(
            data_2_frame, text="Arm Status", font=("Pitch", 25))
        self.data_2_title.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)

        self.data_2_status = tk.Label(
            data_2_frame,
            text="STATUS: Collecting Data",
            font='Pitch 20 bold')
        self.data_2_status.grid(row=1, column=0, padx=10, pady=3, sticky=tk.W)

        self.data_2_body = tk.Label(
            data_2_frame,
            text="Motor 1 Speed: xx rpm",
            font=("Pitch", 20),
            justify=tk.LEFT)
        self.data_2_body.grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)

        # self.data_2_body = ttk.Label(
        #     data_2_frame, text="Length of Arm", font=("Tahoma", 25))
        # self.data_2_body.grid(row=2, column=0, padx=10, pady=10)

        self.data_3_title = ttk.Label(
            data_3_frame, text="Basket Angle: 15°", font=("Tahoma", 25))
        self.data_3_title.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)

        # -------------------------------------------------------------------------
        # Actions Panel
        #
        # This panel will contain a set of action buttons to control the robot
        # and/or the UI. The only button that has been implemented as of 3/5/20
        # is actions_mc, which pauses and resumes Motor Current data collection.
        #
        # Naming convention: actions_<component name>

        # Title
        actions_title = ttk.Label(actions_panel, text="Actions", style="BW.TLabel")
        actions_title.pack(side="top", pady=(50, 25))

        # Pauses or resumes motor current data collection. Updates the text
        # on mc_toggle button.
        def toggleMotorCurrentThread():
            if threads["stream_motor_current"].isCollecting():
                threads["stream_motor_current"].stopCollection()
                actions_mc['text'] = "Resume Motor Data Collection"
            elif "stream_motor_current" in threads:
                threads["stream_motor_current"].resumeCollection()
                actions_mc['text'] = "Pause Motor Data Collection"
            else:
                print("Stream_motor_current not in threads")
        def toggleArmStatusThread():
            if threads2["stream_arm_status"].isCollecting():
                threads2["stream_arm_status"].stopCollection()
                actions_b2['text'] = "Resume Arm Data Collection"
            elif "stream_arm_status" in threads2:
                threads2["stream_arm_status"].resumeCollection()
                actions_b2['text'] = "Pause Arm Data Collection"
            else:
                print("Stream_motor_current not in threads")

        actions_mc = ttk.Button(
            actions_panel,
            text="Pause Motor Data Collection",
            command=toggleMotorCurrentThread,
            width=35)
        actions_mc.pack(side=tk.TOP, pady=(15, 25), padx=10)

        actions_b2 = ttk.Button(
            actions_panel,
            text="Pause Arm Data Collection",
            command=toggleArmStatusThread,
            width=35)
        actions_b2.pack(side=tk.TOP, pady=20, padx=10)

        # Dummy callback functions for b3
        def callback3():
            # Do something
            print("Callback 3 Clicked!")

        actions_b3 = ttk.Button(
            actions_panel, text="Action 3", command=callback3, width=35)
        actions_b3.pack(side=tk.TOP, pady=20, padx=10)

        # -------------------------------------------------------------------------
        # Graphs Panel
        #
        # This panel will contain a graphs that display data in real time. The only
        # graph that has been created as of 3/5/20 is the motor currents line graph.
        #
        # Naming convention: graphs_<tab name (if any)>_<component name>

        # Title
        graphs_title = ttk.Label(graph_panel, text="Graphs", style="BW.TLabel")
        graphs_title.pack(side="top", pady=(50, 25))

        # Notebook and Tabs
        graphs_notebook = ttk.Notebook(graph_panel)
        graphs_mc_frame = tk.Frame(graphs_notebook, background="white")
        graphs_2_frame = tk.Frame(graphs_notebook, background="white") # dummy tab
        graphs_3_frame = tk.Frame(graphs_notebook, background="white") # dummy tab

        graphs_notebook.add(graphs_mc_frame, text="Graph 1")
        graphs_notebook.add(graphs_2_frame, text="Graph 2")
        graphs_notebook.add(graphs_3_frame, text="Graph 3")
        graphs_notebook.pack(expand=1, fill='both')

        # Motor Currents graph. Note that mc stands for motor current.
        graphs_mc_checks = tk.Frame(graphs_mc_frame, background="pink")
        graphs_mc_vars = [tk.IntVar() for i in range(8)]

        for i in range(len(graphs_mc_vars)):
            c = ttk.Checkbutton(
                graphs_mc_checks,
                text="Series " + str(i+1) + " ",
                variable=graphs_mc_vars[i])
            c.grid(row=0, column=i)

        graphs_mc_lineGraph = gui_graph.LineGraph(
            graphs_mc_frame,
            lambda: np.array([data/4 if var.get() == 1 else 0 for data,
            var in zip(threads["stream_motor_current"].get_recent_data(),
            graphs_mc_vars)])
        )

        graphs_mc_lineGraph.ax.set_title("Motor Current")
        graphs_mc_checks.pack(side=tk.TOP)

        # Robotic Arm Length graph.
        graphs_2_checks = tk.Frame(graphs_2_frame, background="pink")
        graphs_2_vars = [tk.IntVar() for i in range(8)]

        for i in range(len(graphs_2_vars)):
            c = ttk.Checkbutton(
                graphs_2_checks,
                text="Series " + str(i+1) + " ",
                variable=graphs_2_vars[i])
            c.grid(row=0, column=i)

        graphs_2_lineGraph = gui_graph.LineGraph(
            graphs_2_frame,

        )

        graphs_2_lineGraph.ax.set_title("Length of Robotic Arm")
        graphs_2_checks.pack(side=tk.TOP)
# Generate random data. Used as a replacement for the generators
# from rcp_client.py
def fake_generator(columns, max=10):
    while True:
        yield np.array([random.randint(0, max) for i in range(columns)])
        time.sleep(0.02)

# Updates label text in the data panel. Called every second using app.after()
def updateDataPanel():
    if threads["stream_motor_current"].isCollecting():
        currents = threads["stream_motor_current"].get_recent_data()/4
        app.data_mc_status['text'] = "STATUS: Collecting Data"
        text = formatMotorCurrents(currents)
        app.data_mc_body['text'] = text
        # x = []
        # y = []
        # currentslist = currents.tolist()
        # x.append(currentslist.pop())
        # y.append(currentslist.pop())
        # print(currentslist)
    if threads2["stream_arm_status"].isCollecting():
        armdata = threads2["stream_arm_status"].get_recent_data()/4
        app.data_2_status['text'] = "STATUS: Collecting Data"
        text = formatArmStatus(armdata)
        app.data_2_body['text'] = text
    elif threads2['stream_arm_status'].stopCollection():
        app.data_2_status['text'] = "STATUS: Paused"
        app.data_2_body['text'] = ""
    elif threads["stream_motor_current"].stopCollection():
        app.data_mc_status['text'] = "STATUS: Paused"
        app.data_mc_body['text'] = ""
    app.after(1000, updateDataPanel)

# Helper method for updateDataPanel().
def formatMotorCurrents(currents):
    s = ""
    for i in range(1,9):
        s += "Motor " + str(i) + ":     "
        s += "{:0<6.3f}".format(currents[i-1]) + " A\n\n"
    return s

def formatArmStatus(armdata):
    angle, translation = armdata
    s = ""

    s += "Arm Angle:     "
    s += "{:0<6.3f}".format(angle) + " Degrees\n\n"
    s += "Arm Translation:     "
    s += "{:0<6.3f}".format(translation) + "  M\n\n"
    return s

if __name__ == '__main__':
    # channel = grpc.insecure_channel('172.27.39.1:50051')
    # stub = jetsonrpc_pb2_grpc.JetsonRPCStub(channel)
    # gen = rpc_client.stream_motor_current(stub)
    threads = {}
    threads["stream_motor_current"] = gui_datathread.DataThread("datathread for stream_motor_current", fake_generator(8, max=40)) # 8 columns of fake data for the 8 motors
    threads["stream_motor_current"].start()

    threads2 = {}
    threads2["stream_arm_status"] = gui_datathread.DataThread("datathread for stream_arm_status", fake_generator(2, max=40))  # 2 columns of fake data for angle and translation
    threads2["stream_arm_status"].start()

    root = tk.Tk()

    style = ttk.Style()
    style.configure("TButton", font="Tahoma 18")
    style.configure("BW.TLabel", foreground="black", background="white", font=("Tahoma 24"))

    app = MainApplication(root)
    app.after(100, updateDataPanel)
    root.mainloop()

    # after ui is closed:
    # channel.close()
    for k in threads.keys():
        threads[k].stop()
        threads[k].join()

