#!/usr/bin/env python
import argparse
import sys

import matplotlib
matplotlib.use('Agg')

from skimage import io
from scipy.ndimage import gaussian_filter


# ----------Import Wavelet Routines----------------
from wavelet_ana_lib import *

# -------------------------------------------------

parser = argparse.ArgumentParser(description='Process some arguments.')

# I/O
parser.add_argument('--movie', help="Movie location", required=True)
parser.add_argument('--phase_out', help='Phase output file name', required=True)
parser.add_argument('--period_out', help='Period output file name', required=True)
parser.add_argument('--power_out', help='Power output file name', required=True)
parser.add_argument('--channel', help='which channel of the hyperstack to process', required=False, type=int, default=1)

# Gaussian smoothing
parser.add_argument('--gauss_sigma', help='Gaussian smoothing parameter, 0 means no smoothing', required=False, default = 0, type=float)

# Wavelet Parameters
parser.add_argument('--dt', help='Sampling interval', required=True, type=float)
parser.add_argument('--Tmin', help='Smallest period', required=True, type=float)
parser.add_argument('--Tmax', help='Biggest period', required=True, type=float)
parser.add_argument('--nT', help='Number of periods to scan for', required=True, type=int)

parser.add_argument('--version', action='version', version='1.0.0')

arguments = parser.parse_args()


# ------------Read the input----------------------------------------
print('Opening:', arguments.movie)

try:
    movie = io.imread(arguments.movie, plugin="tifffile")
except FileNotFoundError:
    print("Couldn't open {}, check movie storage directory!".format(arguments.movie))
    print("Couldn't open {}, check movie storage directory!".format(arguments.movie), file=sys.stderr)

    sys.exit(1)


# ---Hyperstack (F,X,Y,C) or normal image stack (F,X,Y)?-----------


channel = arguments.channel # the selected channel

if len(movie.shape) == 4:

    print('Hyperstack detected, channel {} selected'.format(channel))
    
    try:
        # if only two channels present, tifffile ordering sadly is F,C,X,Y
        if movie.shape[1] == 2:            
            F,C,X,Y = movie.shape # strange ordering                
            print('Input shape:', (F,X,Y,C), '[Frames, X, Y, Channels]')
            movie = movie[:,channel-1,:,:] # select a channel
            # io.imsave('../test_data/2chan_movie.tif', movie, plugin="tifffile")

        # normal F,X,Y,C ordering
        else:
            print('Input shape:', movie.shape, '[Frames, X, Y, Channels]')
            movie = movie[:,:,:,channel-1] # select a channel
            
        NFrames, ydim, xdim = movie.shape
        
    except IndexError:
        print('Channel {} not found.. exiting!'.format(channel), file=sys.stderr)
        print('Channel {} not found.. exiting!'.format(channel))
                
        sys.exit(1)
        
elif len(movie.shape) == 3:
    print('Stack detected')
    print('Input shape:', movie.shape, '[Frames, X, Y]')
    NFrames, ydim, xdim = movie.shape
    
else:
    print('Input shape:', movie.shape, '[?]')
    print('Movie has wrong number of dimensions, is it a single slice stack?!\nExiting..')
    print('Movie has wrong number of dimensions, is it a single slice stack?!\nExiting..', file=sys.stderr)

    sys.exit(1)

# --------Do (optional) pre-smoothing----------------------------------------------

gsigma = arguments.gauss_sigma

# check if pre-smoothing requested, a (non-sensical) value of 0 means no pre-smoothing
if gsigma != 0:
    print('Pre-smoothing the movie with Gaussians, sigma = {:.2f}'.format(arguments.gauss_sigma))

    for frame in range(movie.shape[0]):
        movie[frame,...] = gaussian_filter(movie[frame,...], sigma = gsigma)
else:
    print('No pre-smoothing requested')

    
# -------Set (and sanitize) wavelet parameters--------------------------------------

Nt = len(movie[:, 0, 0])  # number of sample points, length of the input signal
T_c = arguments.Tmax # sinc filter
dt = arguments.dt
Tmin = arguments.Tmin

if arguments.Tmin < 2 * dt:
    print('Warning, Nyquist limit is 2 times the sampling interval!')
    print('..setting Tmin to {:.2f}'.format( 2 * dt ))
    Tmin = 2 * dt

if arguments.Tmax > dt * Nt: 
    print ('Warning: Very large periods chosen!')
    print('..setting Tmax to {:.2f}'.format( dt * Nt ))


periods = np.linspace(arguments.Tmin, arguments.Tmax, arguments.nT)
# -------------------------------------------------------------------

# not working, Fiji can't read this :/
# wm = np.zeros( (*movie.shape,3),dtype = np.float32 ) # initialize empty array for output

# create output arrays
period_movie = np.zeros(movie.shape, dtype=np.float32)  # initialize empty array for output
phase_movie = np.zeros(movie.shape, dtype=np.float32)  # initialize empty array for output
power_movie = np.zeros(movie.shape, dtype=np.float32)  # initialize empty array for output

Npixels = ydim * xdim
print('Computing the transforms for {} pixels:'.format(Npixels))
sys.stdout.flush()

# loop over pixel coordinates
for x in range(xdim):
    
    # print("X = ", x)
    # sys.stdout.flush()

    for y in range(ydim):
        input_vec = movie[:, y, x]  # the time_series at pixel (x,y)
        dsignal = sinc_smooth(input_vec, T_c, dt, detrend=True)

        modulus, wlet = compute_spectrum(dsignal, dt, periods)
        ridge_y = get_maxRidge(modulus)

        # stdout format
        ridge_periods = periods[ridge_y]
        powers = modulus[ridge_y, np.arange(Nt)]
        phases = np.angle(wlet[ridge_y, np.arange(Nt)])

        phase_movie[:, y, x] = phases
        period_movie[:, y, x] = ridge_periods
        power_movie[:, y, x] = powers

print('Done with the transformations')

# save phase movie
io.imsave(arguments.phase_out, phase_movie, plugin="tifffile")
print('Written', arguments.phase_out)

# save period movie
io.imsave(arguments.period_out, period_movie, plugin="tifffile")
print('Written', arguments.period_out)

# save power movie
io.imsave(arguments.power_out, power_movie, plugin="tifffile")
print('Written', arguments.period_out)
