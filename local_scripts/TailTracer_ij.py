from __future__ import with_statement,division
from sys import path
from os.path import expanduser

# scriptpath = expanduser('~/PSM/progs/IJ/')
# path.append( scriptpath)

import ij
from ij import IJ,ImagePlus,ImageStack,WindowManager
from ij.process import ImageStatistics, ShortProcessor, FloatProcessor
from ij.io import SaveDialog
from ij.gui import PolygonRoi,Roi,EllipseRoi,ShapeRoi,Overlay, OvalRoi, ProfilePlot 
from ij.gui import GenericDialog,Overlay,Roi,Plot, NonBlockingGenericDialog
from ij.plugin.filter import GaussianBlur
from ij.measure import ResultsTable,Measurements,SplineFitter
from ij.plugin import ImageCalculator,Selection,ZProjector, HyperStackConverter
from ij.plugin.filter import ThresholdToSelection, LutApplier
from java.awt import Color
from java.lang.Math import atan2, sin, cos

import pickle
# gb_stack = movie.createEmptyStack() # to store the results as movie

# globals
#=============================================
thresh_method = 'Huang'
watershed = False  # do watershed?
wshed_tol = 0.2 # adjustable watershed tolerance, .6 for 15-08 YZ
show_binary = False # if segmentation fails, look at a single frame only!
plot_color = Color.red
roi_color = Color.orange
x_or_y = 'y' # PSM posterior should be at the bottom of the movie!

Color1 = Color(255,5,20,65)    # light red
Color2 = Color(100,250,230,150) # light violet
Color3 = Color(180,250,100,75) # light green
#=============================================

def ema_smoothing(data,s = None):

    ''' Exponential moving average '''

    if s is None:
        s = 1./len(data)

    mav_win_len = int(s * len(data)) # size of initial window
    # initiliazing with mav
    # res = [ sum([ 1./mav_win_len * data[i] for i in range(mav_win_len) ]) ]
    
    # initializing with first val
    res = [ data[0] ]
    for el in data[1:]:
        res.append(s*float(el) + (1-s)*res[-1])
        
    return res

def sort_xy(list1, list2):
    # sort both lists according to list1 ordering

    Nel = len(list1)
    ll = [ (list1[i], i) for i in range(Nel) ]

    # sorted list1
    slist1 = [ll[i][0] for i in range(Nel)]

    slist2 = [list2[ll[i][1]] for i in range(Nel)]

def argmax(in_list):

    ll = [ (in_list[i], i) for i in range( len(in_list) ) ]
    sll = sorted(ll)

    return sll[-1][1] # index of maxima

def mean_phase(phases):

    # sines
    sy = sum( [sin(p) for p in phases] )
    # cosines
    cx = sum( [cos(p) for p in phases] )

    return atan2(sy, cx)
    
def smooth_series(series, sfac = 1., do_plot = False):
    
    ema_series = ema_smoothing(series, s = sfac/len(series))
    t = range(len(ema_series)) # "time vector"
    if do_plot:
       p = Plot('raw and EMA', 'frame','var')
       p.add('circles', t, series)
       p.setColor(Color.red)
       p.add('line', t, ema_series)
       p.show()
       
    return ema_series
        
def plot_series(series, title, xlabel = 'frame', ylabel = 'x'):
    t = range(len(series)) # "time vector"
    p = Plot(title, xlabel, ylabel)
    p.setLineWidth(2.)
    #p.add('circles', t, series)
    p.setColor(plot_color)
    p.add('line', t, series)
    p.show()
    return p
    

def add_to_table(series, table, column):

    for i in range(len(series)):
        table.setValue(column, i, series[i])
    #return table
    
def mk_binary_tail(imp, sigma, watershed = watershed, wshed_tol = wshed_tol):

    # Blur beforehand!
    
    ipr = imp.getProcessor().duplicate()
    ipr.blurGaussian(sigma)

    # to allow for robust thresholding despite moving frame from the registration
    # ipr.min(min_fill_val)
    
    ipr.setAutoThreshold(thresh_method, True, False)
    minv = ipr.getMinThreshold()
    maxv = ipr.getMaxThreshold()

    # now create a binary mask
    ipr.threshold(int(minv))
    ipr = ipr.convertToByteProcessor() # makes it 'binary'
    imp = ImagePlus('bin PSM',ipr)

    if watershed:
        IJ.run(imp,"Adjustable Watershed", "tolerance=" + str(wshed_tol))
    
    return imp

def get_anterior_roi(imp, sigma, perc = 0.95):

    score =  get_score_at_percentile(imp, perc = perc)
    print 'score:', score
    ipr = imp.getProcessor().duplicate()
    
    ipr.setThreshold( int(score), 2**16, 1 )
    
    tts = ThresholdToSelection()
    tts.setup("",imp)
    shape_roi = tts.convert(ipr)

    # no roi found
    if shape_roi is None:
        display_msg('No Roi', 'No anterior roi found, check movie.. exiting!')
        return False
    
    # only one connected roi present
    if type(shape_roi) == ij.gui.PolygonRoi:
        anterior_roi = shape_roi
        return anterior_roi
    
    rois = shape_roi.getRois() # splits into sub rois
    
    anterior_roi = get_largest_roi(rois) # sort out smaller Rois

    return anterior_roi

def scan_y(imp,roi,x_direction = 'right'):

    '''
    Walk through y-coordinate and get roi boundary from 
    hitting from the x-*direction*
    '''

    processor = imp.getProcessor()
    height = processor.getHeight()
    width = processor.getWidth()

    # for one slice
    xpoints = []
    ypoints = []
    
    # loop over byte processor
    for y in range(height-1):
        found = False
        for x in range(width):
            if x_direction == 'right': # dorsal-ventral
                x = width - x

            val = processor.getf(x,y)
            if val == 255:
                # print x,y
                found = True
                
                if roi.contains(x,y):
                    # print x,y
                    xpoints.append(x)
                    ypoints.append(y)
                    break # break x loop

    return xpoints,ypoints


def scan_x(imp,roi,y_direction = 'up'):

    '''
    Walk through x-coordinate and get roi boundary from 
    hitting from the y-*direction* (upwards or downwards).
    '''


    processor = imp.getProcessor()
    height = processor.getHeight()
    width = processor.getWidth()

    # for one slice
    xpoints = []
    ypoints = []

    
    # loop over byte processor
    for x in range(1,width-1):
        found = False
        for y in range(1,height-1):
            if y_direction == 'up': 
                y = height - y

            val = processor.getf(x,y)
            if val == 255:
                # print x,y
                found = True
                
                if roi.contains(x,y):
                    xpoints.append(x)
                    ypoints.append(y)
                    break # break x loop

    return xpoints,ypoints

    
def get_largest_roi(roi_list):

    if not roi_list:
        print IJ.log('Found no object at all..aborting!!')
        return

    max_ind = 0
    if len(roi_list) > 1:
        # IJ.log('Found more than one object, taking the biggest!')

        max_size = 0 # check for area size
        max_ind = 0
        for ii,roi in enumerate(roi_list):
            
            size = len(roi.getContainedPoints())
            
            if size > max_size:
                max_size = size
                max_ind = ii


    largest_roi = roi_list[max_ind]

    return largest_roi

def get_score_at_percentile(movie, perc = 0.5):

    " Score at percentile from Fiji histogram "
    
    ist = movie.getStatistics()
    counts = ist.getHistogram()

    # print ist.nBins
    # print ist.binSize
    nPixels =  ist.pixelCount
    # last value is right bin boundary
    bins = [ist.min + ist.binSize * x for x in range(ist.nBins + 1)] 
    print len(bins),len(counts)

    totalCount = 0
    for i, count in enumerate(counts):
        totalCount += count
        if totalCount/float(nPixels) > perc:
            break
        # print i,totalCount/float(nPixels), bins[i]

    score_at_perc = (bins[i] + bins[i+1])/2. # the (mid-bin) score at percentile
    return score_at_perc

def get_psm_outline(movie, sigma, thresh_method, x_or_y = 'x', direction = 'up'):

    # blur beforehand!
    # direction can be 'up' or 'down' for 'x' OR
    # 'left' and 'right' for 'y'

    binary_psm = mk_binary_tail(movie, sigma, watershed = watershed)
    
    if show_binary:
        binary_psm.show()
        
    bin_ip = binary_psm.getProcessor()

    # get rois from binary without ParticleAnalyzer!
    bin_ip.setThreshold(1,255,1)
    tts = ThresholdToSelection()
    tts.setup("", binary_psm)
    shape_roi = tts.convert(bin_ip)
    
    # only one connected roi present
    if type(shape_roi) == ij.gui.PolygonRoi:
        psm_roi = shape_roi
    else:
        rois = shape_roi.getRois() # splits into sub rois
        psm_roi = get_largest_roi(rois) # sort out smaller Rois

    # scan for the outline
    if x_or_y == 'x':
        xp,yp = scan_x(binary_psm, psm_roi, y_direction = direction)
    elif x_or_y == 'y':
        xp,yp = scan_y(binary_psm, psm_roi, x_direction = direction)

    return xp, yp

def mk_OvRoi(x, y, R = 10):
    
    roi = OvalRoi(x - R/2, y - R/2, R, R)
    roi.setStrokeWidth(1.2)
    roi.setStrokeColor( roi_color )
    return roi
        

def make_post_ant_mid_Rois(xps, yps, # psm outline coordinates
                           ant_xs, ant_ys, # anterior roi centroids
                           ant_w, R, # anterior x weight, Roi radius
                           offset_x, # x-coordinate global offset
                           ant_offset_y, post_offset_y, # y coordinate offsets
                           ema_fac): # the EMA smoothing factor


    # print len(yps),len(xps),len(ant_xs)

    NFrames = len(ant_xs) # number of coords should be number of frames

    # ---- EMA smoothing of the raw coordinates -------

    # smooth posterior
    max_inds = [argmax(yp) for yp in yps]

    x_post = [xp[mx] for xp,mx in zip(xps, max_inds)] # raw coordinate
    x_post = ema_smoothing( x_post, s = ema_fac)

    y_post = [yp[mx] for yp,mx in zip(yps, max_inds)] # raw coordinate
    y_post = ema_smoothing( y_post, s = ema_fac)

    # add post offset
    y_post = [yp + post_offset_y for yp in y_post]

    # smooth anterior
    x_ant = ema_smoothing(ant_xs, s = ema_fac)
    y_ant = ema_smoothing(ant_ys, s = ema_fac)

    # add anterior offset
    y_ant = [yp + ant_offset_y for yp in y_ant]

    # add x-offset
    x_post = [xp + offset_x for xp in x_post]
    x_ant = [xp + offset_x for xp in x_ant]
    

    # get mid PSM coordinates from smoothed ant/post

    # ant_weight for x-coord of mid point
    x_mid = [ant_w * x_a + (1-ant_w) * x_p for x_a,x_p in zip(x_ant,x_post)]
    y_mid = [(y_a + y_p)/2. for y_a,y_p in zip(y_ant,y_post)]

    # --- construct the coordinate Rois
    # --- doesn't actually loop through the movie frames

    post_rois, ant_rois, mid_rois = [], [], []
    for frame in range(1, NFrames + 1):

        post_roi = mk_OvRoi(x_post[frame-1], y_post[frame-1], R = R)
        post_roi.setPosition(frame)
        post_rois.append(post_roi)

        ant_roi = mk_OvRoi(x_ant[frame-1], y_ant[frame-1], R = R)
        ant_roi.setPosition(frame)
        ant_rois.append(ant_roi)

        mid_roi = mk_OvRoi(x_mid[frame-1], y_mid[frame-1], R = R)
        mid_roi.setPosition(frame)
        mid_rois.append(mid_roi)

    return post_rois, ant_rois, mid_rois

def get_psm_splines(the_rois, width = 20):

    poly_rois = []
    # fit a spline to the tracked PSM half
    frame = 1
    for proi, aroi, mroi in zip(*the_rois):
        
        p_x, p_y = proi.getContourCentroid()
        a_x, a_y = aroi.getContourCentroid()
        m_x, m_y = mroi.getContourCentroid()
        
        # spline fitting
        psm_poly_roi = PolygonRoi([p_x, m_x, a_x], [p_y, m_y, a_y], Roi.POLYLINE)
        psm_poly_roi.fitSpline()
        psm_poly_roi.setStrokeWidth(width)
        psm_poly_roi.setStrokeColor(Color1)
        psm_poly_roi.setPosition(frame)
        poly_rois.append(psm_poly_roi)

        # for the kymograph, one pixel spacing
        psm_polygon = psm_poly_roi.getInterpolatedPolygon(1,True)

        frame += 1
        
    return poly_rois

def make_kymograph(movie, psm_roi_splines):

    Channel = movie.getChannel()
    Slice = movie.getSlice()

    # check dimensions needed
    max_roi_length =  max( [roi_spline.getLength() for roi_spline in psm_roi_splines] )

    # spatial extend of the kymograph
    Nx = int( 1.1 * max_roi_length )
    Nt = len(psm_roi_splines)

    kymo = ShortProcessor( Nt, Nx ) # time x space

    frame = 1
    for roi_spline in psm_roi_splines:
        movie.setPositionWithoutUpdate( Channel, Slice, frame )
        movie.setRoi(roi_spline)
        pp = ProfilePlot(movie, True)
        profile = pp.getProfile() 
        # put the profile in the processor, cast down to int and flip vertical
        [kymo.putPixel( frame - 1, Nx - i, int(profile[i])) for i in range(len(profile))]
        frame += 1

    kymo_imp = ImagePlus('Kymograph', kymo)
    
    return kymo_imp

def make_float_kymograph(movie, psm_roi_splines, phase = False):

    Channel = movie.getChannel()
    Slice = movie.getSlice()

    # check dimensions needed
    max_roi_length =  max( [roi_spline.getLength() for roi_spline in psm_roi_splines] )

    # spatial extend of the kymograph
    Nx = int( 1.1 * max_roi_length )
    Nt = len(psm_roi_splines)

    kymo = FloatProcessor( Nt, Nx ) # time x space

    frame = 1
    for roi_spline in psm_roi_splines:
        
        movie.setPositionWithoutUpdate( Channel, Slice, frame )

        if phase:
            roi_spline.setStrokeWidth(1) # avoid horizontal averaging
        else:
            pass # keep original width
        
        movie.setRoi(roi_spline)
        # profile averaging has no effect?!
        pp = ProfilePlot(movie, True)

        profile = pp.getProfile() 
        # put the profile in the processor and flip vertical
        [kymo.putPixelValue( frame - 1, Nx - i, profile[i]) for i in range(len(profile))]
        frame += 1

    if phase:
        kymo_imp = ImagePlus('Phase Kymograph', kymo)

    else:
        kymo_imp = ImagePlus('Kymograph', kymo)

    return kymo_imp

def measure_rois(movie, rois):

    # measures sequence of rois along frames!
    
    Nrois = len(rois)
    NFrames = movie.getNFrames()
    res = []

    if Nrois != NFrames: # one roi for each frame!
        display_msg('Roi count mismatch!', 'Roi count mismatch!\nGot ' + str(Nrois) + ' rois and' + str(NFrames) + ' frames.. !')
        return res
    
    # table = ResultsTable()
    # table.showRowNumbers(True) # the frames
    
    Channel = movie.getChannel()
    Slice = movie.getSlice()
    
    # to distinguish slices from 'real' frames
    if NFrames < 5:
        IJ.log('Warning less than 5 frames found..')

    for frame in range(1, NFrames + 1):
        movie.setPositionWithoutUpdate(Channel, Slice, frame)
        movie.setRoi(rois[frame - 1])
        roi_mean = movie.getStatistics(Measurements.MEAN) # int 2 -> roi mean!
        res.append(roi_mean.mean)
        
    movie.killRoi() # clear roi
    return res

def measure_phase_rois(movie, rois):

    # measures sequence of rois along frames!
    
    Nrois = len(rois)
    NFrames = movie.getNFrames()
    res = []

    if Nrois != NFrames: # one roi for each frame!
        display_msg('Roi count mismatch!', 'Roi count mismatch!\nGot ' + str(Nrois) + ' rois and' + str(NFrames) + ' frames.. !')
        return res
        
    Channel = movie.getChannel()
    Slice = movie.getSlice()
    
    # to distinguish slices from 'real' frames
    if NFrames < 5:
        IJ.log('Warning less than 5 frames found..')

    for frame in range(1, NFrames + 1):
        roi = rois[frame - 1]
        movie.setPositionWithoutUpdate(Channel, Slice, frame)
        movie.setRoi(roi)
        points = roi.getContainedPoints()
        ip = movie.getProcessor()
        
        vals = []
        for point in points:
            val = ip.getf(point.x, point.y)
            vals.append(val)

        mph = mean_phase(vals)
        res.append(mph)
        
    movie.killRoi() # clear roi        
    return res


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

def extract_psm_coords(movie, direction = 'right', sigma = 5):

    ''' Segment the PSM in the tail and return the raw coordinates '''
    
    movie = slices_to_frames(movie)
    dims = movie.getDimensions()
    print dims

    NFrames = dims[-1]
    width = dims[0]
    height = dims[1]

    ov = Overlay() # to store the raw outline rois
    
    xps,yps = [],[] # psm outline coordinates
    ant_xs, ant_ys = [],[] # anterior roi centroid coordinates


    # ---- extract the raw coordinates ------
    for frame in range(1, NFrames +1):
        
        print 'frame:', frame
        movie.setPosition(1,1,frame)

        # blurring
        ip = movie.getProcessor().duplicate()
        ip.blurGaussian(10)
        imp = ImagePlus('Frame ' + str(frame), ip)
        
        xp, yp = get_psm_outline(imp, sigma, thresh_method = thresh_method,
                                 x_or_y = x_or_y, direction = direction)

        # psm outline coordinates
        xps.append(xp)
        yps.append(yp)        

        # confine the anterior search to
        # either right or left side of Tail!
        # with 10% tolerance
        
        x_post = xp[argmax(yp)] # raw x-posterior coordinate
        if direction == 'left':
            rect_roi = Roi(0,0, 1.1 * x_post, height)
            # IJ.log('shooting from the left')
        elif direction == 'right':
            rect_roi = Roi(x_post,0, 0.9 * (width - x_post), height)
            # IJ.log('shooting from the right' + str(x_post))
            
        ip.setValue(0)
        ip.fillOutside(rect_roi)
        cropped_frame = ImagePlus('roi_crop',ip)
        # cropped_frame.show()
        
        anterior_roi = get_anterior_roi(cropped_frame, sigma, perc = 0.99)
        ant_x, ant_y = anterior_roi.getContourCentroid()
        
        ant_xs.append(ant_x)
        ant_ys.append(ant_y)

        
        proi = PolygonRoi(xp,yp,Roi.POLYLINE)
        proi.setPosition(frame)
        proi.setStrokeWidth(1.) # psm outline
        proi.setStrokeColor(Color2)

        # raw percentile anterior rois
        anterior_roi.setPosition(frame) 
        anterior_roi.setColor(Color2)
        anterior_roi.setStrokeWidth(1.)
        
        ov.add(anterior_roi)
        ov.add(proi)
            
    return xps, yps, ant_xs, ant_ys, ov

    # ---- end coordinate extraction loop -------------
    

def apply_rois( the_rois ):

    ''' Measure along the moving rois '''    

    post_rois, ant_rois, mid_rois = the_rois

    # --- Dialog -----------------------------------
    wlist = WindowManager.getImageTitles()
    gd = NonBlockingGenericDialog('Apply rois to?')
    gd.setCancelLabel('Exit')
    gd.addChoice('Select Movie',wlist, wlist[0])
    gd.addCheckbox('Phase-Movie', False)
    gd.addCheckbox('Make Kymograph', False)    
    gd.addCheckbox('Show Plots', True)


    gd.showDialog() # dialog is open

    if gd.wasCanceled():
        return False # to kill the main loop
    
    sel_win = gd.getNextChoice()
    phase_mov = gd.getNextBoolean()
    do_kymo = gd.getNextBoolean()        
    do_plot = gd.getNextBoolean()


    # --- Dialog End ------------------------------
    
    win_name = IJ.selectWindow(sel_win)
    movie = IJ.getImage()

    movie = slices_to_frames(movie)

    # to avoid reference error
    ant_traj, post_traj, mid_traj = [],[],[]

    ov = Overlay()
    [ov.add(ant_roi) for ant_roi in ant_rois]
    [ov.add(mid_roi) for mid_roi in mid_rois]
    [ov.add(post_roi) for post_roi in post_rois]
    movie.setOverlay(ov)

    table = ResultsTable()

    # Kymograph
    if do_kymo:
        psm_roi_splines = get_psm_splines( the_rois )
        [ov.add(psm_roi) for psm_roi in psm_roi_splines]
        if phase_mov:
            IJ.log('Creating phase kymograph..')
            kymo = make_float_kymograph(movie, psm_roi_splines, phase = True)
        else:
            IJ.log('Creating kymograph..')            
            kymo = make_float_kymograph(movie, psm_roi_splines, phase = False)
        kymo.show()
    
    # measure the rois (period or power..)
    if not phase_mov:
        IJ.log('Measuring ' + movie.getShortTitle())
        ant_traj = measure_rois(movie, ant_rois)
        post_traj = measure_rois(movie, post_rois)
        mid_traj = measure_rois(movie, mid_rois)

        add_to_table(ant_traj, table, 'anterior')
        add_to_table(post_traj, table, 'posterior')
        add_to_table(mid_traj, table, 'half psm')
        table.show(movie.getShortTitle() + ' Results')
        if do_plot:
            # plot the trajectories        
            plot_series(ant_traj, 'Anterior', ylabel = 'signal')
            plot_series(post_traj, 'Posterior', ylabel = 'signal')
            plot_series(mid_traj, 'Half PSM', ylabel = 'signal')
        

    # extract average phase of rois
    if phase_mov:
        IJ.log('Measuring phases in ' + movie.getShortTitle())        
        ant_traj = measure_phase_rois(movie, ant_rois)        
        post_traj = measure_phase_rois(movie, post_rois)        
        mid_traj = measure_phase_rois(movie, mid_rois)

        add_to_table(ant_traj, table, 'anterior')
        add_to_table(post_traj, table, 'posterior')
        add_to_table(mid_traj, table, 'half psm')
        table.show(movie.getShortTitle() + ' Phase Results')

        if do_plot:
            # plot the trajectories        
            plot_series(ant_traj, 'Anterior phase', ylabel = 'signal')
            plot_series(post_traj, 'Posterior phase', ylabel = 'signal')
            plot_series(mid_traj, 'Half PSM phase', ylabel = 'signal')

    # to keep it running in the main loop
    return True

# -------- GUI stuff -------------------------------------------

def display_msg(title,message):
    gd = GenericDialog(title)
    gd.addMessage(message)
    gd.hideCancelButton()
    gd.showDialog()

def select_window(title):
    wlist = WindowManager.getImageTitles()
    gd = GenericDialog(title)
    gd.addChoice('Select Window',wlist, wlist[0])
    gd.showDialog() # dialog is open

    sel_win = gd.getNextChoice()
    print(sel_win)
    return sel_win

def start_menu():
    # --- Dialog -----------------------------------
    wlist = WindowManager.getImageTitles()
    gd = NonBlockingGenericDialog('TailTracer - Setup')
    gd.setCancelLabel('Exit')
    gd.addChoice('Select Movie to segment',wlist, wlist[0])
    gd.addChoice('Scan direction', ['right', 'left'], 'right')
    gd.addNumericField('Gaussian blur', 5, 1)
    gd.addNumericField('Anterior y-offset', 15, 0)
    gd.addNumericField('Posterior y-offset', -15, 0)
    gd.addNumericField('x-offset', 0, 0)    
    gd.addNumericField('Roi radius', 15, 0)
    gd.addNumericField('EMA factor', 10, 0)
    gd.addNumericField('Half PSM x-bias', 0.8, 1)
    gd.addCheckbox('Show Intensity Plots', False)
    gd.addCheckbox('Show raw outlines', False)
    gd.addCheckbox('Create Coordinate Table', False)
    gd.addCheckbox('Make Kymograph', False)

    gd.showDialog()

    if gd.wasCanceled():
        return False
    
    pdic = {} # parameters dictionary
    
    pdic['selected_window'] = gd.getNextChoice()
    pdic['direction'] = gd.getNextChoice()
    
    pdic['sigma'] = gd.getNextNumber()
    pdic['ant_offset'] = gd.getNextNumber()
    pdic['post_offset'] = gd.getNextNumber()
    pdic['offset_x'] = gd.getNextNumber()    
    pdic['roi_radius'] = gd.getNextNumber()
    pdic['ema_fac'] = gd.getNextNumber()
    pdic['ant_w'] = gd.getNextNumber() # x-bias of mid-psm roi

    pdic['do_plots'] = gd.getNextBoolean()
    pdic['show_raw'] = gd.getNextBoolean()
    pdic['do_coord_table'] = gd.getNextBoolean()
    pdic['do_kymo'] = gd.getNextBoolean()
    
    return pdic



# --------Main Loop---------------------------------------------

def run():

    # -- Dialog --
    params_dic = start_menu()
    print params_dic

    # exit if Dialog was cancelled
    if not params_dic:
        return

    ov = Overlay() # general overlay containing all Rois
    
    IJ.selectWindow(params_dic['selected_window'])
    movie = IJ.getImage() 
    IJ.log('Started TailTracer on ' + str(movie.getShortTitle()))

    # --- Generate the PSM Rois from the movie in focus ---------
    xps, yps, ant_xs, ant_ys, ov_raw = extract_psm_coords(movie,
                                                  direction = params_dic['direction'],
                                                  sigma = params_dic['sigma'])
    
    # get the roi lists from the raw coordinates
    the_rois = make_post_ant_mid_Rois(xps, yps, ant_xs, ant_ys,
                                      offset_x = params_dic['offset_x'],
                                      ant_offset_y = params_dic['ant_offset'],
                                      post_offset_y = params_dic['post_offset'],
                                      R = params_dic['roi_radius'],
                                      ema_fac = 1/params_dic['ema_fac'],
                                      ant_w = params_dic['ant_w'])
    
    post_rois, ant_rois, mid_rois = the_rois

    
    # get the poly splines for the tracked PSM half
    if params_dic['do_kymo']:
        psm_roi_splines = get_psm_splines(the_rois)
        [ov.add(psm_roi) for psm_roi in psm_roi_splines]    

        kymo = make_kymograph(movie, psm_roi_splines)
        kymo.show()
        
    # add Rois to Overlay
    [ov.add(post_roi) for post_roi in post_rois]
    [ov.add(ant_roi) for ant_roi in ant_rois]
    [ov.add(mid_roi) for mid_roi in mid_rois]

    # shove raw coord rois into general overlay
    if params_dic['show_raw']:
        [ov.add(ov_raw.get(i)) for i in range(ov_raw.size())] 

    movie.setOverlay(ov)


    # put roi coordinates in table
    if params_dic['do_coord_table']:
        coord_table = ResultsTable()
        row = 0
        for proi, aroi, mroi in zip(*the_rois):

            p_x, p_y = proi.getContourCentroid()
            coord_table.setValue('Post X', row, p_x)
            coord_table.setValue('Post Y', row, p_y)
            
            a_x, a_y = aroi.getContourCentroid()
            coord_table.setValue('Ant X', row, a_x)
            coord_table.setValue('Ant Y', row, a_y)
            row += 1
            
        coord_table.show('Roi Coordinates')
                
    # measure the intensity using the rois
    ant_traj = measure_rois(movie, ant_rois)
    post_traj = measure_rois(movie, post_rois)
    mid_traj = measure_rois(movie, mid_rois)

    int_table = ResultsTable()
    add_to_table(ant_traj, int_table, 'anterior')
    add_to_table(post_traj, int_table, 'posterior')
    add_to_table(mid_traj, int_table, 'half psm')

    int_table.show(movie.getShortTitle() + ' Intensity')
    
    # plot the trajectories
    if params_dic['do_plots']:
        plot_series(ant_traj, 'Anterior  Raw Signal', ylabel = 'signal')
        plot_series(post_traj, 'Posterior Raw Signal', ylabel = 'signal')
        plot_series(mid_traj, 'Half PSM Raw Signal', ylabel = 'signal')


    # ---- Start Roi application loop -------------------------------

    while True:
        ret = apply_rois( the_rois )
        if not ret:
            break # end program when no other roi application desired

    IJ.log('Exiting TailTracer')

    

run()
