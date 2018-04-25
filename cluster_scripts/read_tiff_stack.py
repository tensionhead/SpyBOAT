import sys,os
import matplotlib
# matplotlib.use('Agg') # for headless usage

from skimage import io

# base_dir = '/g/aulehla/vLab/WaveletMovieBatch/'
base_dir = './'
movie_path = os.path.join(base_dir, 'twosmall_hom_sines', 'Roi_Movie_0_0_2_2.tif' )
