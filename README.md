# SpyBOAT - Spatial pyBOAT

Small pipeline to wavelet transform 3D-Stacks (time,Y,X) based on the analysis tools
provided by [pyBOAT](https://github.com/tensionhead/pyBOAT). The supplied input
movie gets analyzed pixel by pixel along the time axis, yielding up to
four output movies:

- phase movie
- period movie
- amplitude movie
- power movie

A snapshot of a typical output of the pipeline might look like this:

<img src="./doc/SpyBOATexample.png" alt="drawing" width="1350"/>

From left to right: Intensity of the blurred and down-sampled input; Phasefield; Periods and Amplitude 

This is the complete 3D-analogue to the results for univariate time-series provided by pyBOAT.

## General Usage Tips 

For new users and/or exploratory data analysis it is advisable to first analyse at least a 
few 1D time-series (e.g. ROI tracks) with [pyBOAT](https://github.com/tensionhead/pyBOAT), which
gets automatically installed along SpyBOAT.
This allows to sanity check the key parameters
of the time-frequency analysis:

 - period range
 - sinc filter cut-off period
 - amplitude normalization window size (optional)
 - sampling interval 
 
 before starting the computationally costly 3D stack transforms with SpyBOAT. 


### Spatial downsampling and smoothing

Typically bio-image data aquired by tissue microscopy has much higher spatial resolution 
than temporal resolution. To save computing time and ressources, it 
is advisable to **spatially downscale** the input movie. SpyBOAT offers a simple rescaling based
on a scaling factor in %.

Spatial(!) smoothing is important, as SpyBOAT operates on every time-series *behind* a pixel (so along
the time axis of the stack). Individual pixels tend to be quite noisy, so to faithfully resolve the 
larger structures of an oscillatory field SpyBOAT offers a standard Gaussian blur. For optimal results,
the user might want to smooth (and/or downsample) her input movie beforehand (e.g. with Fiji), and then inspect the signals
sitting on a few single pixels. Or even better, extract a few single-pixel signals, and run them through pyBOAT. If the results
are satisfying there, the transform of the whole movie with SpyBOAT should also work well.

### Masking

Often not everywhere in space an oscillatory signal can be found, hence masking the results 
**after** the transformation is an important step. SpyBOAT provides some simple masking capabilities,
but the user is welcome to work with the raw output and devise a masking strategy most suitable for her needs.

This repository also provides a Fiji plugin in ```/local-scripts/mask_wmovie_ij.py```, which allows for interactive
masking.

## Galaxy Web Server

*Soon..!*

### For Server Admins: Installing SpyBOAT as a Galaxy Tool

See the ```/galaxy``` folder. There is a ```run_tests.sh```
which produces all the outputs in the cwd. 

## Python scripting interface

Install SpyBOAT via pip: 

```bash pip3 install spyboat```

or conda:

```bash
conda config --add channels conda-forge
conda install spyboat
```
The ```scripting-template.py``` in the root of this repository
showcases the analysis with the example ```spyboat.datasets```.
