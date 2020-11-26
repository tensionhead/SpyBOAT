''' Provides I/O convenience routines ''' 

import sys
from os import path
import logging
import numpy as np
from skimage import io

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

    # 'dat' is for Galaxy..
    if not ('tif' in fname) | ('dat' in fname):
        raise ValueError(f'Input file ({fname}) not in tif/tiff format!')

    logger.info(f'Opening {fname}')

    tif_stack = io.imread(fname, plugin = "tifffile")
    
    # 4D-Hyperstack
    if len(tif_stack.shape) > 3:

        logger.critical(f'Hyperstack detected with shape {tif_stack.shape}')
        logger.critical(f'Hyperstacks are not supported, dimension of input stack must be 3!')

        sys.exit(1)

    # 3D-Stack
    elif len(tif_stack.shape) == 3:
        logger.info('Stack detected')
        logger.info(f'Input shape: {tif_stack.shape}, interpreted as [Frames, Y, X]')

        # return as is
        return tif_stack

    else:
        logger.critical(f'Input shape: {tif_stack.shape} [?]')
        logger.critical('Movie has wrong number of dimensions, is it a single slice stack?!')
        sys.exit(1)

# ---- Output -----------------------------------------------

def save_results_to_tifs(results, base_name, directory = '.'):

    '''
    This is just a convenience function to save out
    all transformation results at once with consistent names.

    It will write four tifs to disc:

    *directory*/*base_name*_phase.tif
    *directory*/*base_name*_period.tif
    *directory*/*base_name*_power.tif
    *directory*/*base_name*_amplitude.tif

    Parameters
    ----------

    results : dictionary, holds the four output movies 
                     (phase, period, power and amplitude)

    base_name : str, the common name (of the experiment/sample..)
    directory : str, the target directory
                defaults to cwd
    '''
    # save phase movie
    out_path = path.join(directory, f'{base_name}_phase.tif')
    io.imsave(out_path, results['phase'], plugin="tifffile")
    logger.info(f'Written {out_path}')

    # save period movie
    out_path = path.join(directory, f'{base_name}_period.tif')
    io.imsave(out_path, results['period'], plugin="tifffile")
    logger.info(f'Written {out_path}')    
    
    # save power movie
    out_path = path.join(directory, f'{base_name}_power.tif')
    io.imsave(out_path, results['power'], plugin="tifffile")
    logger.info(f'Written {out_path}')    

    # save amplitude movie
    out_path = path.join(directory, f'{base_name}_amplitude.tif')
    io.imsave(out_path, results['amplitude'], plugin="tifffile")
    logger.info(f'Written {out_path}')    

# --- open a SpyBOAT output set of movies ---

def open_results(base_name, directory='.'):

    '''
    The complementary function to 'save_results_to_tifs',
    given a *base_name* reads the phase-, period-, power- 
    and amplitude-movies from *directory* into a dictionary.

    Parameters
    ----------

    base_name : str, the common name (of the experiment/sample..)
    directory : str, the target directory
                defaults to cwd

    Returns
    -------
    results : dictionary, holds the four output movies 
                     (phase, period, power and amplitude)

    '''

    results = {}
    for key in ['period','phase','power','amplitude']:
        in_path = path.join(directory, f'{base_name}_{key}.tif')
        try:
            results[key] = io.imread(in_path)
        except FileNotFoundError as e:
            logger.critical(f"Could not find {in_path} to open..")

    return results


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
