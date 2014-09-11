#!/usr/bin/env python
from __future__ import print_function
import os
import shutil
import subprocess
import sys
from os.path import join
from string import Template
from paths import AMPL, DATADIR, TMPDIR

def main(args):
    if (len(args)==1):
        generate_gjh()
    elif (args[1] == '--clean'):
        clean()
    else:
        print('Usage: call with no arguments or with --clean', file=sys.stderr)
        
def clean():
    ext = ('.gjh', '.log')
    to_delete = sorted(f for f in os.listdir(DATADIR) if f.endswith(ext))
    for f in to_delete:
        os.remove(join(DATADIR,f))
    print('Deleted',len(to_delete),'files')
    
def generate_gjh():
    clean()
    shutil.rmtree(TMPDIR, ignore_errors=True)
    os.mkdir(TMPDIR)
    modfiles = sorted(f for f in os.listdir(DATADIR) if f.endswith('.mod'))
    for modfile in modfiles:
        print('Generating gjh file for', modfile)
        create_gjh_input(modfile)
        run_ampl(modfile)
    copy_output()

def create_gjh_input(modfile):
    shutil.copy(join(DATADIR, modfile), TMPDIR)
    with open(join(TMPDIR, modfile), 'a') as dst:
        dst.write(gjh_invocation.substitute(problem_name=modfile[:-4]))

def run_ampl(modfile):
    logfile_name = join(TMPDIR, modfile[:-4]+'.log')
    with open(logfile_name, 'w') as logfile:
        ret = subprocess.call([AMPL, modfile], cwd=TMPDIR, stdout=logfile)
    if ret:
        sys.exit(ret)

def copy_output():
    for basename, content in gen_gjh_basename_content():
        with open(join(DATADIR, basename+'.gjh'), 'w') as dst:
            dst.write(content)
        shutil.copy(join(TMPDIR, basename+'.log'), DATADIR)

def gen_gjh_basename_content():
    to_copy = (f for f in os.listdir(TMPDIR) if f.endswith('.gjh'))
    for gjh_name in to_copy:
        content = get_content(gjh_name)
        if 'NaN' in content or 'Infinity' in content:
            print(gjh_name,'has NaN or Inf in it, skipping it',file=sys.stderr)
        else:
            yield gjh_name[:-4], content

def get_content(gjh_name):
    with open(join(TMPDIR, gjh_name), 'r') as f:
        return f.read()    

gjh_invocation = Template('''###################################################
option seed 31;

# Force model generation, otherwise the log may become messed up
print "constraints:", _sncons, "variables:", _snvars;

print "@@@ Variable vector";
print _snvars;

for {j in 1.._snvars} {
  let _svar[j] := Uniform(_svar[j].lb, _svar[j].ub);
  print _svar[j];
}
print "";

print "@@@ Residual vector";
print _sncons;

for {i in 1.._sncons} {
  print _scon[i].body - _scon[i].lb;
}
print "";

write g$problem_name;
option solver gjh;
solve;
''')

if __name__=='__main__':
    main(sys.argv)
