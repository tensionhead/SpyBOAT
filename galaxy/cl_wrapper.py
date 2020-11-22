#!/usr/bin/env python

## Gets interfaced by Galaxy or bash scripting
import argparse
import sys, os
import logging

from skimage import io
from numpy import float32

import spyboat
import output_report

logging.basicConfig(level=logging.INFO, stream=sys.stdout, force=True)
logger = logging.getLogger('wrapper')

# ----------command line parameters ---------------

parser = argparse.ArgumentParser(description='Process some arguments.')

# I/O
parser.add_argument('--input_path', help="Input movie location", required=True)
parser.add_argument('--phase_out', help='Phase output file name', required=True)
parser.add_argument('--period_out', help='Period output file name', required=True)
parser.add_argument('--power_out', help='Power output file name', required=True)
parser.add_argument('--amplitude_out', help='Amplitude output file name', required=True)
parser.add_argument('--preprocessed_out', help="Preprocessed-input output file name, 'None'", required=False)


# (Optional) Multiprocessing

parser.add_argument('--ncpu', help='Number of processors to use',
                    required=False, type=int, default=1)

# Optional spatial downsampling
parser.add_argument('--rescale', help='Rescale the image by a factor given in %%, None means no rescaling',
                    required=False, type=int)
# Optional Gaussian smoothing
parser.add_argument('--gauss_sigma', help='Gaussian smoothing parameter, None means no smoothing', required=False, type=float)

# Wavelet Analysis Parameters
parser.add_argument('--dt', help='Sampling interval', required=True, type=float)
parser.add_argument('--Tmin', help='Smallest period', required=True, type=float)
parser.add_argument('--Tmax', help='Biggest period', required=True, type=float)
parser.add_argument('--nT', help='Number of periods to scan for', required=True, type=int)

parser.add_argument('--Tcutoff', help='Sinc cut-off period, disables detrending if not set', required=False, type=float)
parser.add_argument('--win_size', help='Sliding window size for amplitude normalization, None means no normalization',
                    required=False, type=float)

# Optional masking
parser.add_argument('--masking', help="Set to either 'dynamic', 'fixed' or 'None' which is the default", default='None', required=False, type=str)

parser.add_argument('--mask_frame',
                    help="The frame of the input movie to create a fixed mask from, needs masking set to 'fixed'",
                    required=False, type=int)


parser.add_argument('--mask_thresh', help='The threshold of the mask, all pixels with less than this value get masked (if masking enabled).',
                    required=False, type=float,
                    default=0)

# output overview/snapshots
parser.add_argument('--output-report', help="Set to 'True' to generate an analysis report with snapshots of the output movies", default=False, required=False, type=bool)

parser.add_argument('--version', action='version', version='0.0.1')

arguments = parser.parse_args()

logger.info("Received following arguments:")
for arg in vars(arguments):
    logger.info(f'{arg} -> {getattr(arguments, arg)}')

# ------------Read the input----------------------------------------
try:
    movie = spyboat.open_tif(arguments.input_path)
except FileNotFoundError:
    logger.critical(f"Couldn't open {arguments.input_path}, check movie storage directory!")

    sys.exit(1)

# -------- Do (optional) spatial downsampling ---------------------------

scale_factor = arguments.rescale

# defaults to None
if not scale_factor:
    logger.info('No downsampling requested..')

elif 0 < scale_factor < 100:
    logger.info(f'Downsampling the movie to {scale_factor:d}% of its original size..')
    movie = spyboat.down_sample(movie, scale_factor / 100)
else:
    raise ValueError('Scale factor must be between 0 and 100!')

# -------- Do (optional) pre-smoothing -------------------------
# note that downsampling already is a smoothing operation..

# check if pre-smoothing requested
if not arguments.gauss_sigma:
    logger.info('No pre-smoothing requested..')
else:
    logger.info(f'Pre-smoothing the movie with Gaussians, sigma = {arguments.gauss_sigma:.2f}..')

    movie = spyboat.gaussian_blur(movie, arguments.gauss_sigma)

# ----- Set up Masking before processing ----

mask = None
if arguments.masking == 'fixed':
    if not arguments.mask_frame:
        logger.critical("Frame number for fixed masking is missing!")
        sys.exit(1)

    if (arguments.mask_frame > movie.shape[0]) or (arguments.mask_frame < 0):
        logger.critical(f'Requested frame does not exist, input only has {movie.shape[0]} frames.. exiting')
        sys.exit(1)

    else:
        logger.info(f'Creating fixed mask from frame {arguments.mask_frame} with threshold {arguments.mask_thresh}')  
        mask = spyboat.create_fixed_mask(movie, arguments.mask_frame,
                                         arguments.mask_thresh)
elif arguments.masking == 'dynamic':
    logger.info(f'Creating dynamic mask with threshold {arguments.mask_thresh}')
    mask = spyboat.create_dynamic_mask(movie, arguments.mask_thresh)
        
else:
    logger.info('No masking requested..')

# ------ Retrieve  wavelet parameters ---------------------------

Wkwargs = {'dt': arguments.dt,
           'Tmin': arguments.Tmin,
           'Tmax': arguments.Tmax,           
           'nT': arguments.nT,
           'T_c' : arguments.Tcutoff, # defaults to None
           'win_size' : arguments.win_size # defaults to None          
}

# start parallel processing
results = spyboat.run_parallel(movie, arguments.ncpu, **Wkwargs)

# --- masking? ---

if mask is not None:
    # mask all output movies (in place!)
    for key in results:
        logger.info(f'Masking {key}')
        spyboat.apply_mask(results[key], mask, fill_value=-1)

# --- Produce Output Report Figures/png's ---
# jump to the middle of the movie
snapshot_frame = int(movie.shape[0]/2)
output_report.produce_snapshots(movie, results, snapshot_frame, Wkwargs)
output_report.produce_distr_plots(results, Wkwargs)

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
if arguments.preprocessed_out:
    io.imsave(arguments.preprocessed_out, movie, plugin='tifffile')
    logger.info(f'Written {arguments.preprocessed_out}')
