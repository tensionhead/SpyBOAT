#!/bin/bash
##### These lines are for Slurm
#SBATCH --output=/home/moenke/output/wletM_%A.out
#SBATCH --error=/home/moenke/output/wletM_%A.err
#SBATCH -n 1 
#SBATCH -N 1
#SBATCH -A aulehla
#SBATCH --job-name=wletmovie2
#SBATCH --partition=htc
#SBATCH --mail-type=FAIL,BEGIN,END
#SBATCH --mail-user=gregor.moenke@embl.de
#SBATCH --mem=2000 # memory given in MB
#SBATCH -t 08:00:00

# BaseDir='/g/aulehla/vLab/WaveletMovieBatch'
BaseDir='dummyBaseDir'
MovieDir='dummyDir' # get replaced by prepare script
SCRIPT='ana_Movie.py'

##### load modules
module load Anaconda3

##### copy files to /scratch working directory
touch $BaseDir/$MovieDir/start # mark the beginning

cp -R $BaseDir/$MovieDir /scratch/gregor


#### launch python
cd /scratch/gregor/$MovieDir
python3 $SCRIPT 
echo 'Python is Done'
touch cluster_done # mark it on /scratch

#### copy the results back
cp /scratch/gregor/$MovieDir/phase*tif $BaseDir/$MovieDir/
cp /scratch/gregor/$MovieDir/period*tif $BaseDir/$MovieDir/
cp /scratch/gregor/$MovieDir/power*tif $BaseDir/$MovieDir/
echo 'Everything is done'
touch $BaseDir/$MovieDir/done
