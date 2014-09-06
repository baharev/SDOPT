from itertools import islice, dropwhile

def advance(itr, n):
    return islice(itr, n, None)

def skip_until(pred, itr):
    return dropwhile(lambda s: not pred(s), itr)

def nth(iterable, n, default=None):
    'Returns the nth item or a default value.'
    return next(islice(iterable, n, None), default)