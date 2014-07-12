
def parse(problem, elems):
    for l in elems:
        dispatch(l[0], l, problem)

def dispatch(kind, l, problem):
    if   kind=='C': # <N> C 1 'e3'
        problem.con_num_name[int(l[1])] = l[2][1:-1]
    elif kind=='c': # <N> c 3 1
        problem.con_ends_num[int(l[2])] = int(l[1])
    elif kind=='N': # <N> N 2 'x3'
        problem.var_num_name[int(l[1])] = l[2][1:-1]
    elif kind=='V': # <N> V 3
        problem.nvars = int(l[1])
    elif kind=='m': # <N> m 'ex9_2_8'
        problem.model_name = l[1]