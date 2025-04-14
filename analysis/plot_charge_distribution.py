import sys,os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import scipy as sp

def main():
	pwd = os.getcwd()+'/'
	
	charges1 = pd.read_csv(sys.argv[1])
	charges1.columns = ['name', 'charge', 'energy']
	charges1.set_index(['name'])

#	charges2 = pd.read_csv(sys.argv[2] )
#       charges2.columns = ['name', 'charge', 'energy']
#       charges2.set_index(['name'])

#	charges3 = pd.read_csv(sys.argv[3] )
#       charges3.columns = ['name', 'charge', 'energy']
#       charges3.set_index(['name'])

	#print(charges)
	#charges.info()
	#charges.describe()

	
	fig = plt.figure()
	fig.suptitle('Charge Distribution', fontsize=14, fontweight='bold')
	
	plt.xlabel('Charge')
	plt.ylabel('Energy in DOCK units')
	
	x1 =charges1.T.loc['charge']
	y1 =charges1.T.loc['energy']

#	x2 =charges2.T.loc['charge']
#        y2 =charges2.T.loc['energy']


#	x3 =charges3.T.loc['charge']
#        y3 =charges3.T.loc['energy']

	plt.plot(x1,y1, 'x', color = 'blue', label ='Standard')
#	plt.plot(x2,y2, 'x', color = 'red', label ='Thin-Spheres')
#	plt.plot(x3,y3, 'x', color = 'green', label ='Thin-Spheres w/ ms90')
	plt.xlim(-3.5,3.5)
	plt.legend(loc = 'lower left', fancybox = True, shadow = True)
	#plt.show()
	filename = 'charge_distributions_vs_energy.png'
	plt.savefig(filename, dpi = 600)

main()
