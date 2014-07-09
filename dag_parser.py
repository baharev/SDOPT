import fileinput

class info_line:
    def __init__(self):
        pass
    def __call__(self):
        pass

class edge_line:
    def __init__(self):
        pass
    def __call__(self):
        pass

class node_line:
    def __init__(self):
        pass
    def __call__(self):
        pass

def lines(iterable):
    for line in iterable:
        first_space = line.find(' ')
        kind  = line[1:first_space-1]
        elems = [e.split() for e in line[first_space:].split(':')]
        print kind, elems
        yield line

def parse(f):
    funcs = { 'N': info_line() }
    for line in lines(f):
        line.strip()
        first_char = line[0]
        func = funcs.get(first_char)
        if func:
            func(f, line)
    print 'Finished reading the dag file'

def read_dag(filename):
    try:
        f = fileinput.input(filename, mode='r')
        return parse(f)
    finally:
        print 'Read', f.lineno(), 'lines'
        f.close()

if __name__ == '__main__':
    read_dag('/home/ali/pyton-ws/sparse-matrix-computations/dag/JacobsenTorn2D.dag')
    print
    read_dag('/home/ali/pyton-ws/sparse-matrix-computations/dag/ex9_2_8.dag')
