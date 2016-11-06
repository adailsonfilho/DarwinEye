#######################
### IMPORT -> Numpy ###
#######################
import numpy as np

#########################
### IMPORT -> TKINTER ###
#########################
import tkinter as tk
from tkinter import ttk

###########################
### IMPORT -> DarwinEye ###
###########################
import plots
import config

############################
### IMPORT -> Matplotlib ###
############################
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.cm as cmx
from matplotlib import style
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg

########################
### IMPORT -> SWARMA ###
########################
from swarma.utils import evolutiveReader,normalizeEvolutiveData
from swarma.iterativesammon import iterativesammon

import ipdb

class App(tk.Tk):

	def __init__(self, *args, **kwargs):
		
		tk.Tk.__init__(self, *args, **kwargs)
		tk.Tk.wm_title(self, "SWARMA")
		self.top=tk.Frame(self)
		self.top.pack(side=tk.TOP, fill=tk.X)

		################################
		### Matplotlib Configuration ###
		################################
		style.use("ggplot")

		self.stop = True

		self.config_toolbar()		
		self.config_graphs()   
		self.build_toolbar()

	def config_toolbar(self):
		self.framelapseVar = tk.StringVar()
		self.framelapseVar.set(str(1))

		self.currentFrameVar = tk.StringVar()
		self.maxFrameVar = tk.StringVar()
		self.showLabelVar = tk.IntVar()

		self.toolbar_config = [
			{'text': 'Framelapse:', 'command': None, 'builder':ttk.Label},
			{'text': self.framelapseVar, 'command': None, 'builder':ttk.Entry},
			{'text':'Open', 'command':'OPEN', 'builder':ttk.Button},
			{'text': 'Current frame:', 'command': None, 'builder':ttk.Label},
			{'text': self.currentFrameVar, 'command': None, 'builder':ttk.Entry},
			{'text': self.maxFrameVar, 'command': None, 'builder':ttk.Label},
			{'text':'⭯', 'command':'REFRESH', 'builder':ttk.Button},
			{'text':'Play', 'command':'PLAY', 'builder':ttk.Button},
			{'text':'Pause', 'command':'PAUSE', 'builder':ttk.Button},
			{'text':'Stop', 'command':'STOP', 'builder':ttk.Button},
			{'text':'⭠', 'command':'PREV', 'builder':ttk.Button},
			{'text':'⭢', 'command':'NEXT', 'builder':ttk.Button}
		]

		self.t=0
		self.currentFrameVar.set(self.t)

	def config_graphs(self):

		self.figure = plt.figure()

		self.canvas = FigureCanvasTkAgg(self.figure, master=self)
		self.canvas.show()
		self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

		toolbar = NavigationToolbar2TkAgg(self.canvas, self)
		toolbar.update()
		self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

		self.ax00 = plt.subplot2grid((6,2), (0,0), rowspan=5)	#SAMMONS2D
		self.ax10 = plt.subplot2grid((6,2), (5, 0))				#SAMMONSERROR
		self.ax01 = plt.subplot2grid((6,2), (0,1), rowspan=3)	#PARALEL
		self.ax11 = plt.subplot2grid((6,2), (3,1), rowspan=3)	#BEST

		plt.tight_layout()
		self.figure.subplots_adjust(left=config.LEFT, right=config.RIGHT, top=config.TOP, bottom=config.BOTTOM, wspace=config.WSPACE, hspace=config.HSPACE)

	def buildplothandlers(self):

		cmap, scalar_map = self.buildcolormapping(self.s_fitness)

		#PLOTING OBJECTS
		paralelCoordPlot = plots.ParalelCoordPlot(self.s_dataND, self.ax01, self.s_norm_data, self.s_fitness, scalar_map)
		sammonErrorPlot = plots.SammonErrorPlot(self.sammon_error,self.ax10)
		sammon2DPlot = plots.Sammon2DPlot(self.s_data2D, self.ax00, self.s_fitness, self.s_norm_fitness, cmap, paralelCoordPlot)
		bestFitnessPlot = plots.BestFitnessPlot(self.s_fitness, self.ax11 ,self.objective)

		self.all_plots = plots.PlotComposite(self.figure)
		self.all_plots.add(paralelCoordPlot)
		self.all_plots.add(sammonErrorPlot)
		self.all_plots.add(sammon2DPlot)
		self.all_plots.add(bestFitnessPlot)

		def highlight(event):
			#Parallel Coord
			if event.mouseevent.inaxes is self.ax01:
				paralelCoordPlot.highlight(self.t, event.ind)
				self.figure.canvas.draw()
			elif event.mouseevent.inaxes is self.ax00:
				sammon2DPlot.highlight(self.t, event.ind)
				self.figure.canvas.draw()

		# self.figure.canvas.mpl_connect('key_press_event',update)
		self.figure.canvas.mpl_connect('pick_event',highlight)

	def build_toolbar(self):
		self.toolbar_length = len(self.toolbar_config)
		self.toolbar_buttons = [None] * self.toolbar_length

		for i, item_config in enumerate(self.toolbar_config):

			if item_config['builder'] == ttk.Button:
				text = item_config['text']
			
				button_id = ttk.Button(self.top,text=text)
				button_id.grid(row=0, column=i)
				self.toolbar_buttons[i] = button_id

				# button_id.configure(command=lambda: self.service_toolbar(copy(toolbar_index)))

				def toolbar_button_handler(event, self=self, command=item_config['command']):
					return self.service_toolbar(command)

				#call function when the 1st mouse button is clicked
				button_id.bind("<Button-1>", toolbar_button_handler)

			elif item_config['builder'] == ttk.Entry:
				entry_id = ttk.Entry(self.top, textvariable=item_config['text'], width=6)
				entry_id.grid(row=0, column=i)

			elif item_config['builder'] == ttk.Label:
				if type(item_config['text']) == str:
					label_id = ttk.Label(self.top, text=item_config['text'])
				elif type(item_config['text']) == tk.StringVar:
					label_id = ttk.Label(self.top, textvariable=item_config['text'])
				label_id.grid(row=0, column=i)

			elif item_config['builder'] == ttk.Checkbutton:
				checkbutton_id = ttk.Checkbutton(self.top, variable=item_config['variable'], text=item_config['text'])
				checkbutton_id.grid(row=0, column=i)

	def buildcolormapping(self, fitness):

		cmap = plt.get_cmap('brg')
		cNorm  = colors.Normalize(vmin=fitness.min(), vmax=fitness.max())
		scalar_map = cmx.ScalarMappable(norm=cNorm, cmap=cmap)

		return cmap, scalar_map

	# call blink() if start and set stop when stop            
	def service_toolbar(self, command):

		self.t = int(self.currentFrameVar.get())

		print('service called', command)
		if command == 'PLAY':
			self.all_plots.update(self.t)

		elif command == 'PAUSE':
			print('PAUSE')

		elif command == 'STOP':
			print('STOP')

		elif command == 'PREV':
			if self.t-1 >= 0:
				self.t -=1
				self.currentFrameVar.set(self.t)
				self.all_plots.update(self.t)
			else:
				print('WARNING: Minimum epoch reached')

		elif command == 'NEXT':

			if self.t +1 < self.maxFrame:
				self.t +=1
				self.currentFrameVar.set(self.t)
				self.all_plots.update(self.t)
			else:
				print('WARNING: Maximum epoch reached')

		elif command == 'REFRESH':
			print('REFRASH')

		elif command == 'OPEN':
			# self.Mbox('Loading configuration', [{'var':filename, 'func':func}, {'var':}])
			self.loaddata(filename = self.askopenfilename(), callback = lambda: self.service_toolbar('PLAY'))

	# def update_var_label(self, var, label_var, value):
	# 	var = value
	# 	label_var.set(value)

	def loaddata(self, filename, callback):
		self.filename = filename

		#####################
		### Data Handling ###
		#####################

		dataND, fitness, header= evolutiveReader(filename, withheader=True)

		self.objective = header['objective']

		#get size info
		E, I, D = dataND.shape

		#normilize data
		norm_data, norm_fitness =  normalizeEvolutiveData(dataND, fitness,verbose=True)

		#N-D to 2-D
		# data2D, sammon_error = sammon(self.dataND)
		framelapse = int(self.framelapseVar.get())
		[data2D, self.sammon_error] = iterativesammon(norm_data, framelapse=framelapse)


		self.maxFrame = E
		self.maxFrameVar.set(str(E))
		#SORTING indexes

		if self.objective == 'maximize':
			foi = fitness.argsort()
		elif self.objective == 'minimize':
			foi = fitness.argsort()[::-1]
		else:
			raise('Invalid argument for objective:')

		#SORTING IN_PRACTICE
		self.s_dataND = dataND.copy()
		self.s_data2D = data2D.copy()
		self.s_norm_data = norm_data.copy()
		self.s_fitness = fitness.copy()
		self.s_norm_fitness = norm_fitness.copy()

		for e in range(E):
			self.s_dataND[e] = self.s_dataND[e][foi[e][::]]
			self.s_data2D[e] = self.s_data2D[e][foi[e][::]]
			self.s_norm_data[e] = self.s_norm_data[e][foi[e][::]]
			self.s_fitness[e] = self.s_fitness[e][foi[e][::]]
			self.s_norm_fitness[e] = self.s_norm_fitness[e][foi[e][::]]

		self.buildplothandlers()
		callback()


	def askopenfilename(self):
		#Returns file's name

		self.file_opt = {'defaultextension': '.swarm'}
		return tk.filedialog.askopenfilename(**self.file_opt)

if __name__ == '__main__':
	app = App()
	app.mainloop()