import numpy as np
import matplotlib.pyplot as plt

from skimage import io

import grad_flux as gf
import plotting as pl


def next_step(vy, vx):

    ''' 
    Given a gradient vector (*vy*, *vx*)
    sitting at a pixel, return the direction to 
    select the next best of the 8 neighbouring pixels
    '''

    directions = np.array(
        [
            (-1, 0),
            (-1, -1),
            (0, -1),
            (+1, -1),
            (+1, 0),
            (+1, +1),
            (0, +1),
            (-1, +1),
            (-1, 0),
        ]
    )

    # calculate the vector angle from and instruct the direction
    # increasing angles from -180 to +180 in 45 degree steps
    angle_boxes = np.array(
        [-157.5, -112.5, -67.5, -22.5, 22.5, 67.5, 112.5, 157.5, 180]
    )

    crawl_angle = np.arctan2(vy, vx) * 180 / np.pi
 
    box_index = np.where(crawl_angle < angle_boxes)[0][0]
    dv = directions[box_index]

    return dv


def crawl_gradient(dY, dX, ini_point=(0, 0)):

    # initial values
    x_old, y_old = ini_point

    # lists of (x and y) coordinates
    # giving the crawling path
    xys = []
    
    # gradient descent
    while True:
        xys.append((x_old, y_old))

        vy = dY[y_old, x_old]
        vx = dX[y_old, x_old]

        dx, dy = next_step(vy, vx)
        x_new = x_old + dx
        y_new = y_old + dy

        if (x_new, y_new) in xys:
            # ran into a loop
            # stop crawling and delete the last coordinate
            del xys[-1]
            break

        x_old = x_new
        y_old = y_new

    return np.array(xys)


plt.ion()

movie = io.imread("Quad-movie2-crop.tif")
movie = io.imread('/home/whir/TheoBio/data/GoodPhaseMovies/GB10_phase_Max_L6.tif')
frame = 84

# get the gradient vectorfield
dY, dX = gf.phase_gradient(movie[frame, ...])

plt.contour(movie[frame], levels=15)
#pl.show_vfield(dX, dY, skip=10)
plt.imshow(movie[frame], interpolation="nearest", cmap="bwr")

x_inis = np.arange(100, 400, 50)
y_inis = np.arange(100, 400, 50)

for xi in x_inis:
    ini_point = (xi, 380)
    cpath  = crawl_gradient(dY, dX, ini_point)
    plt.plot(*ini_point, 'ro')
    plt.plot(cpath[:,0], cpath[:,1], c="k", lw=2, marker=".")

for yi in y_inis:
    ini_point = (120, yi)
    cpath  = crawl_gradient(dY, dX, ini_point)
    plt.plot(*ini_point, 'ro')
    plt.plot(cpath[:,0], cpath[:,1], c="k", lw=2, marker=".")
    

def old_instructions(y_o, x_o):

    '''
    Doesn't have uniform probability
    for the 8 neighbouring pixels..
    '''

    # calculating the length of the vector, normalizing
    # however, rounding operation is biased against the diagonal directions
    norm_grad = np.sqrt(dX[y_o, x_o] ** 2 + dY[y_o, x_o] ** 2)
    # step width
    alpha = 1
    x_n = x_o + alpha / norm_grad * dX[y_o, x_o]
    y_n = y_o + alpha / norm_grad * dY[y_o, x_o]
    x_n = int(np.round(x_n))
    y_n = int(np.round(y_n))

    return x_n, y_n

