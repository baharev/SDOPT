from __future__ import print_function
import numpy as np
import scipy.sparse as sp

def stable_partition(arr, pos):
    return np.concatenate((arr[pos], arr[~pos]))

def cols_in_row(m, r):
    c_beg, c_end = m.indptr[r], m.indptr[r+1]
    return m.indices[c_beg:c_end]

def cols_also_in_r(m, r, act_cols):
    # A boolean array of len(act_cols) indicating whether the col is also in r 
    return np.in1d(act_cols, cols_in_row(m, r), assume_unique=True)

def find_row_with_min_count(m, rs_in_asm, cs_in_asm):
    # returns row (value, not the index), cols also in cs_in_asm (i.e. active) 
    gen_row_act_cols = ((r, cols_also_in_r(m, r, cs_in_asm)) for r in rs_in_asm)
    # find the row with min col count
    # TODO The order is undefined if there are ties! (CPython keeps the first.)
    row, cmask = min(gen_row_act_cols, key=lambda t: np.count_nonzero(t[1]))
    return row, cmask

def min_degree_ordering(m, rbeg, rend, cbeg, cend):
    # row_p and col_p store the current permutation
    row_p = np.arange(m.shape[0], dtype=np.int32)
    col_p = np.arange(m.shape[1], dtype=np.int32)
    dbg_show_permuted_matrix(m, row_p, col_p)
    while rbeg < rend:
        # get the rows and cols in the active submatrix (asm)
        rows, cols = row_p[rbeg:rend], col_p[cbeg:cend] 
        r, cmask = find_row_with_min_count(m, rows, cols)
        rmask = rows==r
        row_p[rbeg:rend] = stable_partition(rows, rmask)        
        col_p[cbeg:cend] = stable_partition(cols, cmask)
        cnt  = np.count_nonzero(cmask)
        #
        print('min count at row %d (%dth in blk), count = %d' % (r, np.where(rmask)[0], cnt))
        print('rows after stable partition:',    row_p[rbeg:rend])        
        print('columns after stable partition:', col_p[cbeg:cend])
        print('r perm:', row_p)
        print('c perm:', col_p)   
        #     
        rbeg += 1
        cbeg += cnt 
        dbg_show_permuted_matrix(m, row_p, col_p)

def dbg_show_permuted_matrix(m_sparse, row_p, col_p):
    m = m_sparse.todense()
    for j in range(m.shape[1]):
        m[:,j] = m[row_p,j]
    for i in range(m.shape[0]):
        m[i,:] = m[i,col_p]
    print(m)

if __name__=='__main__':
    
    m = sp.dok_matrix((5,5), dtype=np.int8)
    m[1,1] = m[1,2] = m[1,3] = 1
    m[2,1] = m[2,2]          = 2
    m[3,3] = 3
    print(m.todense(), '\n')
    
    if sp.isspmatrix_csr(m):
        m_csr = m.copy()
    else:
        m_csr = m.tocsr() 
    
    min_degree_ordering(m_csr, 1, 4, 1, 4)
