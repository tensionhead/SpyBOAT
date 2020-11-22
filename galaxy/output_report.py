''' Produces plots and a summary html 'headless' '''

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
    hence the analysis dictionary 'Wkwargs' also gets passed.

    The output files name pattern is:
    [input, phase, period, amplitude]_frame{frame}.png

    These get picked up by 'create_html'
    '''


    spyplot.input_snapshot(input_movie[frame])
    fig = ppl.gcf()
    fig.savefig(f'input_frame{frame}.png', dpi=DPI)
    
    spyplot.phase_snapshot(results['phase'][frame])
    fig = ppl.gcf()
    fig.savefig(f'phase_frame{frame}.png', dpi=DPI)

    spyplot.period_snapshot(results['period'][frame],
                            Wkwargs,
                            time_unit = 'a.u.')
    
    fig = ppl.gcf()
    fig.savefig(f'period_frame{frame}.png', dpi=DPI)

    spyplot.amplitude_snapshot(results['amplitude'][frame])
    fig = ppl.gcf()
    fig.savefig(f'amplitude_frame{frame}.png', dpi=DPI)
        

    logger.info(f'Produced 4 snapshots for frame {frame}..')

def produce_distr_plots(results, Wkwargs):

    '''
    Output file names are:
    
    period_distr.png and power_distr.png
    '''

    spyplot.period_distr_dynamics(results['period'], Wkwargs)
    fig = ppl.gcf()
    fig.savefig(f'period_distr.png', dpi=DPI)    
    spyplot.power_distr_dynamics(results['power'], Wkwargs)
    fig = ppl.gcf()
    fig.savefig(f'power_distr.png', dpi=DPI)
    
    logger.info(f'Produced 2 distribution plots..')

    
def create_html(movie_name, frame_num):

    html_string =f'''
    <html>
    <head>
      <link rel="stylesheet" href="styles.css">
    </head>
    <body>
    <h1 style="text-align:center">SpyBOAT Results for {movie_name}</h1>
    <hr style="width:50%"> 
    <div class="distr_gallery">
       <figure class=”distr_gallery__item distr_gallery__item--1">
         <img src="period_distr.png" alt="Period" class="distr_gallery__img">
       </figure>

       <figure class=”distr_gallery__item distr_gallery__item--2">
         <img src="power_distr.png" alt="Power" class="distr_gallery__img">
       </figure>
    </div>

    <h2 style="text-align:center"> Snapshots - Frame {frame_num}</h2>
    <div class="snapshot_gallery">
       <figure class=”snapshot_gallery__item snapshot_gallery__item--1">
         <img src="input_frame{frame_num}.png" alt="The Input" class="snapshot_gallery__img">
       </figure>

       <figure class=”snapshot_gallery__item snapshot_gallery__item--2">
         <img src="phase_frame{frame_num}.png" alt="Phase" class="snapshot_gallery__img">
       </figure>

       <figure class=”snapshot_gallery__item snapshot_gallery__item--3">
         <img src="period_frame{frame_num}.png" alt="Period" class="snapshot_gallery__img">
       </figure>

       <figure class=”snapshot_gallery__item snapshot_gallery__item--4">
         <img src="amplitude_frame{frame_num}.png" alt="Amplitude" class="snapshot_gallery__img">
       </figure>
    </div>
    

        <!-- *** Section 1 *** --->
    </body>
    </html>
    '''

    OUT = open('test.html', 'w')
    OUT.write(html_string)
    OUT.close()
    return html_string

create_html('L20', 125)
