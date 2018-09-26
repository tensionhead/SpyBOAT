import matplotlib                                                                            
matplotlib.use('Agg')  

import argparse
import sys,os
from sys import argv
from os.path import expanduser
from pathlib import Path

import numpy as np
from os import path,walk

from skimage import io 

#----------Import Wavelet Routines----------------
from wavelet_ana_lib import *
#-------------------------------------------------

parser = argparse.ArgumentParser(description='Process some string arguments')
# I/O
parser.add_argument('--mov_dir', help='movie (sub-)directory', required = 'True', type=str)
parser.add_argument('--mov_name', help='input movie file name', required = 'True', type=str)
parser.add_argument('--phase_out', help='phase output file name', required = 'True', type=str)
parser.add_argument('--period_out', help='period output file name', required = 'True', type=str)
parser.add_argument('--power_out', help='power output file name', required = 'True', type=str)
# Wavelet Parameters
parser.add_argument('--dt', help='sampling interval', required = 'True', type=int)
parser.add_argument('--Tmin', help='smallest period', required = 'True', type=float)
parser.add_argument('--Tmax', help='biggest period', required = 'True', type=float)
parser.add_argument('--nT', help='number of periods to scan for', required = 'True', type=int)

if len(sys.argv) < 2:
    print("Missing command line arguments.. exiting")
    sys.exit(1)

res = parser.parse_args(sys.argv[1:])

wdir = res.mov_dir
print("Working in",wdir)

movie_path = os.path.join( wdir, res.mov_name )
print('Opening :', movie_path)

movie = io.imread(movie_path, plugin="tifffile")
print('Input shape:',movie.shape)
#---------------------------------------------------------
sys.exit(0)

periods = np.linspace(Tmin,Tmax,nT)
T_c = Tmax

NFrames, ydim, xdim = movie.shape
Npixels = ydim*xdim
# not working, Fiji can't read this :/
#wm = np.zeros( (*movie.shape,3),dtype = np.float32 ) # initialize empty array for output

period_movie = np.zeros( movie.shape,dtype = np.float32 ) # initialize empty array for output
phase_movie = np.zeros( movie.shape,dtype = np.float32 ) # initialize empty array for output
power_movie = np.zeros( movie.shape,dtype = np.float32 ) # initialize empty array for output


print( 'Computing the transforms for {} pixels:'.format(Npixels) )
sys.stdout.flush()

# loop over pixel coordinates
for x in range(xdim):

    print("X = ",x)
    sys.stdout.flush()

    for y in range(ydim):
        
        input_vec = movie[:,y,x] # the time_series at pixel (x,y)
        Nt = len(input_vec) # number of sample points
        dsignal = sinc_smooth(input_vec, T_c, dt, detrend = True)

        modulus, wlet = compute_spectrum(dsignal,dt , periods)
        ridge_y = get_maxRidge(modulus)

        # stdout format
        ridge_periods = periods[ridge_y]
        powers = modulus[ridge_y,np.arange(Nt)]
        phases = np.angle(wlet[ridge_y,np.arange(Nt)])

        phase_movie[:,y,x] = phases
        period_movie[:,y,x] = ridge_periods
        power_movie[:,y,x] = powers
        
print('done with the transformations')
# save phase movie
out_name = movie_name.split('input_')[1] # clip off the prefix
out_path1 = os.path.join(wdir, 'phase_' + out_name)
io.imsave(out_path1, phase_movie)
print('written',out_path1)

# save period movie
out_path2 = os.path.join(wdir, 'period_' + out_name)
io.imsave(out_path2, period_movie)
print('written',out_path2)

# save power movie
out_path3 = os.path.join(wdir, 'power_' + out_name)
io.imsave(out_path3, power_movie)
print('written',out_path3)
