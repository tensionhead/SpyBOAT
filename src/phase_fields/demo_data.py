from skimage.io import imread
from os.path import expanduser
from glob import glob

# data_dir = expanduser('~/ownCloud/Shared/Luvelu_cell-ablation/')

# (local) data directory
data_dir = expanduser('~/PSM/data/phase_field_data/')

g = glob(data_dir + '*phase*.tif')
print(g)
L6SO = imread(g[0])
RAFL1 = imread(g[1])
RAFL2 = imread(g[2])


# moving foci
RAFL1_crop1 = RAFL1[:,120:290,260:410]
L6SO_crop1 = L6SO[:,118:395,154:405]

data_dir2 = expanduser('~/Desktop/GoodPhaseMovies/FGF_bead_Take/')
g = glob(data_dir2 + '*phase*.tif')
print(g)
# FGF_SO1 = imread(g[0])
# FGF_SO2  = imread(g[1])

data_dir3 = expanduser('~/Desktop/GoodPhaseMovies/')
g = glob(data_dir3 + '*phase*.tif')
print(g)
RAFL1a = imread(g[0])
SO_W0004  = imread(g[1])
SO_L6 = imread(g[2])

# data_dir4 = '/home/whir/ownCloud/Shared/Luvelu_cell-ablation/20190412_Luvelu-mTmG/'
# g = glob(data_dir4 + '*phase*L2*.tif')
# print(g)

# L2_pre = imread( g[0] )
# L2_post = imread( g[1] )
