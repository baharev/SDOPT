def assertEqual(first, second, msg=None):
    assert first == second, (msg or '%r != %r' % (first, second)) 
    
def assertEqLength(seq1, seq2, msg=None):
    assertEqual(len(seq1), len(seq2), msg)
