import numpy as np
import matplotlib.pyplot as plt

from skimage import io

import grad_flux as gf
from gradient_descent import crawl_gradient
import plotting as pl
import pyboat as pb

plt.ion()


def freqs_from_phase_movie(pmovie):
    
    '''
    Angular frequency by unwrapping and
    1st difference.
    '''

    fmovie = np.diff(np.unwrap(movie, axis=0), axis=0)
    jump2pi = fmovie.min(axis=0) < -6
    fmovie[:, jump2pi] = fmovie[:, jump2pi] + 2*np.pi

    return fmovie


def get_phase_gradient_norm(dY, dX):

    pg = np.array((dY, dX))

    return np.linalg.norm(pg, axis=0)


def mk_velocity_movie(phase_movie, frequency_movie):

    '''
    Angular frequency!
    '''

    pass

# movie = io.imread('/home/whir/TheoBio/data/GoodPhaseMovies/GB10_phase_Max_L6.tif')
movie = io.imread('Quad-movie2-crop.tif')#[100:200,...]
fmovie = freqs_from_phase_movie(movie)

frame = 101

# or all together
# pl.show_phase_gradient(movie[frame, ...], vlen_perc=95, skip=3, plevels=20)

# get the gradient vectorfield
dY, dX = gf.phase_gradient(movie[frame, ...])

# and the norm of those
pgn = get_phase_gradient_norm(dY, dX)

# now get the phase velocities
velo = fmovie[frame]/pgn


def show_frequency_pgrad(movie, frame):

    plt.figure()
    # get the gradient vectorfield
    dY, dX = gf.phase_gradient(movie[frame, ...])
    
    plt.contour(movie[frame], levels=15, cmap='gray_r', linewidths=1.2)
    pl.show_vfield(-dX, -dY, skip=2, vlen_perc=90)
    plt.imshow(fmovie[frame], interpolation='nearest', cmap="magma")
    plt.axis('off')

    cb = plt.colorbar()
    cb.set_label('Frequency $\partial \phi / \partial t$')
    plt.title('Frequency + Phase-gradient Field')

 
def show_pgrad_norm(movie, frame):

    plt.figure()
    # get the gradient vectorfield
    dY, dX = gf.phase_gradient(movie[frame, ...])

    # and the norm of those
    pgn = get_phase_gradient_norm(dY, dX)
    
    plt.contour(movie[frame], levels=15, cmap='gray_r', linewidths=1.2)
    pl.show_vfield(-dX, -dY, skip=2, vlen_perc=90)

    plt.imshow(pgn, interpolation='nearest', cmap='viridis_r',
               vmax=np.percentile(pgn.flatten(), 90))
    plt.axis('off')

    cb = plt.colorbar()
    cb.set_label(r'Phase gradient norm $|\nabla \phi|$')
    plt.title('Phase-gradient norm + Phase-gradient Field')


def show_velo_pgrad(movie, frame):

    plt.figure()

    # get the gradient vectorfield
    dY, dX = gf.phase_gradient(movie[frame, ...])

    # and the norm of those
    pgn = get_phase_gradient_norm(dY, dX)

    # now get the phase velocities
    velo = fmovie[frame]/pgn
        
    plt.contour(movie[frame], levels=10, cmap='Purples', linewidths=.8)
    pl.show_vfield(-dX, -dY, skip=2, vlen_perc=80)

    plt.imshow(velo, interpolation='gaussian', cmap='Oranges_r',
               vmax=np.percentile(velo.flatten(), 98))
    plt.axis('off')

    cb = plt.colorbar()
    cb.set_label(r'Phase velocity $\partial_t \phi / |\nabla \phi|$')
    plt.title('Phase velocity field + gradient')
    

