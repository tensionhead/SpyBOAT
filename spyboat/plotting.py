""" Some convenience plotting functions """
import matplotlib.pylab as ppl
from numpy import pi
import numpy as np

from pyboat.core import complex_average

# same for all snapshots
margins = {'left' : 0.01, 'right':0.95, 'top':0.94, 'bottom':0.01}

FONT_SIZE = 18

def phase_snapshot(snapshot, title='Phase'):

    cmap = ppl.get_cmap("bwr")
    cmap.set_under("gray")
    fig, ax = ppl.subplots()
    im = ax.imshow(snapshot, cmap=cmap, vmin=0, vmax=6.2832)

    cb = ppl.colorbar(im, shrink=0.9, ax=ax)
    cb.set_label("Phase [rad]")
    cb.set_ticks([0, pi / 2, pi, 3 / 2 * pi, 2 * pi])
    # looks better, but you don't get the values by hovering over the plot
    # cb.set_ticklabels(['0', '$\pi/2$', '$\pi$', '$3/4 \pi$','$2\pi$'])
    ax.axis("off")
    ax.set_title(title, fontsize=18)
    fig.subplots_adjust(**margins)

    return ax


def period_snapshot(snapshot, Tmin, Tmax, title='Period', time_unit="a.u."):
    
    cmap = ppl.get_cmap("magma_r")
    cmap.set_under("gray")
    fig, ax = ppl.subplots()

    im = ax.imshow(snapshot, cmap=cmap, vmin=Tmin, vmax=Tmax)

    cb = ppl.colorbar(im, shrink=0.9, ax=ax)
    cb.set_label(f"Period [{time_unit}]")
    ax.axis("off")
    ax.set_title(title, fontsize=FONT_SIZE)
    fig.subplots_adjust(**margins)
    
    return ax


def amplitude_snapshot(snapshot, vmax=None,
                       title='Amplitude', unit="a.u."):

    '''
    Pretty generic, could also be used for the power movie
    '''
    
    cmap = ppl.get_cmap("copper")
    cmap.set_under("gray")
    fig, ax = ppl.subplots()

    im = ax.imshow(snapshot, vmin=0, vmax=vmax, cmap=cmap)

    cb = ppl.colorbar(im, shrink=0.9, ax=ax)
    cb.set_label(f"{title} [{unit}]")
    ax.axis("off")
    ax.set_title(title, fontsize=FONT_SIZE)
    fig.subplots_adjust(**margins)

    return ax

def input_snapshot(snapshot, title='Input', unit='a.u'):

    # input movie snapshot
    fig, ax = ppl.subplots()
    im = ax.imshow(snapshot, cmap='cividis')
    cb = ppl.colorbar(im, shrink=0.9, ax=ax)
    cb.set_label(f'Intensity [{unit}]')
    ppl.axis('off')
    ax.set_title(title, fontsize=FONT_SIZE)
    fig.subplots_adjust(**margins)

    return ax


def compute_distr_dynamics(movie, mask_value = -1):

    '''
    Calculates median and quartiles for every frame.
    Adheres to spyboats stack ordering: (Frames,Y,X)
    and skips over pixels with the *mask_value*.
    '''

    res = {'median' : [], 'q1' : [], 'q3' : []}
    for img in movie:
        
        # flattened
        values = img[img!=mask_value]
        med = np.median(values)
        q1 = np.percentile(values, 25)
        q3 = np.percentile(values, 75)
        res['median'].append(med)
        res['q1'].append(q1)
        res['q3'].append(q3)

    return res

def period_distr_dynamics(period_movie, Wkwargs, mask_value = -1):

    '''
    Pass Wkwargs for axis range and time units.
    '''

    dis = compute_distr_dynamics(period_movie, mask_value)

    fig, ax = ppl.subplots()

    # to match with snapshots show only frames on the x-axis
    xvec = np.arange(period_movie.shape[0]) #* Wkwargs['dt']
    
    ax.plot(xvec, dis['median'], lw = 2.5, alpha = 0.9,
            color = 'cornflowerblue')
    ax.fill_between(xvec, dis['q1'], dis['q3'], color='cornflowerblue',
                    alpha = 0.3)
    ax.plot(xvec, np.ones_like(xvec)* Wkwargs['Tmin'],
            '--', lw=1.5, c='#3f939e')
    ax.plot(xvec, np.ones_like(xvec)* Wkwargs['Tmax'],
            '--', lw=1.5, c='#3f939e',label='Tmin, Tmax')
    # ax.legend(fontsize=FONT_SIZE-2)
    
    ax.set_ylim( (0.95*Wkwargs['Tmin'],1.05*Wkwargs['Tmax']) )
    ax.set_xlabel('Frame Nr.', fontsize=FONT_SIZE)
    ax.set_ylabel('Period [a.u.]', fontsize=FONT_SIZE)
    ax.grid(axis='y')
    ax.set_title("Period dynamics", fontsize=18)

def power_distr_dynamics(power_movie, Wkwargs, mask_value = -1):

    '''
    Pass Wkwargs for time units.
    '''

    dis = compute_distr_dynamics(power_movie, mask_value)

    fig, ax = ppl.subplots()

    xvec = np.arange(power_movie.shape[0]) #* Wkwargs['dt']
    
    ax.plot(xvec, dis['median'], lw = 2.5, alpha = 0.9,
            color = 'darkgray')
    ax.fill_between(xvec, dis['q1'], dis['q3'], color = 'darkgray',
                    alpha = 0.3)
    ax.set_xlabel('Frame Nr.', fontsize=FONT_SIZE)
    ax.set_ylabel('Power [wnp]', fontsize=FONT_SIZE)
    ax.grid(axis='y')
    ax.set_title("Wavelet Power dynamics", fontsize=FONT_SIZE)

def phase_coherence_dynamics(phase_movie, Wkwargs, mask_value = -1):

    '''
    Kuramoto Order paramter over time.
    Pass Wkwargs for time units.
    '''

    Rs = []
    for img in phase_movie:
        
        # flattened
        values = img[img!=mask_value]
        R, Psi = complex_average(values)
        Rs.append(R)

    fig, ax = ppl.subplots()

    xvec = np.arange(phase_movie.shape[0]) #* Wkwargs['dt']
    
    ax.plot(xvec, Rs, lw = 3.5, alpha = 0.7,
            color = 'crimson')
    ax.set_xlabel('Frame Nr.', fontsize=FONT_SIZE)
    ax.set_ylabel('Phase coherence', fontsize=FONT_SIZE)
    ax.set_ylim( (-.05, 1.1) )
    ax.grid(axis='y')
    ax.set_title("Phase Coherence dynamics", fontsize=FONT_SIZE)
    
