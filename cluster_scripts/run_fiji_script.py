#!/bin/bash

fiji_path='/g/aulehla/vLab/HPC_ImageJ/Fiji.app/ImageJ-linux64'
 
#---------------------------------------
# disabling java parallel garbage collection:
#---------------------------------------

# with java option in command line - it's ok now!
$fiji_path -XX:ParallelGCThreads=1 --ij2 --headless -- --run $1

# from environment
#JAVA_OPTS="$JAVA_OPTS -XX:+UseSerialGC"
#export JAVA_OPTS
#$fiji_path --ij2 --headless --run $script_path/process_Roi_movie.py $1
