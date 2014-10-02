
def _message(a, b, op, msg):
    return '%r %s %r\n%s' % (a, op, b, msg if msg is not None else '')

def assertEqual(a, b, msg=None):
    assert a==b, _message(a, b, '!=', msg)
    
def assertLess(a, b, msg=None):
    assert a < b, _message(a, b, '>=', msg) 
    
def assertEqLength(seq1, seq2, msg=None):
    assertEqual(len(seq1), len(seq2), msg)
