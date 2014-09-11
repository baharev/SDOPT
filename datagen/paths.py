from tempfile import gettempdir
from os.path import join

TMPDIR  = join(gettempdir(), 'gjh') # /tmp/gjh on Linux
DATADIR = join('..', 'data')        # ../data on Linux
AMPL = 'ampl' # <- Keep in sync with convert.sh
# regen_all.py knows where that convert.sh is in the datagen directory