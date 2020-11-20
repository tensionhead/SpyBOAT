import matplotlib.pylab as ppl
from skimage import io
import os

import spyboat
import spyboat.plotting as spyplot
from spyboat import datasets

LogLevel = 'INFO' # set to 'WARNING' to turn off info event logging
spyboat.util.logger.setLevel(LogLevel)
spyboat.processing.logger.setLevel(LogLevel)

## included test data
## note the stack ordering is [time, Y, X]

# test_movie = datasets.SCN_Evans2013
# dt = 0.5 # sampling interval, it's half an hour here

## uncomment to analyze very small synthetic movie
test_movie = datasets.two_sines
dt = 2 # sampling interval, it's 2 hours for two_sines

## top open a local file just use skimage's io:
# io.imread('/path/to/my_awesome_movie.tif')

## analysis parameters
Wkwargs = {'dt' : dt, # sampling interval
           'Tmin' : 20, # lowest period to scan, in hours
           'Tmax' : 30, # highest period to scan, in hours          
           'nT' : 200,   # number of periods/transforms
           'T_c' : 40,  # sinc cut off period, in hours, None disables detrending
           'win_size' : None}   # Ampl. normalization sliding window size, None disables

# down sample to 80% of original size
ds_movie = spyboat.down_sample(test_movie, 0.8)

# gaussian blur
input_movie = spyboat.gaussian_blur(ds_movie, sigma = 2.5)

# create a fixed mask from frame 20
mask2d = spyboat.create_fixed_mask(input_movie, frame = 20, threshold = 10)
# create a dynamic mask 
mask3d = spyboat.create_dynamic_mask(input_movie, threshold = 10)


# how many jobs
n_cpu = 10

# results is a dictionary with keys:
# 'phase', 'period','power' and 'amplitude'
results = spyboat.run_parallel(input_movie, n_cpu, **Wkwargs)

# mask all output movies (in place!)
for key in results:
    print(f'Masking {key}')
    spyboat.apply_mask(results[key], mask3d, fill_value = -1)

# snapshots at frame..
frame = 54

# look at a phase snapshot
spyplot.phase_snapshot(results['phase'][frame])

# look at a period snapshot
spyplot.period_snapshot(results['period'][frame],
                                 Tmin = Wkwargs['Tmin'],
                                 Tmax = Wkwargs['Tmax'],
                                 time_unit = 'h')

# look at an amplitude snapshot
spyplot.amplitude_snapshot(results['amplitude'][frame,...])

# finally plot also the input for that frame
spyplot.input_snapshot(input_movie[frame])

base_name = 'example_movie'

# save out results to current working directory
spyboat.save_to_tifs(results, base_name, directory = os.getcwd())

# save out the scaled and blurred input movie for
# direct comparison to results and coordinate mapping etc.
out_path = os.path.join(os.getcwd(),f'{base_name}_preproc.tif')
io.imsave(out_path, input_movie)
