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

# path to the python script doing the job, relative to spinoza/login.cluster

ScriptPath='/g/aulehla/vLab/WaveletMovies/src/ana_movie.py' # relative to 

# the batch folder for the manual (slurm) processing pipeline
BaseDir='/g/aulehla/vLab/WaveletMovieBatch/'

##### all the following should get defined by local prepare script

#----------Paths and input file names--
movie_path="$BaseDir/$MovieName"
channel='dummyChan'
#--------Analysis parameters-----------
par_dt='dummydt'
par_Tmin='dummyTmin'
par_Tmax='dummyTmax'
par_nT='dummynT'
#--------------------------------------

##### galaxy interface input end

# create output name parameters from input_name
phase_out="$BaseDir/phase_$MovieName"
period_out="$BaseDir/period_$MovieName"
power_out="$BaseDir/power_$MovieName"


##### load modules
module load Anaconda3


#### launch python
python3 $ScriptPath --movie $movie_path --channel $channel --phase_out $phase_out --period_out $period_out --power_out $power_out --dt $par_dt --Tmin $par_Tmin --Tmax $par_Tmax --nT $par_nT

# for people who peek into the directory
# ret=$?
# if [ $ret -ne 0 ]; then
#     touch $BaseDir/$MovieSubDir/error
# else
#     touch $BaseDir/$MovieSubDir/done
# fi

