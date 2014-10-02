import numpy as np

def indices_of_first_nonzeros(m):
    return m.indices[m.indptr[:-1]]

def indices_of_last_nonzeros(m):
    return m.indices[m.indptr[1:]-1]               

def invert_permutation(p):
    '''Returns an array s, where s[i] gives the index of i in p.
    The argument p is assumed to be some permutation of 0, 1, ..., len(p)-1. 
    '''
    n = len(p)
    s = np.zeros(n, dtype = np.int32)  # zeros is faster than empty due to the
    i = np.arange(n, dtype = np.int32) # lazy memory allocation of Linux
    np.put(s, p, i) # s[p[i]] = i 
    return s