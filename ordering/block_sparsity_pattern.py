from __future__ import print_function
from future_builtins import zip
import numpy as np
import scipy.sparse as sp
import csr_utils
import misc_utils as util
from util.assert_helpers import assertEqual, assertEqLength
from ordering.minimum_degree import min_degree_ordering

# TODO 1. Do ordering within the blocks, along the upper envelope 
#         (but postpone block orderings)
#         upper envelope: apparently, the blocks are in lower triangular form
#      2. Code gen for AD

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
        # The data below comes from block reconstruction
        self.row_permutation  = None # AMPL row indices in permuted order
        self.col_permutation  = None # AMPL col indices in permuted order
        # TODO Inverse permutations are only used by plot, compute only there?
        self.inverse_row_perm = None # inverse of row_permutation
        self.inverse_col_perm = None # inverse of col_permutation
        # Block boundaries
        self.rblx = None # adjancent elements of blx give the block slices 
        self.cblx = None # block beg end indices: zip(blx[:-1],blx[1:])
        # indices in the ith block = permutation[slice(beg, end)] 
        # block count: len(blx)-1
        
def itr_index_block_slice(blx): 
    for i, beg_end in enumerate(zip(blx[:-1],blx[1:])):
        yield i, slice(*beg_end)

def get_block_boundaries(bsp, i, j):
    return bsp.rblx[i], bsp.rblx[i+1], bsp.cblx[j], bsp.cblx[j+1]
    
################################################################################
# partition: np.array of (index, value) pairs, where value is the block id,
# i.e. partition['index'] gives the indices, partition['values'] the block ids

def set_permutation_with_block_boundaries(bsp):
    blockid = 'blockid'
    if (blockid not in bsp.row_suffixes) or (blockid not in bsp.col_suffixes):
        print('WARNING: No row and/or col partitions!')
        make_one_big_fake_block(bsp)
        return
    row_partition = bsp.row_suffixes[blockid] 
    col_partition = bsp.col_suffixes[blockid]
    bsp.row_permutation, bsp.rblx = reconstruct(row_partition) 
    bsp.col_permutation, bsp.cblx = reconstruct(col_partition)
    set_inverse_permutations(bsp)
    # The rest of this function is just debugging
    assertEqLength(bsp.rblx, bsp.cblx) # it is not necessary in the general case
    print('ROWS')
    dbg_show(row_partition, bsp.row_permutation, bsp.rblx)
    print('COLS')
    dbg_show(col_partition, bsp.col_permutation, bsp.cblx)
    # FIXME Hack to get block profiles
    get_permuted_block_profiles(bsp)
    set_min_degree_order(bsp)

def reconstruct(partition):
    # Sorts partition in place by block ids
    # returns: tuple of permutation vector, block boundaries as (beg, end) tuple
    sort_by_block_id(partition)
    blx = get_blocks(partition)
    check_block_ids(partition, len(blx)-1)
    return partition['index'], blx

def sort_by_block_id(partition):
    # in place, stable sort by block id (by 'value')
    np.ndarray.sort(partition, kind='mergesort', order='value')

def get_blocks(partition):
    # This function assumes that partition has already been sorted by block id 
    # (by 'value'). Find the block boundaries first:
    mask = np.ediff1d(partition['value'], to_begin=1, to_end=1)
    blx = np.flatnonzero(mask) # adjancent elements of blx give the block slices 
    return blx

def check_block_ids(partition, block_count):
    # Assumption: block_ids is already sorted, and has block_count distinct 
    # elements. Checking if distinct block_ids == 1:block_count:
    block_ids = partition['value']
    assertEqual(block_ids[ 0], 1)
    assertEqual(block_ids[-1], block_count)
    
def set_inverse_permutations(bsp):
    bsp.inverse_row_perm = util.invert_permutation(bsp.row_permutation)
    bsp.inverse_col_perm = util.invert_permutation(bsp.col_permutation)   

def dbg_show(partition, permutation, blocks):
    print('permutation:', permutation)
    print('blocks:')
    for i, block_slice in itr_index_block_slice(blocks):
        print(i, partition['value'][block_slice])
    print('indices by block:')
    for i, block_slice in itr_index_block_slice(blocks):
        print(i, permutation[block_slice])

################################################################################
# FIXME This is a temporary hack to test block sparsity pattern
    
def get_permuted_block_profiles(bsp):
    blk_mat = sp.dok_matrix((len(bsp.rblx)-1,len(bsp.cblx)-1), dtype=np.int32)
    # Same logic as in nonzero plotting
    for i, j in csr_utils.itr_nonzero_indices(bsp.csr_mat):
        r, c = bsp.inverse_row_perm[i], bsp.inverse_col_perm[j]
        rblk = np.searchsorted(bsp.rblx, r, side='right') - 1 # inefficient, doesn't move within a row
        cblk = np.searchsorted(bsp.cblx, c, side='right') - 1
        key = (rblk,cblk)
        #print('i=%d j=%d r=%d c=%d rb=%d cb=%d' % (i,j,r,c,rblk,cblk))
        blk_mat[key] = blk_mat.get(key) + 1
    print('Block pattern:\n%s' % blk_mat.todense())
    rprof = get_row_profile(blk_mat)
    cprof = get_col_profile(blk_mat)
    return rprof, cprof

def get_row_profile(blk_mat):
    col_major = blk_mat.tocsc()
    col_major.sort_indices()
    rprof = util.indices_of_first_nonzeros(col_major)
    assert_in_lower_triangular_form(rprof, 'row')
    return rprof

def get_col_profile(blk_mat):
    row_major = blk_mat.tocsr()
    row_major.sort_indices()
    cprof = util.indices_of_last_nonzeros(row_major)
    assert_in_lower_triangular_form(cprof, 'col')
    return cprof

def assert_in_lower_triangular_form(prof, row_or_col):
    diff = np.ediff1d(prof)
    assert np.all(diff == 1) and (prof[0]==0), \
    '%s block profile not in lower triangular form:\n%s' % (row_or_col, prof)
    
################################################################################

def set_min_degree_order(bsp):
    # TODO Check if LTF
    m = bsp.csr_mat
    for i in xrange(len(bsp.rblx)-1):
        # Apply minimum degree ordering to each block on the diagonal (i,i)
        min_degree_ordering(m, bsp.row_permutation, bsp.col_permutation, 
                            *get_block_boundaries(bsp, i, i))
    set_inverse_permutations(bsp)

def make_one_big_fake_block(bsp):
    # The whole matrix is just one big block
    bsp.rblx = np.fromiter((0, bsp.nrows), dtype=np.int32)
    bsp.cblx = np.fromiter((0, bsp.ncols), dtype=np.int32)
    # The permutation is the identity    
    bsp.row_permutation = np.arange(bsp.nrows, dtype=np.int32)
    bsp.col_permutation = np.arange(bsp.ncols, dtype=np.int32)
    # Now we can call minimum degree
    set_min_degree_order(bsp)
