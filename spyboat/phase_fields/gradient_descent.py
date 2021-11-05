import numpy as np
import matplotlib.pyplot as plt

from skimage import io

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
    box_index = np.where(crawl_angle <= angle_boxes)[0][0]
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
        print(f'path is at ({x_old}, {y_old})')

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

        # check for running into image border
        if x_new < 0 or x_new >= dX.shape[1]:
            break
        if y_new < 0 or y_new >= dX.shape[0]:
            break

        # check for running into mask
        if dY[y_new, x_new] == 0 and dX[y_new, x_new] == 0:
            break
        
        x_old = x_new
        y_old = y_new

    print('\n')
    return np.array(xys)


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

