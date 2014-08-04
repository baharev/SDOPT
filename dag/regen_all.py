#!/usr/bin/env python
import subprocess

mods = ['bratu', 'eco9', 'JacobsenDbg', 'JacobsenTorn', 'Luyben', 
        'mss20heatBalance', 'mssTornDbg', 'tunnelDiodes' ]
        
#subprocess.call('rm -f *.col *.row *.nl *.sol' *.dag)

for modfile in mods:
  print 'Flattening', modfile
  subprocess.call(['./convert.sh', modfile + '.mod'])

