#!/usr/bin/env python
from __future__ import print_function
from clean_coconut import cleanup
import subprocess
import os
from paths import DATADIR

cleanup()
mods = sorted(f for f in os.listdir(DATADIR) if f.endswith('.mod'))
for modfile in mods:
    print('Flattening', modfile)
    subprocess.call(['../datagen/convert.sh', modfile], cwd=DATADIR)

# ampl filename.mod coconut.run, coconut.run is shared across all mod files
# and calls solve so that the reference solution ends up in the .dag file as a 
# tracepoint
