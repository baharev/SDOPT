from __future__ import print_function
import numpy as np
import scipy.sparse as sp
import csr_utils as util

DEBUG = False

# m: matrix in csr format
# r, c: row, column
# asm: active submatrix
# active (act_*): in the current submatrix
# row_p, col_p: row and col permutation

def min_degree_ordering(m, row_p, col_p, rbeg, rend, cbeg, cend):
    dbg_show_permuted_matrix(m, row_p, col_p)
    for rbeg in xrange(rbeg, rend):
        # get the rows and cols in the active submatrix (asm)
        rows, cols = row_p[rbeg:rend], col_p[cbeg:cend]
        r, cmask = find_row_with_min_count(m, rows, cols)
        rmask = rows==r
        row_p[rbeg:rend] = stable_partition(rows, rmask)
        col_p[cbeg:cend] = stable_partition(cols, cmask)
        dbg_step(slice(rbeg,rend),slice(cbeg,cend),row_p,col_p,m,r,rmask,cmask)
        cbeg += np.count_nonzero(cmask)

def find_row_with_min_count(m, rows, cols):
    # returns row (value, not the index), cmask (col both in row and in asm) 
    gen_row_act_cols = ((r, cols_also_in_r(m, r, cols)) for r in rows)
    # find the row with min col count
    # TODO The order is undefined if there are ties! (CPython keeps the first.)
    row, cmask = min(gen_row_act_cols, key=lambda t: np.count_nonzero(t[1]))
    return row, cmask

def cols_also_in_r(m, r, cols):
    # returns cmask of len(cols), indicating whether the col is also in r 
    return np.in1d(cols, util.cols_in_row(m, r), assume_unique=True)

def stable_partition(arr, mask):
    return np.concatenate((arr[mask], arr[~mask]))

def dbg_step(r_slice, c_slice, row_p, col_p, m, r, rmask, cmask):
    if DEBUG:    
        r_index =  np.flatnonzero(rmask)
        count = np.count_nonzero(cmask)
        print('min count at row %d (%dth in asm), count = %d'%(r,r_index,count))
        print('rows after stable partition:',    row_p[r_slice])        
        print('columns after stable partition:', col_p[c_slice])
        print('r perm:', row_p)
        print('c perm:', col_p)
        dbg_show_permuted_matrix(m, row_p, col_p)               

def dbg_show_permuted_matrix(m_sparse, row_p, col_p):
    if DEBUG:
        m = m_sparse.todense()
        for j in range(m.shape[1]):
            m[:,j] = m[row_p,j]
        for i in range(m.shape[0]):
            m[i,:] = m[i,col_p]
        print(m)

if __name__=='__main__':  
    DEBUG = True
    m = sp.dok_matrix((5,5), dtype=np.int8)
    m[1,1] = m[1,2] = m[1,3] = 1
    m[2,1] = m[2,2]          = 2
    m[3,3] = 3
    print(m.todense(), '\n')    
    # row_p and col_p store the current permutation
    row_p = np.arange(m.shape[0], dtype=np.int32)
    col_p = np.arange(m.shape[1], dtype=np.int32) 
    #
    min_degree_ordering(m.tocsr(), row_p, col_p, rbeg=1, rend=4, cbeg=1, cend=4)
