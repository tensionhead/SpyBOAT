from __future__ import with_statement,division,print_function
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

def run():

    wdir = IJ.getDirectory("Select Wavelet Movie Batch folder")
    if not wdir:
        IJ.log("Joining aborted..")
        return
    movie_name = wdir.split('/')[-2]
    print(movie_name)



    # renaming
    # fnames = list(walk(wdir))[0][2]
    # wrm_names2 = [name for name in fnames if 'w2Roi_Movie' in name]
    # for name in wrm_names2:
    #     full_path = os.path.join(wdir,name)
    #     new_name = 'w' + name[2:]
    #     print('renaming: ', full_path,new_name )
    #     os.rename(full_path,os.path.join(wdir,new_name))

    fnames = list(walk(wdir))[0][2]
    wrm_names = [name for name in fnames if 'wRoi_Movie' in name]
    IJ.log("\nFound " + str(len(wrm_names)) + " Wavelet Roi-movies calculated from " + movie_name)
    if len(wrm_names) == 0:
        IJ.log("No movies found")
        print("No movies found")
        return
    
    gd = GenericDialog("Start?")
    gd.addMessage("Start joining " + str(len(wrm_names)) +  " Wavelet movies?")
    gd.showDialog()
    if gd.wasCanceled():  
        print ("canceled!" )
        IJ.log("Canceled!" )
        return

    # print(wrm_names)
    # read the dimensions.txt
    txtdir = os.path.join(wdir,'dimensions.txt')
    with open(txtdir,'r') as dimtxt:
        line = dimtxt.read()

    # extract original image/movie dimensions 
    print(line)
    start = line.index('[')
    end = line.index(']')
    str_numbers = line[start+1:end].split(',')
    width, height,_,_,NFrames = [int(num) for num in str_numbers]
    print(width,height,NFrames)

    comb_wMovie = IJ.createHyperStack(movie_name + '_wMovie',width,height,3,1,NFrames,32)
    comb_wMovie.setDisplayMode(IJ.COLOR) # no composite!

    #comb_wMovie.show()

    # defined in wlet_movies_lib.py
    Period_chan = 2
    Power_chan = 3
    Phase_chan = 1

    # insert the wRoi_Movies into the Hyperstack
    comb_wMovie.hide()        
    for nr,name in enumerate(wrm_names):

        #extract position and extend of the Roi
        sub_string = name[:-4].split('_') # [:-4] chops of the '.tif'
        roi_x,roi_y,roi_width,roi_height = [int(num) for num in sub_string[2:6]]        
        #print(roi_x,roi_y,roi_width,roi_height)
        roiMovie = IJ.openImage( os.path.join(wdir,name) )        
        NF = roiMovie.getNFrames()
        
        if NF != NFrames:
            IJ.log("Something went wrong with the frame numbers..")
            return

        IJ.log('Inserting ' + name + ' ' + str(nr))

        for frame in range(1, NFrames + 1):
            
            #insert phases
            comb_wMovie.setPositionWithoutUpdate(Phase_chan,1,frame)
            ip = comb_wMovie.getProcessor()
            roiMovie.setPosition(Phase_chan,1,frame)
            roi_ip = roiMovie.getProcessor()
            ip.insert(roi_ip,roi_x,roi_y)

            #insert periods
            comb_wMovie.setPositionWithoutUpdate(Period_chan,1,frame)
            ip = comb_wMovie.getProcessor()
            roiMovie.setPosition(Period_chan,1,frame)
            roi_ip = roiMovie.getProcessor()
            ip.insert(roi_ip,roi_x,roi_y)

            #insert powers
            comb_wMovie.setPositionWithoutUpdate(Power_chan,1,frame)
            ip = comb_wMovie.getProcessor()
            roiMovie.setPosition(Power_chan,1,frame)
            roi_ip = roiMovie.getProcessor()
            ip.insert(roi_ip,roi_x,roi_y)

    comb_wMovie.show()



run()
