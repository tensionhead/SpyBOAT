#!/usr/bin/env python

''' 
This is the central processing script.
Gets interfaced both by the Galaxy wrapper and
is the computational core of the spyboat module 
'''

import sys
import numpy as np
import multiprocessing as mp

# wavelet analysis
import pyboat as pb

# --- Spatial Wavelet Analysis ---

def transform_stack(movie, dt, Tmin, Tmax, nT, T_c, L = None):

    '''
    Analyzes a 3-dimensional array 
    with shape (NFrames, ydim, xdim) along
    its 1st axis 'pixel-by-pixel'.

    Returns four arrays with the same shape as the input
    array holding the results of the transform for each pixel.

    For high spatial resolution input this might take a very
    long time as ydim \times xdim transformations have to be calculated!
    Parallel execution is recommended (see `run_parallel` below).

    Parameters
    ----------

    movie : ndarray with ndim = 3, transform is done along 1st axis 
    dt    : float, sampling interval               
    Tmin : float, smallest period
    Tmax : float, largest period
    nT  : int,  number of periods/transforms
    T_c : float, sinc cut off period, set to None to disable 
                 sinc-detrending (not recommended)
    L   : float, amplitude normalization sliding window size. 
                 Default is None which disables normalization.

    Returns
    -------
    
    results : dictionary, with keys holding the output movies
          'phase' : 32bit ndarray, holding the instantaneous phases
          'period' : 32bit ndarray, holding the instantaneous periods 
          'power' : 32bit ndarray, holding the wavelet powers 
          'amplitude' : 32bit ndarray, holding the instantaneous amplitudes 

    '''

    # the periods to scan for
    periods = np.linspace(Tmin, Tmax, nT)
    
    # create output arrays, needs 32bit for Fiji FloatProcessor :/
    period_movie = np.zeros(movie.shape, dtype=np.float32)  
    phase_movie = np.zeros(movie.shape, dtype=np.float32)  
    power_movie = np.zeros(movie.shape, dtype=np.float32)  
    amplitude_movie = np.zeros(movie.shape, dtype=np.float32)  

    ydim, xdim = movie.shape[1:] # F, Y, X ordering
    
    Npixels = ydim * xdim
    
    print(f'Computing the transforms for {Npixels} pixels')
    sys.stdout.flush()

    # loop over pixel coordinates
    for x in range(xdim):

        for y in range(ydim):

            # show progress
            if Npixels < 10:
                print(f"Processed {(ydim*x + y)/Npixels * 100 :.1f}%..")
                sys.stdout.flush()

            elif (ydim*x + y)%(int(Npixels/5)) == 0 and x != 0:
                print(f"Processed {(ydim*x + y)/Npixels * 100 :.1f}%..")
            
            input_vec = movie[:, y, x]  # the time_series at pixel (x,y)

            signal = input_vec
            
            # detrending
            if T_c is not None:
                trend = pb.sinc_smooth(input_vec, T_c, dt)
                signal = signal - trend
                
            # amplitude normalization?
            if L is not None:
                signal = pb.normalize_with_envelope(signal, L, dt)

            sigma = np.std(signal)
            Nt = len(signal)
            
            modulus, wlet = pb.compute_spectrum(signal, dt, periods)
            ridge_ys = pb.get_maxRidge_ys(modulus)

            ridge_periods = periods[ridge_ys]
            powers = modulus[ridge_ys, np.arange(Nt)]
            phases = np.angle(wlet[ridge_ys, np.arange(Nt)])
            amplitudes = pb.core.power_to_amplitude(ridge_periods,
                                                    powers, sigma, dt)
            
            phase_movie[:, y, x] = phases
            period_movie[:, y, x] = ridge_periods
            power_movie[:, y, x] = powers
            amplitude_movie[:, y, x] = amplitudes

    results = {'phase' : phase_movie, 'period' : period_movie,
               'power' : power_movie, 'amplitude' : amplitude_movie}
    
    return results

# ------ Set up Multiprocessing  --------------------------

def run_parallel(movie, n_cpu, **wkwargs):

    '''
    Sets up parallel processing of a 3-dimensional input movie.
    See `transform_stack` above for more details. Splits the input into
    *n_cpu* slices which get transformed individually and then get
    stitched back together after all transforms are done. Speedup
    scales practically with *n_cpu*, e.g. 4 processes are 4 times
    faster than just using `transform_stack` directly.

    Returns four output movies with the same shape as the input.

    Parameters
    ----------

    movie : ndarray with ndim = 3, transform is done along 1st axis 
    n_cpu : int, number of requested processors. A check is done if more
                 are requested than available.

    Other Parameters
    ----------------

    **wkwargs : parameters for `transform_stack`,
               the wavelet analysis parameters
    Returns
    -------
    results : dictionary, with keys holding the output movies
          'phase' : 32bit ndarray, holding the instantaneous phases
          'period' : 32bit ndarray, holding the instantaneous periods 
          'power' : 32bit ndarray, holding the wavelet powers 
          'amplitude' : 32bit ndarray, holding the instantaneous amplitudes 
    '''

    ncpu_avail = mp.cpu_count() # number of available processors

    print(f"{ncpu_avail} CPU's available")

    if n_cpu > ncpu_avail:
        print(f"Warning: requested {ncpu_req} CPU's but only {ncpu_avail} available!")
        print(f"Setting number of requested CPU's to {ncpu_avail}..")

        n_cpu = ncpu_avail

    print(f"Starting {n_cpu} process(es)..")


    # initialize pool
    pool = mp.Pool( n_cpu )

    # split input movie row-wise (axis 1, axis 0 is time!)
    movie_split = np.array_split(movie, n_cpu, axis = 1)

    # starmap doesn't support **kwargs passing, we need to explicitly
    # declare the parameters :/

    # default value..
    if not 'L' in wkwargs:
        wkwargs['L'] = None
    
    try:
        dt = wkwargs['dt']
        Tmin = wkwargs['Tmin']
        Tmax = wkwargs['Tmax']
        nT = wkwargs['nT']
        T_c = wkwargs['T_c']
        L = wkwargs['L']
    except KeyError as e:
        print("Wavelet analysis parameter(s) missing:", repr(e),
              file=sys.stderr)
        print("Exiting..", file=sys.stderr)
        return
    
    # start the processes, result is list
    # of tuples (phase, period, power, amplitude)
    res_movies = pool.starmap( transform_stack,
                               [(movie, dt, Tmin, Tmax, nT, T_c, L)
                                for movie in movie_split] )

    results = {}
    # re-join the splitted output movies
    results['phase'] = np.concatenate([r['phase'] for r in res_movies],
                                       axis=1)
    results['period'] = np.concatenate([r['period'] for r in res_movies],
                                    axis=1)
    results['power'] = np.concatenate( [r['power'] for r in res_movies],
                                       axis=1)
    results['amplitude'] = np.concatenate([r['amplitude'] for r in res_movies],
                                          axis=1)

    print('Done with all transformations')        
    return results

