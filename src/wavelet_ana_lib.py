###########################################################################
# Tools for time-frequency analysis with Morlet Wavelets
# Inspired by 'A Practical Guide to Wavelet Analysis' from Torrence
# and Compo 1998
# and 'Identification of Chirps with Continuous Wavelet Transform'
# from Carmona,Hwang and Torresani 1995
#
# Version 0.4 June 2018, Gregor Moenke (gregor.moenke@embl.de)
###########################################################################

import numpy as np
from numpy import cos, pi, sin, sqrt

# =============WAVELETS=======================================================
omega0 = 2 * pi


def scales_from_periods(periods, sfreq, omega0):
    scales = (omega0 + sqrt(2 + omega0 ** 2)) * periods * sfreq / (4 * pi)  # conversion from periods to morlet scales
    return scales


def Morlet_COI(periods, sfreq, omega0):
    # slope of Morlet e-folding time in tau-periods (spectral) view
    m = 4 * pi / (np.sqrt(2) * (omega0 + sqrt(2 + omega0 ** 2)))
    return m


# is normed to have unit energy on all scales! ..to be used with CWT underneath
def mk_Morlet(omega0):
    def Morlet(t, scale):
        res = pi ** (-0.25) * np.exp(omega0 * 1j * t / scale) * np.exp(-0.5 * (t / scale) ** 2)
        return 1 / sqrt(scale) * res

    return Morlet


# allows for complex wavelets, needs scales scaled with sampling freq!
def CWT(data, wavelet, scales):
    # test for complexity
    if np.iscomplexobj(wavelet(10, 1)):
        output = np.zeros([len(scales), len(data)], dtype=complex)
    else:
        output = np.zeros([len(scales), len(data)])

    vec = np.arange(-len(data) / 2, len(data) / 2)  # we want to take always the maximum support available
    for ind, scale in enumerate(scales):
        wavelet_data = wavelet(vec, scale)
        output[ind, :] = np.convolve(data, wavelet_data,
                                     mode='same')
    return output


def compute_spectrum(signal, dt, periods):
    """
    Computes the Wavelet spectrum for a given *signal* for the given *periods*

    signal  : a sequence
    the time-series to be analyzed, detrend beforehand!
    dt      : the sampling interval scaled to desired time units
    periods : the list of periods to compute the Wavelet spectrum for,
          must have same units as dt!

    returns:

    wlet : the Wavelet transform with dimensions len(periods) x len(signal)
    """

    # avoid output for every pixel
    # if periods[0] < 2 * dt:
    #     print()
    #     print('Warning, Nyquist limit is', 2 * dt, '!!')
    #     print()

    signal = np.array(signal)
    periods = np.array(periods)
    dt = float(dt)
    sfreq = 1 / dt  # the sampling frequency
    tvec = np.arange(0, len(signal) * dt + dt, dt)

    Nt = len(signal)  # number of time points

    # --------------------------------------------
    scales = scales_from_periods(periods, sfreq, omega0)
    # --------------------------------------------
    coi_m = Morlet_COI(periods, sfreq, omega0)  # slope of COI

    # mx_per = 4*len(signal)/((omega0+sqrt(2+omega0**2))*sfreq)
    mx_per = dt * len(signal)

    # avoid output for every pixel
    
    # if max(periods) > mx_per:
    #     print()
    #     print ('Warning: Very large periods chosen!')
    #     print ('Max. period should be <', np.rint(mx_per), 'min')
    #     print ('proceeding anyways...')

    Morlet = mk_Morlet(omega0)
    wlet = CWT(signal, Morlet, scales)  # complex wavelet transform
    sigma2 = np.var(signal)
    modulus = np.abs(wlet) ** 2 / sigma2  # normalize with variance of signal

    return modulus, wlet


def get_maxRidge(modulus, Thresh=0):
    """
    Computes the ridge as consecutive maxima of the modulus.

    Returns the ridge_data dictionary (see mk_ridge_data)!
    """

    Nt = modulus.shape[1]  # number of time points

    # ================ridge detection=======================================

    # just pick the consecutive modulus (squared complex wavelet
    # transform) maxima as the ridge

    ridge_y = np.array([np.argmax(modulus[:, t]) for t in np.arange(Nt)], dtype=int)

    return ridge_y


def wsmooth(x, data=None):
    """
    smooth the data using a window with requested size.

    input:
    x: the input signal
    window_len: the dimension of the smoothing window; should be an odd integer
    window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
    flat window will produce a moving average smoothing.
    data: if not None, will be used as evaluated window!

    """

    x = np.array(x)

    # use externally derieved window evaluation
    if data is not None:
        window_len = len(data)
        window = 'extern'
    else:
        raise ValueError('no data!')

    if x.size < window_len:
        raise ValueError("Input vector needs to be bigger than window size.")

    if window_len < 3:
        raise ValueError("window must not be shorter than 3")

    if window_len % 2 is 0:
        raise ValueError("window_len should be odd")

    # mirroring on the sides
    s = np.r_[x[window_len - 1:0:-1], x, x[-1:-window_len:-1]]
    # print(len(s))
    w = data

    y = np.convolve(w / w.sum(), s, mode='valid')

    return y[int((window_len - 1) / 2):len(y) - int((window_len - 1) / 2)]


def sinc_filter(M, f_c=0.2):
    """
    Cutoff frequency f_c in sampling frequency unit, max 0.5!
    M is blackman window length and must be even, output length will be M+1.
    """

    # not very effective, but should be get called only once per convolution

    assert M % 2 == 0, 'M must be even!'
    res = []

    for x in np.arange(0, M + 1):

        if x == M / 2:
            res.append(2 * pi * f_c)
            continue

        r = sin(2 * pi * f_c * (x - M / 2)) / (x - M / 2)  # the sinc filter unwindowed
        r = r * (0.42 - 0.5 * cos(2 * pi * x / M) + 0.08 * cos(4 * pi * x / M))  # blackman window
        res.append(r)

    res = np.array(res)
    res = res / sum(res)

    return res


def sinc_smooth(raw_signal, T_c, dt, M=None, detrend=False):
    signal = np.array(raw_signal)
    dt = float(dt)

    # relative cut_off frequency
    f_c = dt / T_c  # max T_c = 2*dt -> max f_c = 0.5 (Nyquist)

    if M is None:

        M = len(signal) - 1  # max for sharp roll-off

        # M needs to be even
        if M % 2 != 0:
            M = M - 1

    w = sinc_filter(M, f_c)  # the evaluated windowed sinc filter
    sinc_smoothed = wsmooth(signal, data=w)

    if detrend:
        sinc_smoothed = signal - sinc_smoothed

    return sinc_smoothed


