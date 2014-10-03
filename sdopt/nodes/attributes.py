from collections import namedtuple
from ..util.autoenum import AutoNumber

class Bounds(namedtuple('Bounds', 'l u')):
        __slots__ = ()
        def __str__(self):
            return '[%g,%g]' % (self.l, self.u)

class NodeAttr(AutoNumber):
    bounds    = ()
    con_num   = ()
    d_term    = ()
    display   = ()
    input_ord = ()
    n_term    = ()
    name      = ()
    node_id   = ()
    number    = ()
    operation = ()
    type      = ()
    var_num   = ()