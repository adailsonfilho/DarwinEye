from plots import PlotBase, SammonErrorPlot, BestFitnessPlot, Sammon2DPlot, ParalelCoordPlot
import config

import time

import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.cm as cmx
from matplotlib import style

style.use("ggplot")

import numpy as np
from swarma.utils import normalizeEvolutiveData

import ipdb

def load_data():		

	#######################################
	#  FAKE DATA  [BEGIN] #################
	#######################################

	#Data settings
	E = 20
	I = 10
	D = 5

	#DATA NORMALIZED
	norm_data = np.random.random((E,I,D))
	norm_fitness = np.random.random((E,I))

	#SIMULATEE (DATA NON-NOMALIZED)

	#Data bounds
	LOW = -300
	low_bounds = [ np.ceil(np.random.random()*LOW) for i in range(D)]
	print('LOW_BOUNDS:', low_bounds)

	HIGH = 300
	high_bounds = [np.ceil(np.random.random()*HIGH)+low_bounds[i] for i in range(D)]
	print('HIGH_BOUNDS:', high_bounds)

	LOW_FITNESS = np.random.uniform(-300,300)
	HIGH_FITNESS = np.random.uniform(LOW_FITNESS+1,LOW_FITNESS+300)

	print('LOW_FIT:',LOW_FITNESS, 'HIGH_FIT:',HIGH_FITNESS)

	#Denormalize data
	data = norm_data.copy()
	for d in range(D):
		data[:,:,d] = (data[:,:,d]*(high_bounds[d]-low_bounds[d]))+low_bounds[d]

	#Denormalize fitness
	fitness = norm_fitness.copy()
	fitness = (fitness*(HIGH_FITNESS-LOW_FITNESS))-LOW_FITNESS
	#######################################
	#  FAKE DATA  [/END] ##################
	#######################################

	return data, fitness


def sammon(data):
	#fakesammon
	return np.random.random((data.shape[0],data.shape[1],2)), np.random.random(data.shape[0])

if __name__ == '__main__':

	#######################################
	#  Gathering data  [BEGIN] ############
	#######################################

	#load data from file
	dataND, fitness = load_data()

	#get size info
	E, I, D = dataND.shape

	#N-D to 2-D
	data2D, sammon_error = sammon(dataND)

	#normilize data
	norm_data, norm_fitness =  normalizeEvolutiveData(dataND, fitness,verbose=True)


	#SORTING indexes
	foi = fitness.argsort()

	#SORTING IN_PRACTICE
	s_dataND = dataND.copy()
	s_data2D = data2D.copy()
	s_norm_data = norm_data.copy()
	s_fitness = fitness.copy()
	s_norm_fitness = norm_fitness.copy()

	for e in range(E):
		s_dataND[e] = s_dataND[e][foi[e][::]]
		s_data2D[e] = s_data2D[e][foi[e][::]]
		s_norm_data[e] = s_norm_data[e][foi[e][::]]
		s_fitness[e] = s_fitness[e][foi[e][::]]
		s_norm_fitness[e] = s_norm_fitness[e][foi[e][::]]

	# ipdb.set_trace()

	#######################################
	#  Gathering data  [/END]] ############
	#######################################

	#######################################
	#  CONFIG  [BEGIN] ####################
	#######################################
	cmap = plt.get_cmap('brg')
	cNorm  = colors.Normalize(vmin=fitness.min(), vmax=fitness.max())
	scalar_map = cmx.ScalarMappable(norm=cNorm, cmap=cmap)

	figure = plt.figure()
	#GRID
	ax00 = plt.subplot2grid((6,2), (0,0), rowspan=5)	#SAMMONS2D
	ax10 = plt.subplot2grid((6,2), (5, 0))				#SAMMONSERROR
	ax01 = plt.subplot2grid((6,2), (0,1), rowspan=3)	#PARALEL
	ax11 = plt.subplot2grid((6,2), (3,1), rowspan=3)	#BEST

	##PLOTING OBJECTS
	paralelCoordPlot = ParalelCoordPlot(s_dataND, ax01, s_norm_data, s_fitness, scalar_map)

	sammonErrorPlot = SammonErrorPlot(sammon_error,ax10)
	sammon2DPlot = Sammon2DPlot(s_data2D, ax00, s_fitness, s_norm_fitness, cmap, paralelCoordPlot)

	bestFitnessPlot = BestFitnessPlot(fitness, ax11)	

	##animate
	frame = 0

	def update_all_plots(frame):

		#update all
		sammonErrorPlot.update(frame)
		sammon2DPlot.update(frame)
		bestFitnessPlot.update(frame)
		paralelCoordPlot.update(frame)

		#update figure canvas
		figure.canvas.draw()

	def update(event):
		global frame

		if event.key == 'left':

			if frame > 0:
				frame -=1
				update_all_plots(frame)
				
				
				
			else:
				print('Left limit')
		elif event.key == 'right':
			
			if frame < E:		
				frame += 1
				update_all_plots(frame)
			else:
				print('Right limit')

	def highlight(event):
		print('highlight')

		print("fitness",fitness[frame][event.ind])

		#Parallel Coord
		if event.mouseevent.inaxes is ax01:
			paralelCoordPlot.highlight(frame, event.ind)
			figure.canvas.draw()
		elif event.mouseevent.inaxes is ax00:
			sammon2DPlot.highlight(frame, event.ind)
			figure.canvas.draw()


	plt.tight_layout()
	ax11.figure.subplots_adjust(left=config.LEFT, right=config.RIGHT, top=config.TOP, bottom=config.BOTTOM, wspace=config.WSPACE, hspace=config.HSPACE)
	ax11.figure.canvas.mpl_connect('key_press_event',update)
	ax11.figure.canvas.mpl_connect('pick_event',highlight)

	plt.show()


