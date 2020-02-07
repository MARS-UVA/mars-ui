import tkinter as tk
from tkinter import ttk

import numpy as np
import matplotlib.pyplot as plt

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class MainApplication(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        tk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent

        master_pad = 10
        master = tk.Tk()
        master.title("MARS Robot Interface")
        master._geom='200x200+0+0'
        master.geometry("{0}x{1}+0+0".format(
            master.winfo_screenwidth()-master_pad, master.winfo_screenheight()-master_pad))
        master.grid_columnconfigure(0, weight=1)
        master.grid_columnconfigure(1, weight=1)
        master.grid_columnconfigure(2, weight=1)
        master.grid_rowconfigure(0, weight=1)

        master.update()

        # Add the three main Frames
        pad = 10
        data_panel = tk.Frame(master, bg = "#F7F7F7", width=200, height=master.winfo_height()-pad)
        actions_panel = tk.Frame(master, width=200, bg = "#F7F7F7", height=master.winfo_height()-pad)
        graph_panel = tk.Frame(master, width=200, bg = "#F7F7F7", height=master.winfo_height()-pad)

        data_panel.grid(row=0, column=0, sticky="nsew")
        actions_panel.grid(row=0, column=1, sticky="nsew")
        graph_panel.grid(row=0, column=2, sticky="nsew")

        data_panel.pack_propagate(0)
        actions_panel.pack_propagate(0)
        graph_panel.pack_propagate(0)

        # A label for each Frame
        l1 = tk.Label(data_panel, text="Data", bg = "#F7F7F7", font=("Tahoma", 40))
        l2 = tk.Label(actions_panel, text="Actions", bg = "#F7F7F7", font=("Tahoma", 40))
        l3 = tk.Label(graph_panel, text="Graphs", bg = "#F7F7F7", font=("Tahoma", 40))

        l1.pack(side="top", pady=(50,25))
        l2.pack(side="top", pady=(50,25))
        l3.pack(side="top", pady=(50,25))

        # Data Tabs
        tab_parent = ttk.Notebook(data_panel)
        data1 = tk.Frame(tab_parent, background="white")
        data2 = tk.Frame(tab_parent, background="white")
        data3 = tk.Frame(tab_parent, background="white")

        tab_parent.add(data1, text="Arm")
        tab_parent.add(data2, text="Motors")
        tab_parent.add(data3, text="Basket")
        tab_parent.pack(expand=1, fill='both')

        # Data1 tab labels
        lData1_1 = tk.Label(data1, text="Arm Angle: 90°", font=("Tahoma", 25))
        lData1_1.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)

        lData1_2 = tk.Label(data1, text="Arm Status: True", font=("Tahoma", 25))
        lData1_2.grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)

        lData1_3 = tk.Label(data1, text="Other Data: xx", font=("Tahoma", 25))
        lData1_3.grid(row=2, column=0, padx=10, pady=10, sticky=tk.W)

        # Data2 tab labels
        lData2_1 = tk.Label(data2, text="Motor 1 Speed: xx rpm", font=("Tahoma", 25))
        lData2_1.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)

        lData2_2 = tk.Label(data2, text="Motor 2 Speed: xx rpm", font=("Tahoma", 25))
        lData2_2.grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)

        # Data3 tab lebels
        lData3_1 = tk.Label(data3, text="Basket Angle: 15°", font=("Tahoma", 25))
        lData3_1.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)

        # Buttons on Actions Frame
        def callback1():
            # Do something
            lData1_1['text'] = "Arm Angle: 45°"
            print("Callback 1 Clicked!")

        def callback2():
            # Do something
            print("Callback 2 Clicked!")

        def callback3():
            # Do something
            print("Callback 3 Clicked!")

        b1 = tk.Button(actions_panel, text="Set Arm Angle: 45", font=("Tahoma", 17, 'bold'), command=callback1, height = 5, width = 35)
        b2 = tk.Button(actions_panel, text="Dump", font=("Tahoma", 17, 'bold'), command=callback2, height = 5, width = 35)
        b3 = tk.Button(actions_panel, text="Action 3", font=("Tahoma", 17, 'bold'), command=callback3, height = 5, width = 35)

        b1.pack(side = tk.TOP, pady =(15,25), padx=10)
        b2.pack(side = tk.TOP, pady =20, padx=10)
        b3.pack(side = tk.TOP, pady =20, padx=10)

        # Graph Tabs
        tab_parent_graph = ttk.Notebook(graph_panel)
        graph1 = tk.Frame(tab_parent_graph, background="white")
        graph2 = tk.Frame(tab_parent_graph, background="white")
        graph3 = tk.Frame(tab_parent_graph, background="white")

        tab_parent_graph.add(graph1, text="Graph 1")
        tab_parent_graph.add(graph2, text="Graph 2")
        tab_parent_graph.add(graph3, text="Graph 3")
        tab_parent_graph.pack(expand=1, fill='both')

        
        

if __name__ == '__main__':
    root = tk.Tk()
    MainApplication(root).pack(side="top", fill="both", expand=True)
    root.mainloop()




