__author__ = 'Paulo Pereira'

import os
import matplotlib.pyplot as plt

if __name__ == '__main__':

	for root, dirs, files in os.walk('results'):
	    for file in files:
	    	results = []
	    	path = os.path.join(root, file)
	    	name = os.path.splitext(file)[0]

	    	f =  open(path, 'r')
	    	for line in f:
	    		results.append(float(line))
	    	f.close()

	    	plt.plot(results)
	    	plt.ylabel('fitness')
	    	plt.xlabel('number of generation')
	    	plt.title(name)
    		plt.savefig(os.path.join('graphics', name)+'.png', bbox_inches='tight')
    		plt.close()
