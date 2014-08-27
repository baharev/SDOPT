import numpy as np
import scipy.sparse as sp

def cols_in_row(m, row):
    assert isinstance(m, sp.csr_matrix)
    return m.indices[m.indptr[row]:m.indptr[row+1]]

def itr_col_indices(m):
    assert isinstance(m, sp.csr_matrix)
    for row in xrange(m.shape[0]):
        yield m.indices[m.indptr[row]:m.indptr[row+1]]

def itr_col_indices_by_row(m):
    assert isinstance(m, sp.csr_matrix)
    for row in xrange(m.shape[0]):
        yield row, m.indices[m.indptr[row]:m.indptr[row+1]]
        
def itr_nonzero_indices(m):
    assert isinstance(m, sp.csr_matrix)    
    for row in xrange(m.shape[0]):
        for col in m.indices[m.indptr[row]:m.indptr[row+1]]:
            yield row, col
          
def invert_permutation(p):
    '''Returns an array s, where s[i] gives the index of i in p.
    The argument p is assumed to be some permutation of 0, 1, ..., len(p)-1. 
    '''
    n = len(p)
    s = np.zeros(n, dtype = np.int32)  # zeros is faster than empty due to the
    i = np.arange(n, dtype = np.int32) # lazy memory allocation of Linux
    np.put(s, p, i) # s[p[i]] = i 
    return s
