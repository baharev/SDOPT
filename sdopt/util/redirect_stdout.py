import sys
from contextlib import contextmanager

@contextmanager
def redirect_stdout(ostream):
    oldstdout = sys.stdout
    sys.stdout = ostream
    try:
        yield ostream
    finally:
        sys.stdout = oldstdout
