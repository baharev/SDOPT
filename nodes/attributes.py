from collections import namedtuple
from util.autoenum import AutoNumber

# Shouldn't this be a class or something?
Bounds = namedtuple('Bounds', 'l u')

class NodeAttr(AutoNumber):
    bounds    = ()
    con_num   = ()
    d_term    = ()
    dag       = ()
    display   = ()
    n_term    = ()
    name      = ()
    node_id   = ()
    number    = ()
    operation = ()
    type      = ()
    var_num   = ()