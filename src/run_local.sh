#!/usr/bin/env bash

# example command
python ana_movie.py --movie ../test_data/twosmall_sines.tif --phase_out ../test_data/phase_out.tif --period_out ../test_data/period_out.tif --power_out ../test_data/power_out.tif --dt 10 --Tmin 50 --Tmax 220 --nT 120

# example multi_chan command
python ana_movie.py --movie ../test_data/twosmall_sines_multichan.tif --phase_out ../test_data/phase_mc_out.tif --period_out ../test_data/period_mc_out.tif --power_out ../test_data/power_mc_out.tif --dt 10 --Tmin 50 --Tmax 220 --nT 120
