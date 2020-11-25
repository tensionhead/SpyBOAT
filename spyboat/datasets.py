""" Provides the test data stacks of the repository """

import os
from skimage import io

# go to test_data directory
data_dir = os.path.join(os.path.dirname(__file__),'test_data')

# two rectanguar sinusoidal oscillatory domains with slightly
# different periods
two_sines = io.imread( os.path.join(data_dir, 'two_sines.tif'))

# SCN Bmal1 recording from Jhiwan, subsampled in time and space
SCN_Bmal1 = io.imread( os.path.join(data_dir, 'BmalLD-ssds.tif'))


