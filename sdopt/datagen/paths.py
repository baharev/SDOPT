from tempfile import gettempdir
from os.path import join
from .. import _ROOT

TMPDIR  = join(gettempdir(), 'gjh') # /tmp/gjh on Linux
DATADIR = join(_ROOT, 'datagen', 'data')
AMPL = 'ampl' # <- Keep in sync with convert.sh
CONVERTER = _ROOT+'/datagen/convert.sh' # Won't work on Win anyway
