''' Provies I/O and pre- and postprocessing routines ''' 

import sys
from os import path
import logging
import numpy as np
from skimage import io
from skimage.transform import rescale
from skimage.filters import gaussian, threshold_otsu

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- I/O ---

def open_tif(fname):

    '''
    The stack to analyze with SpyBOAT 
    must have (Frames,Y,X) ordering, this is what this function 
    tries to ensure.

    Note that multi-channel (Fiji Hyperstacks) are not directly
    supported. Extract the channel of interest first!


    Parameters
    ----------

    fname : string,
            Path to the tif-stack to be opened

    Returns
    -------

    movie : ndarray with ndim = 3, ordering is (Frames, Y, X)
    '''

    if not ('tif' in fname) | ('tiff' in fname):
        raise ValueError('Input file needs to be in tif/tiff format!')

    logger.info(f'Opening {fname}')
    
    tif_stack = io.imread(fname, plugin = "tifffile")
    
    # 4D-Hyperstack
    if len(tif_stack.shape) > 3:

        logger.critical(f'Hyperstack detected with shape {tif_stack.shape}')
        logger.critical(f'Hyperstacks are not supported, ndim of input stack must be 3!')

        sys.exit(1)
              
        # with this you can handle the quirks of Fiji Hyperstacks
        # try:
        #     # if only two channels present,
        #     # tifffile ordering sadly is F,C,X,Y
        #     if tif_stack.shape[1] == 2:            
        #         F,C,X,Y = tif_stack.shape # special ordering
        #         movie = tif_stack[:,channel-1,:,:] # select a channel
        #         print('Input shape:', (F,X,Y,C), '[Frames, Y, C, Channels]')                
        #     # normal F,X,Y,C ordering
        #     else:
        #         movie = tif_stack[:,:,:,channel-1] # select a channel
        #         print('Input shape:', tif_stack.shape, '[Frames, Y, Y, Channels]')
                

        #     return movie

        # except IndexError:
        #     print('Channel {} not found.. exiting!'.format(channel), file=sys.stderr)
        #     print('Channel {} not found.. exiting!'.format(channel))

        #     sys.exit(1)

    # 3D-Stack
    elif len(tif_stack.shape) == 3:
        logger.info('Stack detected')
        logger.info(f'Input shape: {tif_stack.shape}, interpreted as [Frames, Y, X]')

        # return as is
        return tif_stack

    else:
        logger.critical('Input shape:', tif_stack.shape, '[?]')
        logger.critical('Movie has wrong number of dimensions, is it a single slice stack?!')
        sys.exit(1)

# ---- Output -----------------------------------------------

def save_to_tifs(results, input_name, directory):

    '''
    This is just a convenience function to save out
    all transformation results at once with consistent names.

    It will write four tifs to disc:

    *directory*/phase_*input_name*.tif
    *directory*/period_*input_name*.tif
    *directory*/power_*input_name*.tif
    *directory*/amplitude_*input_name*.tif

    Parameters
    ----------

    results : dictionary, holds the four output movies 
                     (phase, period, power and amplitude)

    input_name : str, the common name (of the experiment/sample..)
    directory : str, the target directory
    '''
    # save phase movie
    out_path = path.join(directory, f'phase_{input_name}.tif')
    io.imsave(out_path, results['phase'], plugin="tifffile")
    logger.info(f'Written {out_path}')

    # save period movie
    out_path = path.join(directory, f'period_{input_name}.tif')
    io.imsave(out_path, results['period'], plugin="tifffile")
    logger.info(f'Written {out_path}')    
    
    # save power movie
    out_path = path.join(directory, f'power_{input_name}.tif')
    io.imsave(out_path, results['power'], plugin="tifffile")
    logger.info(f'Written {out_path}')    

    # save amplitude movie
    out_path = path.join(directory, f'amplitude_{input_name}.tif')
    io.imsave(out_path, results['amplitude'], plugin="tifffile")
    logger.info(f'Written {out_path}')    
    

# --- pre-processing ---

def down_sample(movie, scale_factor):

    '''
    Spatially downsamples a 3-dimensional input movie (NFrames, y, x). 
    It basically wraps around skimage.transform.rescale 
    to properly work on image stacks (movies). 

    Parameters
    ----------

    movie : ndarray with ndim = 3, downsampling is done along 
                                   the last two axis
    scale_factor : float, must be 0 < scale_factor <= 1 as 
                          only downsampling is supported/meaningful 
                          here. Goes into `skimage.transform.rescale`

    Returns
    -------

    movie_ds : ndarray with ndim = 3, the downsampled movie,
               movie_ds.shape[0] == movie.shape[0]
    
    '''

    if scale_factor > 1:
        raise ValueError ('Upscaling is not supported!')
    
    # rescale only 1st frame to inquire output shape
    frame1 = rescale(movie[0,...], scale = scale_factor,
                     preserve_range=True)
    movie_ds = np.zeros( (movie.shape[0], *frame1.shape) )
    
    for frame in range(movie.shape[0]):
        movie_ds[frame,...] = rescale(movie[frame,...],
                                      scale = scale_factor,
                                      preserve_range=True)

    return movie_ds

def gaussian_blur(movie, sigma):

    '''
    Wraps around skimage.filters.gaussian to adhere to SpyBOAT/Fiji
    axis ordering (Frames, ydim, xdim).

    Parameters
    ----------

    movie : ndarray with ndim = 3, smoothing is done along the 
                                   last two axis
    sigma : float, standard deviation of the gaussian kernel.

    Returns
    -------

    movie_gb : ndarray with ndim = 3, the blurred movie
    
    '''

    movie_gb = np.zeros( movie.shape )
    for frame in range(movie.shape[0]):
        movie_gb[frame,...] = gaussian(movie[frame,...], sigma = sigma)

    return movie_gb    

# --- Masking ---

def create_fixed_mask(movie, frame, threshold):

    '''
    This is a convenience function to create 
    a boolean mask from a single *frame* of an input
    *movie* with a fixed *threshold*. It can then be
    used to mask out non-oscillatory regions of the 
    analysis results.

    Visual inspection for choosing a suitable threshold 
    value is recommended.

    Parameters
    ----------

    movie : ndarray with ndim = 3, 1st axis is time
    frame : integer, the frame number (0-based) of the image
                     to create the mask from
    threshold : float, minimal intensity of a pixel to be considered
                       as foreground 

    Returns
    -------

    mask : boolean array with ndim = 2, holds True for masked pixels
    
    '''

    
    img = movie[frame]

    mask = img < threshold
    
    return mask

def create_Otsu_mask(movie, frame):

    '''
    This is a convenience function to create 
    a boolean mask from a single *frame* of an input
    *movie* with a threshold derived by the Otsu method. 
    The mask can then be used to mask out non-oscillatory 
    regions of the analysis results.


    Parameters
    ----------

    movie : ndarray with ndim = 3, 1st axis is time
    frame : integer, the frame number (0-based) of the image
                     to create the mask from

    Returns
    -------

    mask : boolean array with ndim = 2, holds True for masked pixels
    
    '''

    
    img = movie[frame]

    threshold = threshold_otsu(img)
    mask = img < threshold
    
    return mask

def apply_mask(movie, mask, fill_value = -1):

    '''
    Sets the masked pixels to *fill_value*
    for every frame. This changes *movie* in place!

    Parameters
    ----------

    movie : ndarray with ndim = 3, 1st axis is time
    mask : boolean array with ndim = 2, holds True for masked pixels
    fill_value : float, all masked pixels get set to this value
    
    '''

    movie[:,mask] = fill_value
    
