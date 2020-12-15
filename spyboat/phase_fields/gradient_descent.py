import sys
from os.path import expanduser
import numpy as np
import matplotlib.pyplot as plt

from skimage import io

import grad_flux as gf
import plotting as pl
plt.ion()

movie = io.imread('Quad-movie2-crop.tif')

frame = 200

# get the gradient vectorfield
dY, dX = gf.phase_gradient(movie[frame,...])

plt.contour(movie[frame], levels = 35)
pl.show_vfield(dX, dY, skip = 3)
plt.imshow(movie[frame], interpolation='nearest', cmap = 'seismic')


def instructions(vy, vx):
    # calculate the vector angle from and instruct the direction 
    angle_boxes = np.array([-157.5, -112.5, -67.5, -22.5,\
    22.5, 67.5, 112.5, 157.5, 180])
    
    crawl_angle = np.arctan2(vy, vx)* 180 / np.pi

    # directions = np.array(['left', 'left_down', 'down', 'right_down',\
    #  'right','right_up', 'up', 'left_up', 'left'])
    directions = np.array([(-1,0),(-1, -1),(0, -1), (+1, -1),\
    (+1, 0), (+1, +1), (0, +1), (-1, +1), (-1, 0)])
    box_index = np.where(crawl_angle<angle_boxes)][0][0]
    instruction = directions[box_index]

    return instruction


def old_instructions(y_o, x_o):

    # calculating the length of the vector, normalizing
    # however, rounding operation is biased against the diagonal directions
    norm_grad = np.sqrt(dX[y_o,x_o]**2 + dY[y_o,x_o]**2)
    # step width
    alpha = 1
    x_n = x_o + alpha/norm_grad * dX[y_o,x_o]
    y_n = y_o + alpha/norm_grad * dY[y_o,x_o]
    x_n = int(np.round(x_n))
    y_n = int(np.round(y_n))

    return x_n, y_n


def crawl_gradient(dY, dX, ini_point = (0,0)):
    
    # initial values
    x_old, y_old = ini_point
    x_o, y_o = ini_point

    #list of (x,y) coordinates
    xys = []
    xys2 = []

    # gradient descent
    while True:
        xys.append((x_old,y_old))
        xys2.append((x_o,y_o))
 
        vy = dY[y_old,x_old]
        vx = dX[y_old,x_old]

        ix, iy = instructions(vy,vx)
        x_new = x_old + ix
        y_new = y_old + iy
        
        x_n, y_n = old_instructions(y_o, x_o)

        if (x_new, y_new) in xys:
            #stop crawling and delete the last coordinate 
            del xys[-1]
            break

        x_old = x_new
        y_old = y_new

        x_o = x_n
        y_o = y_n

    xs, ys = list(zip(*xys))
    xs2, ys2 = list(zip(*xys2))
    return xs, ys, xs2, ys2


xs, ys, xs2, ys2 = crawl_gradient(dY,dX)
plt.plot(xs2,ys2, c = 'g', lw = 2, marker = 'o')
plt.plot(xs,ys, c = 'k', lw = 2, marker = 'o')





