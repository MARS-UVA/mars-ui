# !/usr/bin/python3

import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation
import numpy as np
from collections import deque

class LineGraph(tk.Frame):
	def __init__(self, parent, get_data_function):
		tk.Frame.__init__(self, parent)

		self.datalen = 30 # how many data points are displayed on the graph
		self.datacolumns = 8 # number of series to graph (8 for 8 motor currents)
		self.data = deque([[0]*self.datacolumns for i in range(self.datalen)], maxlen=self.datalen)

		self.fig = plt.Figure(figsize=(6,5), dpi=100)
		self.ax = self.fig.add_subplot(111)
		self.ax.set_title('X vs. Y')
		self.ax.axis([0, self.datalen, 0, 15])

		self.canvas = FigureCanvasTkAgg(self.fig, parent)
		self.canvas.get_tk_widget().pack() #side=tk.LEFT, fill=tk.BOTH)

		# self.plot = self.ax.plot(list(self.data))[0] # np.arange(0, self.datalen), 
		self.plot = [self.ax.plot([0]*self.datalen)[0] for i in range(self.datacolumns)]

		self.anim = animation.FuncAnimation(self.fig, self.animate, fargs=(self.data, self.plot, get_data_function), interval=1, blit=False) # change graphing interval here

	def animate(b, tick, data, plot, func):
		new_val = func(tick)
		if(new_val == None):
			return
		data.append(new_val)

		for l, d in zip(plot, np.rot90(data)):
			l.set_ydata(d)

	#def animate(b, tick, gen, data, plot):
		#new_val = next(gen())
		#data.append(new_val)
		#print(list(data))
		#print()
		#return
		#plot.set_ydata(list(data))

# def animate(tick, b, data, plot):
	# data.extend(next(g)) # g is generator
	# data.append(int(random.random()*10))
	# plot.set_ydata(list(data))