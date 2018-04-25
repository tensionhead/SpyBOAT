## Small pipeline to Wavelet transform Image Intensity Stacks

### local_scripts - The Fiji UI scripts 

__at the moment it is assumed the Aulehla group share is mounted under
*/Volumes/aulehla* !__

- to be executed at a local machine
- entry point into the pipeline: copies the data/scripts onto /vLab
- creates a slurm script in /g/aulehla/vLab/WaveletMovieBatch

### cluster_scripts - scripts for the computation on the HPC cluster

- slurm template
- python Wavelet analysis template