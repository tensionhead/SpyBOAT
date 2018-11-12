import argparse
import sys

parser = argparse.ArgumentParser(description='Process some string arguments')
# I/O
parser.add_argument('--movie', help='movie (sub-)directory', required = 'True', type=str)
parser.add_argument('--phase_out', help='phase output file name', required = 'True', type=str)
parser.add_argument('--period_out', help='period output file name', required = 'True', type=str)
parser.add_argument('--power_out', help='power output file name', required = 'True', type=str)
parser.add_argument('--channel', help='which channel of the hyperstack to process', required=False, type=int, default=1)

# Gaussian smoothing
parser.add_argument('--gauss_sigma', help='Gaussian smoothing parameter, 0 means no smoothing', required=False, default = 0, type=float)

# Wavelet Parameters
parser.add_argument('--dt', help='sampling interval', required = 'True', type=float)
parser.add_argument('--Tmin', help='smallest period', required = 'True', type=float)
parser.add_argument('--Tmax', help='biggest period', required = 'True', type=float)
parser.add_argument('--nT', help='number of periods to scan for', required = 'True', type=int)

res = parser.parse_args(sys.argv[1:])

print(vars(res))
