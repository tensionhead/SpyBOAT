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


def channel_field(L = 50, H = 21, k = 1):

    '''
    Simple uniform flow field in a rectangular domain
    '''

    skip = 5
    aspect = 0.5 * L/H
    w = 0.005

    ramp1d = np.linspace(L+1, 0, L)

    field = np.ones( (H,L) ).dot( np.diag(ramp1d) )

    
    # laminar flow is no gradient field!
    # ys = np.arange(0, LH) - LH/2 + 0.5 
    # vprofile = 1 - 4 * ys**2 / LH**2    
    # field = np.outer(vprofile, ramp1d)
    

    dy, dx = np.gradient( field )

    dy = -dy
    dx = -dx


    # show gradient
    fig, ax = ppl.subplots(num = 77, figsize = (7,3))
    fig.clf(); ax = ppl.gca()
    im = ax.imshow(field, cmap = 'bwr', aspect = aspect)
    pl.show_vfield(dx, dy, skip = skip, width = w)

    cb1 = ppl.colorbar(im,ax = ax, shrink = 0.8)
    # cb1.set_ticks( )

    
    # flux
    flux = gf.calculate_flux(dx, dy, k=k, nested = False)

    fig2, ax2 = ppl.subplots(num = 78, figsize = (7,3))
    fig2.clf(); ax2 = ppl.gca()
    
    flux_range = max( (flux.max(), -flux.min()) )
    im = ax2.imshow(flux, cmap = flux_cm, aspect = aspect,
                    vmin = -flux_range*1.2, vmax = flux_range*1.2)
    pl.show_vfield(dx, dy, skip = skip, width = w)
    cb = ppl.colorbar(im,ax = ax2, shrink = 0.8)
    cb.set_ticks( [1,.5,0,-.5,-1] )

    ax.axis('off')
    ax2.axis('off')    

    #channel walls
    ax.fill_between(np.arange(-1,L+1),-1,int(-1-H/9), color = '#332d27', alpha = 0.5)
    ax.fill_between(np.arange(-1,L+1),H,int(H + H/9), color = '#332d27', alpha = 0.5)

    ax2.fill_between(np.arange(-1,L+1),-1,int(-1-H/9), color = '#332d27', alpha = 0.5)
    ax2.fill_between(np.arange(-1,L+1),H,int(H + H/9), color = '#332d27', alpha = 0.5)

    
    return field
    
def rad_field(R = 50, k = 1, a2 = 0, eps = 0, nested = True):

    '''
    Synthetic radial (non-phase) field(s).

    a2 - strength of 2nd field.

    k - radius of flux calculation curve

    eps - noise intensity
    '''

    np.random.seed(14314)
    
    yy, xx = np.meshgrid( np.arange(R), np.arange(R) )

    pos1 = 2.8
    
    r_pot = lambda x,y: (np.sqrt((x-R/pos1)**2 + (y-R/pos1)**2))
    r_pot2 = lambda x,y: (np.sqrt((x-R/1.5)**2 + (y-R/1.5)**2))

    rp = r_pot(xx,yy) + a2*r_pot2(xx,yy) + eps*np.random.randn(R,R)

    mask = rp < 2*rp.max()/3
    rp = masked_array(np.abs(rp - 2*rp.max()/3), mask = ~mask)
    
    dy, dx = np.gradient( rp )

    # -grad
    dx = -dx; dy = -dy

    # strange numbers at masked places..fill with zeros (unmask gradient)
    dy[dy.mask] = 0
    dx[dx.mask] = 0

    # show gradient
    fig, ax = ppl.subplots(num = 79)
    fig.clf(); ax = ppl.gca()    
    im = ax.imshow(rp, cmap = 'bwr')
    # pl.show_vfield(dx, dy, skip = int(R/16), width = 0.004)
    ppl.colorbar(im,ax = ax, shrink = 0.7)

    #flux
    flux = gf.calculate_flux(dx, dy, k = k, nested = nested)
    flux = masked_array(flux, mask = ~mask)
    
    fig2, ax2 = ppl.subplots(num = 80)
    fig2.clf(); ax2 = ppl.gca()
    
    flux_range = max( (flux.max(), -flux.min()) )
    im = ax2.imshow(flux, cmap = flux_cm, vmin = -flux_range, vmax = flux_range)
    # pl.show_vfield(dx, dy, skip = int(R/16), width = 0.003)
    ppl.colorbar(im,ax = ax2, shrink = 0.7)

    ax.axis('off')
    ax2.axis('off')    
    
    # profiles
    # fig3 = ppl.figure(num = 13)
    # ax3 = ppl.gca()
    # ax3.plot(flux[int(R/3),:])
    # ax3.plot(flux[:,int(R/3)])
    # ax3.plot(rp[int(R/3),:],'--')
    #ax3.set_ylim( (-3,15) )

    
    
    return rp, flux


# plot the Fiji profiles

