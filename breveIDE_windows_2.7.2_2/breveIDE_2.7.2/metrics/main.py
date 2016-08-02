__author__ = 'Paulo Pereira'

import os
import numpy as np
import matplotlib.pyplot as plt

def check_inf(string, folder):
		# bug no python 2.3
		if string == '1.#INF\n':
			result = 99999
		else:
			result = float(string)

		result = max(0, result)
		if 'tail' in folder:
			result = min(20.0, result)

		return result

if __name__ == '__main__':

	for root, dirs, files in os.walk('results'):
		for folder in dirs:
			for root1, dirs1, files1 in os.walk(os.path.join(root, folder)):
				results = []

				print(folder)

				for file in files1:

					temp_results = []
					path = os.path.join(root1, file)

					f =  open(path, 'r')
					for line in f:
						temp_results.append(check_inf(line, folder))
					f.close()

					results.append(temp_results)

				results = np.transpose(results)

				final_results = []
				for result in results:
					final_results.append(np.mean(result))

				plt.plot(final_results)
				plt.ylabel('fitness')
				plt.xlabel('number of generation')
				plt.title(folder)
				plt.savefig(os.path.join('graphics', folder)+'.png', bbox_inches='tight')
				plt.close()