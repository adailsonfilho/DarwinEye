import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.lines
import matplotlib.collections
import matplotlib.path

import numpy as np
import config

class PlotBase(object):

	"""
	data:	is the main data content to the plot
	axis:	is the matplotlib responsable for store the plot state and draw the content
	"""

	def __init__(self, data, axis):

		self.data = data
		self.axis = axis

		if self.data is not None:
			for i, value in enumerate(self.data.shape):
				if i == 0:
					self.E = value
				elif i == 1:
					self.I = value
				elif i == 2:
					self.D = value
				else:
					raise Exception("Formato de dados inválido. Deve-se ter no máximo 3 eixos: Epocas, Indivíduos e Dimensões")
		

	def build(self):
		raise Exception("Not implemented")

	def update(self,frame):
		self._update(frame)

	def _update(self,frame):
		raise Exception("Not implemented")

class PlotComposite(PlotBase):

	def __init__(self):
		super(PlotComposite, self).__init__(None, None)
		self.plots = []

	def add(self, plot):
		self.plots.append(plot)

	def remove(self, plot):
		self.plots.remove(plot)

	def update(self, frame):
		for plot in self.plots:
			plot.update(frame)

class BestFitnessPlot(PlotBase):

	def __init__(self, data, axis, objective, **kwargs):
		super(BestFitnessPlot, self).__init__(data,axis)
		 
		if objective == config.MAXIMIZE:
			self._arrangedata_maximize()
		elif objective == config.MINIMIZE:
			self._arrangedata_minimize()
		else:
			raise Exception('Invalig argument value: {0}'.format(objective))
			

		self._build(**kwargs)
		self._set_padding()

	def _build(self,**kwargs):

		#PLOTLINES
		self.axis.plot(self.best_fitness_acc,label="Best until",lw=config.LW_TICK,c=config.GREEN)
		self.axis.plot(self.best_fitness,label="Best in each",lw=config.LW_TICK,c=config.ORANGE)
		self.axis.plot(self.avg_fitness,label="Average",lw=config.LW_TICK, c=config.BLUE)
		
		#plot vertical line ate real epoch
		key = 'single_axvline'
		if key in kwargs:
			if kwargs[key]:
				self.interest = self.axis.axvline(x=0)

		#LABELS & LEGEND
		if 'title' in kwargs:
			self.axis.set_title(kwargs['title'], fontsize=config.NORMAL)
		self.axis.set_ylabel('Fitness', fontsize=config.SMALL)
		self.axis.set_xlabel('Epoch', fontsize=config.SMALL)
		
		handles, labels = self.axis.get_legend_handles_labels()
		self.axis.legend(handles, labels, loc='upper left', ncol=3)

	def _arrangedata_maximize(self):
		self.best_fitness_acc = np.array([self.data[:(i+1)].max() for i,fit_epoch in enumerate(self.data)])
		self.best_fitness = np.array([fit_epoch.max() for i,fit_epoch in enumerate(self.data)])
		self.avg_fitness = np.array([np.mean(fit_epoch) for fit_epoch in self.data])

	def _arrangedata_minimize(self):
		self.best_fitness_acc = np.array([self.data[:(i+1)].min() for i,fit_epoch in enumerate(self.data)])
		self.best_fitness = np.array([fit_epoch.min() for i,fit_epoch in enumerate(self.data)])
		self.avg_fitness = np.array([np.mean(fit_epoch) for fit_epoch in self.data])

	def _set_padding(self):

		# X - boundaries
		self.xmin = 0
		self.xmax = self.E-1

		xoffset = (self.xmax-self.xmin)*(config.PAD/2)

		self.xmin -= xoffset
		self.xmax += xoffset		

		# Y - boundaries
		self.ymin = np.min([self.best_fitness.min(), self.best_fitness_acc.min(), self.avg_fitness.min()])
		self.ymax = self.data.max()		

		yoffset = (self.ymax-self.ymin)*config.PAD
		yoffset_label_magin = (self.ymax-self.ymin)*.2

		self.ymin -= yoffset
		self.ymax += yoffset + yoffset_label_magin

		# set boudaries
		self.axis.set_xlim(self.xmin, self.xmax)
		self.axis.set_ylim(self.ymin, self.ymax)
	

	def _update(self, frame):		
		self.interest.set_xdata([frame])

class SammonErrorPlot(PlotBase):

	def __init__(self, data, axis):
		super(SammonErrorPlot, self).__init__(data, axis)

		self._build()
		self._set_padding()

	def _build(self):
		self.axis.set_title("Sammon's Mapping Error", fontsize=config.NORMAL)
		self.axis.set_ylabel('Error', fontsize=config.SMALL)
		self.axis.set_xlabel('Epoch', fontsize=config.SMALL)
		self.axis.fill_between(range(self.E), self.data,edgecolor=config.RED, facecolor=config.RED)
		self.axis.plot(self.data, c=config.RED_DARK)

		#plot vertical line ate real epoch
		self.interest = self.axis.axvline(x=0)

	def _set_padding(self):
		# X - boudaries
		self.xmin = 0
		self.xmax = self.E-1

		xoffset = (self.xmax-self.xmin)*(config.PAD/2)

		self.xmin -= xoffset
		self.xmax += xoffset

		# Y - boudaries
		self.ymin = self.data.min()
		self.ymax = self.data.max()

		yoffset = (self.ymax-self.ymin)*config.PAD
		self.ymin -= yoffset
		self.ymax += yoffset

		#set boundaries
		self.axis.set_xlim(self.xmin, self.xmax)
		self.axis.set_ylim(self.ymin, self.ymax)

	def _update(self, frame):
		self.interest.set_xdata([frame])
		
class ParalelCoordPlot(PlotBase):

	def __init__(self, data, axis, norm_data, fitness, objective, norm_fitness, scalar_map):
		super(ParalelCoordPlot, self).__init__(data, axis)

		self.norm_data = norm_data
		self.fitness = fitness
		self.norm_fitness = norm_fitness
		self.scalar_map = scalar_map
		self.objective = objective
		
		# Create an slot for every individual pyplot.Line2D
		self.interest = np.array([None]*self.I, dtype=mpl.lines.Line2D)
		self.instancemap = {}

		self._build()
		self._set_padding()

	def _arange_maximize(self):
		self.zorders = (self.norm_fitness*100).astype(int)

	def _arange_minimize(self):

		fit_inv = 1/(self.norm_fitness+(-self.norm_fitness.min()+1))
		fit_inv = (fit_inv-fit_inv.min())/(fit_inv.max()-fit_inv.min())

		print('fit_inv:',fit_inv.min(), fit_inv.max())

		self.zorders = (fit_inv*100).astype(int)

	def _build(self):

		if self.objective == config.MAXIMIZE:
			self._arange_maximize()
		elif self.objective == config.MINIMIZE:
			self._arange_minimize()
		else:
			raise Exception('Invalig argument value: {0}'.format(objective))

		self.axis.set_title("Paralel Coordinates", fontsize=config.NORMAL)
		self.axis.set_ylabel('Value', fontsize=config.SMALL)
		self.axis.set_xlabel('Dimension', fontsize=config.SMALL)

		startframe = 0
		for i, individual in enumerate(self.norm_data[startframe]):

			colorVal = self.scalar_map.to_rgba(self.fitness[startframe][i])
			alpha = 0.5
			lw = config.LW_MEDIUM

			self.interest[i] = self.axis.plot(individual, lw=lw, color=colorVal, alpha = alpha, picker=2)[0]
			self.instancemap[self.interest[i]] = i

	def _set_padding(self):
		self.xmin = 0
		self.xmax = self.D-1

		xoffset = (self.xmax-self.xmin)*(config.PAD/2)

		self.xmin -= xoffset
		self.xmax += xoffset

		self.ymin = 0
		self.ymax = 1

		yoffset = (self.ymax-self.ymin)*config.PAD
		self.ymin -= yoffset
		self.ymax += yoffset

		self.axis.set_xlim(self.xmin, self.xmax)
		self.axis.set_ylim(self.ymin, self.ymax)

	def _update(self,frame):

		for i, individual in enumerate(self.norm_data[frame]):

			colorVal = self.scalar_map.to_rgba(self.fitness[frame][i])

			self.interest[i].set_ydata(individual)
			self.interest[i].set_color(colorVal)
			self.interest[i].set_zorder(self.zorders[frame][i])
			self.interest[i].set(alpha=config.ALPHA80, lw=config.LW_MEDIUM)

class Sammon2DPlot(PlotBase):

	def __init__(self, data, axis, fitness, norm_fitness, cmap, objective):
		super(Sammon2DPlot, self).__init__(data,axis)
		self.fitness = fitness
		self.norm_fitness = norm_fitness
		self.cmap = cmap
		self.cbar = None
		self.objective = objective

		self.interest = np.array([None]*self.I, dtype=mpl.path.Path)

		self.instancemap = {}
		self._build()
		self._set_padding()
		self.last_frame = 0
		self.fittodata = False

	def _arange_maximize(self):
		self.sizes = (self.norm_fitness*(config.SMAX-config.SMIN))+config.SMIN
		self.zorders = (self.norm_fitness*100).astype(int)

	def _arange_minimize(self):

		fit_inv = 1/(self.norm_fitness+(-self.norm_fitness.min()+1))
		fit_inv = (fit_inv-fit_inv.min())/(fit_inv.max()-fit_inv.min())

		print('fit_inv:',fit_inv.min(), fit_inv.max())

		self.zorders = (fit_inv*100).astype(int)

		self.sizes = (fit_inv*(config.SMAX-config.SMIN))+config.SMIN


	def _build(self):

		startframe = 0

		if self.objective == config.MAXIMIZE:
			self._arange_maximize()
		elif self.objective == config.MINIMIZE:
			self._arange_minimize()
		else:
			raise Exception('Invalig argument value: {0}'.format(objective))

		self.axis.set_title("Sammon's Mapping", fontsize=config.NORMAL)

		self.edgecolor = np.array([config.GRAY8 for i in range(self.I)])
		self.lw = np.zeros(self.I)

		for i in range(self.I):

			x = self.data[startframe][i][0]
			y = self.data[startframe][i][1]
			color = self.fitness[startframe][i]

			self.interest[i] = self.axis.scatter(x, y, c=color, s=self.sizes[startframe][i], edgecolor=self.edgecolor, lw=self.lw, alpha=config.ALPHA100, cmap = self.cmap, vmin=self.fitness.min(), vmax=self.fitness.max(), picker=1.5)
			self.instancemap[self.interest[i]] = i
		self.cbar = plt.colorbar(self.interest[0], ax=self.axis)

	def _fit_padding(self, epoch):

		intervalx = self.data[epoch,:,0].max()-self.data[epoch,:,0].min()
		intervaly = self.data[epoch,:,1].max()-self.data[epoch,:,1].min()
		self.axis.set_xlim(self.data[epoch,:,0].min()-(intervalx*config.PAD), self.data[epoch,:,0].max()+(intervalx*config.PAD))
		self.axis.set_ylim(self.data[epoch,:,1].min()-(intervaly*config.PAD), self.data[epoch,:,1].max()+(intervaly*config.PAD))

	def _set_padding(self):
		self.axis.set_xlim(self.data[:,:,0].min()-(config.PAD), self.data[:,:,0].max()+(config.PAD))
		self.axis.set_ylim(self.data[:,:,1].min()-(config.PAD), self.data[:,:,1].max()+(config.PAD))

	def _update(self, frame):

		if self.fittodata:
			self._fit_padding(frame)
		else:
			self._set_padding()

		for i in range(self.I):

			color = self.fitness[frame][i]

			if self.interest[i] is not None:
				# Set x and y data...
				self.interest[i].set_offsets(self.data[frame][i])
				# Set sizes...
				self.interest[i].set_sizes(np.array([self.sizes[frame][i]]))
				# Set colors..
				self.interest[i].set_array(np.array([color]))
				#zorder
				self.interest[i].set_zorder(self.zorders[frame][i])

class HighlightPlots(PlotBase):

	def __init__(self, sam2d, paralel):
		super(HighlightPlots, self).__init__(None,None)
		self.E,self.I,self.D = paralel.data.shape
		self.sam2d = sam2d
		self.paralel = paralel
		self.highlights = np.array([False for i in range(self.I)])
		self.annotations = np.array([None for d in range(self.D*self.I*self.E)], dtype=object).reshape([self.E, self.I, self.D])
		self.last_frame = 0;

	def _update(self, frame):

		bbox_args = dict(boxstyle="round", fc="0.8")

		for  i in range(self.I):

			if self.last_frame != frame and self.annotations[self.last_frame][i][0] is not None:
				for d in range(self.D):
						self.annotations[self.last_frame][i][d].remove()
						self.annotations[self.last_frame][i][d]=None

			if self.highlights[i]:

				self.sam2d.interest[i].set(**config.SCATTER_HIGH)
				self.paralel.interest[i].set(**config.LINE_HIGH)

				if self.annotations[frame][i][0] is None:
					for d in range(self.D):

						text = str(self.paralel.data[frame][i][d])
						
						if d ==0:
							mid = 0
						elif d == self.D-1:
							mid = 0.05
						else:
							mid = len(text)*0.

						x = d-mid
						y = self.paralel.norm_data[frame][i][d]

						self.annotations[frame][i][d] = self.paralel.axis.annotate(text, xy=(x, y), xytext=(x, y),bbox=bbox_args, ha='center', zorder=self.paralel.zorders.max()+1)
			else:
				for d in range(self.D):
					if self.annotations[frame][i][d] is not None:
						self.annotations[frame][i][d].remove()
						self.annotations[frame][i][d]=None

				self.sam2d.interest[i].set(**config.SCATTER_DEFAULT)
				self.paralel.interest[i].set(**config.LINE_DEFAULT)

		self.last_frame = frame

				
