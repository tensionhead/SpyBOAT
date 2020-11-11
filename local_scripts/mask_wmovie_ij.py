###########################################################
##      Fiji plugin for interactive masking ##
# Usage: Open the movie to create the mask from
# as well as the movies to be masked. They all must
# have the same dimensions!
# Either directly open this script with Fiji
# or move to plugins folder.
# Run the script, 1st menu lets you select the masking
# options, 2nd menu applys the mask, one movie at a time.
###########################################################

from __future__ import with_statement,division
import sys,os
from os import walk,environ
from os.path import expanduser
from math import sqrt,cos,sin,pi

import ij
from ij import IJ,ImagePlus,ImageStack, WindowManager
from ij.io import OpenDialog, DirectoryChooser
from ij.gui import PolygonRoi, Roi, EllipseRoi, ShapeRoi, Overlay, Line 
from ij.gui import GenericDialog, Overlay,Roi, NonBlockingGenericDialog
from ij.plugin.filter import RankFilters, EDM, GaussianBlur, ParticleAnalyzer, BackgroundSubtracter
from ij.measure import ResultsTable,Measurements
from ij.plugin import ImageCalculator,Selection,ZProjector, HyperStackConverter
from ij.plugin.filter import ThresholdToSelection
from ij.process import FloatProcessor,ShortProcessor, BinaryProcessor, ByteProcessor
from java.awt import Color
import re, glob

from java.util import Arrays
#from jarray import toString
import pickle

ic = ImageCalculator()


def display_msg(title,message):
    gd = GenericDialog(title)
    gd.addMessage(message)
    gd.hideCancelButton()
    gd.showDialog()

def get_largest_roi(roi_list):

    if not roi_list:
        print IJ.log('Found no object at all..aborting!!')
        return

    max_ind = 0
    if len(roi_list) > 1:
        # IJ.log('Found more than one object, taking the biggest!')

        max_size = 0 # check perimeter
        max_ind = 0
        for ii,roi in enumerate(roi_list):
            size = len(roi.getContainedPoints())

            if size > max_size:
                max_size = size
                max_ind = ii
            # IJ.log('Roi ' + str(ii) + ' perimeter: ' + str(per))


    largest_roi = roi_list[max_ind]

    return largest_roi

def slices_to_frames(hstack):

    ''' Reorder Hyperstack in case of slices - frames confusion '''
    
    hc = HyperStackConverter()

    x,y,c,z,t = hstack.getDimensions()

    new_hstack = hstack # to avoid 'reference before assignment' error
    # more slices than frames indicate mis-placed dimensions
    if z > t:
        IJ.log('Shuffling\n' + hstack.getShortTitle() + '\n slices to frames..')
        new_hstack = hc.toHyperStack(hstack, c, t, z) # shuffle indices
        IJ.log('New dimensions: ' + str(c) + ', ' + str(t) + ', ' + str(z))

    else:
        IJ.log(hstack.getShortTitle() + '\n needs no shuffling')
        
    return new_hstack

def create_mask_selection(movie, sigma = 0, thresh_method = 'Huang', threshold = None):

    ''' 
    If threshold is *None* use selected AutoThreshold, otherwise
    use fixed *threshold* '''

    C = movie.getC()
    S = movie.getSlice()
    NFrames = movie.getNFrames()
    
    maxThresh = 2**movie.getBitDepth()
    
    tts = ThresholdToSelection()

    ov = Overlay() # to save the rois
    for frame in range(1, NFrames + 1):
        
        movie.setPosition(C, S, frame)
        ip = movie.getProcessor().duplicate()
        # imp = ImagePlus('Blurred', ip)
        if sigma != 0:
            ip.blurGaussian(sigma)
        
        # manual thresholding
        if threshold:
            ip.setThreshold( threshold, maxThresh, 0) # no LUT update

        # automatic thresholding
        else:
            ip.setAutoThreshold(thresh_method, True, False)
        
        tts.setup("",movie)
        shape_roi = tts.convert(ip)

        
        # only one connected roi present
        if type(shape_roi) == ij.gui.PolygonRoi:
            mask_roi = shape_roi
            
        else:
            # for disconnected regions.. take the shape_roi as is
            # rois = shape_roi.getRois() # splits into sub rois
            # mask_roi = get_largest_roi(rois) # sort out smaller Rois
            mask_roi = shape_roi
            
        mask_roi.setPosition(frame)
        ov.add(mask_roi)
        
    return ov
        
def apply_thresh_overlay( overlay ):

    ''' Clear outside rois in overlay '''

    # --- Dialog -----------------------------------
    wlist = WindowManager.getImageTitles()
    gd = NonBlockingGenericDialog('Apply Mask to')
    gd.setCancelLabel('Exit')
    gd.addChoice('Select Movie',wlist, wlist[0])
    gd.addCheckbox('Duplicate', True)

    gd.showDialog() # dialog is open

    if gd.wasCanceled():
        return False
    
    sel_win = gd.getNextChoice()
    do_duplicate = gd.getNextBoolean()

    # --- Dialog End ------------------------------
    
    win_name = IJ.selectWindow(sel_win)
    movie = IJ.getImage()
    movie = slices_to_frames(movie)

    C = movie.getC()
    S = movie.getSlice()
    
    if do_duplicate:
        IJ.log('duplicating ' + movie.shortTitle  )
        movie = movie.duplicate()

    NFrames = movie.getNFrames()
    
    if overlay.size() != NFrames: # one roi for each frame!
        display_msg('Mask count mismatch!', 'Mask count mismatch!\nGot ' + str(Nrois) + ' masks and ' + str(NFrames) + ' frames.. !')

    for frame in range(1, NFrames + 1):
        movie.setPosition(C, S, frame)
        mask_roi = overlay.get(frame - 1)
        ip = movie.getProcessor()
        ip.setValue(0)
        ip.setRoi( mask_roi )
        ip.fillOutside(mask_roi)
        
    movie.show()
    return True
        
def start_masking_menu():
    
    wlist = WindowManager.getImageTitles()
    gd = GenericDialog('Masking - Setup')
    gd.setCancelLabel('Exit')

    gd.addChoice('Create mask from',wlist, wlist[0])
    gd.addNumericField("Gaussian blur:",0,1)    
    gd.addNumericField("Fixed threshold:",0,0)
    gd.addCheckbox('Use automatic thresholding',False)
    gd.addChoice('Method',['Default','Huang','Otsu','Yen'],'Default')

    gd.showDialog()

    if gd.wasCanceled():
        return False

    pdic = {}

    pdic['sel_win'] = gd.getNextChoice()
    pdic['sigma'] = gd.getNextNumber()    
    pdic['threshold'] = gd.getNextNumber()
    pdic['use_auto'] = gd.getNextBoolean()
    pdic['thresh_method'] = gd.getNextChoice()

    return pdic


def run():
    
    pdic = start_masking_menu()

    # exited..
    if not pdic:
        return
    
    print pdic

    IJ.selectWindow(pdic['sel_win'])

    input_movie = IJ.getImage() # the movie to create the mask from

    slices_to_frames(input_movie)

    ov = create_mask_selection(input_movie,
                               sigma = pdic['sigma'],
                               thresh_method = pdic['thresh_method'],
                               threshold = pdic['threshold'])

    input_movie.setOverlay(ov)
    
    while True:
        res = apply_thresh_overlay( ov )
        if not res:
            break # exit
run()
