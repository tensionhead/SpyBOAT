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
# ScriptPath='/g/aulehla/Gregor/progs/WaveletMovies/src/ana_movie.py'
ScriptPath='/g/aulehla/Gregor/progs/WaveletMovies/src/test_argparse.py'

# the (soon to be) galaxy connected directory
BaseDir='/g/aulehla/WaveletMovieBatchG'

# these get replaced by the prepare script
MovieSubDir='Gregor'
MovieName='Luvelu-D_130-10_L6.tif'
par_dt='3'
par_Tmin='3.3'
par_Tmax='33.3'
par_nT='333'

##### load modules
module load Anaconda3


#### launch python
python3 $ScriptPath --mov_dir $MovieSubDir --mov_name $MovieName  --dt $par_dt --Tmin $par_Tmin --Tmax $par_Tmax --nT $par_nT

# for people who peek into the directory
ret=$?
if [ $ret -ne 0 ]; then
    touch $BaseDir/$MovieSubDir/error
else
    touch $BaseDir/$MovieSubDir/done
fi


