""" Provides the test data stacks of the repository """

import os
from skimage import io

# go to test_data directory
data_dir = os.path.join(os.path.dirname(__file__),'test_data')

# SCN_Evans2013 = io.imread( os.path.join(data_dir, 'SCN_L20_Evans2013.tif') )

# Teststack [time, Y, X] ordering,
# two rectanguar sinusoidal oscillatory domains, 
two_sines = io.imread( os.path.join(data_dir, 'two_sines.tif'))



