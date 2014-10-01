from __future__ import print_function

__all__ = [ 'plot' ]

from math import floor
import numpy as np
import scipy.sparse as sp
import matplotlib.pyplot as plt
import matplotlib.cm as cmx
import matplotlib.colors as colors
from . import csr_utils as util

def plot(bsp, plot_permuted, show_coloring=False):
    # Unpack bsp
    m = bsp.csr_mat
    assert isinstance(m, sp.csr_matrix)
    assert plot_permuted or not show_coloring # color only permuted patterns
    row_names, col_names = bsp.row_names, bsp.col_names 
    inv_row_p, inv_col_p = get_inverse_permutation(bsp, plot_permuted)
    rblx, cblx = bsp.rblx, bsp.cblx
    coloring = bsp.coloring
    color_count = bsp.color_count
    # Do the actual work 
    fig, ax = setup(*m.shape)
    column_cmap = get_column_cmap(coloring, color_count, show_coloring)
    draw_nzeros(ax, m, inv_row_p, inv_col_p, column_cmap)
    if plot_permuted:
        draw_partitions(ax, rblx, cblx)
    fs = get_font_size(fig, ax)
    write_names(ax, row_names, col_names, inv_row_p, inv_col_p, fs) 
    beautify_axes(ax)
    plt.show()

def get_inverse_permutation(bsp, plot_permuted):
    if plot_permuted:
        return bsp.inverse_row_perm, bsp.inverse_col_perm
    else:
        return np.arange(bsp.nrows), np.arange(bsp.ncols)

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

def get_column_cmap(coloring, color_count, show_coloring):
    if not show_coloring:
        return lambda i: 'black'
    # The magic number 1.09 is a hack as I cannot distinguish the 2 ends of hsv
    color_norm  = colors.Normalize(vmin=0, vmax=int(floor(color_count*1.09)))
    scalar_map = cmx.ScalarMappable(norm=color_norm, cmap='hsv') 
    def cmap(i):
        return scalar_map.to_rgba(coloring[i])
    return cmap

def draw_nzeros(ax, m, inv_row_p, inv_col_p, column_cmap):
    for i, j in util.itr_nonzero_indices(m):
        r, c = inv_row_p[i], inv_col_p[j]
        # r and c must be swapped: row -> y axis, col -> x axis
        color_of_c = column_cmap(c)
        rect = plt.Rectangle((c,r), 1,1, facecolor=color_of_c, edgecolor='0.7')
        ax.add_artist(rect)

def draw_partitions(ax, rblx, cblx):
    line_color, line_width = 'blue', 5
    for r in rblx:
        ax.axhline(r, c=line_color, lw=line_width)        
    for c in cblx:
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
