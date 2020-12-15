import matplotlib.pylab as ppl
from skimage import io
import os

import spyboat
import spyboat.plotting as spyplot
from spyboat import datasets

LogLevel = 'INFO' # set to 'WARNING' to turn off info event logging
spyboat.util.logger.setLevel(LogLevel)
spyboat.processing.logger.setLevel(LogLevel)

## two sinusoids with slightly
## different period on rectangular domains
## note the stack ordering is [time, Y, X]
# movie = datasets.two_sines
# dt = 2 # it's 2 hours for two_sines

## SCN Bmal1 recording from Jihwan..
movie = datasets.SCN_Bmal1
dt = 1 # 1h sampling

## top open a local file just use skimage's io:
# io.imread('/path/to/my_awesome_movie.tif')

## analysis parameters
Wkwargs = {'dt' : dt, # sampling interval
           'Tmin' : 20, # lowest period to scan, in hours
           'Tmax' : 28, # highest period to scan, in hours          
           'nT' : 200,  # number of periods/transforms
           'T_c' : 40, # sinc cut off period, in hours, None disables detrending
           'win_size' : 34} # Ampl. normalization sliding window size, None disables

# down sample to 80% of original size
input_movie = spyboat.down_sample(movie, 0.8)

# gaussian blur
input_movie = spyboat.gaussian_blur(input_movie, sigma = 1.5)

# create a static mask from frame 47
mask2d = spyboat.create_static_mask(input_movie, frame = 47, threshold = 320)

# create a dynamic mask, different for each frame but fixed threshold
mask3d = spyboat.create_dynamic_mask(input_movie, threshold = 10)

# how many jobs
n_cpu = 10

# results is a dictionary with keys:
# 'phase', 'period','power' and 'amplitude'
results = spyboat.run_parallel(input_movie, n_cpu, **Wkwargs)

# mask all output movies (in place!)
for key in results:
    print(f'Masking {key}')
    spyboat.apply_mask(results[key], mask2d, fill_value = -1)

# snapshots at frame..
frame = 23

# look at a phase snapshot
spyplot.phase_snapshot(results['phase'][frame])

# look at a period snapshot
spyplot.period_snapshot(results['period'][frame],
                        Wkwargs['Tmin'], Wkwargs['Tmax'],
                        time_unit = 'h')

# look at an amplitude snapshot
spyplot.amplitude_snapshot(results['amplitude'][frame,...])

# finally plot also the input for that frame
spyplot.input_snapshot(input_movie[frame])

# distributions over time
spyplot.period_distr_dynamics(results['period'], Wkwargs)
spyplot.power_distr_dynamics(results['power'], Wkwargs)
spyplot.phase_coherence_dynamics(results['phase'], Wkwargs)

base_name = 'SCN_Bmal1'

# save out results to current working directory
spyboat.save_results_to_tifs(results, base_name, directory = '.')

# save out the scaled and blurred input movie for
# direct comparison to results and coordinate mapping etc.
out_path = os.path.join(os.getcwd(),f'{base_name}_preproc.tif')
io.imsave(out_path, input_movie)
