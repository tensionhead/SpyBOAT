import sys
from os.path import expanduser
import numpy as np

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
               color = 'k', width = width)

    # cmap(norm(vec_len(dx_flat, dy_flat))))

    return vc[1]*skip, vc[0]*skip, -dx_flat, -dy_flat
    
def show_gradient( frame, skip = 5, vlen_perc = 99, title = None):


    pdx, pdy, _ = gf.get_masked_gradient(frame, mask_value = 0)

    # -grad phi
    vx, vy = -pdx, -pdy



    fig, ax = ppl.subplots()

    ax.imshow(frame, cmap = 'bwr')#, vmin = -pi, vmax = pi)

    show_vfield(vx, vy, skip = skip, vlen_perc = vlen_perc)

    ax.set_title('frame {}'.format(title))
    ax.axis('off')
    fig.subplots_adjust(left = 0, right = 1, bottom = 0, top = 1)





def show_flux_grad(frame, k = 15, vlen_perc = 99, flux_perc = 98, skip = 10):

    pdx, pdy, mask = get_masked_gradient(frame, mask_value = frame[0,0])
    # -grad phi
    vx, vy = -pdx, -pdy

    fig, ax = ppl.subplots(num = 1)
    ax.imshow(frame, cmap = 'bwr')
    show_vfield(vx, vy, skip = skip, vlen_perc = vlen_perc)
    ax.axis('off')

    # # -- flux calculation --

    C_flux = mk_nested_C_flux(vx.shape, k = k)
    # C_flux = mk_C_flux(vx.shape, k = k) # old style with single curve
    flux = calculate_flux(vx, vy, C_flux)
    flux = masked_array(flux, mask = ~mask)


    fig2 = ppl.figure(num = 2); fig2.clf(); ax2 = fig2.gca()
    flux_range = score(abs(flux.flatten()), flux_perc)
    print( 'flux range: {:.3f}'.format(flux_range) )
    # mask flux
    flux_m = masked_array(flux, mask = (flux > flux_range) | (flux < -flux_range))

    # cmap.set_under('0.73')
    # cmap.set_over('0.73')
    im = ax2.imshow(flux, cmap = flux_cm, vmax = flux_range, vmin = -flux_range)
    ax2.axis('off')
    
    ppl.colorbar(im,ax = ax2)
    # vector field on flux
    show_vfield(vx, vy, skip = skip, vlen_perc = vlen_perc, color = 'k')

    return flux, mask

def mk_flux_tifs(movie, k = 15, flux_range = 0.1, skip = 8):
    
    ppl.ioff()
    
    for i,frame in enumerate(movie):
        print('Plotting frame ',i)
        pdx, pdy, mask = get_masked_gradient(frame, mask_value = frame[0,0])
        # -grad phi
        vx, vy = -pdx, -pdy
        
        C_flux = mk_nested_C_flux(vx.shape, k = k)
        flux = calculate_flux(vx, vy, C_flux)
        flux = masked_array(flux, mask = ~mask)

        fig = ppl.figure(num = 134) ; fig.clear() ; ax = fig.gca()
        im = ax.imshow(flux, cmap = 'RdGy_r', vmax = flux_range, vmin = -flux_range)
        # vector field on flux
        show_vfield(vx, vy, skip = skip, vlen_perc = 98, color = 'k')

        ax.axis('off')
        fig.subplots_adjust(left = 0, right = 1, bottom = 0, top = 1)
        fig.savefig(tif_out_dir + f'flux_frame{i}.tif', dpi = DPI)

    ppl.ion()

def mk_gradient_tifs(movie, skip = 7):

    ppl.ioff()
    
    for i,frame in enumerate(movie):
        print('Plotting frame ',i)
        pdx, pdy, mask = get_masked_gradient(frame, mask_value = frame[0,0])
        # -grad phi
        vx, vy = -pdx, -pdy
        
        fig = ppl.figure(num = 134) ; fig.clear() ; ax = fig.gca()
        ax.imshow(frame, cmap = 'bwr', vmin = -pi, vmax = pi)
        
        # vector field on flux
        show_vfield(vx, vy, skip = skip, vlen_perc = 98, color = 'k')

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

