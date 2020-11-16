''' Some convenience plotting functions '''
import matplotlib.pylab as ppl
from numpy import pi

def phase_snapshot(snapshot):

    cmap = ppl.get_cmap('bwr')
    cmap.set_under('gray')
    fig,ax = ppl.subplots()
    im = ax.imshow(snapshot,
               cmap = 'bwr', vmin = 0, vmax = 6.2832)
    
    cb = ppl.colorbar(im, shrink = 0.9, ax = ax)
    cb.set_label('Phase [rad]')
    cb.set_ticks([0, pi/2, pi, 3/2 * pi, 2*pi])
    # looks better, but you don't get the values by hovering over the plot
    # cb.set_ticklabels(['0', '$\pi/2$', '$\pi$', '$3/4 \pi$','$2\pi$'])    
    ax.axis('off')
    

def period_snapshot(snapshot, Tmin, Tmax, time_unit = 'h'):

    cmap = ppl.get_cmap('magma_r')
    cmap.set_under('gray')
    fig,ax = ppl.subplots()
    
    im = ax.imshow(snapshot,
               cmap = 'magma_r',
               vmin = Tmin, vmax = Tmax)
    
    cb = ppl.colorbar(im, shrink = 0.9, ax = ax)
    cb.set_label(f'Period [{time_unit}]')
    ax.axis('off')
