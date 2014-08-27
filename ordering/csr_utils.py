import scipy.sparse as sp

def itr_col_indices_by_row(m):
    assert isinstance(m, sp.csr_matrix)
    for row in xrange(m.shape[0]):
        yield row, m.indices[m.indptr[row]:m.indptr[row+1]]
        
def itr_nonzero_indices(m):
    assert isinstance(m, sp.csr_matrix)    
    for row in xrange(m.shape[0]):
        for col in m.indices[m.indptr[row]:m.indptr[row+1]]:
            yield row, col
