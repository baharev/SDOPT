from __future__ import print_function
import numpy as np
import scipy.sparse as sp
import matplotlib.pyplot as plt
import csr_utils as util

def plot(bsp, plot_permuted):
    # Unpack bsp
    m = bsp.csr_mat
    assert isinstance(m, sp.csr_matrix)    
    row_names, col_names = bsp.row_names, bsp.col_names 
    inv_row_p, inv_col_p = get_inverse_permutation(bsp, plot_permuted)
    ridx, cidx = get_block_boundaries(bsp, plot_permuted)
    # Do the actual work 
    fig, ax = setup(*m.shape)
    draw_nzeros(ax, m, inv_row_p, inv_col_p)
    draw_partitions(ax, ridx, cidx)
    fs = get_font_size(fig, ax)
    write_names(ax, row_names, col_names, inv_row_p, inv_col_p, fs) 
    beautify_axes(ax)
    plt.show()

def get_inverse_permutation(bsp, plot_permuted):
    if plot_permuted and bsp.inverse_row_perm is not None:
        return bsp.inverse_row_perm, bsp.inverse_col_perm
    else:
        # TODO Emit a warning if inverse permutations were None?
        return np.arange(bsp.nrows), np.arange(bsp.ncols)

def get_block_boundaries(bsp, plot_permuted):
    # TODO Ugly to return None
    if plot_permuted and bsp.inverse_row_perm is not None:
        return bsp.ridx, bsp.cidx
    else:
        return None, None

def setup(nrows, ncols):
    fig=plt.figure()
    ax=fig.add_subplot(111)
    mng = plt.get_current_fig_manager()
    mng.resize(1865,1025)
    # TODO Post a wrapper to Code Review?
    #mng.full_screen_toggle()     
    plt.axis('scaled')
    ax.set_xlim([0, ncols])
    ax.set_ylim([0, nrows])
    return fig, ax

def draw_nzeros(ax, m, inv_row_p, inv_col_p):
    for i, j in util.itr_nonzero_indices(m):
        r, c = inv_row_p[i], inv_col_p[j]
        # r and c must be swapped: row -> y axis, col -> x axis
        rect = plt.Rectangle((c, r), 1, 1, facecolor='black', edgecolor='0.7')
        ax.add_artist(rect)

def draw_partitions(ax, ridx, cidx):
    # Nonsense to plot this if we do not have blocks OR not permuted
    if ridx is None:
        return
    line_color, line_width = 'blue', 5
    for r in ridx:
        ax.axhline(r, c=line_color, lw=line_width)        
    for c in cidx:
        ax.axvline(c, c=line_color, lw=line_width)

def get_font_size(fig, ax):
    # TODO Ask on Code Review
    SIZE = 12.0
    invisible = (1,1,1,0)
    t = plt.text(0, 1, 'X', fontsize=SIZE, color=invisible)
    bb = t.get_window_extent(renderer=fig.canvas.get_renderer())
    print('X size in points: {:.2f} x {:.2f}'.format(bb.width, bb.height))
    inv = ax.transData.inverted()
    bbox = inv.transform(bb.get_points())
    w, h = bbox[1,:]-bbox[0,:]
    print('X size in coordinates: {:.2f} x {:.2f}'.format(w, h))
    print('approximate font size to set: {:.2f}'.format(SIZE/h))
    return 0.8*SIZE/h

def write_names(ax, row_names, col_names, inv_row_p, inv_col_p, fs):
    for i, r_name in enumerate(row_names):
        r = inv_row_p[i]
        ax.text(-0.25, r+0.5,r_name,ha='right', va='center',size=fs)
    for j, c_name in enumerate(col_names):
        c = inv_col_p[j]
        ax.text(c+0.5, -0.25,c_name,ha='center',va='bottom',size=fs,rotation=90)

def beautify_axes(ax):
    ax.invert_yaxis()
    ax.set_xticks([])
    ax.set_yticks([])
