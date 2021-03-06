from sammon.sammon import sammon
import numpy as np

"""Perform Sammon mapping on dataset x iteratively, using the last sammon mapping reduction as the initialization of the next

	Description : Using a simple python implementation of Sammon's non-linear
				  mapping algorithm [1] for plot an animated chart of individuals in swarm algorithms

	Sammon mapping base implementation from: https://github.com/tompollard/sammon

	Copyright   : (c) Adailson Filho de Castro Queiroz Filho, Cin/UFPE, Recife/PE, BR, 2016

	This program is free software; you can redistribute it and/or modify
	it under the terms of the GNU General Public License as published by
	the Free Software Foundation; either version 2 of the License, or
	(at your option) any later version.

	This program is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.

	You should have received a copy of the GNU General Public License
	along with this program; if not, write to the Free Software
	Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

	"""

def cascadesammon(data, framelapse = 1, init='pca', verbose = True, distancefunc = None, eachepoch = None, maxiter=500):
	
	"""
	Args description:

	- data = numpy array in the format [Epochs][Individuals][Dimension]
	- framelapse = integer, a stepsize for not necessarialy use all epoch data, last epoch is always included
	- init = is the option of initialization of first sammons mapping operation, can be 'pca' (principal component analysis) or 'random'
	- verbose = flag for prompt the process details
	- distancefunc = is a funcation that should receive two args 'distancefunc(a,b)' where a and b are the same numpy array of an epoch, and must return a distance matrix, if none is give euclidian distance will be used
	"""

	assert type(data) == type(np.array([]))

	if data.shape[2] > 2:

		# #Assert there is no duplicated data
		# for e in data.shape[0]:
		# 	for ind in data[e]
		# 		assert (data[e] == ind).sum() == data.shape[2]
		
		reduced = np.array([])
		outputData = []
		errorData = []
		
		i = 0

		while i < len(data):

			epoch = data[i]

			if data.shape[2] > 2:
				if verbose:
					print('Sammon procedure - Log Epoch:',i,'of',(len(data)-1))
			
				if len(reduced) == 0 :
					[reduced, errors] = sammon(epoch,display=0,init=init, distancefunc=distancefunc, maxiter=maxiter)
				else:
					[reduced, errors] = sammon(epoch,display=0,init=reduced, distancefunc=distancefunc, maxiter=maxiter)
			else:
				reduced = epoch
				errors = 0

			outputData.append(reduced)
			errorData.append(errors)

			if verbose:
				print('Real Epoch caught:',i)

			if eachepoch is not None:
				eachepoch(i)

			i += framelapse

		if (data.shape[0]-1) % framelapse != 0:
			epoch = data[-1]

			if data.shape[2] > 2:
				[reduced, errors] = sammon(epoch,display=0,init=reduced, maxiter=maxiter)
				outputData.append(reduced)
				errorData.append(errors)
			else:
				outputData.append(epoch)
				errorData.append(0)

			if verbose:
				print('LAST - Real Epoch caught:',len(data)-1)

			if eachepoch is not None:
				eachepoch(len(data)-1)
				
		return [np.array(outputData), np.array(errorData)]
	else:
		return [data, np.zeros(data.shape[0])]