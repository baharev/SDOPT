from __future__ import print_function
import numpy as np
import scipy.sparse as sp
from . import minimum_degree as md
from ordering.csr_utils import cols_in_row
from ordering.misc_utils import invert_permutation

def rows_in_col(m, c):
    assert isinstance(m, sp.csc_matrix)
    return m.indices[m.indptr[c]:m.indptr[c+1]]

def get_permuted_sp_matrices(m, inv_row_p, inv_col_p):
    A = m.tocoo()
    A.row = inv_row_p[A.row]
    A.col = inv_col_p[A.col]
    return A.tocsr(), A.tocsc()

def coloring(m, inv_row_p, inv_col_p):
    # The permutation must give a matrix in Hessenberg form
    row_major, col_major = get_permuted_sp_matrices(m, inv_row_p, inv_col_p)
    ncols = col_major.shape[1]
    # Initially all column colors are set to the invalid "color" -1
    column_colors = np.full(ncols, -1, np.int32)
    # If color i is available: color_available[i] is 1, otherwise 0
    # Initially, "color" 0 is available 
    color_available = np.ones(1, np.int8)
    # Iterate through the columns backwards, from right to left
    for c in reversed(xrange(ncols)):
        # All rows containing c
        for r in rows_in_col(col_major, c):
            # All other columns in those rows, c's "neighbors"
            cols = cols_in_row(row_major, r)
            idx = np.flatnonzero(cols==c)
            # cols in r: [ left | c | right]
            # only the right index set has been processed so far
            right = cols[idx+1:]
            used_colors = column_colors[right]
            color_available[used_colors] = 0
        #print('Colors available:\n%s' % color_available)
        index = np.flatnonzero(color_available)[0]
        column_colors[c] = index
        # introduce new "color" if index == color_available.size-1 
        color_available = np.ones(max(index+2, color_available.size), np.int8)
    print('Colors:\n%s' % column_colors)
    # chromatic number >= max nonzeros in a row
    lb_chromatic_number = np.max(np.diff(row_major.indptr))
    color_count = color_available.size-1
    print('Color count: %d (>=%d)' % (color_count, lb_chromatic_number))
    return  column_colors, color_count

if __name__=='__main__':  
    m = sp.dok_matrix((3,3), dtype=np.int8)
    m[0,0] = m[0,1] = m[0,2] = 1
    m[1,0] = m[1,1]          = 2
    m[2,2] = 3
    print(m.todense(), '\n')
    # row_p and col_p store the current permutation
    row_p = np.arange(m.shape[0], dtype=np.int32)
    col_p = np.arange(m.shape[1], dtype=np.int32) 
    #
    md.DEBUG = True
    # TODO Index violation in slice causes a weird error, give better error msg
    m_csr = m.tocsr() 
    md.min_degree_ordering(m_csr, row_p, col_p, rbeg=0, rend=3, cbeg=0, cend=3)
    
    coloring(m_csr, invert_permutation(row_p), invert_permutation(col_p))
