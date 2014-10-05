from collections import namedtuple

class Bounds(namedtuple('Bounds', 'l u')):
        __slots__ = ()
        def __str__(self):
            return '[%g,%g]' % (self.l, self.u)

# AutoNumber, derived from Enum gave all sorts of weird "Error when calling the 
# metaclass bases" errors, crashing the problem. Interestingly, the tests also 
# run 25% faster now...

class NodeAttr:
    bounds    =  1
    con_num   =  2
    d_term    =  3
    display   =  4
    input_ord =  5
    n_term    =  6
    name      =  7
    node_id   =  8
    number    =  9
    operation = 10
    type      = 11
    var_num   = 12
