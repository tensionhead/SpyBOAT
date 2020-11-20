## Produces plots and a summary html 'headless'

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as ppl

import logging
from skimage import io

import spyboat.plotting as spyplot

logger = logging.getLogger(__name__)

# figure resolution
DPI=250

def produce_snapshots(input_movie, results, frame, Wkwargs):

    '''
    Takes the *input_movie* and the 
    *results* dictionary from spyboat.processing.run_parallel
    and produces phase, period and amplitude snapshot png's.

    For the period snapshot also the period range is needed,
    hence the analysis dictionary 'Wkwargs' also is needed.
    '''


    spyplot.input_snapshot(input_movie[frame])
    fig = ppl.gcf()
    fig.savefig(f'input_frame{frame}.png', dpi=DPI)
    
    spyplot.phase_snapshot(results['phase'][frame])
    fig = ppl.gcf()
    fig.savefig(f'phase_frame{frame}.png', dpi=DPI)

    spyplot.period_snapshot(results['period'][frame],
                                 Tmin = Wkwargs['Tmin'],
                                 Tmax = Wkwargs['Tmax'],
                                 time_unit = 'a.u.')
    
    fig = ppl.gcf()
    fig.savefig(f'period_frame{frame}.png', dpi=DPI)

    spyplot.amplitude_snapshot(results['amplitude'][frame])
    fig = ppl.gcf()
    fig.savefig(f'amplitude_frame{frame}.png', dpi=DPI)
        

    logger.info(f'Produced 4 snapshots for frame {frame}..')
