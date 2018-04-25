from __future__ import with_statement,division
import sys,os
from os import walk,environ
from os.path import expanduser
from math import sqrt,cos,sin,pi

from ij import IJ,ImagePlus,ImageStack
from java.awt import Color
from ij.gui import PolygonRoi,Roi,EllipseRoi,ShapeRoi,Overlay,Line 
from ij.gui import GenericDialog,Overlay,Roi,DialogListener,Plot,ProfilePlot 
from ij.plugin.filter import RankFilters,EDM,GaussianBlur,ParticleAnalyzer,BackgroundSubtracter
from ij.measure import ResultsTable,Measurements
from ij.plugin import ImageCalculator,Selection,ZProjector
from ij.process import FloatProcessor,ShortProcessor
from java.awt import Color
import re

from java.util import Arrays
#from jarray import toString
import pickle

#-------------------------------------------------------------
scriptpath = expanduser('~/HPC_dir/WaveletMovies/') 
# cluster directory
cluster_dir = '/g/aulehla/vLab/WaveletMovieBatch/'
#-------------------------------------------------------------

def make_tile_rois(movie,xwidth,ywidth):

    '''
    Construct the roi-grid used for every frame of the movie here once.
    '''
    
    width,height,NChannels,NSlices,NFrames = movie.getDimensions()
    
    # print height, width, NChannels, NSlices,NFrames

    ov = Overlay()

    xoff,yoff = 0,0
    # get roi corner coordinates
    xcoords,ycoords = [],[]
    while True:
        
        xcoords.append(xoff)
        xoff += xwidth
        
        if xoff > width:
            xcoords.append(width)
            break

    while True:
                
        ycoords.append(yoff)
        yoff += ywidth
        
        if yoff > height:
            ycoords.append(height)
            break

    # construct rectangular rois
    Rois = []
    for i,x in enumerate(xcoords[:-1]):
        if i > len(xcoords):
            break
        for j,y in enumerate(ycoords[:-1]):
            if j > len(ycoords):
                break
            
            width = xcoords[i+1] - x
            height = ycoords[j+1] - y
            new_roi = Roi(x,y,width,height)
            Rois.append(new_roi)
            ov.add(new_roi)

    movie.setOverlay(ov)

    return Rois,ov
    
def crop_tile_movie(movie, Roi):
        
    NFrames = movie.getNFrames()
    NSlices = movie.getNSlices()
    BitDepth = movie.getBitDepth()
    Channel = movie.getChannel() # use current channel!

    # get Roi specifications
    awt_rect = Roi.getBounds()
    # print(dir(awt_rect))
    roi_width = awt_rect.width
    roi_height = awt_rect.height
    roi_x = awt_rect.x
    roi_y = awt_rect.y
    
    if NSlices > 1:
        IJ.log("Too many slices.. use z-projection beforehand!")
        return False

    name = '_'.join(['Roi','Movie',str(roi_x),str(roi_y),str(roi_width), str(roi_height)])

    # same number of frames, dimensions of roi
    roi_movie= IJ.createHyperStack( name ,roi_width,roi_height,1,1,NFrames,BitDepth)
    
    for frame in range(1, NFrames + 1):
        movie.setPosition(Channel,1,frame)
        roi_movie.setPosition(1,1,frame)
        ip = movie.getProcessor()
        ip.setRoi(Roi)

        crop_ip = ip.crop()
        roi_movie.setProcessor(crop_ip)

    return roi_movie

def create_slurm_script(MovieDir,Nrm):

    # global scriptpath for template location

    print(
        ''' 
        ## Slurm Parameters ## 
        ''')


    tdir = os.path.join(scriptpath,'slurm_py_template.sh')
    out_lines = []
    with open(tdir,'r') as template:
        for line in template:

            #insert correct directory name
            if 'dummyDir' in line:
                line = ''.join( ['MovieDir="',MovieDir,'"\n'] )
                print(line)

            if 'SBATCH --array' in line:
                line = ''.join( ['#SBATCH --array=1-',str(Nrm),'\n'] )
                print(line)

            #print(line)
            out_lines.append(line)

    # directory to save the slurm script
    sname = 'start_' + MovieDir + '.sh'
    sdir = os.path.join(cluster_dir,sname)
            
    with open(sdir,'w') as OUT:
        for line in out_lines:
            OUT.write(line)

    IJ.log('\nwrote slurm script to:\n'+sdir)

def create_wavelet_script(MovieDir,dt,Tmin,Tmax,nT):

    # global scriptpath for template location
    tdir = os.path.join(scriptpath,'ana_RoiMovie_template.py')
    out_lines = []
    print(
        ''' 
        ## Wavelet Parameters ## 
        ''')

    with open(tdir,'r') as template:
        for line in template:

            #insert dt
            if 'dt =' in line:
                line = ''.join( ['dt = ',str(dt),'\n'] )
                print(line)


            #insert Tmin
            if 'Tmin =' in line:
                line = ''.join( ['Tmin = ',str(Tmin),'\n'] )
                print(line)

            #insert Tmax
            if 'Tmax =' in line:
                line = ''.join( ['Tmax = ',str(Tmax),'\n'] )
                print(line)

            #insert nT
            if 'nT =' in line:
                line = ''.join( ['nT = ',str(nT),'\n'] )
                print(line)

            if 'movie_dir =' in line:
                line = ''.join( ['movie_dir = "',MovieDir,'"\n'] )
                print(line)


            #print(line)
            out_lines.append(line)

    # directory to save the slurm script
    sname = 'ana_RoiMovie.py'
    sdir = os.path.join(cluster_dir,MovieDir,sname)
            
    with open(sdir,'w') as OUT:
        for line in out_lines:
            OUT.write(line)

    IJ.log('\nwrote wavelet script to:\n'+sdir)


# clears a directory!
def clear_directory(dir_path):
    if not 'vLab' in dir_path:
        print("Can not remove outside of vLab folder!!")
        IJ.log("Can not remove outside of vLab folder!!")
        return 
    for f in os.listdir(dir_path):
        p = os.path.join(dir_path,f) # the path to delete
        if os.path.isfile(p):
            os.remove(p)

def run():

    take_path = '/g/aulehla/Takehito/to Gregor RAFL spreadouts/more spreadouts for Gregor'

    #-------Image Path---------------
    orig_path = os.path.join(take_path,'unconfined','MAX_20180304_LuVeLu_spreadout_W0006.tif')
    if not os.path.exists(orig_path):
        IJ.log("Movie \n" + orig_path + "\nnot found..!\n")
        return

    #-------Wavelet Parameters-------
    dt = 10
    Tmin = 100
    Tmax = 200
    nT = 150
    #------ Tiling Parameters--------
    roi_width = 250
    roi_height = 250
    #-------------------------------


    # single LuVeLu channel or select the right one, only one slice MaxProject!
    orig = IJ.openImage(orig_path)

    # the unique identifier used to create the working directory
    title = orig.getShortTitle()
    print(title)

    if not os.path.exists(cluster_dir):
        IJ.log("Cluster directory\n" + cluster_dir + "\nnot found..have you mounted the group share?")
        return
    # maybe add possibility to manually point to the cluster directory?

    # create the working directory from the movie title
    wdir = os.path.join(cluster_dir,title) # the working directory
    if not os.path.exists(wdir):
        IJ.log('Created ' + wdir)
        os.mkdir(wdir, mode = 0770)
    else:
        IJ.log('\nWorking in existing directory\n' + wdir)
        answer = raw_input('Clear it and start over: yes/no ?\n')
        if answer == 'no':
            print ("exiting..")
            return
        else:
            clear_directory(wdir)
            IJ.log("Cleared " + wdir + " !")

            
    Rois,ov = make_tile_rois(orig,roi_width,roi_height)
    orig.setOverlay(ov)
    IJ.log( '\nCreated ' + str(len(Rois)) + ' rectangular Rois')

    
    answer = raw_input('Continue: yes/no ?\n')
    if answer == 'no':  
        print ("cancelled.." )
        return  
        

    #print Rois[0].toString()
    IJ.log('\nCreating ' + str(len(Rois)) + ' roi movies...')
    for Roi in Rois:
        orig.hide()
        print Roi.toString()
        rm = crop_tile_movie(orig,Roi)
        if not rm:
            return
        rm_title = rm.getShortTitle() # Roi_Movie_x_y_width_height - for restitching!
        # IJ.log( 'Created ' + rm_title)
        file_path = os.path.join(wdir,rm_title)

        IJ.save(rm, file_path)

    IJ.log( '\nCreated ' + str(len(Rois)) + ' roi movies')

    # write the original movie dimensions to a .txt for later restitching
    txt_path = os.path.join(wdir,'dimensions.txt')
    IJ.saveString(str(orig.getDimensions()),txt_path) # no better string represenation so far :/
    
    # create the python wavelet script
    create_wavelet_script(title,dt,Tmin,Tmax,nT)

    # create the slurm script
    create_slurm_script(title,len(Rois))


run()
