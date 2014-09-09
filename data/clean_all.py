#!/usr/bin/env python
import os        

ext = ('.col', '.row', '.nl', '.sol', '.dag')
to_delete = sorted(f for f in os.listdir('.') if f.endswith(ext))

for f in to_delete:
    os.remove(f)
  
print 'Deleted', len(to_delete), 'files'
