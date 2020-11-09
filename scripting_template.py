import spyboat
import matplotlib.pylab as ppl
import os

movie = spyboat.open_tif('test_data/SCN_L16_Evans.tif') 

# down sample to 80% of original size
ds_movie = spyboat.down_sample(movie, 0.8)

# gaussian blur

input_movie = spyboat.gaussian_blur(ds_movie, sigma = 3.5)

# analysis parameters
wkwargs = {'dt' : 0.5, # sampling interval
           'Tmin' : 20, # lowest period to scan
           'Tmax' : 28, # highest period to scan          
           'nT' : 200,   # number of periods/transforms
           'T_c' : 40,  # sinc cut off period
           'L' : None}   # Ampltidue normalization sliding window size

# results is a dictionary with keys:
# 'phase', 'period','power' and 'amplitude'
results = spyboat.run_parallel(input_movie, n_cpu = 8, **wkwargs)

frame = 25

# look at a phase snapshot
ppl.figure()
ppl.imshow(results['phase'][frame,...], aspect = 'auto', cmap = 'bwr')

# look at a period snapshot
ppl.figure()
ppl.imshow(results['period'][frame,...], aspect = 'auto', cmap = 'magma_r')
ppl.colorbar()

# input movie snapshot
ppl.figure()
ppl.imshow(input_movie[frame,...], aspect = 'auto', cmap = 'gray')

# save out results to current working directory
spyboat.save_to_tifs(results, 'L16', directory = os.getcwd())
