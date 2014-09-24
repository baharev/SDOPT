#!/usr/bin/env python
from __future__ import print_function
import os
import shutil
import subprocess
import sys
from os.path import join
from string import Template
from paths import AMPL, DATADIR, TMPDIR

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
        try_generation(modfile)
    copy_output()
    
def try_generation(modfile):
    SEEDS = [1, 31, 42, 13, 26, 87, 59, 64, 77, 95]    
    for seed in SEEDS:
        create_gjh_input(modfile, seed)
        ret = run_ampl(modfile)
        if ret==0:
            return
    sys.exit(ret)        

def create_gjh_input(modfile, seed):
    shutil.copy(join(DATADIR, modfile), TMPDIR)
    with open(join(TMPDIR, modfile), 'a') as dst:
        dst.write(gjh_run.substitute(problem_name=modfile[:-4], seed=seed))

def run_ampl(modfile):
    logfile_name = join(TMPDIR, modfile[:-4]+'.log')
    with open(logfile_name, 'w') as logfile:
        return subprocess.call([AMPL, modfile], cwd=TMPDIR, stdout=logfile)

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

gjh_run = Template('''##########################################################
option randseed $seed;
# Force model generation, otherwise the log becomes messed up
print "ignore this line", _snzcons;

print "@@@ Problem statistics";
print "constraints:", _sncons, "variables:", _snvars, "nonzeros:", _snzcons;

print "Variable vector:";

for {j in 1.._snvars} {
  let _svar[j] := Uniform(_svar[j].lb, _svar[j].ub);
  print _svar[j];
}
print "";

print "Residual vector:";

for {i in 1.._sncons} {
  print _scon[i].body - _scon[i].lb;
}
print "";

write g$problem_name;
option solver gjh;
solve;
''')

if __name__=='__main__':
    generate_gjh()
