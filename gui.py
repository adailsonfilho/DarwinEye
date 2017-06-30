#######################
### IMPORT -> Numpy ###
#######################
import numpy as np

#########################
### IMPORT -> TKINTER ###
#########################
import tkinter as tk
import tkinter.font
from tkinter import messagebox
from tkinter import ttk

###########################
### IMPORT -> DarwinEye ###
###########################
import plots
import config
import progressbar

############################
### IMPORT -> Matplotlib ###
############################
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.cm as cmx
from matplotlib import style
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
import matplotlib.lines
import matplotlib.path

########################
### IMPORT -> SWARMA ###
########################
# from swarma.utils import evolutiveReader,normalizeEvolutiveData
from sammon.cascadesammon import cascadesammon

import utils

import ast
import json
# import ipdb

class App(tk.Tk):

	def __init__(self, *args, **kwargs):
		
		tk.Tk.__init__(self, *args, **kwargs)
		tk.Tk.wm_title(self, "DarwinEye")
		self.top=tk.Frame(self)
		self.top.pack(side=tk.TOP, fill=tk.X)

		################################
		### Matplotlib Configuration ###
		################################
		style.use("ggplot")

		self.cid_hightlight = None

		self.stop = True
		self.config_toolbar()
		self.build_toolbar()
		self.config_graphs()

		# popup window flow control
		self.next = False

		###############################
		### tkinter styles 			###
		###############################
		self.TKFONT_TITLE = tk.font.Font(size = config.SMALL, weight=tk.font.BOLD)
		self.TKFONT_CONTENT = tk.font.Font(size = config.SMALL)
		self.TKFONT_INFO = tk.font.Font(size = config.XSMALL)

		# self.style = ttk.Style()
		# self.style.configure("btn_danger", foreground="white", background="#FF3946")
		# self.style.configure("btn_primary", foreground="white", background="#4A3CD9")
		# self.style.configure("btn_success", foreground="white", background="#56B239")

	def config_toolbar(self):

		self.currentFrameVar = tk.StringVar()
		self.maxFrameVar = tk.StringVar()
		self.showLabelVar = tk.IntVar()
		self.progressvar = tk.StringVar()

		self.toolbar_config = [
			{'text':'Open', 'command':'OPEN', 'builder':ttk.Button},
			{'text': 'Current epoch:', 'command': None, 'builder':ttk.Label},
			{'text': self.currentFrameVar, 'command': None, 'builder':ttk.Entry},
			{'text': self.maxFrameVar, 'command': None, 'builder':ttk.Label},
			{'text':'⭯', 'command':'REFRESH', 'builder':ttk.Button},
			{'text':'Play', 'command':'PLAY', 'builder':ttk.Button},
			{'text':'Pause', 'command':'PAUSE', 'builder':ttk.Button},
			# {'text':'Stop', 'command':'STOP', 'builder':ttk.Button},
			{'text':'⭠', 'command':'PREV', 'builder':ttk.Button},
			{'text':'⭢', 'command':'NEXT', 'builder':ttk.Button},
			{'text':'Fit Sammon Data', 'command':'FITSAMMON', 'builder':ttk.Button},
			{'text':'Clear Highlitghs', 'command':'CLEARHIGH', 'builder':ttk.Button},
			{'text':'Info', 'command':'INFO', 'builder':ttk.Button},
			{'text': self.progressvar, 'command': None, 'builder':ttk.Label},
			{'text':None, 'command': None, 'builder': ttk.Progressbar}
		]

		self.t=0
		self.currentFrameVar.set(self.t)

	def config_graphs(self):

		self.figure = plt.figure(1)

		self.canvas = FigureCanvasTkAgg(self.figure, master=self)
		self.canvas.show()
		self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

		toolbar = NavigationToolbar2TkAgg(self.canvas, self)
		toolbar.update()
		self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

	def _build_axes(self):
		self.ax00 = plt.subplot2grid((6,2), (0,0), rowspan=5)	#SAMMONS2D
		self.ax10 = plt.subplot2grid((6,2), (5, 0))				#SAMMONSERROR
		self.ax01 = plt.subplot2grid((6,2), (0,1), rowspan=3)	#PARALEL
		self.ax11 = plt.subplot2grid((6,2), (3,1), rowspan=3)	#BEST

		plt.tight_layout()
		self.figure.subplots_adjust(left=config.LEFT, right=config.RIGHT, top=config.TOP, bottom=config.BOTTOM, wspace=config.WSPACE, hspace=config.HSPACE)

	def showwarning(self, title, message):
		messagebox.showwarning(title, message)

	def showinfo(self, title, message):
		messagebox.showinfo(title, message)

	def _buildplothandlers(self):

		cmap, scalar_map = self.buildcolormapping(self.fitness)

		#PLOTING OBJECTS
		self.paralelCoordPlot = plots.ParalelCoordPlot(
			data = self.dataND,
			axis = self.ax01,
			norm_data = self.norm_data,
			fitness = self.fitness,
			norm_fitness = self.norm_fitness,
			objective = self.objective,
			scalar_map = scalar_map)

		self.sammonErrorPlot = plots.SammonErrorPlot(
			data = self.sammon_error,
			axis = self.ax10)

		self.sammon2DPlot = plots.Sammon2DPlot(
			data = self.data2D,
			axis = self.ax00,
			fitness = self.fitness,
			norm_fitness = self.norm_fitness,
			cmap = cmap,
			objective = self.objective
			)

		self.bestFitnessPlot = plots.BestFitnessPlot(
			data = self.fitness,
			axis = self.ax11,
			objective = self.objective,
			single_axvline = True)

		self.highlightPlot = plots.HighlightPlots(
			sam2d = self.sammon2DPlot,
			paralel = self.paralelCoordPlot)

		self.all_plots = plots.PlotComposite()
		self.all_plots.add(self.paralelCoordPlot)
		self.all_plots.add(self.sammonErrorPlot)
		self.all_plots.add(self.sammon2DPlot)
		self.all_plots.add(self.bestFitnessPlot)
		self.all_plots.add(self.highlightPlot)

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
			elif item_config['builder'] == ttk.Progressbar:
				self.progress = ttk.Progressbar(self.top, orient="horizontal",length=0, mode="determinate")
				self.progress.grid(row=0, column=i)


	def buildcolormapping(self, fitness):

		cmap_name = config.MPL_COLORMAP 
		if self.objective == config.MINIMIZE:
			cmap_name += '_r'		

		cmap = plt.get_cmap(cmap_name)
		cNorm  = colors.Normalize(vmin=fitness.min(), vmax=fitness.max())
		scalar_map = cmx.ScalarMappable(norm=cNorm, cmap=cmap)

		return cmap, scalar_map

	def updateplots(self, frame):
		self.all_plots.update(frame)
		self.figure.canvas.draw()

	# call blink() if start and set stop when stop            
	def service_toolbar(self, command):

		self.t = int(self.currentFrameVar.get())

		print('service called', command)
		if command == 'PLAY':
			self.stop = False
			self.blink()

		elif command == 'PAUSE':
			self.stop = True

		elif command == 'STOP':
			print('STOP')

		elif command == 'PREV':
			if self.t-1 >= 0:
				self.t -=1
				self.currentFrameVar.set(self.t)
				self.updateplots(self.t)
			else:
				self.showwarning('Warning!','Minimum epoch reached')
				print('WARNING: Minimum epoch reached')

		elif command == 'NEXT':

			if self.t +1 < self.maxFrame:
				self.t +=1
				self.currentFrameVar.set(self.t)
				self.updateplots(self.t)
			else:
				self.showwarning('Warning!','Maximum epoch reached')
				print('WARNING: Maximum epoch reached')

		elif command == 'REFRESH':
			frame = int(self.currentFrameVar.get())

			if frame >= 0 and frame < self.maxFrame:
				self.t = frame
				self.updateplots(self.t)
			else:
				self.showwarning('Warning!','Epoch out of range')

		elif command == 'OPEN':
			# self.Mbox('Loading configuration', [{'var':filename, 'func':func}, {'var':}])
			self.loaddata(filename = self.askopenfilename(), callback = lambda: self.service_toolbar('REFRESH'))
		elif command == 'INFO':

			pretty = json.dumps(self.info, sort_keys=True, indent=4)
			self.showinfo('Log Information',pretty)
		elif command == 'CLEARHIGH':
			self.highlightPlot.highlights = np.logical_and(self.highlightPlot.highlights, False);
			self.updatehighlith()
		elif command == 'FITSAMMON':
			self.sammon2DPlot.fittodata = not self.sammon2DPlot.fittodata
			self.sammon2DPlot.update(self.t)
			self.figure.canvas.draw()

		else:
			raise Exception('ERROR: Invalid Operation: {0}'.format(command))

	# def update_var_label(self, var, label_var, value):
	# 	var = value
	# 	label_var.set(value)

	def blink(self):

		if self.t +1 < self.maxFrame and not self.stop:
			self.t +=1
			print('Playing:',self.t)
			self.currentFrameVar.set(self.t)
			self.updateplots(self.t)
			self.after(100, self.blink)

	def _connect(self):

		if self.cid_hightlight is not None:
			self.figure.canvas.mpl_disconnect(self.cid_hightlight)

		def _pick_artist_sammon(event):
			
			i = -1
			if event.mouseevent.inaxes is self.sammon2DPlot.axis:
				i = self.sammon2DPlot.instancemap[event.artist]
			elif event.mouseevent.inaxes is self.paralelCoordPlot.axis:
				i = self.paralelCoordPlot.instancemap[event.artist]				
				
			if i >= 0:
				if event.mouseevent.button == 1: #left button
					self.highlightPlot.highlights[i] = not self.highlightPlot.highlights[i]
					self.updatehighlith()	
				elif event.mouseevent.button == 3: #right button
					title = 'Individual {0} in epoch {1}'.format(i, self.t)
					message = '{0} | fitness: {1}'.format(self.dataND[self.t][i].tolist(),self.fitness[self.t][i])
					self.showinfo(title, message)

		self.cid_hightlight = self.figure.canvas.mpl_connect('pick_event',_pick_artist_sammon)

	def updatehighlith(self):
		self.highlightPlot.update(self.t)
		self.figure.canvas.draw()

	def loaddata(self, filename, callback):

		#####################
		### Data Handling ###
		#####################

		self.filename = filename

		dataND, fitness, self.header= utils.readlog(filename)

		self.dataND = dataND
		self.fitness = fitness

		self.objective = self.header['objective']

		# Epochs, Individuals, Dimensions
		self.E, self.I, self.D = dataND.shape

		self.info = self.header.copy()
		self.info['Filename'] = self.filename
		self.info['Epochs'] = self.E
		self.info['Individuals'] = self.I
		self.info['Dimensions'] =self.D

		self.figure.clf()
		self._build_modal_selecepoch()
		# self.next =True

		if self.next:

			# Normalization with progress feedback
			with progressbar.Process(progressbar=self.progress, length=200, start=0, end=self.E, label='Normalizing Data:', stringvar=self.progressvar):

				def progbar_norm_update(epoch):
					print('PROG',epoch)
					self.progress["value"] = epoch
					self.update()

				try:
					bounds = self.header['bounds']
				except e:
					bounds = None

				#normilize data
				norm_data, norm_fitness =  utils.normalizeEvolutiveData(dataND, fitness, dimensions_boundaries=bounds, verbose=True, eachepoch=progbar_norm_update)

			self.norm_data = norm_data		
			self.norm_fitness = norm_fitness

			#SAMMON DATA FOR TESTING
			# self.sammon_error = np.random.random(fitness.shape[0])
			# data2D = np.random.random([fitness.shape[0],fitness.shape[1],2])

			self.maxFrame = self.E
			self.maxFrameVar.set(str(self.E-1))

			self.t = 0
			self.currentFrameVar.set(str(0))

		

			# Sammon's Mapping with progress feedback
			with progressbar.Process(progressbar=self.progress, length=200, start=0, end=self.E, label='Sammons Mapping:', stringvar=self.progressvar):

				def progbar_sammon_update(epoch):
					print('PROG',epoch)
					self.progress["value"] = epoch
					self.update()

				[self.data2D, self.sammon_error] = cascadesammon(dataND, eachepoch=progbar_sammon_update, init='pca', maxiter=500)

			self._build_axes()
			self._buildplothandlers()
			self._connect()

			callback()

	def _update_selectedepoch(self, epoch):
			#print('clicked', event.x, event.y, event.xdata, event.ydata)
			# print(event.button)
			if not self.allepochsvar.get():

				if self.selectedepochs_line2d[epoch] is None:
					self.selectedepochs_line2d[epoch] = self.selectepochPlot.axis.axvline(x=epoch)
				else:
					self.selectedepochs_line2d[epoch].remove()
					self.selectedepochs_line2d[epoch] = None

				epochslist = []
				for e in range(self.E):
					if self.selectedepochs_line2d[e] is not None:
						epochslist.append(e)

				self.epochslistVar.set(str(epochslist))

				self.selectepochPlot.axis.figure.canvas.draw()

	def _config_behaviour_graph_selectepoch(self):

		def selectepoch(event):
			if event.xdata is not None:
				self._update_selectedepoch(int(event.xdata))

		self.selectepochPlot.axis.figure.canvas.mpl_connect('button_press_event', selectepoch)

	def _build_graph_selectepoch(self, master, row):

		figure2 = plt.figure(2)

		master.canvas = FigureCanvasTkAgg(figure2, master=master)
		master.canvas.show()
		# master.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)
		master.canvas.get_tk_widget().grid(row=row, column=0,columnspan=6)

		ax_selecetepoch = plt.subplot()

		self.selectepochPlot = plots.BestFitnessPlot(
			data = self.fitness,
			axis = ax_selecetepoch,
			objective = self.objective,
			title = "Fitness Evolution",
			single_axvline = False
			)

		self._config_behaviour_graph_selectepoch()

		return figure2

	def _label_title(self, master, text):
		return ttk.Label(master, text=text, anchor=tk.E, justify=tk.RIGHT, font=self.TKFONT_TITLE)

	def _label_content(self, master, text):
		return ttk.Label(master, text=text, anchor=tk.W, justify=tk.LEFT, font=self.TKFONT_CONTENT, wraplength=400)

	def _label_info(self, master, text):
		return ttk.Label(master, text=text, font=self.TKFONT_INFO)

	def _entry(self, master, stringvar, **kwargs):
		return ttk.Entry(master, textvariable = stringvar, font=self.TKFONT_CONTENT, **kwargs)


	def _build_modal_selecepoch(self):
		#open modal window to selecet epochs
		dlg = tk.Toplevel(master=self)
		self.selectedepochs_line2d = np.array([None for e in range(self.E)], dtype=mpl.lines.Line2D)
		self.epochslistVar = tk.StringVar()
		self.epochslistVar.set(str([]))

		############################
		# Controls and Labels	####
		############################

		LEFT = sticky=tk.W
		RIGHT = sticky=tk.E

		################# ROW ###############################
		rowShape = 0
		self._label_title(master=dlg, text='Epochs:').grid(row=rowShape, column=0, sticky=RIGHT)
		self._label_content(master=dlg, text=str(self.E)).grid(row=rowShape, column=1, sticky=LEFT)

		self._label_title(master=dlg, text='Individuals:').grid(row=rowShape, column=2, sticky=RIGHT)
		self._label_content(master=dlg, text=str(self.I)).grid(row=rowShape, column=3, sticky=LEFT)

		self._label_title(master=dlg, text='Dimensions:').grid(row=rowShape, column=4, sticky=RIGHT)
		self._label_content(master=dlg, text=str(self.D)).grid(row=rowShape, column=5, sticky=LEFT)

		################# ROW ###############################
		rowDesc = 1
		self._label_title(master=dlg, text='Description:').grid(row=rowDesc, column=0, sticky=RIGHT)
		self._label_content(master=dlg, text=self.header['description']).grid(row=rowDesc, column=1, sticky=LEFT)

		self._label_title(master=dlg, text='Objective:').grid(row=rowDesc, column=2, sticky=RIGHT)
		self._label_content(master=dlg, text=self.header['objective']).grid(row=rowDesc, column=3, sticky=LEFT)

		################# ROW ###############################
		rowControls = 2
		wgts = []
		framelapseVar = tk.StringVar()
		self._label_title(master=dlg, text='Framelapse:').grid(row=rowControls, column=0, sticky=RIGHT)

		w1 = self._entry(master=dlg, stringvar=framelapseVar, state=tk.DISABLED)
		w1.grid(row=rowControls, column=1, sticky=LEFT)
		wgts.append(w1)

		def cleanepochs():
			for e,l in enumerate(self.selectedepochs_line2d):
				if l is not None:
					self.selectedepochs_line2d[e].remove()
					self.selectedepochs_line2d[e] = None
			self.epochslistVar.set(str([]))
			self.selectepochPlot.axis.figure.canvas.draw()

		def refresh():
			cleanepochs()
			try:
				fl = int(framelapseVar.get())
				fl_list = utils.framelapse(self.E, fl)
				self.epochslistVar.set(str(fl_list))
				for e in fl_list:
					self._update_selectedepoch(e)
			except Exception:
				self.showwarning('Invalid input', 'Framelapse is required and must be an integer')

		w2 = ttk.Button(dlg, text="Refresh", command=refresh, state=tk.DISABLED)
		w2.grid(row=rowControls, column=2)
		wgts.append(w2)



		w3 = ttk.Button(dlg, text="Clean", command=cleanepochs, state=tk.DISABLED)
		w3.grid(row=rowControls, column=3)
		wgts.append(w3)
		
		self.allepochsvar = tk.BooleanVar()
		self.allepochsvar.set(True)

		def wdgt_state_update(w):
			if self.allepochsvar.get():
				w.configure(state=tk.DISABLED)
			else:
				w.configure(state=tk.NORMAL)

		def allepochsvar_changed():
			for w in wgts:
				wdgt_state_update(w)


		ttk.Checkbutton(dlg, text="All epochs", command= allepochsvar_changed, variable=self.allepochsvar).grid(row=rowControls, column=4)

		################# ROW ###############################
		rowepochs = 3

		def epochslistVar_changed(event):

			try:
				epochs = ast.literal_eval(self.epochslistVar.get())			

				cleanepochs()

				for e in epochs:
					self._update_selectedepoch(e)
			except Exception:
				self.showwarning('Invalid Input','The epochs list is not wellformed')

		w4 = self._entry(master=dlg, stringvar=self.epochslistVar, state=tk.DISABLED)
		w4.grid(row=rowepochs, column=0, columnspan=6, sticky=LEFT+RIGHT)
		w4.bind("<FocusOut>", epochslistVar_changed)
		wgts.append(w4)


		################# ROW ###############################
		rowinfo = 4
		textinfo = "Clique abaixo ou modifique a lista diretamente acima"
		self._label_info(master=dlg, text=textinfo).grid(row=rowinfo, column=1, columnspan=6, sticky=LEFT+RIGHT)

		################# ROW ###############################
		rowgraph = 5
		figure2 = self._build_graph_selectepoch(dlg, row=rowgraph)

		################# ROW ###############################
		rowdecision = 6
		def done():
			self.next = True
			dlg.destroy()

		def cancel():
			self.next = False
			dlg.destroy()

		ttk.Button(dlg, text="Cancel", command=cancel).grid(row=rowdecision, column=0, columnspan=3)
		ttk.Button(dlg, text="Done", command=done).grid(row=rowdecision, column=1, columnspan=3)

		############################
		# Frame behavior		####
		############################
		dlg.transient(self)   	# only one window in the task bar
		dlg.grab_set()         	# modal
		self.wait_window(dlg)	# why?
		figure2.clf()			# clear popup figure
		plt.figure(1)			# return contexto to figure1 (main figure)


	def askopenfilename(self):
		#Returns file's name

		self.file_opt = {'defaultextension': '.swarm'}
		return tk.filedialog.askopenfilename(**self.file_opt)

if __name__ == '__main__':
	app = App()
	app.mainloop()