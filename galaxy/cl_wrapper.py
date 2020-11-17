#!/usr/bin/env python

## Gets interfaced by Galaxy or bash scripting
import argparse
import sys, os
import logging

import spyboat

from skimage import io
from numpy import float32

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('wrapper')

# ----------command line parameters ---------------

parser = argparse.ArgumentParser(description='Process some arguments.')

# I/O
parser.add_argument('--input_path', help="Input movie location", required=True)
parser.add_argument('--phase_out', help='Phase output file name', required=True)
parser.add_argument('--period_out', help='Period output file name', required=True)
parser.add_argument('--power_out', help='Power output file name', required=True)
parser.add_argument('--amplitude_out', help='Amplitude output file name', required=True)
parser.add_argument('--save_input', help='Set to true to save out the pre-processed input movie', type=bool, default=False, required=False)


# (Optional) Multiprocessing

parser.add_argument('--ncpu', help='Number of processors to use',
                    required=False, type=int, default=1)

# Optional spatial downsampling
parser.add_argument('--rescale', help='Rescale the image by a factor given in %%, 100 means no rescaling', required=False, default = -1, type=int)
# Optional Gaussian smoothing
parser.add_argument('--gauss_sigma', help='Gaussian smoothing parameter, 0 means no smoothing', required=False, default=-1, type=float)

# Wavelet Analysis Parameters
parser.add_argument('--dt', help='Sampling interval', required=True, type=float)
parser.add_argument('--Tmin', help='Smallest period', required=True, type=float)
parser.add_argument('--Tmax', help='Biggest period', required=True, type=float)
parser.add_argument('--nT', help='Number of periods to scan for', required=True, type=int)

parser.add_argument('--Tcutoff', help='Sinc cut-off period, -1 means no detrending', required=False, type=float, default=-1)
parser.add_argument('--win_size', help='Sliding window size for amplitude normalization, -1 means no normalization', required=False, type=float)

# Optional fixed masking
parser.add_argument('--mask_frame', help='The frame of the input movie to create a mask from, -1 means no masking of the output', required=False, type=int,
                    default=-1)

parser.add_argument('--mask_thresh', help='The threshold of the mask, all pixels with less than this value get masked', required=False, type=int,
                    default=0)

parser.add_argument('--version', action='version', version='0.0.1')

arguments = parser.parse_args()


# ------------Read the input----------------------------------------
try:
    movie = spyboat.open_tif(arguments.input_path)
except FileNotFoundError:
    logger.critical("Couldn't open {}, check movie storage directory!".format(arguments.input_path))

    sys.exit(1)


# -------- Do (optional) spatial downsampling ---------------------------    

scale_factor = arguments.rescale 

if scale_factor == -1:
    logger.info('No downsampling requested..')

elif 0 < scale_factor < 100:
    logger.info(f'Downsampling the movie to {scale_factor:d}% of its original size..')
    movie = spyboat.down_sample(movie, scale_factor / 100)
else:
    raise ValueError('Scale factor must be between 0 and 100!')
        
# -------- Do (optional) pre-smoothing -------------------------
# note that downsampling already is a smoothing operation..

# check if pre-smoothing requested, a (non-sensical) value of 0 means no pre-smoothing
if arguments.gauss_sigma == -1:
    logger.info('No pre-smoothing requested')
else:
    logger.info(f'Pre-smoothing the movie with Gaussians, sigma = {arguments.gauss_sigma:.2f}..')

    movie = spyboat.gaussian_blur(movie, arguments.gauss_sigma)    
    


# ----- Set up Masking before processing ----

mask = None
if arguments.mask_frame != -1:
    logger.info(f'Creating mask from frame {arguments.mask_frame}')
    
    if (arguments.mask_frame > movie.shape[0]) or (arguments.mask_frame < 0):
        logger.critical(f'Requested frame does not exist, input only has \
        {movie.shape[0]} frames.. exiting', file = sys.stderr)
        sys.exit(0)

    else:
        mask = spyboat.create_fixed_mask(movie, arguments.mask_frame,
                                  arguments.mask_thresh)
else:
    logger.info('No masking requested..')
    

# ------ Retrieve  wavelet parameters ---------------------------

Wkwargs = {'dt' : arguments.dt,
           'Tmin' : arguments.Tmin,
           'Tmax' : arguments.Tmax,
           'nT' : arguments.nT}

# the switches
if arguments.Tcutoff == -1:
    Wkwargs['T_c'] = None
else:
    Wkwargs['T_c'] = arguments.Tcutoff

if arguments.win_size == -1:
    Wkwargs['win_size'] = None
else:
    Wkwargs['win_size'] = arguments.win_size

# start parallel processing
results = spyboat.run_parallel(movie, arguments.ncpu, **Wkwargs)

# --- masking? ---

if mask is not None:
    # mask all output movies (in place!)
    for key in results:
        logger.info(f'Masking {key}')
        spyboat.apply_mask(results[key], mask, fill_value = -1)

# save phase movie
io.imsave(arguments.phase_out, results['phase'], plugin="tifffile")
logger.info(f'Written {arguments.phase_out}')
# save period movie
io.imsave(arguments.period_out, results['period'], plugin="tifffile")
logger.info(f'Written {arguments.period_out}')
# save power movie
io.imsave(arguments.power_out, results['power'], plugin="tifffile")
logger.info(f'Written {arguments.power_out}')
# save amplitude movie
io.imsave(arguments.amplitude_out, results['amplitude'], plugin="tifffile")
logger.info(f'Written {arguments.amplitude_out}')

# save out the probably pre-processed (scaled and blurred) input movie for
# direct comparison to results and coordinate mapping etc.
# probably won't work with galaxy
if arguments.save_input:
    input_name = os.path.basename(arguments.input_path)
    input_name = input_name.split('.')[-2]
    dirname = os.path.dirname(arguments.input_path)
    out_path = os.path.join(dirname, input_name + '_preproc.tif')
    io.imsave(out_path, movie.astype(float32))
    logger.info(f'Written {out_path}')
    



