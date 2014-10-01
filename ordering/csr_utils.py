import scipy.sparse as sp
from six.moves import range as irange

def cols_in_row(m, row):
    assert isinstance(m, sp.csr_matrix)
    return m.indices[m.indptr[row]:m.indptr[row+1]]

def itr_col_indices(m):
    assert isinstance(m, sp.csr_matrix)
    for row in irange(m.shape[0]):
        yield m.indices[m.indptr[row]:m.indptr[row+1]]

def itr_col_indices_with_row_index(m):
    assert isinstance(m, sp.csr_matrix)
    for row in irange(m.shape[0]):
        yield row, m.indices[m.indptr[row]:m.indptr[row+1]]
        
def itr_nonzero_indices(m):
    assert isinstance(m, sp.csr_matrix)    
    for row in irange(m.shape[0]):
        for col in m.indices[m.indptr[row]:m.indptr[row+1]]:
            yield row, col

