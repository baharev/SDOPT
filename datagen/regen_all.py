#!/usr/bin/env python
from __future__ import print_function
from clean_coconut import cleanup
import subprocess
import os
from paths import DATADIR

cleanup()
mods = sorted(f for f in os.listdir('.') if f.endswith('.mod'))
for modfile in mods:
    print('Flattening', modfile)
    subprocess.call(['./convert.sh', modfile], cwd=DATADIR)
