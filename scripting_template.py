import spyboat
import matplotlib.pylab as ppl
import os

movie = spyboat.open_tif('test_data/LuVeLu_Tail_L6.tif') 

# down sample by 50%
ds_movie = spyboat.down_sample(movie, 0.5)

# analysis parameters
wkwargs = {'dt' : 10, # sampling interval
           'Tmin' : 110, # lowest period to scan
           'Tmax' : 170, # highest period to scan          
           'nT' : 200,   # number of periods/transforms
           'T_c' : 160,  # sinc cut off period
           'L' : None}   # Ampltidue normalization sliding window size

# results is a dictionary with keys:
# 'phase', 'period','power' and 'amplitude'
results = spyboat.run_parallel(ds_movie, n_cpu = 8, **wkwargs)

frame = 20

# look at a phase snapshot
ppl.figure()
ppl.imshow(results['phase'][frame,...], aspect = 'auto', cmap = 'bwr')

# look at a period snapshot
ppl.figure()
ppl.imshow(results['period'][frame,...], aspect = 'auto', cmap = 'magma_r')
ppl.colorbar()

# save out results to current working directory
spyboat.save_to_tifs(results, 'L6', directory = os.getcwd())
