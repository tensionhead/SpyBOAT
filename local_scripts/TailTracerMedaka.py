import numpy as np
import pandas as pd
from os import path
from skimage.morphology import skeletonize, disk
from skimage.measure import profile_line
import matplotlib.pyplot as plt
from tifffile import imread,imsave
import sys, glob
from skimage.filters import threshold_otsu
from skimage.measure import profile_line
from scipy.ndimage import gaussian_filter
from scipy.ndimage.morphology import binary_fill_holes, binary_dilation, binary_erosion
from scipy.interpolate import splprep, splev, RectBivariateSpline
from scipy.stats import scoreatpercentile as score
import skan as sk # fancy skeleton analyzer module, see https://jni.github.io/skan/getting_started.html,
#INSTALLING SKAN: execute this in command line, pip install git+https://github.com/jni/skan

plt.ion()#enables interactive mode


# --- globals -----------------

# gaussian blur bandwidth
GBsigma = 5

# number of spline evaluations
# of fitted midline
NpointsMidLine = 100

# directory to store the output tifs
tif_dir = path.expanduser('~/tif_dir/')

# --- globals end ------------


def mk_blurred_binary(frame, sigma,
                      num_erode = 15,
                      num_dilate = 5,
                      perc = 98):

    '''
    Set 0 < perc < 100 to do a percentile filtering before
    thresholding, careful to not throw out too much!

    Put perc = None, to disable that filter
    '''

    blurred_frame = gaussian_filter(frame, sigma=sigma)  # gaussian_filter(input, sigma=4)

    if perc:
        perc_score = score(blurred_frame, perc)
        perc_filtered = blurred_frame[blurred_frame < perc_score]
        threshold = threshold_otsu(perc_filtered)
    else:        
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

    # function from skan allows to trace path of
    # longest branch following "unique skeleton ID"
    skel_csr = sk.csr.Skeleton(skel_frame)  
    all_paths = []

    for i in range(skel_csr.n_paths):
        all_paths.append(skel_csr.path_coordinates(i))

    # find longest path
    index_longest = np.argmax(list(map(len, all_paths)))
    longest_branch_coords = all_paths[index_longest]

    return longest_branch_coords

def fit_midline_spline(midline, smoothing = 0.5):

    '''
    Take the raw midline coordinates from a single frame,
    and do a spline curve interpolation. 
    Only return the spline itself (tck), no coordinates.
    '''
    
    # parameter of the curve,
    # go from start to end

    y = midline[:,0]
    x = midline[:,1]

    # normalize and scale smoothing condition
    s = smoothing * len(x)

    # tck is the spline representation
    tck,_ = splprep( [x, y], s=s)


    return tck


def calc_spline_length(tck):

    '''
    Use arc length formula to 
    calculate length of parameterized spline curve
    given by splprep function
    '''

    Npoints = 500
    
    u = np.linspace(0,1, Npoints)

    # derivative
    dsx, dsy = splev(u,tck,der = 1)

    # arc length formula -> integral of norm of derivatives
    curve_length = np.sum( np.sqrt(dsx**2 + dsy**2) )
    # normalize
    curve_length /= Npoints

    return curve_length

def get_posterior_tangent(tck, nr_tangents = 10):

    '''
    get average tangent on the last 10% of the
    midline spline, assuming that u = 1 is posterior end!
    '''

    u = np.linspace(0.90, 1, nr_tangents)
    tangents = splev(u, tck, der = 1)

    dx = np.mean(tangents[0])
    dy = np.mean(tangents[1])

    # normalize
    vector_length = np.sqrt(dx ** 2 + dy ** 2)
    dx_norm = dx / vector_length
    dy_norm = dy / vector_length
    
    return dx_norm, dy_norm


def get_splines_tangents(frame, sigma = GBsigma, num_erode = 15,
                         num_dilate = 10, perc = 98,
                         spline_smooth = 0.5):

    '''
    Input is raw movie frame, does: blurring -> binarization
    -> morphological operations -> skeletonization and midline extraction
    -> spline curve fitting + tanget component averaging

    Output is spline midline coordinates and tangent components

    This function is for monitoring only...
    '''

    blurred_frame, binary_frame_morph = mk_blurred_binary(frame, sigma,
                                                          num_erode=num_erode,
                                                          num_dilate=num_dilate,
                                                          perc = perc)
    
    longest_branch_coords = get_raw_midline(binary_frame_morph)
        
    tck = fit_midline_spline(longest_branch_coords[::10],
                                            smoothing=spline_smooth)


    # evaluate parametric spline
    u = np.linspace(0, 1, NpointsMidLine )
    spl_x, spl_y = splev(u, tck, der = 0)

    
    # construct and average posterior tangents
    dx, dy = get_posterior_tangent(tck)

    return spl_x, spl_y, dx, dy, binary_frame_morph
    

def get_extrap_midline(frame, num_erode = 20,
                         num_dilate = 10, perc = 98,
                       spline_smooth = 0.5):


    '''
    Input is raw movie frame, does: 
    -> blurring -> binarization
    -> morphological operations -> skeletonization and midline extraction
    -> spline curve fitting + average tanget components
    -> posterior edge detection
    -> tangential extrapolation

    Result:
    1-pixel-spaced coordinates
    representing the posterior-anterior axis
    for (intensity) profile extraction
    '''

    
    blurred_frame, binary_frame_morph = mk_blurred_binary(frame, sigma = GBsigma,
                                                          num_erode=num_erode,
                                                          num_dilate=num_dilate,
                                                          perc = perc)
    
    longest_branch_coords = get_raw_midline(binary_frame_morph)
        
    tck = fit_midline_spline(longest_branch_coords[::5],
                             smoothing=spline_smooth)
            

    # construct and average posterior tangents
    dx, dy = get_posterior_tangent(tck)

    # posterior (u = 1) end of splined skel midline:
    X,Y = splev(1, tck)

    # get pixel distance to edge
    post_dist = posterior_edge_detection( (X,Y), (dx, dy),
                                          binary_frame_morph)
    
    # tangent coordinates till binary posterior edge
    # may add some margin, output is already 'pixel-spaced'
    tx, ty = get_tangent_coords( (dx,dy), (X,Y), length = post_dist)

    # construct pixel unit spaced spline coordinates
    L = np.around( calc_spline_length(tck) )    
    u = np.linspace(0, 1, int(L) - 1)
    
    sx, sy = splev(u, tck)

    # join extrapolation and spline coords
    lx = np.concatenate( [sx, tx] )[::-1]
    ly = np.concatenate( [sy, ty] )[::-1]
    
    return lx, ly
    
def posterior_edge_detection(XY, dXY, binary_frame):

    '''
    Taking posterior end of skeleton midline (XY) and
    tangent components (dXY), evaluate the binarized
    frame along the extrapolated tangent line and return
    the euclidian pixel distance to the edge of the mask.

    Max scan distance along tangent is :mxScan:.
    '''

    mxScan = 100
    
    X,Y = XY
    dx, dy = dXY

    # end point of extrapolation
    Xend = X + mxScan * dx
    Yend = Y + mxScan * dy

    profile = profile_line( binary_frame.astype(int), [Y,X], [Yend, Xend] )

    # find index (=distance in pixel units) of high-to-low transition
    post_dist = np.argmin( np.diff(profile) )

    return post_dist

def get_tangent_coords(delta_xy, posterior_xy, length = 100):

    '''

    Given the unit-vector of the average tangent
    and the posterior origin, return tangent coordinates.

    :param delta_xy:
    :param posterior_x:
    :param posterior_y:
    :param length:
    :return:
    '''

    tpoints_x = np.arange(length) * delta_xy[0] + posterior_xy[0]
    tpoints_y = np.arange(length) * delta_xy[1] + posterior_xy[1]

    return tpoints_x, tpoints_y


def extract_profile(frame, coords):

    '''
    Extract (intensity) profile along curve :coords:
    of a single frame. Blurring recommended!

    :coords: have xy ordering!
    BivariateSpline has yx ordering!

    Sub-pixel coordinates supported
    via bivariate spline interpolation
    (no smoothing!)
    '''

    # default row wise ordering
    yd = np.arange(frame.shape[0])
    xd = np.arange(frame.shape[1])

    biv_spl = RectBivariateSpline(yd,xd,frame)

    profile = biv_spl.ev(coords[1], coords[0])

    return profile    
    

# --- Kymographs ------------------------------------------------

def construct_Kymograph(movie, MxPAsteps = 150, sigma = GBsigma, **kwargs):

    '''
    **kwargs are for *get_etrap_midline* !
    '''

    NFrames= movie.shape[0]

    Kymo = np.zeros( (MxPAsteps, NFrames) )

    for frame_num in range(NFrames):


        frame = movie[frame_num,...]
        
        # blurring for profile
        bframe = gaussian_filter(frame, GBsigma)
        
        # get the complete midline coordinates
        lx, ly = get_extrap_midline(frame, **kwargs)

        profile = extract_profile(bframe, [lx,ly])
        print(f'Processed frame {frame_num}, profile length: {profile.shape}')
        
        # is safe if profile is longer than spatial axis
        Kymo[:, frame_num][:len(profile)] = profile[:MxPAsteps]

    return Kymo

    



#---------------EMA stuff ---------------------------------------

def get_EMA_midline(movie, ema_smooth = 0.5):


    '''
    Loops through movie and collects midline coordinates +
    posterior tangent components and does EMA smoothing
    for both
    '''
    
    NFrames= movie.shape[0] #if you write movie.shape you will see (nr.frames, size x, size y), so movie.shape[0] gives you the nr. frames

    binary_mov = np.zeros( movie.shape )
    
    # store x and y coordinates of spline evaluations
    splines_x_df = pd.DataFrame(columns=[f'coord {i}' for i in range(NpointsMidLine)])
    splines_y_df = pd.DataFrame(columns=[f'coord {i}' for i in range(NpointsMidLine)])

    # store averaged tangents
    dxy_df = pd.DataFrame(columns=['dx', 'dy'])

    for frame_num in range(NFrames):
        print(f'Processing frame {frame_num}...')
        frame = movie[frame_num,...]

        # get spline coordinates, tangent components and binary frame
        spl_x, spl_y, dx, dy, bf = process_single_frame(frame) 

        # collect the binary morph

        binary_mov[frame_num,...] = bf
        
        # collect spline coordinates into data frame
        splines_x_df.loc[frame_num, :] = spl_x
        splines_y_df.loc[frame_num, :] = spl_y
        
        # add the dx and dy to a df, and do ema on these
        dxy_df.loc[frame_num, 'dx'] = dx
        dxy_df.loc[frame_num, 'dy'] = dy

    # EMA smooth splines coordinates AND
    # average delta_xy

    # axis defines direction of smoothing- 0 means along row,
    # which should smooth in time
    ema_splines_x = splines_x_df.ewm(alpha=ema_smooth, axis=0).mean()
    ema_splines_y = splines_y_df.ewm(alpha=ema_smooth, axis=0).mean()

    ema_delta_xy = dxy_df.ewm(alpha = ema_smooth, axis = 0).mean()

    # length of tangent coordinates
    tang_len = 100
    tangents_x = []
    tangents_y = []

    for frame_num in range(NFrames):

        # posterior spline end coordinates
        X = ema_splines_x.iloc[frame_num, -1]
        Y = ema_splines_y.iloc[frame_num, -1]

        # tangent components
        dx, dy  = ema_delta_xy.iloc[frame_num,:]


        post_end = posterior_edge_detection([XY], [dx,dy],
                                            binary_mov[frame_num,...])
        
        tx, ty = get_tangent_coords([dx,dy], [X,Y],
                                    length = post_end)

        tangents_x.append(tx)
        tangents_y.append(ty)

    return ema_splines_x.T, ema_splines_y.T, tangents_x, tangents_y


# --- Plotting ------------------------------

def Plot_single_frame(frame, **kwargs):

    '''
    Plot splined midline and extrapolation
    separately
    kwargs are for :process_single_frame"
    '''

    # sc is spline coords
    sx, sy, dx, dy, bf = get_splines_tangents(frame, **kwargs)

    blurred = gaussian_filter(frame, GBsigma)
    
    # posterior end of skel midline:
    X,Y = sx[-1], sy[-1]
    
    post_dist = posterior_edge_detection( (X,Y), (dx, dy), bf)

    # tangent till binary posterior edge
    # may add some margin, output is already 'pixel-spaced'

    tx, ty = get_tangent_coords( (dx,dy), (X,Y), length = post_dist)
    

    fig, ax = plt.subplots()
    ax.imshow(blurred)
    ax.imshow(bf, alpha = 0.13, cmap = 'gray')
    ax.plot(sx, sy, lw = 2., color = 'orange')
    ax.arrow(sx[-1],sy[-1],100*dx,100*dy, color = 'orange', ls = '--')

    ax.plot(tx,ty, lw = 2., color = 'r')

    return fig, ax


def Plot_single_frame2(frame, **kwargs):

    '''
    Plot complete midline with start and end
    kwargs are for :get_extrap_midline"
    '''

    # sc is spline coords

    # get the complete midline coordinates
    lx, ly = get_extrap_midline(frame, **kwargs)
    
    blurred = gaussian_filter(frame, GBsigma)
    

    fig, ax = plt.subplots()
    ax.imshow(blurred)


    ax.plot(lx[0], ly[0], 'ko')
    ax.plot(lx[-1], ly[-1], 'wo')
    ax.plot(lx,ly, lw = 3., color = 'r', alpha = 0.5)

    return fig, ax


def mk_tif_series(movie, plot_func, **kwargs):

    '''
    Loop over movie and save the individual 
    plots made by :plot_func(frame): as tifs
    '''

    plt.ioff()
                                  
    for frame_num in range(movie.shape[0]):

        print(f'Plotting frame {frame_num}...')
        frame = movie[frame_num,...]
        fig, ax = plot_func(frame, **kwargs)

        fig.savefig( path.join(tif_dir, f'frame_{frame_num}.tif') )
        plt.close(fig)

    plt.ion()

# --- not used atm ------------
    
def Plot_EMA_frame(movie, frame_num, esx, esy, etx, ety):

    '''
    Use ema smoothed spline and tangent coordinates
    '''

    frame = movie[frame_num,...]
    # sc is spline coords
    sx, sy, dx, dy, bf = process_single_frame(frame, sigma = 5,
                                              num_erode = 15, num_dilate = 7)


    fig, ax = plt.subplots()
    ax.imshow(frame)
    ax.imshow(bf, alpha = 0.13, cmap = 'gray')
    
    ax.plot(esx[frame_num][::-1], esy[frame_num][::-1], lw = 1.5, color = 'r')
    ax.plot(etx[frame_num], ety[frame_num], '-', color = 'yellow', lw = 1.5)
    return fig, ax

def mk_EMA_tifs(movie):


    esx, esy, etx, ety = get_EMA_midline(movie)

    plt.ioff()
    
    for frame_num in range(movie.shape[0]):

        print(f'Plotting frame {frame_num}...')
        frame = movie[frame_num,...]
    
        fig, ax = Plot_EMA_frame(movie, frame_num, esx, esy, etx, ety)

        fig.savefig( path.join(tif_dir, f'frame_{frame_num}.tif') )
        plt.close(fig)

    plt.ion()

# --- do some processing ---


movie_dir = path.expanduser('~/ownCloud/Shared/TailTracerMedaka/')
fnames = glob.glob(path.join(movie_dir, '*tif'))

print(fnames)
movie_path = path.join(movie_dir, fnames[0])
movie = imread(movie_path)
print(f'Read in {movie_path}')


frame = movie[75,...]



sys.exit()
# look at a single frame

Plot_single_frame(movie[25,...], num_erode = 17, num_dilate = 5)

Plot_single_frame2(movie[25,...], num_erode = 17, num_dilate = 5)


# make a kymo and plot it
Kymo = construct_Kymograph(movie, MxPAsteps = 110, num_erode = 20, num_dilate = 12)

# carefully blur Kymo with very narrow bandwidth
KymoB = gaussian_filter(Kymo, 1)

plt.figure()
plt.imshow(KymoB[:,:], origin = 'lower', cmap = 'magma')


# uncomment (one only, otherwise tifs get overwritten)
# to make a movie of the line extraction

# spline and extrapolation separate
# mk_tif_series(movie, plot_func=Plot_single_frame, num_erode = 20, num_dilate = 12)

# complete midline
# mk_tif_series(movie, plot_func=Plot_single_frame2, num_erode = 20, num_dilate = 12)













