import matplotlib.pyplot as plt
import numpy as np
import config

# import ipdb

class PlotBase(object):

	def __init__(self, data,axis):
		self.data = data
		self.axis = axis

		try:
			self.E = data.shape[0]
			self.I = data.shape[1]
			self.D = data.shape[2]
		except Exception as e:
			pass
		

	def build(self):
		raise("'build' method was not implemented")

	def update(self,frame):
		self.axis.clear()
		self._update(frame)

	def _update(self,frame):
		raise("'_update' method was not implemented")

class PlotComposite(PlotBase):

	def __init__(self, figure):
		super(PlotComposite, self).__init__(None, None)
		self.plots = []
		self.figure = figure

	def add(self, plot):
		self.plots.append(plot)

	def remove(self, plot):
		self.plots.remove(plot)

	def update(self, frame):
		for plot in self.plots:
			plot.update(frame)
		self.figure.canvas.draw()
	
class SammonErrorPlot(PlotBase):

	def __init__(self, data, axis):
		super(SammonErrorPlot, self).__init__(data, axis)

		# Limits setup
		self.xmin = 0
		self.xmax = self.E-1

		xoffset = (self.xmax-self.xmin)*(config.PAD/2)

		self.xmin -= xoffset
		self.xmax += xoffset

		self.ymin = self.data.min()
		self.ymax = self.data.max()

		yoffset = (self.ymax-self.ymin)*config.PAD
		self.ymin -= yoffset
		self.ymax += yoffset


	def _update(self, frame):

		self.axis.set_title("Sammon's Mapping Error", fontsize=config.NORMAL)
		self.axis.set_ylabel('Error', fontsize=config.SMALL)
		self.axis.set_xlabel('Epoch', fontsize=config.SMALL)
		self.axis.fill_between(range(self.E), self.data,edgecolor=config.RED, facecolor=config.RED)
		self.axis.plot(self.data, c=config.RED_DARK)

		self.axis.set_xlim(self.xmin, self.xmax)
		self.axis.set_ylim(self.ymin, self.ymax)

		#plot vertical line ate real epoch
		self.axis.axvline(x=frame)

class BestFitnessPlot(PlotBase):

	def __init__(self, data, axis, objective):
		super(BestFitnessPlot, self).__init__(data,axis)
		 
		if objective == 'maximize':
			self.best_fitness_acc = np.array([self.data[:(i+1)].max() for i,fit_epoch in enumerate(self.data)])
			self.best_fitness = np.array([fit_epoch.max() for i,fit_epoch in enumerate(self.data)])
			self.avg_fitness = np.array([np.mean(fit_epoch) for fit_epoch in self.data])
		else:
			self.best_fitness_acc = np.array([self.data[:(i+1)].min() for i,fit_epoch in enumerate(self.data)])
			self.best_fitness = np.array([fit_epoch.min() for i,fit_epoch in enumerate(self.data)])
			self.avg_fitness = np.array([np.mean(fit_epoch) for fit_epoch in self.data])

		# ipdb.set_trace()

		self.xmin = 0
		self.xmax = self.E-1

		xoffset = (self.xmax-self.xmin)*(config.PAD/2)

		self.xmin -= xoffset
		self.xmax += xoffset

		self.ymin = np.min([self.best_fitness.min(), self.best_fitness_acc.min(), self.avg_fitness.min()])
		self.ymax = self.data.max()

		yoffset = (self.ymax-self.ymin)*config.PAD
		yoffset_label_magin = (self.ymax-self.ymin)*.2
		self.ymin -= yoffset
		self.ymax += yoffset + yoffset_label_magin


	def _update(self, frame):
		#FITNESS VS EPOCH
		# ax11.set_title("Fitness vs Epoch", fontsize=NORMAL)
		self.axis.set_ylabel('Fitness', fontsize=config.SMALL)
		self.axis.set_xlabel('Epoch', fontsize=config.SMALL)

		#PLOTLINES
		self.axis.plot(self.best_fitness_acc,label="Best until",lw=config.LW_TICK,c=config.GREEN)
		self.axis.plot(self.best_fitness,label="Best in each",lw=config.LW_TICK,c=config.ORANGE)
		self.axis.plot(self.avg_fitness,label="Average",lw=config.LW_TICK, c=config.BLUE)
		
		#PADDING
		self.axis.set_xlim(self.xmin, self.xmax)
		self.axis.set_ylim(self.ymin, self.ymax)

		#plot vertical line ate real epoch
		self.axis.axvline(x=frame)

		#legenda
		handles, labels = self.axis.get_legend_handles_labels()
		self.axis.legend(handles, labels, loc='upper left', ncol=3)
		# plt.legend(bbox_to_anchor=(0, 1), loc='upper left', ncol=1)

class Sammon2DPlot(PlotBase):

	def __init__(self, data, axis, fitness, norm_fitness, cmap, paralel):
		super(Sammon2DPlot, self).__init__(data,axis)
		self.fitness = fitness
		self.norm_fitness = norm_fitness
		self.cmap = cmap
		self.cbar = None
		self.paralel = paralel
		self.highlight_inds = np.zeros(self.I)!=0

	def _update(self, frame):

		if self.cbar is not None:
			self.cbar.remove()

		self.axis.set_title("Sammon's Mapping", fontsize=config.NORMAL)

		# self.axis.set_xlim(self.data[:,0].min()*(1-config.PAD), self.data[:,0].max()*(1+config.PAD))
		# self.axis.set_ylim(self.data[:,1].min()*(1-config.PAD), self.data[:,1].max()*(1+config.PAD))
		self.axis.set_xlim(self.data[:,0].min(), self.data[:,0].max())
		self.axis.set_ylim(self.data[:,1].min(), self.data[:,1].max())

		self.edgecolor = np.array(['#888888' for i in range(self.I)])
		self.lw = np.zeros(self.I)

		for i, hl in enumerate(self.highlight_inds):
			if hl:
				self.edgecolor[i] = '#000000'
				self.lw[i] = 2 

		sizes = ((self.norm_fitness[frame]*config.SMAX)+config.SMIN)

		xs = self.data[frame][:,0]
		ys = self.data[frame][:,1]
		colors = self.fitness[frame]
		
		sc = self.axis.scatter(xs, ys, c=colors, s=sizes, edgecolor=self.edgecolor, lw=self.lw, alpha=0.75, cmap = self.cmap, vmin=self.fitness.min(), vmax=self.fitness.max(), picker=1.5)
		self.cbar = plt.colorbar(sc, ax=self.axis)

	def highlight(self, frame, ind):

		for _ind in ind:
			self.highlight_inds[_ind] = not self.highlight_inds[_ind]
			self.paralel.highlight(_ind)

		self.update(frame)
		self.paralel.update(frame)

class ParalelCoordPlot(PlotBase):

	def __init__(self, data, axis, norm_data, fitness, scalar_map):
		super(ParalelCoordPlot, self).__init__(data, axis)
		self.norm_data = norm_data
		self.fitness = fitness
		self.scalar_map = scalar_map
		self.highlight_inds = np.zeros((self.E,self.I))!=0
		self.labels = np.array([[[{} for d in range(self.D)] for i in range(self.I)] for e in range(self.E)], dtype=dict)

	def _update(self,frame):
		self.axis.set_title("Paralel Coordinates", fontsize=config.NORMAL)
		self.axis.set_ylabel('Value', fontsize=config.SMALL)
		self.axis.set_xlabel('Dimension', fontsize=config.SMALL)

		for i, individual in enumerate(self.norm_data[frame]):
			colorVal = self.scalar_map.to_rgba(self.fitness[frame][i])

			alpha = 0.5
			lw = config.LW_MEDIUM

			bbox_args = dict(boxstyle="round", fc="0.8")

			if self.highlight_inds[frame][i]:
				alpha = 1.0
				lw = config.LW_NORMAL
				for d in range(self.D):
					self.axis.scatter(self.labels[frame][i][d]['scatter_x'], self.labels[frame][i][d]['y'], s=30, c='#2222DD')
					# t = self.axis.text(self.labels[frame][i][d]['x'],self.labels[frame][i][d]['y'],self.labels[frame][i][d]['text'])

					lblsize = len(self.labels[frame][i][d]['text'])

					x = self.labels[frame][i][d]['x'] - ((lblsize/2)*config.PAD*0.5)
					y = self.labels[frame][i][d]['y']+(config.PAD)
					text = self.labels[frame][i][d]['text']

					self.axis.annotate(text, xy=(x, y), xytext=(x, y),bbox=bbox_args)
					# bb = t.get_bbox_patch()
					# bb.set_boxstyle("round", pad=0.6)
					

			self.axis.plot(individual, lw=lw, color=colorVal, alpha = alpha, picker=1)

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

	def highlight(self,ind):

		for e in range(self.E):

			self.highlight_inds[e][ind] = not self.highlight_inds[e][ind]

			if self.highlight_inds[e][ind] and self.labels[e][ind][0] == {}:
				norm_individual = self.norm_data[e][ind]
				individual = self.data[e][ind]

				for d in range(self.D):

					offset = 0
					if d == 0:
						offset = +0.15
					if d == self.D-1:
						offset = -0.35

					self.labels[e][ind][d]['x'] = d+offset
					self.labels[e][ind][d]['y'] = norm_individual[d]
					self.labels[e][ind][d]['text'] = str(individual[d])
					self.labels[e][ind][d]['scatter_x'] = d

