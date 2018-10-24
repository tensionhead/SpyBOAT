#!/usr/bin/env bash

# example command
python3 ana_movie.py --movie ../test_data/twosmall_sines.tif --phase_out ../test_data/phase_out.tif --period_out ../test_data/period_out.tif --power_out ../test_data/power_out.tif --dt 10 --Tmin 50 --Tmax 220 --nT 120

printf "\n"

# example multi_chan 3 channels command
python3 ana_movie.py --movie ../test_data/twosmall_sines_multichan3.tif --phase_out ../test_data/phase_mc3_out.tif --period_out ../test_data/period_mc3_out.tif --power_out ../test_data/power_mc3_out.tif --dt 10 --Tmin 50 --Tmax 220 --nT 120 --channel 2 --gauss_sigma 0


printf "\nWarning examples:\n"

# example multi_chan 2 channels command
python3 ana_movie.py --movie ../test_data/twosmall_sines_multichan.tif --phase_out ../test_data/phase_mc2_out.tif --period_out ../test_data/period_mc2_out.tif --power_out ../test_data/power_mc2_out.tif --dt 7.5 --Tmin 3.2 --Tmax 2200 --nT 120 --channel 2 


# error examples
printf "\nError examples:\n"

python3 ana_movie.py --movie ../test_data/Xtwosmall_sines_multichan.tifX --phase_out ../test_data/phase_mc_out.tif --period_out ../test_data/period_mc_out.tif --power_out ../test_data/power_mc_out.tif --dt 10 --Tmin 50 --Tmax 220 --nT 120 --channel 2 

printf '\n'

python3 ana_movie.py --movie ../test_data/twosmall_sines_multichan.tif --phase_out ../test_data/phase_mc_out.tif --period_out ../test_data/period_mc_out.tif --power_out ../test_data/power_mc_out.tif --dt 10 --Tmin 50 --Tmax 220 --nT 120 --channel 7

printf '\n'


