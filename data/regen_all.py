#!/usr/bin/env python
import clean_all
import subprocess
import os

mods = sorted(f for f in os.listdir('.') if f.endswith('.mod'))

for modfile in mods:
  print 'Flattening', modfile
  subprocess.call(['./convert.sh', modfile])

