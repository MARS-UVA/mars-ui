"""
Animated matplotlib graphs
"""

import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation
import numpy as np
from collections import deque
import math
import random
import gui


class LineGraph(tk.Frame):
   def __init__(self, parent, get_data_function):
      tk.Frame.__init__(self, parent)

      self.datalen = 100 # how many data points are displayed on the graph
      self.datacolumns = 11 # number of series to graph (11 motor currents)
      self.data = deque([[0]*self.datacolumns for i in range(self.datalen)], maxlen=self.datalen)

      self.fig = plt.Figure()#figsize=(6,5), dpi=100)
      self.ax = self.fig.add_subplot(111)
      self.ax.set_title('Motor Currents')
      self.ax.axis([0, self.datalen, -2, 20])

      self.canvas = FigureCanvasTkAgg(self.fig, parent)
      self.canvas.get_tk_widget().pack() #side=tk.LEFT, fill=tk.BOTH)

      # self.plot = self.ax.plot(list(self.data))[0] # np.arange(0, self.datalen),
      # code right below plots a horizontal axis line to fit the screen
      self.plot = [self.ax.plot([0]*self.datalen)[0] for i in range(self.datacolumns)]

      def animate(i, data, plot, func):
         new_val = func()
         if(new_val is None):
            return
         data.append(new_val)

         for l, d in zip(plot, np.rot90(data)):
            l.set_ydata(d)

      self.anim = animation.FuncAnimation(self.fig, animate, fargs=(self.data, self.plot, get_data_function), interval=50, blit=False) # change graphing interval here

class ArmGraph(tk.Frame):
   def __init__(self, parent, get_data_function=0):
      if get_data_function == 0:
         tk.Frame.__init__(self, parent)

         self.datalen = 100  # how many data points are displayed on the graph
         self.datacolumns = 8  # number of series to graph (8 for 8 motor currents)
         self.data = deque([[0] * self.datacolumns for i in range(self.datalen)], maxlen=self.datalen)

         self.fig = plt.Figure()  # figsize=(6,5), dpi=100)
         self.ax = self.fig.add_subplot(111)
         self.ax.set_title('X vs. Y')
         self.ax.axis([-25, 25, -25, 25])

         self.canvas = FigureCanvasTkAgg(self.fig, parent)
         self.canvas.get_tk_widget().pack()  # side=tk.LEFT, fill=tk.BOTH)


         x1 = np.arange(0,8,.05) # TYPE np.ndarray
         x2 = np.arange(-8,0,.05) # TYPE np.ndarray
         # x3 = np.arange(0, 2 * np.pi, .05)
         # x = np.arange(0, 2 * np.pi, .05)  # x denotes an array of x values
         y1 = [] # TYPE list
         y2 = [] # TYPE list
         for i in range(0,len(x1)):
            y1.append(0)
            y2.append(0)


         line1, = self.ax.plot(x1,y1)
         line2, = self.ax.plot(x2,y2)

         # line, = self.ax.plot(np.sin(x), np.sin(x))  # line, creates the line that must be plotted
         # line3, = self.ax.plot(-5*np.sin(x), np.sin(x))
         global old_y1_endpt
         global old_x1_endpt
         old_x1_endpt = 0
         old_y1_endpt = 0

         def animate(i):

            global old_x1_endpt
            global old_y1_endpt
            # set_ydata changes the y components of the line that must be plotted (i.e. the array of y values)
            # A 2x2 Rotation Transformation Matrix for x,y coordinates
            new_x1 = [] #TYPE list
            new_y1 = [] #TYPE list
            new_x2 = []
            new_y2 = []
            theta = math.radians(i)
            for j in range(len(x1)):
               A = [[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]]
               column_matrix1 = []
               column_matrix1.append([x1[j]] - np.array([8]))
               column_matrix1.append([y1[j]] - np.array([0]))
               answer = np.dot(A, column_matrix1)
               xyrot1 = answer.tolist() # TYPE list
               yrot1 = xyrot1.pop() + np.array([0]) # TYPE np.ndarray
               xrot1 = xyrot1.pop() + np.array([8]) # TYPE np.ndarray
               new_x1.append(xrot1)
               new_y1.append(yrot1)

            shift_x = new_x1[0] - old_x1_endpt
            shift_y = new_y1[0] - old_y1_endpt
            # print(shift_x)
            # print(new_x1[0])
            # print(old_x1_endpt)
            # print(shift_x)
            # Translation ONLY Attempt #1
            for k in range(len(x2)):
               shifted_x = x2[k] + np.array([shift_x])
               shifted_y = y2[k] + np.array([shift_y])
               new_x2.append(shifted_x)
               new_y2.append(shifted_y)


            # Rotation and Translation Attempt #1
            # for k in range(len(x2)):
            #  A = [[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]]
            #  column_matrix2 = []
            #  column_matrix2.append([x2[k]] + np.array()
            #  column_matrix2.append([y2[k]] + )
               # answer = np.dot(A, column_matrix2)
               # xyrot2 = answer.tolist()
               # yrot2 = xyrot2.pop() + np.array(endpty1)
               # xrot2 = xyrot2.pop() + np.array(endptx1)
               # new_x2.append(xrot2)
               # new_y2.append(yrot2)

            # line.set_ydata(5*np.sin(x + i / 10.0))  # update the data
            line1.set_ydata(new_y1)
            line1.set_xdata(new_x1)
            line2.set_xdata(new_x2)
            line2.set_ydata(new_y2)
            # line3.set_ydata(5*np.sin(x + i / 10.0))
            return line1,line2

         # Init only required for blitting to give a clean slate.
         # def init():
         #  line.set_ydata(np.ma.array(x, mask=True))
         #  line2.set_ydata(np.ma.array(x2, mask=True))
         #  return line, line2

         animation.FuncAnimation(self.fig, animate, np.arange(1, 1000),
                           interval=30, blit=True)
         plt.show()

         # self.ax.plot([2, 4, 6, 8], [5, 4, 7, 9])
         # self.ax.set_title('X vs. Y')
         # self.ax.axis([-10, 10, -10, 10])


