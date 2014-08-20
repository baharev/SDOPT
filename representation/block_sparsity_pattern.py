
class BlockSparsityPattern:
    def __init__(self, name, nrows, ncols, nzeros):
        self.name = name
        self.nrows = nrows
        self.ncols = ncols
        self.nzeros = nzeros
        self.jacobian = [ ] # jacobian[i]: col indices in row i
        self.col_len = None # redundant info, can be computed from jacobian too
        self.row_suffixes = { } # suffix name -> np.array of (index, value)
        self.col_suffixes = { } # suffix name -> np.array of (index, value)
