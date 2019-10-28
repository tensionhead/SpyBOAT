#!/usr/bin/env bash

# adjust to absolute paths

movie_dir='../test_data'
movie_name='twosmall_sines_multichan3.tif'
script_path='../src/ana_movie_mp.py'

dt=10
Tmin=50
Tmax=220
nT=120
channel=1
gauss_sigma=0

# number of processors
ncpu=2

# example command
python3 $script_path --movie $movie_dir/$movie_name --phase_out $movie_dir/'phase_mp_'$movie_name --period_out $movie_dir/'period_mp_'$movie_name --power_out $movie_dir/'power_mp_'$movie_name --amplitude_out $movie_dir/'amplitude_mp_'$movie_name --dt $dt --Tmin $Tmin --Tmax $Tmax --nT $nT --channel $channel --gauss_sigma $gauss_sigma --ncpu $ncpu
