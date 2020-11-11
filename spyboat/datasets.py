""" Provides the test data stacks of the repository """

import os
from skimage import io
from .util import open_tif

# go to test_data directory
data_dir = os.path.join(os.path.dirname(__file__),'..','test_data')

SCN_L20_Evans = io.imread( os.path.join(data_dir, 'SCN_L20_Evans.tif') )

# check the convenience function spyboat.open_tif() 
# Hyperstack with 2 Channels, [time, Channels, Y, X] ordering
multichan2 = open_tif( os.path.join(data_dir, 'multichan2.tif'), channel = 1)

# Hyperstack with 3 Channels, [time, Y, X, Channels] ordering
multichan3 = open_tif( os.path.join(data_dir, 'multichan3.tif'), channel = 3)



