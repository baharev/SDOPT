from ..nodes.types import ntype, is_var_node
from ..nodes.attributes import NodeAttr, Bounds

def parse(problem, elems):
    node_id = elems.pop()
    node_dict = create_node(node_id, elems)
    if is_var_node(node_dict):
        problem.var_node_ids.add(node_id)
    problem.dag.add_node(node_id, node_dict)

def create_node(node_id, line_as_list):
    attr = { NodeAttr.node_id : node_id}
    for elems in line_as_list:
        kind = elems[0]
        func = lookup_table.get(kind, unimplemented)
        func(node_id, elems, attr)
    attr[NodeAttr.display] = '?'
    attr[NodeAttr.node_id] = node_id
    return attr

def bounds(unused1, elems, attr):
    # b [0,I]
    lb, ub = elems[1][1:-1].replace('I','inf').split(',')
    attr[NodeAttr.bounds] = Bounds(float(lb), float(ub))

def d_term(unused1, elems, attr):
    # d 0.1; lambda*x1 + d or d/(lambda*x1)
    attr[NodeAttr.d_term] = float(elems[1])

def n_term(unused1, elems, attr):
    # n 3; (lamba*x)^n
    attr[NodeAttr.n_term] = int(elems[1])

def var_number(node_id, elems, attr):
    # V 2
    attr[NodeAttr.var_num] = int(elems[1])
    attr[NodeAttr.type] = ntype.VAR

def constant(node_id, elems, attr):
    # C 0.1
    attr[NodeAttr.number] = float(elems[1])
    attr[NodeAttr.type] = ntype.NUM

def sumnode(node_id, elems, attr):
    # Update negate below *and* neg_node if the implementation changes
    attr[NodeAttr.operation] = '+'
    attr[NodeAttr.type] = ntype.SUM

def negate(node_id, elems, attr):
    # Update if sumnode changes
    # symbol in .dag file: -#
    attr[NodeAttr.operation] = '-'
    attr[NodeAttr.type] = ntype.NEG

def mul(node_id, elems, attr):
    attr[NodeAttr.operation] = '*'
    attr[NodeAttr.type] = ntype.MUL

def div(node_id, elems, attr):
    attr[NodeAttr.operation] = '/'
    attr[NodeAttr.type] = ntype.DIV

def exp(node_id, elems, attr):
    attr[NodeAttr.operation] = 'exp'
    attr[NodeAttr.type] = ntype.EXP

def log(node_id, elems, attr):
    attr[NodeAttr.operation] = 'log'
    attr[NodeAttr.type] = ntype.LOG

def power(node_id, elems, attr):
    attr[NodeAttr.operation] = 'pow'
    attr[NodeAttr.type] = ntype.POW

def square(node_id, elems, attr):
    attr[NodeAttr.operation] = 'sqr'
    attr[NodeAttr.type] = ntype.SQR

def coconut_simplifier_ignored(node_id, elems, attr):
    pass

def unimplemented(node_id, elems, attr):
    raise NotImplementedError('%d  %s' % (node_id, elems))

lookup_table = {  'b':   bounds,
                  'V':   var_number,
                  'C':   constant,
                  'd':   d_term,
                  'n':   n_term,
                  's':   coconut_simplifier_ignored,
                  '+':   sumnode,
                  '-#':  negate,
                  '*':   mul,
                  '/':   div,
                  'exp': exp,
                  'log': log,
                  '^'  : power,
                  '2'  : square }
