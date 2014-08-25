from __future__ import print_function
import numpy as np
import scipy.sparse as sp
import matplotlib.pyplot as plt

def get_font_size(fig, ax):
    SIZE = 72.0
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

# FIXME Duplication
def cols_in_row(m, r):
    c_beg, c_end = m.indptr[r], m.indptr[r+1]
    return m.indices[c_beg:c_end]

def plot_matrix(m, row_names, col_names):
    isinstance(m, sp.csr_matrix)
    fig=plt.figure()
    ax=fig.add_subplot(111)
    mng = plt.get_current_fig_manager()
    mng.resize(1865,1025)
    #mng.full_screen_toggle()     
    plt.axis('scaled')
    n_row = m.shape[0]
    n_col = m.shape[1]    
    ax.set_xlim([0, n_col])
    ax.set_ylim([0, n_row])
    # TODO Write a custom, csr iterator?
    for r in xrange(n_row):
        for i in cols_in_row(m, r):
            rect = plt.Rectangle((i, r), 1, 1, facecolor='black', edgecolor='0.7', linewidth=1.0)
            ax.add_artist(rect)
    fs = get_font_size(fig, ax)
    for r in xrange(n_row):
        ax.text(-0.25, r+0.5, row_names[r], ha='right', va='center', size=fs)
    for c in xrange(n_col):
        ax.text(c+0.5, -0.25, col_names[c], ha='center', va='bottom', rotation=90, size=fs)        
    ax.invert_yaxis()
    ax.set_xticks([])
    ax.set_yticks([])
    plt.show()
    
def plot(bsp):
    # TODO Find a more efficient way, perhaps store the Jacobian in csr format 
    # in the first place
    m = sp.dok_matrix((bsp.nrows, bsp.ncols), dtype=np.int8)
    for r, cols in enumerate(bsp.jacobian):
        for c in cols:
            m[r,c] = 1
    row_names = ['']*bsp.nrows
    col_names = ['']*bsp.ncols
    plot_matrix(m.tocsr(), row_names, col_names)
