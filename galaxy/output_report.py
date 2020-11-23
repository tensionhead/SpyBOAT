''' Produces plots and a summary html 'headless' '''

import os
import matplotlib
# headless plotting and disable latex
matplotlib.use('Agg')
matplotlib.rcParams['text.usetex'] = False
import matplotlib.pyplot as ppl

import logging

import spyboat.plotting as spyplot

logger = logging.getLogger(__name__)

# figure resolution
DPI=250

def produce_snapshots(input_movie, results, frame, Wkwargs,
                      img_path='.'):

    '''
    Takes the *input_movie* and the 
    *results* dictionary from spyboat.processing.run_parallel
    and produces phase, period and amplitude snapshot png's.

    For the period snapshot also the period range is needed,
    hence the analysis dictionary 'Wkwargs' also gets passed.

    The output files name pattern is:
    [input, phase, period, amplitude]_frame{frame}.png
    and the storage location in *img_path*.

    These get picked up by 'create_html'
    '''


    spyplot.input_snapshot(input_movie[frame])
    fig = ppl.gcf()
    out_path = os.path.join(img_path, f'input_frame{frame}.png')
    fig.savefig(out_path, dpi=DPI)
    
    spyplot.phase_snapshot(results['phase'][frame])
    fig = ppl.gcf()
    out_path = os.path.join(img_path, f'phase_frame{frame}.png')    
    fig.savefig(out_path, dpi=DPI)

    spyplot.period_snapshot(results['period'][frame],
                            Wkwargs,
                            time_unit = 'a.u.')
    
    fig = ppl.gcf()
    out_path = os.path.join(img_path, f'period_frame{frame}.png')    
    fig.savefig(out_path, dpi=DPI)
    
    spyplot.amplitude_snapshot(results['amplitude'][frame])
    fig = ppl.gcf()
    out_path = os.path.join(img_path, f'amplitude_frame{frame}.png')    
    fig.savefig(out_path, dpi=DPI)
        

    logger.info(f'Produced 4 snapshots for frame {frame}..')

def produce_distr_plots(results, Wkwargs, img_path='.'):

    '''
    Output file names are:
    
    period_distr.png, power_distr.png and phase_distr.png   
    '''

    spyplot.period_distr_dynamics(results['period'], Wkwargs)
    fig = ppl.gcf()
    out_path = os.path.join(img_path, f'period_distr.png')    
    fig.savefig(out_path, dpi=DPI)
    
    spyplot.power_distr_dynamics(results['power'], Wkwargs)
    fig = ppl.gcf()
    out_path = os.path.join(img_path, f'power_distr.png')    
    fig.savefig(out_path, dpi=DPI)

    spyplot.phase_coherence_dynamics(results['phase'], Wkwargs)
    fig = ppl.gcf()
    out_path = os.path.join(img_path, f'phase_distr.png')    
    fig.savefig(out_path, dpi=DPI)
        
    logger.info(f'Produced 3 distribution plots..')

    
def create_html(frame_num, html_fname='OutputReport.html'):

    '''
    The html generated assumes the respective png's (7 in total)
    have been created with 'produce_snapshots' and 'produce_distr_plots'
    and can be found at the cwd (that's how Galaxy works..)
    '''

    html_string =f'''
    <html>
    <title>SpyBOAT Output Report</title>
    <head>
        <!-- that doesn't work with galaxy.. -->
        <!--link rel="stylesheet" href="styles.css"-->
      <style type="text/css">
        body{{ margin:10 100; background:whitesmoke; }}
        /*body{{ margin:10 100; background:darkslategrey; }}*/
        .center{{
            display: block;
            margin-left: auto;
            margin-right: auto;
            width: 40%;}}

        /* matplotlib output at 1600x1200  */
        .distr_gallery {{
            display: grid;
            margin: 0 auto;
            text-align: center;
            /* border: 1px dashed rgba(4, 4, 4, 0.35);     */
            grid-template-columns: repeat(3,1fr);
            grid-template-rows: 25vw;    
            grid-gap: 0px;
            column-gap: 0px
        }}
        .distr_gallery__img {{
            width: 100%;
            height: 100%;
            object-fit: contain;
        }}


        /* matplotlib output at 1600x1200  */
        .snapshot_gallery {{
            display: grid;
            margin: 0 auto;
            border: 1px dashed rgba(4, 4, 4, 0.35);
            text-align: center;
            grid-template-columns: repeat(2,1fr);
            grid-template-rows: repeat(2,20vw);
            grid-gap: 5px;
        }}
        .snapshot_gallery__img {{
            width: 100%;
            height: 100%;
            object-fit: contain;
        }}
     </style>
    </head>
    <body>
    <h1 style="text-align:center">SpyBOAT Results Report</h1>
    <hr style="width:50%"> 
    <div class="distr_gallery">
       <figure class=”distr_gallery__item distr_gallery__item--1">
         <img src="period_distr.png" alt="Period" class="distr_gallery__img">
       </figure>

       <figure class=”distr_gallery__item distr_gallery__item--2">
         <img src="power_distr.png" alt="Power" class="distr_gallery__img">
       </figure>

       <figure class=”distr_gallery__item distr_gallery__item--3">
         <img src="phase_distr.png" alt="Phase" class="distr_gallery__img">
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

    with open(html_fname, 'w') as OUT:

        OUT.write(html_string)

    logger.info(f'Created html report')
    return html_string

# for local testing
# create_html(125)
