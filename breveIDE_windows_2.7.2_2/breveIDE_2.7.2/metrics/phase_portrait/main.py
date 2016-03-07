__author__ = 'Paulo Pereira'

import os
import matplotlib.pyplot as plt

if __name__ == '__main__':

	for root, dirs, files in os.walk('results'):
	    for file in files:
	    	x = []
	    	y = []
	    	
	    	path = os.path.join(root, file)
	    	name = os.path.splitext(file)[0]

	    	f =  open(path, 'r')
	    	for line in f:
	    		array = line.split()
	    		x.append(float(array[0]))
	    		y.append(float(array[1]))
	    	f.close()

	    	plt.plot(x, y, 'ro')
	    	plt.ylabel('number of predators')
	    	plt.xlabel('number of preys')
	    	plt.title(name)
    		plt.savefig(os.path.join('graphics', name)+'.png', bbox_inches='tight')
    		plt.close()
