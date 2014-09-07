from itertools import islice, dropwhile

def advance(itr, n):
    return islice(itr, n, None)

def skip_until(pred, itr):
    return dropwhile(lambda s: not pred(s), itr)

def nth(iterable, n, default=None):
    'Returns the nth item or a default value.'
    return next(islice(iterable, n, None), default)

# http://code.activestate.com/recipes/82234-importing-a-dynamically-generated-module/
def import_code(code, name):
    import imp
    module = imp.new_module(name)
    exec code in module.__dict__
    return module