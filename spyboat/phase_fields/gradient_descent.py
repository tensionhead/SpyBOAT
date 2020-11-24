import sys
from os.path import expanduser
import numpy as np
import matplotlib.pyplot as plt

from skimage import io

import grad_flux as gf
import plotting as pl
plt.ion()

movie = io.imread('Quad-movie2-crop.tif')

frame = 100

# get the gradient vectorfield
dY, dX = gf.phase_gradient(movie[frame,...])

plt.contour(movie[frame], levels = 35)
pl.show_vfield(dX, dY, skip = 3)
plt.imshow(movie[frame], interpolation='nearest', cmap = 'seismic')



def crawl_gradient(dY, dX, ini_point = (0,0)):
    
    # initial values
    x_old, y_old = ini_point
    # step width
    alpha = 1
    xys = []

    # gradient descent
    while True:
        # print(x_old,y_old)
        xys.append((x_old,y_old))

        norm_grad = np.sqrt(dX[y_old,x_old]**2 + dY[y_old,x_old]**2)
        # print(norm_grad)
        # x_new = x_old + alpha* dX[y_old,x_old]
        # y_new = y_old + alpha* dY[y_old,x_old]
        x_new = x_old + alpha/norm_grad * dX[y_old,x_old]
        y_new = y_old + alpha/norm_grad * dY[y_old,x_old]
        

        x_new = int(np.round(x_new))
        y_new = int(np.round(y_new))
        # print(x_new, y_new)


        if (x_new, y_new) in xys:
            #delete the last coordinate
            del xys[-1]
            break

        x_old = x_new
        y_old = y_new

    xs, ys = list(zip(*xys))

    return xs, ys


xs, ys = crawl_gradient(dY,dX)
plt.plot(xs,ys, c = 'k', lw = 2, marker = 'o')

