from __future__ import print_function
from itertools import islice, dropwhile
import os

def advance(itr, n):
    return islice(itr, n, None)

def skip_until(pred, itr):
    return dropwhile(lambda s: not pred(s), itr)

def nth(iterable, n, default=None):
    'Returns the nth item or a default value.'
    return next(islice(iterable, n, None), default)

# http://code.activestate.com/recipes/82234-importing-a-dynamically-generated-module/
def import_code(code):
    import imp
    module = imp.new_module('someFakeName')
    try:
        exec code in module.__dict__
    except:
        print(code)
        raise
    return module

def get_all_files(directory, extension):
    files = sorted(f for f in os.listdir(directory) if f.endswith(extension))
    return [ os.path.join(directory, filename) for filename in files ]
