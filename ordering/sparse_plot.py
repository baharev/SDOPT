from __future__ import print_function
import scipy.sparse as sp
import matplotlib.pyplot as plt
import csr_utils as util

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

def plot_matrix(m, row_names, col_names):
    assert isinstance(m, sp.csr_matrix)
    fig=plt.figure()
    ax=fig.add_subplot(111)
    mng = plt.get_current_fig_manager()
    mng.resize(1865,1025)
    # TODO Post a wrapper to Code Review?
    #mng.full_screen_toggle()     
    plt.axis('scaled')
    n_row = m.shape[0]
    n_col = m.shape[1]    
    ax.set_xlim([0, n_col])
    ax.set_ylim([0, n_row])
    for i, j in util.itr_nonzero_indices(m):
        # i and j must be swapped: row -> x axis, col -> y axis 
        rect = plt.Rectangle((j, i), 1,1, facecolor='black',edgecolor='0.7')
        ax.add_artist(rect)
    fs = get_font_size(fig, ax)
    for r in xrange(n_row):
        ax.text(-0.25, r+0.5, row_names[r], ha='right',  va='center', size=fs)
    for c in xrange(n_col):
        ax.text(c+0.5, -0.25, col_names[c], ha='center', va='bottom', size=fs, 
                rotation=90)        
    ax.invert_yaxis()
    ax.set_xticks([])
    ax.set_yticks([])
    plt.show()

def plot(bsp):
    plot_matrix(bsp.csr_mat, bsp.row_names, bsp.col_names)
