from __future__ import print_function
import numpy as np
import scipy.sparse as sp
from bidict import bidict
from bidict import namedbidict

def min_degree_ordering(m, row_slice, col_slice):
    # row and col slices define the active submatrix
    
    # row_p and col_p store the current permutation
    row_p = np.arange(m.shape[0], dtype=np.int32)
    col_p = np.arange(m.shape[1], dtype=np.int32)
    
    # get the rows and cols in the active submatrix
    rows = row_p[row_slice]
    cols = col_p[col_slice]
    for r in rows:
        c_beg, c_end = m.indptr[r], m.indptr[r+1]
        cols_in_r = m.indices[c_beg:c_end]
        active_cols = np.intersect1d(cols, cols_in_r, assume_unique=True) 
        print('cols in row %d:'%r, cols_in_r, ' active:', active_cols, active_cols.size)
    return

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
    
    

