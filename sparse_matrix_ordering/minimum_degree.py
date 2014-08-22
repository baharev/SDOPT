from __future__ import print_function
import numpy as np
import scipy.sparse as sp
from bidict import bidict
from bidict import namedbidict

def stable_partition(arr, pos, cnt):
    tmp = np.empty(arr.size, dtype=np.int32)
    tmp[0:cnt] = arr[pos]
    tmp[cnt: ] = arr[np.invert(pos)]
    return tmp

def cols_in_row(m, r):
    c_beg, c_end = m.indptr[r], m.indptr[r+1]
    return m.indices[c_beg:c_end]

def act_cols_count_and_pos(m, r, cols_in_blk):
    # return the count, and a boolean array whether the col in r is active
    cols_in_r = cols_in_row(m, r)
    act_cols_pos = np.in1d(cols_in_blk, cols_in_r, assume_unique=True)
    count = np.count_nonzero(act_cols_pos)
    return count, act_cols_pos
    
def find_row_with_min_count(m, rows_in_blk, cols_in_blk):
    MAXINT = np.int32(2**31-1)
    min_count, i_row, cols_pos = MAXINT, np.int32(0), np.array([], np.int32) 
    for i, r in enumerate(rows_in_blk):
        count, pos = act_cols_count_and_pos(m, r, cols_in_blk)
        if (count < min_count):
            min_count, i_row, cols_pos = count, i, pos
    return min_count, i_row, cols_pos        

def min_degree_ordering(m, row_slice, col_slice):
    # row and col slices define the active submatrix
    
    # row_p and col_p store the current permutation
    row_p = np.arange(m.shape[0], dtype=np.int32)
    col_p = np.arange(m.shape[1], dtype=np.int32)
    
    # get the rows and cols in the active submatrix
    rows = row_p[row_slice]
    cols = col_p[col_slice]
    #
    cnt, i, pos = find_row_with_min_count(m, rows, cols)
    print('min count at row %d (%dth in blk), count = %d'%(rows[i],i,cnt))
    # TODO Don't forget all empty rows!
    cols = stable_partition(cols, pos, cnt)
    #
    print('Columns after stable partition:', cols) 

if __name__=='__main__':
    
    bimap = namedbidict('bimap', 'active_to_orig', 'orig_to_active')
    bm = bimap({})
    bm.active_to_orig[2] = 0
    print(bm.orig_to_active[0])
    bd = bidict()
    bd[2] = 0
    print(bd[:0])
    
    m = sp.dok_matrix((3,3), dtype=np.int8)
    m[0,0] = m[0,1] = m[0,2] = 1
    m[1,0] = m[1,1]          = 1
    m[2,2] = 1
    print(m.todense(), '\n')
    
    if sp.isspmatrix_csr(m):
        mcsr = m.copy()
    else:
        mcsr = m.tocsr() 
    
    min_degree_ordering(mcsr, slice(0,3), slice(0,3))
