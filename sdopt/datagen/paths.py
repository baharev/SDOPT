from tempfile import gettempdir
from os.path import join, abspath, dirname

_ROOT = abspath(dirname(__file__))

TMPDIR  = join(gettempdir(), 'gjh') # /tmp/gjh on Linux
DATADIR = join(_ROOT, 'data')
AMPL = 'ampl' # <- Keep in sync with convert.sh
CONVERTER = _ROOT+'/convert.sh' # Won't work on Win anyway
