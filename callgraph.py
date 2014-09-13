from pycallgraph import PyCallGraph
from pycallgraph import Config
from pycallgraph import GlobbingFilter
from pycallgraph.output import GraphvizOutput

from nodes.reverse_ad import prepare_evaluation_code
from coconut_parser.dag_parser import read_problem


config = Config(max_depth=5)
config.trace_filter = GlobbingFilter(exclude=[
    'pycallgraph.*',
    '*.secret_function',
])

graphviz = GraphvizOutput(output_file='/tmp/callgraph.png')

with PyCallGraph(output=graphviz, config=config):
    problem = read_problem('./data/mssheatBalanceDbg.dag', plot_dag=False, show_sparsity=False)
    print('===============================================')
    print( prepare_evaluation_code(problem) )