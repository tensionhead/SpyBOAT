#!/usr/bin/env python

'''
Handles the quirks of multichannel tiffile formats 
found e.g. in Fiji Hyperstacks
'''

from os import path

# image processing modules
from skimage import io

def handle_tif(tif_stack, channel = 1):

    '''
    Handles the quirks of multichannel tiffile formats 
    found e.g. in Fiji Hyperstacks. The stack to analyze with SpyBOAT must 
    have (Frames, Y, X) ordering, this is what this function tries to achieve.

    Identifies if a 4D-Hyperstack (Frames,Y,X,Channels) or normal image 3D-stack (Frames,Y,X)
    was loaded, and picks the correct 3D-stack in the former case based on the user
    selected channel. 

    If only two channels are present, tifffile ordering surprisingly 
    is (Frames,Channels,Y,X). You can test this with 
    skimage.io.imread on the 'multichan2.tif' and 'multichan3.tif'
    in the 'test_data' folder of this repository. In case the tiffile
    plugin corrects this, this whole function becomes obsolete/erroneous.


    Parameters
    ----------

    tif_stack : ndarray, output of skimage.io.imread on a tif image stack
    channel : int, the desired channel for the analysis

    Returns
    -------

    movie : ndarray with ndim = 3, ordering is (Frames, Y, X)
    '''
    
    
    # 4D-Hyperstack
    if len(tif_stack.shape) == 4:

        print('Hyperstack detected, channel {} selected'.format(channel))

        try:
            # if only two channels present, tifffile ordering sadly is F,C,X,Y
            if tif_stack.shape[1] == 2:            
                F,C,X,Y = tif_stack.shape # special ordering
                print('Input shape:', (F,X,Y,C), '[Frames, X, Y, Channels]')
                movie = tif_stack[:,channel-1,:,:] # select a channel

            # normal F,X,Y,C ordering
            else:
                print('Input shape:', tif_stack.shape, '[Frames, X, Y, Channels]')
                movie = tif_stack[:,:,:,channel-1] # select a channel

            return movie

        except IndexError:
            print('Channel {} not found.. exiting!'.format(channel), file=sys.stderr)
            print('Channel {} not found.. exiting!'.format(channel))

            sys.exit(1)

    # 3D-Stack
    elif len(movie.shape) == 3:
        print('Stack detected')
        print('Input shape:', tif_stack.shape, '[Frames, X, Y]')

        return movie

    else:
        print('Input shape:', movie.shape, '[?]')
        print('Movie has wrong number of dimensions, is it a single slice stack?!\nExiting..')
        print('Movie has wrong number of dimensions, is it a single slice stack?!\nExiting..', file=sys.stderr)

        sys.exit(1)

# ---- Output -----------------------------------------------

def save_results(results, input_name, directory):

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

    results : tuple, holds the four output movies 
                     (phase, period, power and amplitude)

    input_name : str, the common name (of the experiment/sample..)
    directory : str, the target directory
    '''
    # save phase movie
    out_path = path.join(directory, f'phase_{input_name}.tif')
    io.imsave(out_path, results[0], plugin="tifffile")
    print('Written', out_path)

    # save period movie
    out_path = path.join(directory, f'period_{input_name}.tif')
    io.imsave(out_path, results[1], plugin="tifffile")
    print('Written', out_path)
    
    # save power movie
    out_path = path.join(directory, f'power_{input_name}.tif')
    io.imsave(out_path, results[2], plugin="tifffile")
    print('Written', out_path)

    # save amplitude movie
    out_path = path.join(directory, f'amplitude_{input_name}.tif')
    io.imsave(out_path, results[3], plugin="tifffile")
    print('Written', out_path)
