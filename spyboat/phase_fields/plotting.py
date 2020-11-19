import sys
from os.path import expanduser
import numpy as np
from numpy import pi

from numpy.ma import masked_array
from scipy.stats import scoreatpercentile as score

import matplotlib.cm as cm
from matplotlib.colors import Normalize,ListedColormap
import matplotlib.pyplot as ppl
import seaborn as sns

import grad_flux as gf
ppl.ion()

# Husl diverging
div_cmap = sns.diverging_palette(240,20,n = 100,
                             sep = 10, center = 'dark', as_cmap = True)

flux_cm = 'RdGy_r'

def show_vfield(vx, vy, skip = 5, vlen_perc = None, color = 'k', width = 0.0015):

    ''' 
    Assumes underlying rectangular grid with shape = vx.shape 
    Removes long vectors with a score higher then vlen_perc
    Plots on active figure.
    ''' 

    # threshold vectors to remove large outliers
    vlen = gf.vec_len(vx[::skip,::skip], vy[::skip,::skip])


    if vlen_perc is None:
        vc = np.where(vlen) # complete coordinate arrays
    else:
        vlen_range = score(vlen, vlen_perc)        
        vc = np.where(vlen < vlen_range) # 1d coordinate array

    # 1d vector component sequences
    # plots on the active axis!
    dy_flat = vy[vc[0]*skip, vc[1]*skip]
    dx_flat = vx[vc[0]*skip, vc[1]*skip]

    norm.autoscale( gf.vec_len(dx_flat, dy_flat) )

    # x,y ordering as opposed to y,x for arrays (and imshow)!!
    ppl.quiver(vc[1]*skip, vc[0]*skip, dx_flat, dy_flat, angles = 'xy',
               color = color, width = width)

    # cmap(norm(vec_len(dx_flat, dy_flat))))

    return vc[1]*skip, vc[0]*skip, -dx_flat, -dy_flat
    
def show_gradient( frame, skip = 5, vlen_perc = 99, title = None):


    pdx, pdy, _ = gf.get_masked_gradient(frame, mask_value = 0)

    # -grad phi
    vx, vy = -pdx, -pdy



    fig, ax = ppl.subplots()

    im = ax.imshow(frame, vmin = -pi, vmax = pi, cmap = 'bwr')#, vmin = -pi, vmax = pi)

    show_vfield(vx, vy, skip = skip, vlen_perc = vlen_perc, width = 0.0025)

    cb = ppl.colorbar(im,ax = ax, shrink = 0.35, orientation = 'horizontal', pad = 0.02)
    cb.set_ticks( [-pi, -pi/2, 0, pi/2, pi] )
    cb.set_ticklabels( [r'$-\pi$', r'$-\pi/2$', 0, r'$\pi/2$', r'$\pi$'] )
    cb.ax.tick_params(labelsize=8)

    
    ax.set_title('frame {}'.format(title))
    ax.axis('off')
    fig.subplots_adjust(left = 0, right = 1, bottom = 0, top = 1)





def show_flux_grad(frame, k = 15, vlen_perc = 99,
                   flux_perc = 98, skip = 10, show_masked = True):

    pdx, pdy, mask = gf.get_masked_gradient(frame, mask_value = frame[0,0])
    # -grad phi
    vx, vy = -pdx, -pdy

    fig, ax = ppl.subplots(num = 1); fig.clf(); ax = fig.gca()
    im = ax.imshow(frame, cmap = 'bwr', vmin = -pi, vmax = pi)
    show_vfield(vx, vy, skip = skip, vlen_perc = vlen_perc)
    cb = ppl.colorbar(im,ax = ax, shrink = 0.7)
    cb.set_ticks( [-pi, -pi/2, 0, pi/2, pi] )
    cb.set_ticklabels( [r'$-\pi$', r'$-\pi/2$', 0, r'$\pi/2$', r'$\pi$'] )
    ax.axis('off')

    # # -- flux calculation --

    flux = gf.calculate_flux(vx, vy, k = k, nested = True)
    flux = masked_array(flux, mask = ~mask)


    fig2 = ppl.figure(num = 2); fig2.clf(); ax2 = fig2.gca()
    flux_range = score(abs(flux.flatten()), flux_perc)
    print( 'flux range: {:.3f}'.format(flux_range) )
    # mask flux
    flux_m = masked_array(flux, mask = (flux > flux_range) | (flux < -flux_range))

    # cmap.set_under('0.73')
    # cmap.set_over('0.73')

    if show_masked:
        im2 = ax2.imshow(flux_m, cmap = flux_cm, vmax = flux_range, vmin = -flux_range)
    else:
        im2 = ax2.imshow(flux, cmap = flux_cm, vmax = flux_range, vmin = -flux_range)
    ax2.axis('off')
    
    cb = ppl.colorbar(im2,ax = ax2, shrink = 0.7)
    cb.set_ticks( cb.get_ticks()[::2] )
    # vector field on flux
    show_vfield(vx, vy, skip = skip, vlen_perc = vlen_perc, color = 'teal', width = 0.001)

    return flux_m

def mk_flux_tifs(movie, k = 15, flux_range = 0.1, skip = 8, show_masked = False):
    
    ppl.ioff()
    
    for i,frame in enumerate(movie):
        print('Plotting frame ',i)
        pdx, pdy, mask = gf.get_masked_gradient(frame, mask_value = frame[0,0])
        # -grad phi
        vx, vy = -pdx, -pdy
        
        flux = gf.calculate_flux(vx, vy, k = k)
        # flux = masked_array(flux, mask = ~mask)
        flux_m = masked_array(flux, mask = (flux > flux_range) | (flux < -flux_range))
        
        fig = ppl.figure(num = 134) ; fig.clear() ; ax = fig.gca()
        if show_masked:
            im = ax.imshow(flux_m, cmap = flux_cm, vmax = flux_range, vmin = -flux_range)
        else:
            im = ax.imshow(flux, cmap = flux_cm, vmax = flux_range, vmin = -flux_range)
        # vector field on flux
        show_vfield(vx, vy, skip = skip, vlen_perc = 100, color = 'teal', width = 0.001)

        cb = ppl.colorbar(im,ax = ax, shrink = 0.7)
        cb.set_ticks( cb.get_ticks()[::2] )
        

        ax.axis('off')
        fig.subplots_adjust(left = 0, right = 1, bottom = 0, top = 1)
        fig.savefig(tif_out_dir + f'flux_frame{i}.tif', dpi = DPI)

    ppl.ion()

def mk_gradient_tifs(movie, skip = 7):

    ppl.ioff()
    
    for i,frame in enumerate(movie):
        print('Plotting frame ',i)
        pdx, pdy, mask = gf.get_masked_gradient(frame, mask_value = frame[0,0])
        # -grad phi
        vx, vy = -pdx, -pdy
        
        fig = ppl.figure(num = 134) ; fig.clear() ; ax = fig.gca()
        im = ax.imshow(frame, cmap = 'bwr', vmin = -pi, vmax = pi)

        cb = ppl.colorbar(im,ax = ax, shrink = 0.5)
        cb.set_ticks( [-pi, -pi/2, 0, pi/2, pi] )
        cb.set_ticklabels( [r'$-\pi$', r'$-\pi/2$', 0, r'$\pi/2$', r'$\pi$'] )
        
        
        # vector field on flux
        show_vfield(vx, vy, skip = skip, vlen_perc = 98, color = 'k', width = 0.001)

        ax.axis('off')
        fig.subplots_adjust(left = 0, right = 1, bottom = 0, top = 1)
        fig.savefig(tif_out_dir + f'grad_frame{i}.tif', dpi = DPI)

    ppl.ion()
    

# get test data

if __name__ == '__main__':
    
    print("Loading demo data..")
    from demo_data import RAFL1, RAFL2, L6SO

# for the tif pyplots
cmap = cm.gray
norm = Normalize() # initiate normalizing instance

DPI = 180
# local output directory
tif_out_dir = expanduser('~/tif_dir/')

#--------
#im = RAFL1
#im = Luim1
#im = Axim
#--------

