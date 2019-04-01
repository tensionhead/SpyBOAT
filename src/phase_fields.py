import sys
from os.path import expanduser
import numpy as np
import matplotlib.pyplot as ppl
from numpy import pi, cos, sin,exp
from numpy.ma import masked_array
from skimage import measure
from skimage.io import imread
import scipy.ndimage as ndi
from scipy.stats import scoreatpercentile as score

import matplotlib.cm as cm
from matplotlib.colors import Normalize

from scipy.interpolate import splprep
from scipy import interpolate
from glob import glob
ppl.ion()

def vec_len(dy, dx):

    return np.sqrt( dx**2 + dy**2 )

def pgradient(phase_field):

    ''' 
    "repairs" the central differences of np.gradient
    to accomodate for phase differences
    '''

    dy, dx = np.gradient(phase_field)
    
    # central difference denominator
    qq = 2 * np.ones( phase_field.shape )
    qq[0,:] = 1; qq[-1,:] = 1; qq[:,0] = 1; qq[:,-1] = 1

    dx = qq * dx # element wise, recover central differences
    pdx = np.arctan2( sin(dx), cos(dx) ) # 'central phase difference'

    dy = qq * dy # element wise, recover central differences    
    pdy = np.arctan2( sin(dy), cos(dy) )

    # normalize again for central difference distance
    return pdy/qq, pdx/qq

def mk_flux_c(vx, k = 1):

    ''' 
    Defines the closed curve in matrix form

    k: width of the closed grid curve

    only for quadratic grids so far... 
    '''

    m = np.ones( vx.shape ) # to extract 1-diagonals
    
    flux_c = -np.diag( np.diag(m, k = k), k = k )
    flux_c = flux_c + np.diag( np.diag(m, k = -k), k = -k )

    # didn't help
    #if mask is not None:
    #    flux_c = masked_array(flux_c, mask = mask)
    
    return flux_c

def calculate_flux(vx, vy, flux_c):

    '''
    Given a flux-curve matrix, evaluate the 'integrals'
    '''

    assert vx.shape == flux_c.shape

    # x-direction
    fx = vx.dot(flux_c)

    # y-direction
    fy = flux_c.T.dot(vy)

    flux = fx + fy

    return flux


def show_vfield(vx, vy, skip = 5, vlen_perc = None, color = 'k'):

    ''' 
    Assumes underlying rectangular grid with shape = vx.shape 
    Plots on active figure.
    ''' 

    # threshold vectors to remove large outliers
    vlen = vec_len(vx[::skip,::skip], vy[::skip,::skip])


    if vlen_perc is None:
        vc = np.where(vlen) # complete coordinate arrays
    else:
        vlen_range = score(vlen, vlen_perc)        
        vc = np.where(vlen < vlen_range) # 1d coordinate array

    # 1d vector component sequences
    # plots no the active axis!
    dy_flat = vy[vc[0]*skip, vc[1]*skip]
    dx_flat = vx[vc[0]*skip, vc[1]*skip]

    norm.autoscale( vec_len(dx_flat, dy_flat) )

    # x,y ordering as opposed to y,x for arrays (and imshow)!!
    ppl.quiver(vc[1]*skip, vc[0]*skip, dx_flat, dy_flat, angles = 'xy',
               color = 'k')

    # cmap(norm(vec_len(dx_flat, dy_flat))))

    return vc[1]*skip, vc[0]*skip, -dx_flat, -dy_flat
    
def show_gradient( frame, skip = 5, vlen_perc = 99, title = None):


    pdx, pdy, _ = get_masked_gradient(frame, mask_value = 0)

    # -grad phi
    vx, vy = -pdx, -pdy



    fig, ax = ppl.subplots()

    ax.imshow(frame, cmap = 'bwr')#, vmin = -pi, vmax = pi)

    show_vfield(vx, vy, skip = skip, vlen_perc = vlen_perc)

    ax.set_title('frame {}'.format(title))
    ax.axis('off')
    fig.subplots_adjust(left = 0, right = 1, bottom = 0, top = 1)



def get_masked_gradient(frame, mask_value = 0):

    # the mask
    mask = frame != mask_value

    # make a masked array
    frame = masked_array(frame, mask = ~mask)

    yy, xx = np.meshgrid( np.arange(frame.shape[1]), np.arange(frame.shape[0]) )

    pdy, pdx = pgradient(frame)

    # strange numbers at masked places..fill with zeros (unmask gradient)
    pdy[pdy.mask] = 0
    pdx[pdx.mask] = 0

    return pdx, pdy, mask
# sys.exit()



def show_flux_grad(frame, k = 15, vlen_perc = 99, skip = 10):

    pdx, pdy, mask = get_masked_gradient(frame, mask_value = frame[0,0])
    # -grad phi
    vx, vy = -pdx, -pdy

    fig, ax = ppl.subplots(num = 1)
    ax.imshow(frame, cmap = 'bwr')
    show_vfield(vx, vy, skip = skip, vlen_perc = vlen_perc)
    ax.axis('off')

    # # -- flux calculation --

    flux_c = mk_flux_c(vx, k = k)
    flux = calculate_flux(vx, vy, flux_c)
    flux = masked_array(flux, mask = ~mask)


    fig2, ax2 = ppl.subplots(num = 2)
    flux_range = score(abs(flux.flatten()), 98)
    print( 'flux range: {:.3f}'.format(flux_range) )
    im = ax2.imshow(flux, cmap = 'plasma', vmax = flux_range, vmin = -flux_range)
    ax2.axis('off')
    
    ppl.colorbar(im,ax = ax2)
    # vector field on flux
    show_vfield(vx, vy, skip = skip, vlen_perc = vlen_perc, color = 'k')


def mk_flux_tifs(movie, k = 15, flux_range = 0.1):
    
    ppl.ioff()
    
    for i,frame in enumerate(movie):
        print('Plotting frame ',i)
        pdx, pdy, mask = get_masked_gradient(frame, mask_value = frame[0,0])
        # -grad phi
        vx, vy = -pdx, -pdy
        
        flux_c = mk_flux_c(vx, k = k)
        flux = calculate_flux(vx, vy, flux_c)
        flux = masked_array(flux, mask = ~mask)

        fig = ppl.figure(num = 134) ; fig.clear() ; ax = fig.gca()
        im = ax.imshow(flux, cmap = 'plasma', vmax = flux_range, vmin = -flux_range)
        # vector field on flux
        show_vfield(vx, vy, skip = 10, vlen_perc = 98, color = 'k')

        ax.axis('off')
        fig.subplots_adjust(left = 0, right = 1, bottom = 0, top = 1)
        fig.savefig(tif_out_dir + 'flux_frame{}.tif'.format(i), dpi = DPI)

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
        fig.savefig(tif_out_dir + 'grad_frame{}.tif'.format(i), dpi = DPI)

    ppl.ion()
    

# synthetic field
def synth_field(R = 50, k = 1, a2 = 0, eps = 0):

    yy, xx = np.meshgrid( np.arange(R), np.arange(R) )

    r_pot = lambda x,y: (np.sqrt((x-R/3)**2 + (y-R/3)**2))
    r_pot2 = lambda x,y: (np.sqrt((x-R/1.5)**2 + (y-R/1.5)**2))

    rp = r_pot(xx,yy) + a2*r_pot2(xx,yy) + eps*np.random.randn(R,R)

    mask = rp < 2*rp.max()/3
    rp = masked_array(rp, mask = ~mask)
    
    dy, dx = np.gradient( rp )

    # strange numbers at masked places..fill with zeros (unmask gradient)
    dy[dy.mask] = 0
    dx[dx.mask] = 0

    fig, ax = ppl.subplots()
    ax.imshow(rp, cmap = 'bwr')
    show_vfield(dx, dy, skip = int(R/15))


    # defining the closed curve in matrix form
    flux_c = mk_flux_c(dx, k = k)
    flux = calculate_flux(dx, dy, flux_c)
    flux = masked_array(flux, mask = ~mask)
    fig2, ax2 = ppl.subplots()
    ax2.imshow(flux, cmap = 'plasma')
    show_vfield(dx, dy, skip = int(R/15))


    fig3 = ppl.figure(num = 13)
    ax3 = ppl.gca()
    ax3.plot(flux[int(R/3),:])
    ax3.plot(flux[:,int(R/3)])
    ax3.plot(rp[int(R/3),:],'--')
    #ax3.set_ylim( (-3,15) )

    return dx, dy

    
# ------ the fun starts ---



# own cloud directory
# Axim = imread('../good_ones/masked_phase_sigma10_Axin_0905.tif', dtype = np.int16)
# Luim1 = imread('../good_ones/masked_sigma10_phase_20180905_Luvelu_L1.tif')

data_dir = expanduser('~/ownCloud/Shared/Luvelu_cell-ablation/')

# (local) data directory
# data_dir = expanduser('~/PSM/data/phase_field_data/')

g = glob(data_dir + '*mask*phase*.tif')
print(g)
# L6SO = imread(g[0])
# RAFL1 = imread(g[1])
# RAFL2 = imread(g[2])

cmap = cm.gray
norm = Normalize() # initiate normalizing instance

# local output directory
tif_out_dir = expanduser('~/tif_dir/')


# for the pyplots
DPI = 180
#--------
#im = RAFL1
#im = Luim1
#im = Axim
#--------

