import matplotlib.pylab as ppl
from skimage import io
import os

import spyboat
from spyboat import datasets


# included test data,
# note the stack ordering is [time, Y, X]
test_movie = datasets.SCN_L20_Evans

# down sample to 80% of original size
ds_movie = spyboat.down_sample(test_movie, 0.8)

# gaussian blur
input_movie = spyboat.gaussian_blur(ds_movie, sigma = 2.5)

# create a mask from frame 20
mask = spyboat.create_fixed_mask(input_movie, frame = 20, threshold = 10)

# analysis parameters
wkwargs = {'dt' : 0.5, # sampling interval, it's half an hour here
           'Tmin' : 20, # lowest period to scan, in hours
           'Tmax' : 28, # highest period to scan, in hours          
           'nT' : 200,   # number of periods/transforms
           'T_c' : 40,  # sinc cut off period, in hours
           'L' : None}   # Ampltidue normalization sliding window size

# how many jobs
n_cpu = 10

# results is a dictionary with keys:
# 'phase', 'period','power' and 'amplitude'
results = spyboat.run_parallel(input_movie, n_cpu, **wkwargs)

# mask all output movies
for key in results:
    print(f'Masking {key}')
    spyboat.apply_mask(results[key], mask, fill_value = 0)

frame = 30

# look at a phase snapshot
ppl.figure()
ppl.imshow(results['phase'][frame,...],
           aspect = 'auto', cmap = 'bwr', vmin = -3.14, vmax = 3.14)

# look at a period snapshot
ppl.figure()
ppl.imshow(results['period'][frame,...],
           aspect = 'auto', cmap = 'magma_r', vmin = 20, vmax = 28)
cb = ppl.colorbar()

# input movie snapshot
ppl.figure()
ppl.imshow(input_movie[frame,...], aspect = 'auto', cmap = 'gray')

base_name = 'SCN_L20_Evans'

# save out results to current working directory
spyboat.save_to_tifs(results, base_name, directory = os.getcwd())

# save out the scaled and blurred input movie for
# direct comparison to results and coordinate mapping etc.
io.imsave(f'orig_{base_name}.tif', input_movie)
