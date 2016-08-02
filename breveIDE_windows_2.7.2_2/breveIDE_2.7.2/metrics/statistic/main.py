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

	# get data
	for root, dirs, files in os.walk('results'):
		for folder in dirs:
			
			if count < 2:

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
					else:
						results2 = results
						name2 = folder

			else:
				break

			count += 1

	if len(results1) == 0:
		print('Ops! Something went wrong with data1')
		exit()

	elif len(results2) == 0:
		print('Ops! Something went wrong with data2')
		exit()

	# process data
	p_value_list_equal = []
	p_value_list_1 = []
	p_value_list_2 = []
	for i in range(len(results1)):
		result1 = results1[i]
		result2 = results2[i]

		m1 = np.mean(result1)
		m2 = np.mean(result2)

		data1.append(m1)
		data2.append(m2)

		if i % 10 == 0:
			data1_x.append(i)
			data1_mean.append(m1)
			data1_sem.append(st.sem(result1))

		elif i % 5 == 0:
			data2_x.append(i)
			data2_mean.append(m2)
			data2_sem.append(st.sem(result2))

		if i > 10:
			# warm up
			p_value_list_equal.append(st.mannwhitneyu(result1, result2)[1])
			p_value_list_1.append(st.mannwhitneyu(result1, result2, alternative='less')[1])
			p_value_list_2.append(st.mannwhitneyu(result1, result2, alternative='greater')[1])

	# get statistics
	fig, ax = plt.subplots()
	ax.plot(data1, color='b', label=name1)
	ax.plot(data2, color='g', label=name2)

	#legend = ax.legend(loc='upper right')
	legend = ax.legend(loc='lower left')

	plt.errorbar(data1_x, data1_mean, yerr=data1_sem, fmt='bo', markersize=1)
	plt.errorbar(data2_x, data2_mean, yerr=data2_sem, fmt='go', markersize=1)

	plt.ylabel('fitness')
	#plt.ylabel('number of deaths')
	#plt.ylabel('diversity')
	#plt.ylabel('brightness')
	#plt.ylabel('size')

	plt.xlabel('number of generations')
	plt.savefig('data.png', bbox_inches='tight')
	plt.close()

	p_value = np.mean(p_value_list_equal)
	print('\np value:\n\t' + str(p_value) + '\n\n')

	if p_value >= 0.05:
		# two tailed
		print('With a confidence level of 95, there are not a difference between those results\n')

	else:
		print('With a confidence level of 95, those results are different\n')

		# one tailed

		p_value = np.mean(p_value_list_1)
		if p_value >= 0.025:
			print('\np value:\n\t' + str(p_value) + '\n\n')
			print('With a confidence level of 95, the result 1 (' + name1 + ') is higher than the other (' + name2 + ')')
		else:
			p_value = np.mean(p_value_list_2)
			if p_value >= 0.025:
				print('\np value:\n\t' + str(p_value) + '\n\n')
				print('With a confidence level of 95, the result 2 (' + name2 + ') is higher than the other (' + name1 + ')')
		