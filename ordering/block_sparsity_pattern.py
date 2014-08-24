from __future__ import print_function
from future_builtins import zip     # Python 2 only
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

def sort_by_block_id(partition):
    # partition: array of (index, value) pairs, where value is the block id
    # in place, stable sort by block id
    np.ndarray.sort(partition, kind='mergesort', order='value')

def get_block_slices(partition):
    # This function assumes that partition has already been sorted by block id 
    # (by 'value'). Find the block boundaries first:
    mask = np.ediff1d(partition['value'], to_begin=1, to_end=1)
    idx = np.flatnonzero(mask) # adjancent elements of idx give the block slices 
    return [slice(*t) for t in zip(idx[:-1],idx[1:])]

def check_block_ids(partition, block_count):
    # Assumption: block_ids == 1:block_count.
    # block_ids is already sorted, and has block_count distinct elements.
    block_ids = partition['value']
    assert block_ids[ 0] == 1
    assert block_ids[-1] == block_count

def reconstruct(partition):
    # returns: tuple of permutation vector, block boundaries (as slices)
    sort_by_block_id(partition)
    block_slices = get_block_slices(partition)
    check_block_ids(partition, len(block_slices))
    return partition['index'], block_slices

def dbg_show(partition, permutation, block_slices):
    print('permutation:', permutation)
    print('blocks:')
    for i, slc in enumerate(block_slices):
        print(i, partition['value'][slc])
    print('indices by block:')
    for i, slc in enumerate(block_slices):
        print(i, permutation[slc])        

def reconstruct_partitions(bsp):
    blockid = 'blockid'
    if (blockid not in bsp.row_suffixes) or (blockid not in bsp.col_suffixes):
        print('WARNING: No row and/or col partitions!')
        return
    row_partition = bsp.row_suffixes[blockid] 
    col_partition = bsp.col_suffixes[blockid]
    # Reconstruct sorts in place its argument
    row_perm, row_blk_slices = reconstruct(row_partition) 
    col_perm, col_blk_slices = reconstruct(col_partition)
    assert len(row_blk_slices)==len(col_blk_slices)    
    print('ROWS')
    dbg_show(row_partition, row_perm, row_blk_slices)
    print('COLS')
    dbg_show(col_partition, col_perm, col_blk_slices)
    return row_perm, row_blk_slices, col_perm, col_blk_slices

