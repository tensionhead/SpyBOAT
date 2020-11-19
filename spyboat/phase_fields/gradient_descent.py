import sys
from os.path import expanduser
import numpy as np
import numpy as np
import matplotlib.pyplot as plt

from skimage import io

import grad_flux as gf
import plotting as pl
plt.ion()

movie = io.imread('Quad-movie2-crop.tif')

frame = 250

# get the gradient vectorfield
dY, dX = gf.phase_gradient(movie[frame,...])

plt.contour(movie[frame], levels = 35)
pl.show_vfield(dX, dY, skip = 2)

# initial values
x_old, y_old = 49, 0
alpha = 2

xs, ys = [], []
# stupid gradient descent
for i in range(30):
    print(x_old,y_old)
    xs.append(x_old)
    ys.append(y_old)

    norm_grad = np.sqrt(dX[y_old,x_old]**2 + dY[y_old,x_old]**2)
    print(norm_grad)
    x_new = x_old + alpha/norm_grad * dX[y_old,x_old]
    y_new = y_old + alpha/norm_grad * dY[y_old,x_old]

    print(x_new, y_new)
    x_old = int(np.round(x_new))
    y_old = int(np.round(y_new))

plt.plot(xs,ys, c = 'r', lw = 2, marker = 'o')
