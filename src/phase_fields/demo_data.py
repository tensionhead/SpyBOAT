from skimage.io import imread
from os.path import expanduser
from glob import glob

# data_dir = expanduser('~/ownCloud/Shared/Luvelu_cell-ablation/')

# (local) data directory
data_dir = expanduser('~/PSM/data/phase_field_data/')

g = glob(data_dir + '*mask*phase*.tif')
print(g)
L6SO = imread(g[0])
RAFL1 = imread(g[1])
RAFL2 = imread(g[2])

# moving foci
RAFL1_crop1 = RAFL1[:,140:290,260:410]

