#!/usr/bin/env bash

# adjust to absolute paths

movie_dir='../test_data'
#movie_name='twosmall_sines_multichan3.tif'
movie_name='LuVeLu_Tail_L6.tif'
script_path='../src/transform_movie.py'

channel=1

# Wavelet parameters
dt=10
Tmin=50
Tmax=200
T_c=180
nT=120
L=0 # 0 means no ampltiude normalization

# movie pre-processing
gauss_sigma=0 # no smoothing
scale_fac=50

# number of processors
ncpu=8

# example command
python3 $script_path --movie $movie_dir/$movie_name --phase_out $movie_dir/'phase_'$movie_name --period_out $movie_dir/'period_'$movie_name --power_out $movie_dir/'power_'$movie_name --amplitude_out $movie_dir/'amplitude_'$movie_name --dt $dt --Tmin $Tmin --Tmax $Tmax --nT $nT --channel $channel --gauss_sigma $gauss_sigma --ncpu $ncpu --L $L --Tcutoff $T_c --rescale $scale_fac
