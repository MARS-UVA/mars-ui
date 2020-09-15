"""
An animated matplotlib graph
"""

import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.animation as animation
import numpy as np
from collections import deque
import gui


class LineGraph(tk.Frame):
	def __init__(self, parent, get_data_function=0):
		if get_data_function == 0:
			tk.Frame.__init__(self, parent)
			self.fig = plt.Figure()  # figsize=(6,5), dpi=100)
			self.ax = self.fig.add_subplot(111)
			self.canvas = FigureCanvasTkAgg(self.fig, parent)
			self.canvas.get_tk_widget().pack()  # side=tk.LEFT, fill=tk.BOTH)


			# self.ax.plot([2, 4, 6, 8], [5, 4, 7, 9])
			# self.ax.set_title('X vs. Y')
			# self.ax.axis([-10, 10, -10, 10])
			# self.anim = animation.FuncAnimation(self.fig,self.animate(, interval=1000)


			x = np.arange(0, 2 * np.pi, .05) # x denotes an array of x values
			line, = self.ax.plot(np.sin(x), np.sin(x)) # line, creates the line that must be plotted

			def animate(i):
				# set_ydata changes the y components of the line that must be plotted (i.e. the array of y values)
				line.set_ydata(np.sin(x + i / 10.0))  # update the data
				return line,

			# Init only required for blitting to give a clean slate.
			def init():
				line.set_ydata(np.ma.array(x, mask=True))
				return line,

			animation.FuncAnimation(self.fig, animate, np.arange(1, 1000), init_func=init,
										  interval=30, blit=True)
			plt.show()



		else:
			tk.Frame.__init__(self, parent)

			self.datalen = 100 # how many data points are displayed on the graph
			self.datacolumns = 8 # number of series to graph (8 for 8 motor currents)
			self.data = deque([[0]*self.datacolumns for i in range(self.datalen)], maxlen=self.datalen)

			self.fig = plt.Figure()#figsize=(6,5), dpi=100)
			self.ax = self.fig.add_subplot(111)
			self.ax.set_title('X vs. Y')
			self.ax.axis([0, self.datalen, -8, 8])

			self.canvas = FigureCanvasTkAgg(self.fig, parent)
			self.canvas.get_tk_widget().pack() #side=tk.LEFT, fill=tk.BOTH)

			# self.plot = self.ax.plot(list(self.data))[0] # np.arange(0, self.datalen),
			# code right below plots a horizontal axis line to fit the screen
			self.plot = [self.ax.plot([0]*self.datalen)[0] for i in range(self.datacolumns)]

			# self.anim = animation.FuncAnimation(self.fig, self.animate, fargs=(self.data, self.plot, get_data_function), interval=1, blit=False) # change graphing interval here


	# def animate(b, tick, data, plot, func):
	# 	new_val = func()
	# 	if(new_val is None):
	# 		return
	# 	data.append(new_val)
	#
	# 	for l, d in zip(plot, np.rot90(data)):
	# 		l.set_ydata(d)

# def animate(b, tick, gen, data, plot):
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