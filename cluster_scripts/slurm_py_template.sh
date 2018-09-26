#!/bin/bash
##### These lines are for Slurm
#SBATCH --output=/home/moenke/hpc_output/wletM_%A.out
#SBATCH --error=/home/moenke/hpc_output/wletM_%A.err
#SBATCH -n 1 
#SBATCH -N 1
#SBATCH -A aulehla
#SBATCH --job-name=wletmovie2
#SBATCH --partition=htc
#SBATCH --mail-type=FAIL,BEGIN,END
#SBATCH --mail-user=gregor.moenke@embl.de
#SBATCH --mem=2000 # memory given in MB
#SBATCH -t 08:00:00

# path to the python script doing the job
ScriptPath='../src/ana_movie.py' # relative to /WaveletMovies/cluster_scripts
# ScriptPath='/g/aulehla/Gregor/progs/WaveletMovies/src/ana_movie.py' # works on spinoza

# to test and define the arguments
# ScriptPath='../src/test_argparse.py' # relative to /WaveletMovies/cluster_scripts

# the (soon to be) galaxy connected directory, needs to be changed to galaxy-storage location?!
BaseDir='/g/aulehla/WaveletMovieBatchG'

# all the following should get defined by the galaxy interface

#----------Paths and input file names--
MovieSubDir='Gregor'
MovieName='Luvelu-D_130-10_L6.tif'

#--------Analysis parameters-----------
par_dt='10'
par_Tmin='50'
par_Tmax='220'
par_nT='20'
#--------------------------------------

# create output names from input_name
phase_out="phase_$MovieName"
period_out="period_$MovieName"
power_out="power_$MovieName"


##### load modules
module load Anaconda3


#### launch python
python3 $ScriptPath --mov_dir $BaseDir/$MovieSubDir --mov_name $MovieName  --phase_out $phase_out --period_out $period_out --power_out $power_out --dt $par_dt --Tmin $par_Tmin --Tmax $par_Tmax --nT $par_nT

# for people who peek into the directory
# ret=$?
# if [ $ret -ne 0 ]; then
#     touch $BaseDir/$MovieSubDir/error
# else
#     touch $BaseDir/$MovieSubDir/done
# fi


