import numpy as np

from numpy import pi, cos, sin,exp
from numpy.ma import masked_array

import matplotlib.cm as cm
from matplotlib.colors import Normalize
import matplotlib.pyplot as ppl
import seaborn as sns

ppl.ion()

import grad_flux as gf
import plotting as pl


flux_cm = 'RdGy_r'
# flux_cm = 'BrBG'

# Husl diverging
div_cmap = sns.diverging_palette(240,60,n = 100,s = 90,
                             sep = 10, center = 'light', as_cmap = True)

# flux_cm = div_cmap


def channel_field(L = 50, H = 21, k = 1, eps = 0):

    '''
    Simple flow field in a quadratic domain
    -> plot with aspect ratio

    '''

    aspect = 1.
    skip = 5

    ramp1d = np.linspace(5, 0, L)

    field = np.ones( (H,L) ).dot( np.diag(ramp1d) )

    
    # laminar flow is no gradient field!
    # ys = np.arange(0, LH) - LH/2 + 0.5 
    # vprofile = 1 - 4 * ys**2 / LH**2    
    # field = np.outer(vprofile, ramp1d)
    

    dy, dx = np.gradient( field )

    dy = -dy
    dx = -dx

    print(field.shape, dx.shape)

    # show gradient
    fig, ax = ppl.subplots()
    ax.imshow(field, cmap = 'bwr', aspect = aspect)
    pl.show_vfield(dx, dy, skip = skip, width = 0.003)


    # defining the closed curve in matrix form
    C_flux = gf.mk_nested_C_flux(dx.shape, k = k)
    flux = gf.calculate_quad_flux(dx, dy, C_flux)

    # flux = gf.calculate_flux(dx, dy, k=k)


    fig2, ax2 = ppl.subplots()
    flux_range = max( (flux.max(), -flux.min()) )
    im = ax2.imshow(flux, cmap = flux_cm, aspect = aspect,
                    vmin = -flux_range, vmax = flux_range)
    pl.show_vfield(dx, dy, skip = skip, width = 0.003)
    ppl.colorbar(im,ax = ax2)

    
    return field
    
def rad_field(R = 50, k = 1, a2 = 0, eps = 0):

    '''
    Synthetic radial (non-phase) field(s).

    a2 - strength of 2nd field.

    k - radius of flux calculation curve

    eps - noise intensity
    '''

    yy, xx = np.meshgrid( np.arange(R), np.arange(R) )

    r_pot = lambda x,y: (np.sqrt((x-R/3)**2 + (y-R/3)**2))
    r_pot2 = lambda x,y: (np.sqrt((x-R/1.5)**2 + (y-R/1.5)**2))

    rp = r_pot(xx,yy) + a2*r_pot2(xx,yy) + eps*np.random.randn(R,R)

    rp = rp[:30,:]
    mask = rp < 2*rp.max()/3
    rp = masked_array(rp, mask = ~mask)
    
    dy, dx = np.gradient( rp )

    # strange numbers at masked places..fill with zeros (unmask gradient)
    dy[dy.mask] = 0
    dx[dx.mask] = 0

    # show gradient
    # fig, ax = ppl.subplots()
    # ax.imshow(rp, cmap = 'bwr')
    # pl.show_vfield(dx, dy, skip = int(R/17), width = 0.003)

    flux = gf.calculate_flux(dx, dy, k = k)

    flux = masked_array(flux, mask = ~mask)
    
    fig2, ax2 = ppl.subplots()
    flux_range = max( (flux.max(), -flux.min()) )
    im = ax2.imshow(flux, cmap = flux_cm, vmin = -flux_range, vmax = flux_range)
    pl.show_vfield(dx, dy, skip = int(R/17), width = 0.003)
    ppl.colorbar(im,ax = ax2)


    # profiles
    # fig3 = ppl.figure(num = 13)
    # ax3 = ppl.gca()
    # ax3.plot(flux[int(R/3),:])
    # ax3.plot(flux[:,int(R/3)])
    # ax3.plot(rp[int(R/3),:],'--')
    #ax3.set_ylim( (-3,15) )

    return dx, dy

