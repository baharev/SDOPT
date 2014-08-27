from __future__ import print_function
from future_builtins import zip
import numpy as np
import csr_utils as util

# TODO 1. Reconstruct and somehow visualize blocks
#      2. Check if the blocks happen to be in Hessenberg form 
#         (both row and col profiles are monotone) 
#      3. Do ordering within the blocks, along the diagonal 
#         (but postpone block orderings)
#         diagonal is both on row and col profiles

class BlockSparsityPattern:
    def __init__(self, name, nrows, ncols, nzeros):
        self.name = name
        self.nrows = nrows
        self.ncols = ncols
        self.nzeros = nzeros
        self.row_names = None
        self.col_names = None
        self.row_suffixes = { } # suffix name -> np.array of (index, value)
        self.col_suffixes = { } # suffix name -> np.array of (index, value)
        # Sparsity pattern of the Jacobian in the CSR format
        self.csr_data    = np.zeros(nzeros,  dtype=np.float64)
        self.csr_indices = np.zeros(nzeros,  dtype=np.int32)
        self.csr_indptr  = np.zeros(nrows+1, dtype=np.int32)
        self.csr_mat     = None   # View of (data, indices, indptr) as a csr_mat
        self.col_len = None # redundant info, can be computed from Jacobian too
        # These below are only needed to build the Jacobian, factor them out?
        self.csr_pos     = int(0) # Counter needed to build the csr_mat
        self.dbg_prev_row= int(-1)# Check whether the J segments are ordered 
        # the data below comes from block reconstruction
        self.row_permutation  = None # AMPL row indices in permuted order
        self.col_permutation  = None # AMPL col indices in permuted order
        # TODO Inverse permutations are only used by plot, compute only there?
        self.inverse_row_perm = None # inverse of row_permutation
        self.inverse_col_perm = None # inverse of col_permutation
        # indices in block the ith block = permutation[slice(*blocks[i])] 
        self.row_blocks = None
        self.col_blocks = None

################################################################################
# partition: np.array of (index, value) pairs, where value is the block id,
# i.e. partition['index'] gives the indices, partition['values'] the block ids

def set_permutation_with_block_boundaries(bsp):
    blockid = 'blockid'
    if (blockid not in bsp.row_suffixes) or (blockid not in bsp.col_suffixes):
        print('WARNING: No row and/or col partitions!')
        return
    row_partition = bsp.row_suffixes[blockid] 
    col_partition = bsp.col_suffixes[blockid]
    bsp.row_permutation, bsp.row_blocks = reconstruct(row_partition) 
    bsp.col_permutation, bsp.col_blocks = reconstruct(col_partition)
    set_inverse_permutations(bsp)
    # The rest of this function is just debugging
    assert len(bsp.row_blocks)==len(bsp.col_blocks)    
    print('ROWS')
    dbg_show(row_partition, bsp.row_permutation, bsp.row_blocks)
    print('COLS')
    dbg_show(col_partition, bsp.col_permutation, bsp.col_blocks)

def reconstruct(partition):
    # Sorts partition in place by block ids
    # returns: tuple of permutation vector, block boundaries as (beg, end) tuple
    sort_by_block_id(partition)
    blocks = get_blocks(partition)
    check_block_ids(partition, len(blocks))
    return partition['index'], blocks

def sort_by_block_id(partition):
    # in place, stable sort by block id (by 'value')
    np.ndarray.sort(partition, kind='mergesort', order='value')

def get_blocks(partition):
    # This function assumes that partition has already been sorted by block id 
    # (by 'value'). Find the block boundaries first:
    mask = np.ediff1d(partition['value'], to_begin=1, to_end=1)
    idx = np.flatnonzero(mask) # adjancent elements of idx give the block slices 
    return [t for t in zip(idx[:-1],idx[1:])]

def check_block_ids(partition, block_count):
    # Assumption: block_ids is already sorted, and has block_count distinct 
    # elements. Checking if distinct block_ids == 1:block_count:
    block_ids = partition['value']
    assert block_ids[ 0] == 1
    assert block_ids[-1] == block_count
    
def set_inverse_permutations(bsp):
    bsp.inverse_row_perm = util.invert_permutation(bsp.row_permutation)
    bsp.inverse_col_perm = util.invert_permutation(bsp.col_permutation)   

def dbg_show(partition, permutation, blocks):
    print('permutation:', permutation)
    print('blocks:')
    for i, boundaries in enumerate(blocks):
        print(i, partition['value'][slice(*boundaries)])
    print('indices by block:')
    for i, boundaries in enumerate(blocks):
        print(i, permutation[slice(*boundaries)])

