import argparse
import sys

parser = argparse.ArgumentParser(description='Process some string arguments')
# I/O
parser.add_argument('--mov_dir', help='movie (sub-)directory', required = 'True', type=str)
parser.add_argument('--mov_name', help='input movie file name', required = 'True', type=str)
parser.add_argument('--phase_out', help='phase output file name', required = 'True', type=str)
parser.add_argument('--period_out', help='period output file name', required = 'True', type=str)
parser.add_argument('--power_out', help='power output file name', required = 'True', type=str)
# Wavelet Parameters
parser.add_argument('--dt', help='sampling interval', required = 'True', type=int)
parser.add_argument('--Tmin', help='smallest period', required = 'True', type=float)
parser.add_argument('--Tmax', help='biggest period', required = 'True', type=float)
parser.add_argument('--nT', help='number of periods to scan for', required = 'True', type=int)

res = parser.parse_args(sys.argv[1:])

print(vars(res))
