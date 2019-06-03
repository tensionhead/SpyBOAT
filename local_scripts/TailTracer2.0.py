import numpy as np
import pandas as pd
from os import path
from skimage.morphology import skeletonize, disk
from skimage.measure import profile_line
import matplotlib.pyplot as plt
from tifffile import imread,imsave
import sys, glob
from skimage.filters import threshold_otsu
from scipy.ndimage import gaussian_filter
from scipy.ndimage.morphology import binary_fill_holes, binary_dilation, binary_erosion
from scipy.interpolate import splprep, splev
import skan as sk # fancy skeleton analyzer module, see https://jni.github.io/skan/getting_started.html,
#INSTALLING SKAN: execute this in command line, pip install git+https://github.com/jni/skan


plt.ion()#enables interactive mode
movie_dir = '/Users/vibe/Desktop/SAVE_TO_SERVER/Learning_Python/Skeletonize_project/'
fnames = glob.glob(path.join(movie_dir, '*tif'))
# print(fnames)
movie_path = path.join(movie_dir, 'MAX_reg_20190426_P1_crop.tif')
movie = imread(movie_path)

frame = movie[35,...]

def mk_blurred_binary(frame, sigma, num_erode = 15, num_dilate = 5):

    blurred_frame = gaussian_filter(frame, sigma=sigma)  # gaussian_filter(input, sigma=4)
    threshold = threshold_otsu(blurred_frame)
    binary_frame = blurred_frame > threshold

    binary_frame_morph = binary_fill_holes(binary_frame)
    binary_frame_morph = binary_erosion(binary_frame_morph, iterations=num_erode)
    binary_frame_morph = binary_dilation(binary_frame_morph, iterations=num_dilate)

    return blurred_frame, binary_frame_morph

def get_raw_midline(binary_frame):

    skel_frame = skeletonize(binary_frame)
    # if you wanna have a look, plot degrees
    # pixel_graph, coordinates, degrees = sk.csr.skeleton_to_csgraph(skel_frame)
    # branch_summary = sk.csr.summarise(skel_frame)
    skel_csr = sk.csr.Skeleton(skel_frame)  # function from skan allows to trace path of longest branch following "unique skeleton ID"
    all_paths = []

    for i in range(skel_csr.n_paths):
        all_paths.append(skel_csr.path_coordinates(i))

    index_longest = np.argmax(list(map(len, all_paths)))
    longest_branch_coords = all_paths[index_longest]

    #longest_branch_index = branch_result['branch-distance'].idxmax()  # Returns the branch index of the branch with the max value in the dataframe "branch_result", in the colum "branch-distance"
    #longest_branch_coords = skeleton.path_coordinates(longest_branch_index)  # extract path coordinates

    return skel_frame, longest_branch_coords

def mk_splined_midline(midline, smoothing = 0.5, Npoints = 100):

    '''
    Take the raw midline coordinates from a single frame,
    and do a spline curve interpolation. Return *Npoints*
    spline coordinates and the spline itself (tck).
    '''



    # parameter of the curve,
    # go from start to end

    y = midline[:,0]
    x = midline[:,1]

    # normalize and scale smoothing condition
    s = smoothing * len(x)

    # tck is the spline representation
    tck,_ = splprep( [x, y], s=s)

    # evaluate parametric spline
    u = np.linspace(0, 1, Npoints )
    spline_coords = splev(u, tck, der = 0)

    return spline_coords, tck


#def extrapolate_midline_spline(tck, binary_frame):
def extrapolate_midline_spline(tck, nr_tangents = 10):
    # get average tangent on the last 10% of the
    # midline spline, assuming that 1 is posterior end

    u = np.linspace(0.95, 1, nr_tangents)
    tangents = splev(u, tck, der = 1)


    return tangents






#------------------------Loop through movie-----------------------------------------------

def get_splines_tangents(movie, Npoints = 100, spline_smooth = 0.5, ema_smooth = 0.5):
    NFrames= movie.shape[0] #if you write movie.shape you will see (nr.frames, size x, size y), so movie.shape[0] gives you the nr. frames
    blurred_movie = np.zeros(movie.shape)
    skel_movie = np.zeros(movie.shape)
    pruned_skel_movie = np.zeros(movie.shape)

    splines_x_df = pd.DataFrame(columns=[f'coord {i}' for i in range(Npoints)])
    splines_y_df = pd.DataFrame(columns=[f'coord {i}' for i in range(Npoints)])
    delta_xy_df = pd.DataFrame(columns=['dx', 'dy'])

    for frame_num in range(NFrames):
        frame = movie[frame_num,...]
        blurred_frame, binary_frame_morph = mk_blurred_binary(frame, 5, num_erode=15, num_dilate=5)
        blurred_movie[frame_num, ...] = blurred_frame
        skel_frame, longest_branch_coords = get_raw_midline(binary_frame_morph)
        skel_movie[frame_num, ...] = skel_frame

        # coordinate mix up - fix later!
        pruned_skel_movie[frame_num, longest_branch_coords[:,1].astype(int), longest_branch_coords[:,0].astype(int)] = 1

        #midline (here called "longest_branch_coords" is the x and y coordinates of the longest branch in an array- size 2 x Nframes
        spline_coords, tck = mk_splined_midline(longest_branch_coords, smoothing=spline_smooth, Npoints = Npoints)  # spline_coords is now a list containing two elements (each of which is an array: xcoords and ycoords)

        # collect spline coordinates


        splines_x_df.loc[frame_num, :] = spline_coords[0]
        splines_y_df.loc[frame_num, :] = spline_coords[1]

        # construct and average posterior tangents
        tangents = extrapolate_midline_spline(tck)

        # tangents is now a list containing two elements (each of which is an array)
        # first is dx second is dy of the tangent vectors
        dx = np.mean(tangents[0])
        dy = np.mean(tangents[1])
        vector_length = np.sqrt(dx ** 2 + dy ** 2)
        dx_norm = dx / vector_length
        dy_norm = dy / vector_length
        # add the dx and dy to a df, and do ema on these
        delta_xy_df.loc[frame_num, 'dx'] = dx_norm
        delta_xy_df.loc[frame_num, 'dy'] = dy_norm

    # EMA smooth splines coordinates AND
    # average delta_xy

    # axis defines direction of smoothing- 0 means along row,
    # which should smooth in time
    ema_splines_x = splines_x_df.ewm(alpha=ema_smooth, axis=0).mean()
    ema_splines_y = splines_y_df.ewm(alpha=ema_smooth, axis=0).mean()

    ema_delta_xy = delta_xy_df.ewm(alpha = ema_smooth, axis = 0).mean()

    # length of tangent coordinates
    tang_len = 100
    tangents_x = pd.DataFrame(index = range(NFrames), columns= [f'coord {i}' for i in range(tang_len)])
    tangents_y = pd.DataFrame(index = range(NFrames), columns= [f'coord {i}' for i in range(tang_len)])

    for frame_num in range(NFrames):
        tx, ty = get_tangent_coords(ema_delta_xy.iloc[frame_num,:],
                                                          ema_splines_x.iloc[frame_num,-1],
                                                          ema_splines_y.iloc[frame_num, -1],
                                                          length = tang_len
                                                          )

        tangents_x.loc[frame_num, :] = tx
        tangents_y.loc[frame_num, :] = ty

    return ema_splines_x, ema_splines_y, tangents_x, tangents_y, pruned_skel_movie


def get_tangent_coords(delta_xy, posterior_x, posterior_y, length = 100):

    '''

    Given the unit-vector of the average tangent
    and the posterior origin, return tangent coordinates.

    :param delta_xy:
    :param posterior_x:
    :param posterior_y:
    :param length:
    :return:
    '''

    tpoints_x = np.arange(length) * delta_xy[0] + posterior_x
    tpoints_y = np.arange(length) * delta_xy[1] + posterior_y

    return tpoints_x, tpoints_y




def extrapolate2edge(outline, line_coordinates, max_length=100):  # Interpolates the last few coordinates from the branch until the outline of the tail
    #line_coordinates is a dictionary where each key is the frame_num and frame_num[0] is x, frame_num[1] is y
    #outline is a binary movie

    fit_n = 30  # the number of points from the end to consider for the fit
    coordFinal = {}  # will contain the lines with their extrapolated parts
    # movingROI = np.zeros(outline.shape)

    for f in range(np.shape(outline)[0]):

        x = np.copy(line_coordinates[str(f)][0])
        y = np.copy(line_coordinates[str(f)][1])

        fit = np.polyfit(x[-fit_n:], y[-fit_n:],
                         1)  # fits a line of order 1 (linear) to the last 10 points (=fit_n) of the branch

        # loop over a list of 1001 points starting from the last point in the line (closest to the posterior) until the edge of teh frame
        # check the value in the outline movie (binary) for each of those points, if =0, stop the loop
        for step in np.linspace(x[-1], np.shape(outline[f, ...])[0] - 1, 1001):
            new_x = np.round(step).astype('uint8')
            new_y = np.round(fit[0] * step + fit[1]).astype('uint8')
            value = outline[f, new_x, new_y]
            if value == 1:
                x = np.concatenate(([new_x], x))
                y = np.concatenate(([new_y], y))
            else:
                break

        x, y = np.unique([x, y], axis=1)

        tree = spatial.KDTree(list(zip(x, y)))
        dist, id_sorted = tree.query([x[0], y[0]], k=len(x))
        x_sorted, y_sorted = x[id_sorted], y[id_sorted]

        # plt.figure()
        # plt.imshow(outline[f, ...], cmap='gray')
        # plt.scatter(y_sorted, x_sorted, 10, range(len(x)))
        # plt.show()
        # plt.savefig(
        #     r'/Users/vibe/Desktop/SAVE_TO_SERVER/Learning_Python/Skeletonize_project/Results/viz/vizÅ{}.png'.format(
        #         f))
        # plt.close('all')

        coordFinal[str(f)] = x[-max_length:], y[-max_length:]

    return coordFinal






#blurred_movie, skel_movie, pruned_skel_movie, splined_skel_movie, splines_x, splines_y = loop_through_movie(movie)
#smoothed_coords_x, smoothed_coords_y, smoothed_skeleton_movie, movie = EMA_smoothing(movie, splines_x, splines_y)

#save output to visualize whole skeleton and only longest branch
# imsave(movie_dir+'skel_movie.tif', skel_movie.astype(np.uint16))
# imsave(movie_dir+'pruned_skel_movie.tif', pruned_skel_movie.astype(np.uint16))
# imsave(movie_dir +'splined_skel_movie.tif', splined_skel_movie.astype(np.uint16))
# imsave(movie_dir+'smooth_skel_movie.tif', smoothed_skeleton_movie.astype(np.uint16))
# imsave(movie_dir+'overlay_movie.tif', movie.astype(np.uint16))





















