from tempfile import gettempdir
from os.path import join
from util.rootpkg_path import rootpkg_path

TMPDIR  = join(gettempdir(), 'gjh') # /tmp/gjh on Linux
DATADIR = join(rootpkg_path, 'data')
AMPL = 'ampl' # <- Keep in sync with convert.sh
CONVERTER = rootpkg_path+'/datagen/convert.sh' # Won't work on Win anyway
