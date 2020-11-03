# SpyBOAT - Spatial pyBOAT

Small pipeline to wavelet transform 3D-Stacks (X,Y,T) based on the analysis tools
provided by [pyBOAT](https://github.com/tensionhead/pyBOAT). The supplied input
movie gets wavelet transformed pixel by pixel along the time axis, yielding up to
four output movies:

- phase movie
- period movie
- amplitude movie
- power movie

This is the complete 2D-analogue to the results for univariate time-series data provided by pyBOAT.

## General Usage Tips 

For new users and/or exploratory data analysis it is advisable to first analyse at least a 
few 1D time-series (e.g. ROI tracks) with pyBOAT. This allows to sanity check the key parameters
of the time-frequency analysis:

 - period range
 - sinc filter cut-off period
 - amplitude normalization window size (optional)
 - sampling interval 
 
 before starting the computationally costly 2D stack transforms with SpyBOAT. 


### Spatial downscaling and smoothing

Typically bio-image data aquired by tissue microscopy has much higher spatial resolution 
than temporal resolution. To save computing time and ressources, it 
is advisable to **spatially downscale** the input movie. SpyBOAT offers a simple rescaling based
on a scaling factor in %. 

### Masking

Often not everywhere in space an oscillatory signal can be found, hence masking the results 
**after** the transformation is an important step. SpyBOAT provides some simple masking capabilities,
but the user is welcome to work with the raw output and devise a masking strategy most suitable for her needs.

## Command Line Interface

To run locally: 

1. create a conda environment:
    
    ``conda env create -f environment.yml``
    
2. Run the example from `src`:

    ```bash
    cd src
    bash run_local.sh
    ```






## Available scripts:

- example configuration in ```/src/slurm_bash_template.sh```, this runs both from the shell and via slurm
- the script in ```/src/ana_movie.py``` accepts command line parameters managing I/O and the analysis parameters
- actual algorithms are in ```/src/wavelet_ana_lib.py```
