import numpy as np
import matplotlib.pyplot as plt

from skimage import io

import grad_flux as gf
from gradient_descent import crawl_gradient
import grad_plotting 

plt.ion()

movie = io.imread("Quad-movie.tif")
frame = 7

# get the gradient vectorfield
dY, dX = gf.phase_gradient(movie[frame, ...])

plt.contour(movie[frame], levels=15)
grad_plotting.show_vfield(dX, dY, skip=2)
plt.imshow(movie[frame], interpolation="nearest", cmap="bwr")

x_inis = np.arange(1, 50, 5)
y_inis = np.arange(1, 50, 5)

for xi in x_inis:
    ini_point = (xi, 0)
    cpath  = crawl_gradient(-dY, -dX, ini_point)
    plt.plot(*ini_point, 'ro')
    plt.plot(cpath[:,0], cpath[:,1], c="k", lw=2, marker=".")

for yi in y_inis:
    ini_point = (0, yi)
    cpath  = crawl_gradient(-dY, -dX, ini_point)
    plt.plot(*ini_point, 'ro')
    plt.plot(cpath[:,0], cpath[:,1], c="k", lw=2, marker=".")
    
