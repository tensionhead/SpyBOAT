#!/usr/bin/env bash

# example command, minimal options: no detrending,
# no rescaling, no masking, no amplitude norm., no blurring

INPUT_PATH='./test-data/test_movie.tif'
#INPUT_PATH='../../SCN_L20_Evans2013-1frame.tif'
SCRIPT_PATH='.'

python3 $SCRIPT_PATH/cl_wrapper.py --input_path $INPUT_PATH --phase_out phase_twosines_out.tif --period_out period_twosines_out.tif --power_out power_twosines_out.tif  --amplitude_out amplitude_twosines_out.tif --dt 2. --Tmin 20 --Tmax 30 --nT 200 --ncpu 6 --save_input True --masking dynamic

printf "\n"
# printf "\nError examples:\n"

# python3 $SCRIPT_PATH/cl_wrapper.py --input_path $INPUT_PATH --phase_out phase_twosines_out.tif --period_out period_twosines_out.tif --power_out power_twosines_out.tif  --amplitude_out amplitude_twosines_out.tif --dt 2. --Tmin 20 --Tmax 30 --nT 200 --ncpu 6 --save_input True --masking fixed
