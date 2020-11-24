""" SpyBOAT - Spatial pyBOAT """


__version__ = '0.1.0'

# io
from .util import open_tif, save_to_tifs
# pre-processing
from .util import down_sample, gaussian_blur
# post-processing
from .util import create_static_mask, create_dynamic_mask, apply_mask

# analysis
from .processing import transform_stack, run_parallel


