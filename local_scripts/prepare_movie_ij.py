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
import re

from java.util import Arrays
#from jarray import toString
import pickle

#-------------------------------------------------------------
script_path = expanduser('/Volumes/aulehla/Gregor/progs/WaveletMovies/cluster_scripts') 
# group share directory - set by user!
base_dir = '/Volumes/aulehla/vLab/WaveletMovieBatch'
# cluster_base_dir = expanduser('~/PSM')
#-------------------------------------------------------------


def display_msg(title,message):
    gd = GenericDialog(title)
    gd.addMessage(message)
    gd.hideCancelButton()
    gd.showDialog()


def create_slurm_script(MovieDir, base_dir):

    # global scriptpath for template location

    tdir = os.path.join(script_path,'slurm_py_template.sh')
    out_lines = []
    with open(tdir,'r') as template:
        for line in template:

            # path on the cluster/spinoza
            cluster_base_dir = base_dir.replace('Volumes','g')
            
            #insert correct directory name
            if 'dummyBaseDir' in line:
                line = ''.join( ['BaseDir="',cluster_base_dir,'"\n'] )
                print(line)

        
            #insert correct movie directory name
            if 'dummyDir' in line:
                line = ''.join( ['MovieDir="',MovieDir,'"\n'] )
                print(line)

            #print(line)
            out_lines.append(line)

    # directory to save the slurm script
    sname = 'start_' + MovieDir + '.sh'
    sdir = os.path.join(base_dir,sname)
            
    with open(sdir,'w') as OUT:
        for line in out_lines:
            OUT.write(line)

    IJ.log('\nwrote slurm script to:\n'+sdir)

def create_wavelet_script(MovieDir,base_dir,dt,Tmin,Tmax,nT):

    # global scriptpath for template location!
    
    tdir = os.path.join(script_path,'ana_Movie_template.py')
    out_lines = []
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

            #print(line)
            out_lines.append(line)


    #------Script to execute on the HPC cluster--
    sname = 'ana_Movie.py'
    #--------------------------------------------
    
    # directory to save the slurm script
    sdir = os.path.join(base_dir,MovieDir,sname)
            
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

    # IJ.getFilePath # for interactive use
    orig = IJ.getImage() # single LuVeLu channel or select the right one, only one slice MaxProject!
    # the unique(?!) identifier used to create the working directory
    title = orig.getShortTitle()
    print(title)

    width,height,NChannels,NSlices,NFrames = orig.getDimensions()

    if NChannels > 1:
        IJ.log("Error: only one channel allowed, split the channels first..exiting!")
        display_msg("Too much channels!","Only one channel allowed, split the channels first..exiting!")
        return

    if NSlices > 1:
        display_msg("Too much slices!","Only one slice allowed, use maximum projection first..exiting!")
        IJ.log("Error: only one slice allowed, use maximum projection first..exiting!")
        return
            
    if not os.path.exists(base_dir):
        display_msg("No group share?!",base_dir + "\nnot found..have you mounted the group share?")
        IJ.log("Directory\n" + base_dir + "\nnot found..have you mounted the group share?")
        return

    if not os.path.exists(script_path):
        display_msg("No group share?!",script_path + "\nnot found..have you mounted the group share?")
        IJ.log("Script directory\n" + script_path + "\nnot found..have you mounted the group share?")
        return

    dc = DirectoryChooser('Choose a directory on the group share')
    dc.setDefaultDirectory(base_dir)

    #-------------- user's directory------------------
    user_base_dir = dc.getDirectory()
    #-------------------------------------------------

    
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
        

run()
