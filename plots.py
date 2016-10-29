import matplotlib.pyplot as plt
import numpy as np
import config

import ipdb

class PlotBase(object):

	def __init__(self, data,axis):
		self.data = data
		self.axis = axis

	def build(self):
		raise("'build' method was not implemented")

	def update(self,frame):
		self.axis.clear()
		self._update(frame)

	def _update(self,frame):
		raise("'_update' method was not implemented")

	
class SammonErrorPlot(PlotBase):

	def _update(self, frame):

		self.axis.set_title("Sammon's Mapping Error", fontsize=config.NORMAL)
		self.axis.set_ylabel('Error', fontsize=config.SMALL)
		self.axis.set_xlabel('Epoch', fontsize=config.SMALL)
		self.axis.fill_between(range(self.data.shape[0]), self.data,edgecolor=config.RED, facecolor=config.RED)
		self.axis.plot(self.data, c=config.RED_DARK)

		#plot vertical line ate real epoch
		self.axis.axvline(x=frame)

class BestFitnessPlot(PlotBase):

	def __init__(self, data, axis):
		super(BestFitnessPlot, self).__init__(data,axis)
		self.best_fitness_acc = np.array([self.data[:(i+1)].max() for i,fit_epoch in enumerate(self.data)])
		self.best_fitness = np.array([fit_epoch[:(i+1)].max() for i,fit_epoch in enumerate(self.data)])
		self.avg_fitness = np.array([np.mean(fit_epoch) for fit_epoch in self.data])

		self.xmin = 0
		self.xmax = data.shape[0]-1

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

	def _update(self, frame):

		if self.cbar is not None:
			self.cbar.remove()

		self.axis.set_title("Sammon's Mapping", fontsize=config.NORMAL)
		sc = self.axis.scatter(self.data[frame][:,0],self.data[frame][:,1], c=self.fitness[frame],s=((self.norm_fitness[frame]*50)+10), edgecolor='#888888', alpha=0.75, cmap = self.cmap, vmin=self.fitness.min(), vmax=self.fitness.max(), picker=1.5)
		self.cbar = plt.colorbar(sc, ax=self.axis)

	def highlight(self, frame, ind):
		self.highlight_ind = ind
		self.update(frame)
		self.paralel.highlight(frame,ind)

class ParalelCoordPlot(PlotBase):

	def __init__(self, data, axis, norm_data, fitness, scalar_map):
		super(ParalelCoordPlot, self).__init__(data, axis)
		self.norm_data = norm_data
		self.fitness = fitness
		self.scalar_map = scalar_map
		self.highlight_ind = None

	def _update(self,frame):
		self.axis.set_title("Paralel Coordinates", fontsize=config.NORMAL)
		self.axis.set_ylabel('Value', fontsize=config.SMALL)
		self.axis.set_xlabel('Dimension', fontsize=config.SMALL)

		for i, individual in enumerate(self.norm_data[frame]):
			colorVal = self.scalar_map.to_rgba(self.fitness[frame][i])

			alpha = 1
			lw = config.LW_NORMAL

			if self.highlight_ind is not None and i != self.highlight_ind:
				alpha = 0.5
				lw = config.LW_MEDIUM

			self.axis.plot(individual, lw=lw, color=colorVal, alpha = alpha, picker=1)

		self.xmin = 0
		self.xmax = self.data.shape[2]-1

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

	def highlight(self,frame,ind):
		self.highlight_ind = ind
		self.update(frame)

		print('Ind:',ind)

		norm_individual = (self.norm_data[frame][ind])[0]
		individual = (self.data[frame][ind])[0]

		for d in range(self.data.shape[2]):
			self.axis.scatter(d, norm_individual[d], s=30, c='#2222DD')
			offset = 0
			if(d == self.data.shape[2]-1):
				offset = -0.35
			self.axis.text(d+offset, norm_individual[d], str(individual[d]))

		

