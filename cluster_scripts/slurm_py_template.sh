#!/bin/bash
##### These lines are for Slurm
#SBATCH --output=/home/moenke/output/wletM_%A_%a.out
#SBATCH --error=/home/moenke/output/wletM_%A_%a.err
#SBATCH --array=1-60
#SBATCH -n 1 
#SBATCH -N 1
#SBATCH -A aulehla
#SBATCH --job-name=wletmovie2
#SBATCH --partition=htc
#SBATCH --mail-type=FAIL,BEGIN,END
#SBATCH --mail-user=gregor.moenke@embl.de
#SBATCH --mem=2000 # memory given in MB
#SBATCH -t 05:00:00

BaseDir='/g/aulehla/vLab/WaveletMovieBatch'
MovieDir='dummyDir'
SCRIPT='ana_RoiMovie.py'

FileNum=$SLURM_ARRAY_TASK_ID
# FileNum=3

##### load modules
module load Anaconda3

##### Launch parallel job using srun
echo 'starting'
python3 $BaseDir/$MovieDir/$SCRIPT $FileNum 
echo 'Done'
