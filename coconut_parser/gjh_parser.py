'''
Use only read_flattened_ampl, ignore all other functions.
'''
from __future__ import print_function
import numpy as np
import scipy.sparse as sp
from util.file_reader import lines_of
from util.misc import nth

# FIXME: We need the point where we calculated this Jacobian!
#        Save also the residual values?

def read_gjh(filename):
    with lines_of(filename) as lines:
        return parse(lines)

def parse(lines):
    nrows, ncols = get_J_shape(lines)
    jac = sp.dok_matrix((nrows,ncols), dtype=np.float64)
    # Move to first row
    nth(lines, 1) # FIXME Write consume; Why only 1 move is necessary???
    for line in lines:
        if line[0]=='[':
            # has hit a new row: [12,*]
            comma = line.find(',')
            row = int(line[1:comma])-1
        elif line[0] == '\t':
            # data in row: <tab> col index <tab> entry
            col_idx, data = line.split()
            col, data = int(col_idx)-1, float(data)
            jac[row,col] = data
        else:
            break
    print('Jacobian:\n%s' % jac.tocsr())

def get_J_shape(lines):
    # param J{1..16, 1..16} default 0;
    line = nth(lines, 3)
    after_1st_dotdot = line.find('..') + 2
    comma = line.find(',')
    nrows = int(line[after_1st_dotdot:comma])
    after_2nd_dotdot = line.find('..', comma) + 2
    closing_bracket = line.find('}')
    ncols = int(line[after_2nd_dotdot:closing_bracket])
    print('Shape: %dx%d' % (nrows, ncols))
    return nrows, ncols

if __name__=='__main__':
    read_gjh('/home/ali/ampl/gjh')
