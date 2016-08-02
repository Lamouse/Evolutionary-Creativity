__author__ = 'Paulo Pereira'

import os
import numpy as np
import scipy.stats as st
import matplotlib.pyplot as plt

def check_inf(string):
	# bug no python 2.3
	if string == '1.#INF\n':
		result = 99999
	else:
		result = float(string)

	result = max(0, result)

	#result = min(20.0, result)

	return result


if __name__ == '__main__':

	count = 0
	results1 = []
	data1 = []
	data1_mean = []
	data1_sem = []
	data1_x = []
	name1 = ''

	results2 = []
	data2 = []
	data2_mean = []
	data2_sem = []
	data2_x = []
	name2 = ''

	results3 = []
	data3 = []
	data3_mean = []
	data3_sem = []
	data3_x = []
	name3 = ''

	# get data
	for root, dirs, files in os.walk('results'):
		for folder in dirs:
			
			if count < 3:

				for root1, dirs1, files1 in os.walk(os.path.join(root, folder)):

					results = []

					for file in files1:

						temp_results = []
						path = os.path.join(root1, file)

						f =  open(path, 'r')
						for line in f:
							temp_results.append(check_inf(line))
						f.close()

						results.append(temp_results)

					results = np.transpose(results)

					if count == 0:
						results1 = results
						name1 = folder
					elif count == 1:
						results2 = results
						name2 = folder
					else:
						results3 = results
						name3 = folder

			else:
				break

			count += 1

	if len(results1) == 0:
		print('Ops! Something went wrong with data1')
		exit()

	elif len(results2) == 0:
		print('Ops! Something went wrong with data2')
		exit()

	elif len(results3) == 0:
		print('Ops! Something went wrong with data3')
		exit()

	# process data
	p_value_list_equal = []
	p_value_list_1 = []
	p_value_list_2 = []

	ct = 0
	for i in range(len(results1)):
		result1 = results1[i]
		result2 = results2[i]
		result3 = results3[i]

		m1 = np.mean(result1)
		m2 = np.mean(result2)
		m3 = np.mean(result3)

		data1.append(m1)
		data2.append(m2)
		data3.append(m3)

		if i % 5 == 0:
			if ct == 0:
				data1_x.append(i)
				data1_mean.append(m1)
				data1_sem.append(st.sem(result1))
			elif ct == 1:
				data2_x.append(i)
				data2_mean.append(m2)
				data2_sem.append(st.sem(result2))
			else:
				data3_x.append(i)
				data3_mean.append(m3)
				data3_sem.append(st.sem(result3))
			ct = (ct + 1) % 3


	# get statistics
	fig, ax = plt.subplots()
	ax.plot(data1, color='b', label=name1)
	ax.plot(data2, color='g', label=name2)
	ax.plot(data3, color='r', label=name3)

	#legend = ax.legend(loc='upper right')
	legend = ax.legend(loc='lower left')

	plt.errorbar(data1_x, data1_mean, yerr=data1_sem, fmt='bo', markersize=1)
	plt.errorbar(data2_x, data2_mean, yerr=data2_sem, fmt='go', markersize=1)
	plt.errorbar(data3_x, data3_mean, yerr=data3_sem, fmt='ro', markersize=1)


	#plt.ylabel('fitness')
	plt.ylabel('number of deaths')
	#plt.ylabel('diversity')
	#plt.ylabel('brightness')
	#plt.ylabel('size')

	plt.xlabel('number of generations')
	plt.savefig('data.png', bbox_inches='tight')
	plt.close()