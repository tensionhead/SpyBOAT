#!/usr/bin/env bash

# example command, minimal options: no detrending,
# no rescaling, no masking, no amplitude norm., no blurring

INPUT_PATH='./test-data/test-movie.tif'
# INPUT_PATH='./test-data/SCN_L20_Evans2013-half.tif'
SCRIPT_PATH='.'

python3 $SCRIPT_PATH/cl_wrapper.py --input_path $INPUT_PATH --phase_out phase_twosines_out.tif --period_out period_twosines_out.tif --power_out power_twosines_out.tif  --amplitude_out amplitude_twosines_out.tif --dt .5 --Tmin 20 --Tmax 30 --nT 200 --ncpu 6 --masking dynamic --preprocessed_out preproc_two_sines.tif --gauss_sigma 3 --rescale 50 --Tcutoff 40 --masking fixed --mask_frame 10 --mask_thresh 8

printf "\n"
# printf "\nError examples:\n"

# python3 $SCRIPT_PATH/cl_wrapper.py --input_path $INPUT_PATH --phase_out phase_twosines_out.tif --period_out period_twosines_out.tif --power_out power_twosines_out.tif  --amplitude_out amplitude_twosines_out.tif --dt 2. --Tmin 20 --Tmax 30 --nT 200 --ncpu 6 --save_input True --masking fixed
