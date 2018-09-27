import matplotlib

matplotlib.use('Agg')

import argparse
import sys
import os

from skimage import io

# ----------Import Wavelet Routines----------------
from wavelet_ana_lib import *

# -------------------------------------------------

parser = argparse.ArgumentParser(description='Process some string arguments')
# I/O
parser.add_argument('--mov_dir', help='movie (sub-)directory', required='True', type=str)
parser.add_argument('--mov_name', help='input movie file name', required='True', type=str)
parser.add_argument('--phase_out', help='phase output file name', required='True', type=str)
parser.add_argument('--period_out', help='period output file name', required='True', type=str)
parser.add_argument('--power_out', help='power output file name', required='True', type=str)
# Wavelet Parameters
parser.add_argument('--dt', help='sampling interval', required='True', type=int)
parser.add_argument('--Tmin', help='smallest period', required='True', type=float)
parser.add_argument('--Tmax', help='biggest period', required='True', type=float)
parser.add_argument('--nT', help='number of periods to scan for', required='True', type=int)

if len(sys.argv) < 2:
    print("Missing command line arguments.. exiting")
    sys.exit(1)

arguments = parser.parse_args(sys.argv[1:])

# ------------Read the input----------------------------------------
work_dir = arguments.mov_dir
print("Working in:", work_dir)
print('Opening:', arguments.mov_name)

movie_path = os.path.join(work_dir, arguments.mov_name)
try:
    movie = io.imread(movie_path, plugin="tifffile")
except io.FileNotFoundError:
    print("Couldn't open {}, check movie storage directory!".format(movie_path))
    sys.exit(1)

print('Input shape:', movie.shape)
NFrames, ydim, xdim = movie.shape
Npixels = ydim * xdim

# ------------Set output paths---------------------------------------
out_path1 = os.path.join(work_dir, arguments.phase_out)
out_path2 = os.path.join(work_dir, arguments.period_out)
out_path3 = os.path.join(work_dir, arguments.power_out)

# -------Set wavelet parameters--------------------------------------
periods = np.linspace(arguments.Tmin, arguments.Tmax, arguments.nT)
T_c = arguments.Tmax
dt = arguments.dt
# -------------------------------------------------------------------

# not working, Fiji can't read this :/
# wm = np.zeros( (*movie.shape,3),dtype = np.float32 ) # initialize empty array for output

# create output arrays
period_movie = np.zeros(movie.shape, dtype=np.float32)  # initialize empty array for output
phase_movie = np.zeros(movie.shape, dtype=np.float32)  # initialize empty array for output
power_movie = np.zeros(movie.shape, dtype=np.float32)  # initialize empty array for output

print('Computing the transforms for {} pixels:'.format(Npixels))
sys.stdout.flush()

# loop over pixel coordinates
for x in range(xdim):

    print("X = ", x)
    sys.stdout.flush()

    for y in range(ydim):
        input_vec = movie[:, y, x]  # the time_series at pixel (x,y)
        Nt = len(input_vec)  # number of sample points
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

print('done with the transformations')

# save phase movie
io.imsave(out_path1, phase_movie)
print('written', out_path1)

# save period movie
io.imsave(out_path2, period_movie)
print('written', out_path2)

# save power movie
io.imsave(out_path3, power_movie)
print('written', out_path3)
