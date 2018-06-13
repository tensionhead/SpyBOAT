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
from ij.process import FloatProcessor,ShortProcessor, BinaryProcessor, ByteProcessor
from java.awt import Color
import re, glob

from java.util import Arrays
#from jarray import toString
import pickle

ic = ImageCalculator()

#-------------------------------------------------------------
base_dir = '/Volumes/aulehla/vLab/WaveletMovieBatch/'
#-------------------------------------------------------------


def display_msg(title,message):
    gd = GenericDialog(title)
    gd.addMessage(message)
    gd.hideCancelButton()
    gd.showDialog()


# works not for float processors :/
def threshold_ip(ip,thresh):

    ''' Returns a byte processor, 255 for unmasked '''

    mask = ByteProcessor(ip, False)

    width = ip.getWidth()
    height = ip.getHeight()

    for x in range(width):
        for y in range(height):
            val = ip.getPixel(x,y)
            if val > thresh:
                mask.putPixel(x,y,255) # over threshold
            else:
                mask.putPixel(x,y,0) # under threshold

    return mask
    
def create_mask_stack(orig,thresh_method = 'Huang',minThresh = None):

    width,height,NChannels,NSlices,NT = orig.getDimensions()
    mask_stack = ImageStack(width,height)

    # one-based-indexing! (input movies have only 1-slice)
    NFrames = NT if NSlices < NT else NSlices
    for frame in range(1,NFrames + 1):
        orig.setPosition(frame)
        ip = orig.getProcessor().duplicate()

        # auto thresholding
        if thresh_method:
            ip.setAutoThreshold(thresh_method, True, False)
            minThresh = ip.getMinThreshold() # set automatically
            maxv = ip.getMaxThreshold()

        ip.threshold(int(minThresh))
        
        # mask_ip = ip.createMask()
        mask_stack.addSlice(ip)

    mask_imp = ImagePlus('Masks',mask_stack)
    return mask_imp
    
def run():    
    
    dc = DirectoryChooser('Choose a directory')
    dc.setDefaultDirectory(base_dir)
    
    #--------------working directory------------------
    work_dir = dc.getDirectory()
    #-------------------------------------------------
    
    if work_dir is None:
        display_msg("Cancelled", "Aborted!")
        return

    tif_paths = glob.glob(os.path.join(work_dir,'*tif'))

    try:
        LuVeLu_movie = [n for n in tif_paths if 'input_' in n][0]
    except IndexError:
        display_msg('No Input Found', 'No "input_..." movie found in\n' + work_dir)
        return
    try:
        Power_movie = glob.glob(os.path.join(work_dir,'power*tif'))[0]
    except IndexError:
        display_msg('File not found', 'No "power_..." movie found in\n' + work_dir)
        return

    # gd = GenericDialog("Masking from?")
    
    # gd.addMessage("Use input intensity or Wavelet power?")
    # gd.addChoice('Mask from',['Intensity','Power'],'Intensity')

    
    # to apply mask on all remaining tifs    
    wmovies = [n for n in tif_paths if 'input_' not in n]
        
    # IJ.getFilePath # for interactive use
    

    gd = GenericDialog("Masking options")
    
    gd.addMessage("Select a fixed threshold value OR \n threshold method")
    gd.addNumericField("min. Intensity:",0,0)
    gd.addCheckbox('Use automatic thresholding',False)
    gd.addChoice('Method',['Default','Huang','Otsu','Yen'],'Default')
    
    gd.showDialog()
    if gd.wasCanceled():  
        #IJ.log("Dialog canceled!" )
        display_msg("Cancelled", "Aborted!")
        return

    minThresh = gd.getNextNumber()
    use_auto = gd.getNextBoolean()

    method = None # defaults to manual Threshold
    if use_auto:
        method = gd.getNextChoice()

    #-----------------------------------
    input_movie = IJ.openImage(LuVeLu_movie)
    #-----------------------------------
    mask = create_mask_stack(input_movie,thresh_method = method, minThresh = minThresh)
        
    # mask.show()
    # return
    # mask the wmovies: phase, period and power
    for movie in wmovies:
        imp = IJ.openImage(movie)
        masked_imp = ic.run("Multiply create 32-bit stack",imp, mask)
        masked_imp.show()
    
run()
