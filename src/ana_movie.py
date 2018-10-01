#!/usr/bin/env python

import argparse
import sys

import matplotlib
matplotlib.use('Agg')

from skimage import io


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
    print("Couldn't open {}, check movie storage directory!".format(arguments.movie), file = sys.stderr)

    sys.exit(1)

print('Input shape:', movie.shape,'[Frames, Channels, X, Y]')

# ---Hyperstack (X,Y,T,C) or normal image stack (X,Y,T)?-----------

channel = arguments.channel # the selected channel

if len(movie.shape) == 4:
    print('Hyperstack detected, channel {} selected'.format(channel))

    try:
        movie = movie[:,channel-1,:,:] # select a channel
        NFrames, ydim, xdim = movie.shape

    except IndexError:
        print('Channel {} not found.. exiting!'.format(channel), file = sys.stderr)
        print('Channel {} not found.. exiting!'.format(channel))
                
        sys.exit(1)
        
elif len(movie.shape) == 3:
    print('Stack detected')
    NFrames, ydim, xdim = movie.shape
    
else:                      
    print('Movie has wrong number of dimensions, is it a stack?!\nExiting..')
    print('Movie has wrong number of dimensions, is it a stack?!\nExiting..', file = sys.stderr)

    sys.exit(1)

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
