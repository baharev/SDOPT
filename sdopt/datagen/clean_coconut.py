#!/usr/bin/env python
from __future__ import print_function
import os
from os.path import join
from paths import DATADIR

def cleanup():
    # Keep ext in sync with convert.sh
    ext = ('.col', '.row', '.nl', '.sol', '.dag')
    to_delete = sorted(f for f in os.listdir(DATADIR) if f.endswith(ext))
    for f in to_delete:
        os.remove(join(DATADIR,f)) 
    print('Deleted', len(to_delete), 'files')
    
if __name__=='__main__':
    cleanup()
