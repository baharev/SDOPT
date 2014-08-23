from __future__ import print_function
import numpy as np
from itertools import izip

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

def stable_sort(partition):
    # partition: (index, value), where value is the block id
    # sort by block id
    indices = np.argsort(partition, kind='mergesort', order='value')
    for i in indices:
        print('%d: %d' % (partition['value'][i], partition['index'][i]))
    blk_ids = partition['value'][indices] # of length len(partition)==len(indices) 
    print(blk_ids)
    mask = np.ediff1d(blk_ids, to_begin=1, to_end=1) 
    print(mask)
    idx = np.flatnonzero(mask)
    print(idx)
    for i in xrange(idx.size-1):
        print('%d: %s ' % (i, blk_ids[idx[i]:idx[i+1]]) )
    p = partition['index'][indices]
    for i in xrange(idx.size-1):
        print('%d: %s ' % (i, p[idx[i]:idx[i+1]]) )
    print([j for j in izip(idx, idx[1:])])
    #return p, list of slices?

# FIXME Finish partition reconstruction from here
def reconstruct_partitions(bsp):
    blk_id = 'blockid'
    if (blk_id not in bsp.row_suffixes) or (blk_id not in bsp.col_suffixes):
        print('WARNING: No row and/or col partitions!')
        return
    row_part, col_part = bsp.row_suffixes[blk_id], bsp.col_suffixes[blk_id]
    # TODO Sanity checks: 1:nb, and all rows/columns have blk_id
    print('rows:')
    stable_sort(row_part)
    print('cols:')
    stable_sort(col_part)

    #for k, g in groupby(row_part[i] for i in ind):
    #    print(k, sorted(g))
    quit()
    return

