import numpy as np

# TODO 1. Reconstruct and somehow visualize blocks
#      2. Do an ordering in the blocks, along the diagonal 
#         (postpone block orderings)

class BlockSparsityPattern:
    def __init__(self, name, nrows, ncols, nzeros):
        self.name = name
        self.nrows = nrows
        self.ncols = ncols
        self.nzeros = nzeros
        self.jacobian = [ ] # jacobian[i]: col indices in row i (np.int32 array)
        self.col_len = None # redundant info, can be computed from jacobian too
        self.row_suffixes = { } # suffix name -> np.array of (index, value)
        self.col_suffixes = { } # suffix name -> np.array of (index, value)

def reconstruct_partitions(bsp):
    bid = 'blockid'
    if (bid not in bsp.row_suffixes) or (bid not in bsp.col_suffixes):
        print('WARNING: No row and/or col partitions!')
        return
    row_partitions = bsp.row_suffixes[bid]
    #col_partitions = bsp.col_suffixes[bid]
    ind = np.argsort(row_partitions, kind='mergesort', order='value')
    print('Sorted by blockid:')
    for i in ind:
        print('%d: %d' % (row_partitions['value'][i], row_partitions['index'][i]))
    #for k, g in groupby(row_partitions[i] for i in ind):
    #    print(k, sorted(g))
    return

