import numpy as np
from numpy import pi, cos, sin,exp
from numpy.ma import masked_array

def vec_len(dy, dx):

    return np.sqrt( dx**2 + dy**2 )

def phase_gradient(phase_field):

    ''' 
    "repairs" the central differences of np.gradient
    to accomodate for phase differences
    '''

    dy, dx = np.gradient(phase_field)
    
    # central difference denominator
    qq = 2 * np.ones( phase_field.shape )
    qq[0,:] = 1; qq[-1,:] = 1; qq[:,0] = 1; qq[:,-1] = 1

    dx = qq * dx # element wise, recover central differences
    pdx = np.arctan2( sin(dx), cos(dx) ) # 'central phase difference'

    dy = qq * dy # element wise, recover central differences    
    pdy = np.arctan2( sin(dy), cos(dy) )

    # normalize again for central difference distance
    return pdy/qq, pdx/qq

def mk_C_flux(field_shape, k = 1):

    ''' 
    Defines the closed curve in matrix form
    Symmetric output!

    k: width of the closed grid curve

    '''

    m = np.ones( field_shape ) # to extract 1-diagonals
    
    C_flux = -np.diag( np.diag(m, k = k), k = k )
    C_flux = C_flux + np.diag( np.diag(m, k = -k), k = -k )
    
    return C_flux

def mk_nested_C_flux(field_shape, k = 1):

    ''' 
    Superpositions flux evaluation curves up to order k.    
    Symmetric output!
    '''

    C_flux = np.zeros( field_shape )
    for ki in range(1, k+1):
        
        flux_k = mk_C_flux(field_shape, k = ki)
        C_flux = C_flux + flux_k

    # average over nested curves
    C_flux = C_flux/k
    
    return C_flux



def calculate_flux(vx, vy, k = 1, nested = True):

    '''
    Given a rectangular vector field, create the flux
    curves and evaluate the 'integrals'

    k: max. order of the nested curves
    '''

    # choose flux matrix generating function
    if nested:
        mk_flux_mat = mk_nested_C_flux
    else:
        mk_flux_mat = mk_C_flux
    
    Ny, Nx = vx.shape

    # C_x = Nx X Ny
    C_x = mk_flux_mat( (Nx, Nx), k = k)

    # x-direction
    fx = vx.dot(C_x)
    
    # y-direction
    C_y = mk_flux_mat( (Ny, Ny), k = k)    

    fy = C_y.T.dot(vy)

    flux = fx + fy

    return flux

def get_masked_gradient(frame, mask_value = 0):

    '''
    Utility function, mask frame where it corresponds to
    *mask_value*
    '''

    # the mask
    mask = frame != mask_value

    # make a masked array
    frame = masked_array(frame, mask = ~mask)

    yy, xx = np.meshgrid( np.arange(frame.shape[1]), np.arange(frame.shape[0]) )

    pdy, pdx = pgradient(frame)

    # strange numbers at masked places..fill with zeros (unmask gradient)
    pdy[pdy.mask] = 0
    pdx[pdx.mask] = 0

    return pdx, pdy, mask

def calculate_quad_flux(vx, vy, C_flux):

    '''
    Given a flux-curve matrix, evaluate the 'integrals'
    Only for quadratic fields.. legacy
    '''

    # quadratic version
    # assert vx.shape == C_flux.shape

    Ny, Nx = vx.shape

    
    
    # x-direction
    fx = vx.dot(C_flux)

    # y-direction
    fy = C_flux.T.dot(vy)

    flux = fx + fy

    return flux
