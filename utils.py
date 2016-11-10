import json
import numpy as np
import ipdb
import datetime

def normalizeEvolutiveData(data, fitness,dimensions_boundaries=None, fitness_boundaries=None, verbose=False, eachepoch=None):

	"""
	Normalize all values based in each dimension values

	Parametters:

	- data:
	Numpy array with individuals values in each epoch in the shape (E, I, D), where E = number of epochs, I = number of individuals, D = number of dimensions

	- fitness:
	Numpy array with all the fitness of each individual in each epoch, with shape (E,I) [letters same meaning in the last item described here]

	- dimensions_boundaries:

	Default is none, so the values considered as min and max for each dimension are the values in data and fitness, if is given, should have the following format: [{'min': <VALUE>, 'max': <VALUE>}, ...], one dict like these for each dimension

	- fitness_boundaries:

	Same idea that the last parameter, but is only one dict in the form {'min': <VALUE>, 'max': <VALUE>}
	""" 

	E = data.shape[0]
	I = data.shape[1]
	D = data.shape[2]

	data_norm = np.zeros(data.shape)
	fitness_norm = np.zeros(fitness.shape)

	#Normalize fitnesss
	if fitness_boundaries is None:
		minFitness = fitness.min()
		maxFitness = fitness.max()
	else:
		minFitness = fitness_boundaries['min']
		maxFitness = fitness_boundaries['max']

	fitness_norm = (fitness- minFitness)/(maxFitness-minFitness)

	#normalize data
	for e in range(E):

		if eachepoch is not None:
			eachepoch(e)

		if verbose:
			print('Normalizing:',e,'of',E,'->',((e+1)/E)*100,'%')

		for d in range(D):

			if dimensions_boundaries is None:
				minInD = data[:,:,d].min()
				maxInD = data[:,:,d].max()
			else:
				minInD = dimensions_boundaries[d]['min']
				maxInD = dimensions_boundaries[d]['max']

			data_norm[:,:,d] = (data[:,:,d]-minInD)/(maxInD-minInD)

	return data_norm, fitness_norm

def readlog(filename, withheader=False):

	with open(filename,'r', encoding='utf-8') as dotswarm:
		json_str = dotswarm.read()
		swarm_json = json.loads(json_str)

	data = np.array(swarm_json['data'])
	fitness = np.array(swarm_json['fitness'])
	try:
		header = swarm_json['header']
	except e:
		header = None

	return data,fitness, header
 

def deaplog2numpy(log):
	data = []
	fitness = []

	epoch = 0
	epoch_individuals = []
	epoch_fitness = []

	for record in log:

		if epoch != record['gen']:
			data.append(epoch_individuals)
			fitness.append(epoch_fitness)
			epoch_individuals = []
			epoch_fitness = []
			epoch = record['gen']
		
		epoch_individuals.append(record['individual'])
		epoch_fitness.append(record['fitness'])

	return np.array(data), np.array(fitness)

def savelog(data, fitness, header, path, fileprefix):

	#generete a timestap string
	timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S").replace(' ','-').replace(':','')

	filename = fileprefix+timestamp

	dict_file = {'data':data.tolist(), 'fitness':fitness.tolist(), 'header': header}

	json_file = json.dumps(dict_file)

	with open(path+'/'+filename,'w',encoding='utf-8') as logfile:
		logfile.write(json_file)