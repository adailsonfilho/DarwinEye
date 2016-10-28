import matplotlib.pyplot as plt
import numpy as np
import setup

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

		self.axis.set_title("Sammon's Mapping Error", fontsize=setup.NORMAL)
		self.axis.set_ylabel('Error', fontsize=setup.SMALL)
		self.axis.set_xlabel('Epoch', fontsize=setup.SMALL)
		self.axis.fill_between(range(self.data.shape[0]), self.data,edgecolor=setup.RED, facecolor=setup.RED)
		self.axis.plot(self.data, c=setup.RED_DARK)

		#plot vertical line ate real epoch
		self.axis.axvline(x=frame, picker=3)

class BestFitnessPlot(PlotBase):

	def __init__(self, data, axis):
		super(BestFitnessPlot, self).__init__(data,axis)
		self.best_fitness_acc = np.array([self.data[:(i+1)].max() for i,fit_epoch in enumerate(self.data)])
		self.best_fitness = np.array([fit_epoch[:(i+1)].max() for i,fit_epoch in enumerate(self.data)])
		self.avg_fitness = np.array([np.mean(fit_epoch) for fit_epoch in self.data])

		self.xmin = 0
		self.xmax = data.shape[0]-1

		xoffset = (self.xmax-self.xmin)*(setup.PAD/2)

		self.xmin -= xoffset
		self.xmax += xoffset

		self.ymin = np.min([self.best_fitness.min(), self.best_fitness_acc.min(), self.avg_fitness.min()])
		self.ymax = self.data.max()

		yoffset = (self.ymax-self.ymin)*setup.PAD
		yoffset_label_magin = (self.ymax-self.ymin)*.2
		self.ymin -= yoffset
		self.ymax += yoffset + yoffset_label_magin


	def _update(self, frame):
		#FITNESS VS EPOCH
		# ax11.set_title("Fitness vs Epoch", fontsize=NORMAL)
		self.axis.set_ylabel('Fitness', fontsize=setup.SMALL)
		self.axis.set_xlabel('Epoch', fontsize=setup.SMALL)

		#PLOTLINES
		self.axis.plot(self.best_fitness_acc,label="Best until",lw=setup.LW_TICK,c=setup.GREEN)
		self.axis.plot(self.best_fitness,label="Best in each",lw=setup.LW_TICK,c=setup.ORANGE)
		self.axis.plot(self.avg_fitness,label="Average",lw=setup.LW_TICK, c=setup.BLUE)
		
		#PADDING
		self.axis.set_xlim(self.xmin, self.xmax)
		self.axis.set_ylim(self.ymin, self.ymax)

		#plot vertical line ate real epoch
		self.axis.axvline(x=frame, picker=3)

		#legenda
		handles, labels = self.axis.get_legend_handles_labels()
		self.axis.legend(handles, labels, loc='upper left', ncol=3)
		# plt.legend(bbox_to_anchor=(0, 1), loc='upper left', ncol=1)

class Sammon2DPlot(PlotBase):

	def __init__(self, data, axis, fitness, norm_fitness, cmap):
		super(Sammon2DPlot, self).__init__(data,axis)
		self.fitness = fitness
		self.norm_fitness = norm_fitness
		self.cmap = cmap
		self.cbar = None


	def _update(self, frame):

		if self.cbar is not None:
			self.cbar.remove()

		self.axis.set_title("Sammon's Mapping", fontsize=setup.NORMAL)
		sc = self.axis.scatter(self.data[frame][:,0],self.data[frame][:,1], c=self.fitness[frame],s=((self.norm_fitness[frame]*50)+10), edgecolor='#888888', alpha=0.75, cmap = self.cmap, vmin=self.fitness.min(), vmax=self.fitness.max())
		self.cbar = plt.colorbar(sc, ax=self.axis)

class ParalelCoordPlot(PlotBase):

	def __init__(self,data,axis):
		super(Sammon2D,self).__init__(self,data,axis)

