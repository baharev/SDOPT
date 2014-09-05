from itertools import islice

def nth(iterable, n, default=None):
    'Returns the nth item or a default value.'
    return next(islice(iterable, n, None), default)