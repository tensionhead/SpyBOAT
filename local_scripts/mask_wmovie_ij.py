from __future__ import with_statement,division
import sys,os
from os import walk,environ
from os.path import expanduser
from math import sqrt,cos,sin,pi

from ij import IJ,ImagePlus,ImageStack
from ij.io import OpenDialog, DirectoryChooser
from ij.gui import PolygonRoi,Roi,EllipseRoi,ShapeRoi,Overlay,Line 
from ij.gui import GenericDialog,Overlay,Roi,DialogListener,Plot,ProfilePlot 
from ij.plugin.filter import RankFilters,EDM,GaussianBlur,ParticleAnalyzer,BackgroundSubtracter
from ij.measure import ResultsTable,Measurements
from ij.plugin import ImageCalculator,Selection,ZProjector
from ij.process import FloatProcessor,ShortProcessor
from java.awt import Color
import re, glob

from java.util import Arrays
#from jarray import toString
import pickle


#-------------------------------------------------------------
base_dir = '/Volumes/aulehla/vLab/WaveletMovieBatch/'
#-------------------------------------------------------------


def display_msg(title,message):
    gd = GenericDialog(title)
    gd.addMessage(message)
    gd.hideCancelButton()
    gd.showDialog()


def run():

    dc = DirectoryChooser('Choose a directory')
    dc.setDefaultDirectory(base_dir)
    
    #--------------working directory------------------
    work_dir = dc.getDirectory()
    #-------------------------------------------------

    tifs = glob.glob(os.path.join(work_dir,'*tif'))

    try:
        LuVeLu_movie = [n for n in tifs if 'input_' in n][0]
    except IndexError:
        display_msg('No Input Found', 'No "input_..." movie found in\n' + work_dir)
        return

    wmovies = [n for n in tifs if 'input_' not in n]
        
    print(tifs,LuVeLu_movie)
    
    return
    # IJ.getFilePath # for interactive use
    orig = IJ.getImage() # single LuVeLu channel or select the right one, only one slice MaxProject!
    # the unique(?!) identifier used to create the working directory
    title = orig.getShortTitle()
    print(title)

    width,height,NChannels,NSlices,NFrames = orig.getDimensions()




    
    if not 'vLab' in user_base_dir:
        display_msg("Invalid directory", "Please choose a directory in ../aulehla/vLab !")
        return


    IJ.log("Working in " + user_base_dir)
    
    # create the working directory from the movie title
    #-------- movie's directory-----------------
    wdir = os.path.join(user_base_dir,title) # the working directory
    #-------------------------------------------
    if not os.path.exists(wdir):
        IJ.log('Created ' + wdir)
        os.mkdir(wdir)
    else:
        IJ.log('\nWorking in existing directory\n' + wdir)
        gd3 = GenericDialog("Directory exists")
        gd3.addMessage("Directory already exists.. overwrite existing files?")
        gd3.showDialog()
        if gd3.wasCanceled():  
            print ("Canceled!" )
            IJ.log("Canceled!" )
            return
        else:
            IJ.log("Continuing in existing directory..")
        # without roi_movies we can easily overwrite existing files
        # else:
        #     clear_directory(wdir)
        #     IJ.log("Cleared " + wdir + " !")

        
    gd = GenericDialog("Wavelet options - T_c = T_max!")
    gd.addNumericField("dt (min):",10,1)
    gd.addNumericField("Tmin (min):",100,0)
    gd.addNumericField("Tmax (min):",220,0)
    gd.addNumericField("Period steps:",150,0)
    gd.showDialog()
    if gd.wasCanceled():  
        print ("Wavelet Dialog canceled!" )
        IJ.log("Wavelet Dialog canceled!" )
        return


    dt = gd.getNextNumber()
    Tmin = gd.getNextNumber()
    Tmax = gd.getNextNumber()
    nT = gd.getNextNumber()

    # create wavelet script
    create_wavelet_script(title, user_base_dir, dt, Tmin, Tmax, nT)
        
    # create the slurm script
    create_slurm_script(title, user_base_dir)

    gd = GenericDialog("Almost done")
    gd.addMessage("All good, copy movie for processing onto vLab?")
    gd.showDialog()
    if gd.wasCanceled():  
        IJ.log("Warning: did not copy movie..")
        return
        
    file_path = os.path.join(wdir,'input_' + title)
    IJ.log("Copy movie to " + file_path)

    IJ.save(orig, file_path)
    IJ.log("Done!")    

run()
