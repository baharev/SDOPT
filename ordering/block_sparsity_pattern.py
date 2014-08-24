from __future__ import print_function
from future_builtins import zip
import numpy as np

# TODO 1. Reconstruct and somehow visualize blocks
#      2. Check if the blocks happen to be in Hessenberg form 
#         (both row and col profiles are monotone) 
#      3. Do ordering within the blocks, along the diagonal 
#         (but postpone block orderings)

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
        # the data below comes from block reconstruction
        self.row_permutation = None # AMPL row indices in permuted order
        self.col_permutation = None # AMPL col indices in permuted order
        # indices in block the ith block = permutation[block_slices[i]] 
        self.row_block_slices = None
        self.col_block_slices = None

################################################################################
# partition: np.array of (index, value) pairs, where value is the block id,
# i.e. partition['index'] gives the indices, partition['values'] the block ids

def set_permutation_with_block_slices(bsp):
    blockid = 'blockid'
    if (blockid not in bsp.row_suffixes) or (blockid not in bsp.col_suffixes):
        print('WARNING: No row and/or col partitions!')
        return
    row_partition = bsp.row_suffixes[blockid] 
    col_partition = bsp.col_suffixes[blockid]
    bsp.row_permutation, bsp.row_block_slices = reconstruct(row_partition) 
    bsp.col_permutation, bsp.col_block_slices = reconstruct(col_partition)
    # The rest of this function is just debugging
    assert len(bsp.row_block_slices)==len(bsp.col_block_slices)    
    print('ROWS')
    dbg_show(row_partition, bsp.row_permutation, bsp.row_block_slices)
    print('COLS')
    dbg_show(col_partition, bsp.col_permutation, bsp.col_block_slices)

def reconstruct(partition):
    # Sorts partition in place by block ids
    # returns: tuple of permutation vector, block boundaries (as slices)
    sort_by_block_id(partition)
    block_slices = get_block_slices(partition)
    check_block_ids(partition, len(block_slices))
    return partition['index'], block_slices

def sort_by_block_id(partition):
    # in place, stable sort by block id (by 'value')
    np.ndarray.sort(partition, kind='mergesort', order='value')

def get_block_slices(partition):
    # This function assumes that partition has already been sorted by block id 
    # (by 'value'). Find the block boundaries first:
    mask = np.ediff1d(partition['value'], to_begin=1, to_end=1)
    idx = np.flatnonzero(mask) # adjancent elements of idx give the block slices 
    return [slice(*t) for t in zip(idx[:-1],idx[1:])]

def check_block_ids(partition, block_count):
    # Assumption: block_ids is already sorted, and has block_count distinct 
    # elements. Checking if distinct block_ids == 1:block_count:
    block_ids = partition['value']
    assert block_ids[ 0] == 1
    assert block_ids[-1] == block_count

def dbg_show(partition, permutation, block_slices):
    print('permutation:', permutation)
    print('blocks:')
    for i, slc in enumerate(block_slices):
        print(i, partition['value'][slc])
    print('indices by block:')
    for i, slc in enumerate(block_slices):
        print(i, permutation[slc])
        
def write_asy_input(bsp):
    pass