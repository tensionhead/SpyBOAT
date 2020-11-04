#!/usr/bin/env python

## This is the central processing script.
## Gets interfaced both by Galaxy and the
## command line tool of SpyBOAT

import argparse
import sys
import multiprocessing as mp

# image processing modules
from skimage import io
from skimage.transform import rescale
from skimage.filters import gaussian

# wavelet processing
import pyboat as pb

# ----------Import Wavelet Routines----------------
from wavelet_ana_lib import *

# ----------command line parameters ---------------

parser = argparse.ArgumentParser(description='Process some arguments.')

# I/O
parser.add_argument('--movie', help="Movie location", required=True)
parser.add_argument('--phase_out', help='Phase output file name', required=True)
parser.add_argument('--period_out', help='Period output file name', required=True)
parser.add_argument('--power_out', help='Power output file name', required=True)
parser.add_argument('--amplitude_out', help='Amplitude output file name', required=True)
parser.add_argument('--channel', help='which channel of the hyperstack to process',
                    required=False, type=int, default=1)

# (Optional) Multiprocessing

parser.add_argument('--ncpu', help='Number of processors to use',
                    required=False, type=int, default=1)

# Optional spatial downsampling
parser.add_argument('--rescale', help='Rescale the image by a factor given in %, 100 means no rescaling', required=False, default = 100, type=int)


# Optional Gaussian smoothing
parser.add_argument('--gauss_sigma', help='Gaussian smoothing parameter, 0 means no smoothing', required=False, default = 0, type=float)

# Wavelet Parameters
parser.add_argument('--dt', help='Sampling interval', required=True, type=float)
parser.add_argument('--Tmin', help='Smallest period', required=True, type=float)
parser.add_argument('--Tmax', help='Biggest period', required=True, type=float)
parser.add_argument('--Tcutoff', help='Sinc cut-off period', required=True, type=float)
parser.add_argument('--L', help='Sliding window size for amplitude normalization, 0 means no normalization', required=False, type=float)
parser.add_argument('--nT', help='Number of periods to scan for', required=True, type=int)

parser.add_argument('--version', action='version', version='1.1.0')

arguments = parser.parse_args()

# ------------Read the input----------------------------------------
print('Opening:', arguments.movie)

try:
    movie = io.imread(arguments.movie, plugin="tifffile")
except FileNotFoundError:
    print("Couldn't open {}, check movie storage directory!".format(arguments.movie))
    print("Couldn't open {}, check movie storage directory!".format(arguments.movie), file=sys.stderr)

    sys.exit(1)


# Hyperstack (Frames,X,Y,Channels) or normal image stack (Frames,X,Y)?
# The stack to analyze must have (Frames, X, Y) ordering after being
# read in below (see also processing.transform_stack(...))

channel = arguments.channel # the selected channel

# 4D-Hyperstack
if len(movie.shape) == 4:

    print('Hyperstack detected, channel {} selected'.format(channel))
    
    try:
        # if only two channels present, tifffile ordering sadly is F,C,X,Y
        if movie.shape[1] == 2:            
            F,C,X,Y = movie.shape # special ordering
            print('Input shape:', (F,X,Y,C), '[Frames, X, Y, Channels]')
            movie = movie[:,channel-1,:,:] # select a channel

        # normal F,X,Y,C ordering
        else:
            print('Input shape:', movie.shape, '[Frames, X, Y, Channels]')
            movie = movie[:,:,:,channel-1] # select a channel
            
    except IndexError:
        print('Channel {} not found.. exiting!'.format(channel), file=sys.stderr)
        print('Channel {} not found.. exiting!'.format(channel))
                
        sys.exit(1)

# 3D-Stack
elif len(movie.shape) == 3:
    print('Stack detected')
    print('Input shape:', movie.shape, '[Frames, X, Y]')
    
else:
    print('Input shape:', movie.shape, '[?]')
    print('Movie has wrong number of dimensions, is it a single slice stack?!\nExiting..')
    print('Movie has wrong number of dimensions, is it a single slice stack?!\nExiting..', file=sys.stderr)

    sys.exit(1)

# -------- Do (optional) spatial downsampling ---------------------------    

scale_factor = arguments.rescale

if scale_factor > 100:
    print('Requested upscaling, however only downsampling is supported (and meaningful)!')
    print('..doing no rescaling')
    
elif scale_factor != 100:
    print(f'Downsampling the movie to {scale_factor:d}% of its original size..')

    # rescale 1st frame to inquire output shape
    frame1 = rescale(movie[0,...], scale = scale_factor/100, preserve_range=True)
    movie_rs = np.zeros( (movie.shape[0], *frame1.shape) )
    
    for frame in range(movie.shape[0]):
        movie_rs[frame,...] = rescale(movie[frame,...], scale = scale_factor/100,
                                      preserve_range=True)

    # overwrite
    movie = movie_rs
else:
    print('No downsampling requested')
        
# -------- Do (optional) pre-smoothing -------------------------
# note that downsampling already is a smoothing operation..

gsigma = arguments.gauss_sigma

# check if pre-smoothing requested, a (non-sensical) value of 0 means no pre-smoothing
if gsigma != 0:
    print(f'Pre-smoothing the movie with Gaussians, sigma = {arguments.gauss_sigma:.2f}..')

    for frame in range(movie.shape[0]):
        movie[frame,...] = gaussian(movie[frame,...], sigma = gsigma)
else:
    print('No pre-smoothing requested')


    
# -------Retrieve (and sanitize) wavelet parameters--------------------------------------

Nt = movie.shape[0]  # number of sample points, length of the input signal
T_c = arguments.Tcutoff
dt = arguments.dt
Tmin = arguments.Tmin
Tmax = arguments.Tmax
L = arguments.L # defaults to 0 which mean no normalization requested

if Tmin < 2 * dt:
    print('Warning, Nyquist limit is 2 times the sampling interval!')
    print('..setting Tmin to {:.2f}'.format( 2 * dt ))
    Tmin = 2 * dt

if Tmax > dt * Nt: 
    print ('Warning: Very large periods chosen!')
    print('..setting Tmax to {:.2f}'.format( dt * Nt ))
    Tmax = dt * Nt

periods = np.linspace(Tmin, Tmax, arguments.nT)

# -------------------------------------------------------------------------------
# the function to be executed in parallel, Wavelet parameters are global!

def process_array(movie):

    '''
    Wavelet-process a 3-dimensional array 
    with shape (NFrames, ydim, xdim).

    Parameters for Wavelet transform are global
    (thanks to multiprocessing.Pool)!
    '''

    # create output arrays, needs 32bit for Fiji FloatProcessor :/
    period_movie = np.zeros(movie.shape, dtype=np.float32)  
    phase_movie = np.zeros(movie.shape, dtype=np.float32)  
    power_movie = np.zeros(movie.shape, dtype=np.float32)  
    amplitude_movie = np.zeros(movie.shape, dtype=np.float32)  

    ydim, xdim = movie.shape[1:] # F, Y, X ordering
    
    Npixels = ydim * xdim
    print(f'Computing the transforms for {Npixels} pixels')
    sys.stdout.flush()

    # loop over pixel coordinates
    for x in range(xdim):

        for y in range(ydim):

            # show progress
            if Npixels < 10:
                print(f"Processed {(ydim*x + y)/Npixels * 100 :.1f}%..")
                sys.stdout.flush()

            elif (ydim*x + y)%(int(Npixels/10)) == 0 and x != 0:
                print(f"Processed {(ydim*x + y)/Npixels * 100 :.1f}%..")
            
            input_vec = movie[:, y, x]  # the time_series at pixel (x,y)
            
            # detrending
            trend = pb.sinc_smooth(input_vec, T_c, dt)
            dsignal = input_vec - trend
            
            # amplitude normalization?
            if L != 0:
                dsignal = pb.normalize_with_envelope(dsignal, L, dt)

            sigma = np.std(dsignal)
            modulus, wlet = pb.compute_spectrum(dsignal, dt, periods)
            ridge_ys,_ = pb.get_maxRidge_ys(modulus)

            ridge_periods = periods[ridge_ys]
            powers = modulus[ridge_ys, np.arange(Nt)]
            phases = np.angle(wlet[ridge_ys, np.arange(Nt)])
            amplitudes = pb.core.power_to_amplitude(ridge_periods,
                                                    powers, sigma, dt)
            
            phase_movie[:, y, x] = phases
            period_movie[:, y, x] = ridge_periods
            power_movie[:, y, x] = powers
            amplitude_movie[:, y, x] = amplitudes

    return phase_movie, period_movie, power_movie, amplitude_movie

# ------ Set up Multiprocessing  --------------------------

ncpu_avail = mp.cpu_count() # number of available processors
ncpu_req = arguments.ncpu   # requested number of cpu's


print(f"{ncpu_avail} CPU's available")

if ncpu_req > ncpu_avail:
    print(f"Warning: requested {ncpu_req} CPU's but only {ncpu_avail} available!")
    print(f"Setting number of requested CPU's to {ncpu_avail}..")
    
    ncpu_req = ncpu_avail

print(f"Starting {ncpu_req} process(es)..")


# initialize pool
pool = mp.Pool( ncpu_req )
    
# split input movie row-wise (axis 1, axis 0 is time!)
movie_split = np.array_split(movie, ncpu_req, axis = 1)

# start the processes, result is list of tuples (phase, period, power)
res_movies = pool.map( process_array, [movie for movie in movie_split] )

# re-join the splitted output movies
phase_movie = np.concatenate( [r[0] for r in res_movies], axis = 1 )
period_movie = np.concatenate( [r[1] for r in res_movies], axis = 1 )
power_movie = np.concatenate( [r[2] for r in res_movies], axis = 1 )
amplitude_movie = np.concatenate( [r[3] for r in res_movies], axis = 1 )


print('Done with all transformations')

# ---- Output -----------------------------------------------

# save phase movie
io.imsave(arguments.phase_out, phase_movie, plugin="tifffile")
print('Written', arguments.phase_out)

# save period movie
io.imsave(arguments.period_out, period_movie, plugin="tifffile")
print('Written', arguments.period_out)

# save power movie
io.imsave(arguments.power_out, power_movie, plugin="tifffile")
print('Written', arguments.power_out)

# save amplitude movie
io.imsave(arguments.amplitude_out, amplitude_movie, plugin="tifffile")
print('Written', arguments.amplitude_out)
