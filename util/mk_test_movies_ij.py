from __future__ import with_statement,division
from sys import path,exit
from os import walk
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

from jarray import *
import pickle
from subprocess import call,Popen,PIPE

def make_sine_movie(T,NFrames, width = 50, height = 50, dt = 10):
    ''' create a homogeneous oscillating movie '''

    BitDepth = 16
    signal = [2**(BitDepth-1) * ( 1 + sin(2*pi/T * t * dt)) for t in range(NFrames)]
    

    # width, height = 50, 50
    print 'w',width,'h',height
    print 'NFrames', NFrames

    # new stack
    movie = IJ.createHyperStack('hom sine',width,height,1,1,NFrames,BitDepth)

    for frame in range(1, NFrames + 1):
        movie.setPosition(1,1,frame)
        ip = movie.getProcessor()
        # x,y starts with zero?!
        for x in range(width ):
            for y in range(height):
                ip.putPixel(x, y, int(signal[frame-1]))
            
            

    return movie

def make_pshift_sine_movie(T,NFrames, width = 50, height = 50, dt = 10):
    ''' create a homogeneous oscillating movie with two phase-shifted oscillations '''

    BitDepth = 16
    signal1 = [2**(BitDepth-1) * ( 1 + sin(2*pi/T * t * dt)) for t in range(NFrames)]
    signal2 = [2**(BitDepth-1) * ( 1 + sin(2*pi/T * t * dt + pi/3.)) for t in range(NFrames)]
    

    # width, height = 50, 50
    print 'w',width,'h',height
    print 'NFrames', NFrames

    # new stack
    movie = IJ.createHyperStack('hom sine',width,height,1,1,NFrames,BitDepth)

    for frame in range(1, NFrames + 1):
        movie.setPosition(1,1,frame)
        ip = movie.getProcessor()
        # x,y starts with zero?!
        for x in range(width ):
            for y in range(height):
                if y > height/2:
                    ip.putPixel(x, y, int(signal1[frame-1]))
                else:
                    ip.putPixel(x, y, int(signal2[frame-1]))
            
            

    return movie


def make_Tshift_sine_movie(T,NFrames, width = 50, height = 50, dt = 10):
    ''' create a homogeneous oscillating movie with two different periods'''

    BitDepth = 16 # no float processor
    signal1 = [2**(BitDepth-1) * ( 1 + sin(2*pi/T * t * dt)) for t in range(NFrames)]
    signal2 = [2**(BitDepth-1) * ( 1 + sin(2*pi/(1.2*T) * t * dt )) for t in range(NFrames)]
    # 2**(BitDepth-1) * # not needed for float processor 

    # width, height = 50, 50
    print 'w',width,'h',height
    print 'NFrames', NFrames

    # new stack
    movie = IJ.createHyperStack('two hom. sines',width,height,1,1,NFrames,BitDepth)

    for frame in range(1, NFrames + 1):
        movie.setPosition(1,1,frame)
        ip = movie.getProcessor()
        # x,y starts with zero?!
        for x in range(width ):
            for y in range(height):
                if y > height/2:
                    ip.putPixelValue(x, y, signal1[frame-1])
                else:
                    ip.putPixelValue(x, y, signal2[frame-1])

    return movie


m1 = make_Tshift_sine_movie(T = 120, width = 5, height = 5,NFrames = 100)
m1.show()
