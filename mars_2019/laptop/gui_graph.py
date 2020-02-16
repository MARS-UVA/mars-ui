# !/usr/bin/python3

import tkinter as tk

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation
import numpy as np
from collections import deque
# import random

class LineGraph(tk.Frame):
	def __init__(self, parent, get_data_function):
		tk.Frame.__init__(self, parent)

		self.datalen = 30
		self.data = deque([i for i in range(self.datalen)], maxlen=self.datalen)

		self.fig = plt.Figure(figsize=(6,5), dpi=100)
		self.ax = self.fig.add_subplot(111)
		self.ax.set_title('X vs. Y')
		self.ax.axis([0, self.datalen, 0, 10])

		self.canvas = FigureCanvasTkAgg(self.fig, parent)
		self.canvas.get_tk_widget().pack() #side=tk.LEFT, fill=tk.BOTH)

		self.plot = self.ax.plot(list(self.data)[0])[0] # np.arange(0, self.datalen), 

		# self.anim = animation.FuncAnimation(self.fig, get_data_function, fargs=(self.data, self.plot), interval=50, blit=False)
		self.anim = animation.FuncAnimation(self.fig, self.animate, fargs=(self.data, self.plot, get_data_function), interval=50, blit=False)

	def animate(b, tick, data, plot, func):
		# new_val = func(tick)
		# if(new_val == None):
		# 	return

		new_val = [1, 2, 3, 4, 5, 6, 7, 8]

		data.append(new_val)

		print(np.array(data))
		plot.set_ydata(list(data))


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