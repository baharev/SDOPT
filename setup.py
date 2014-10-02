#!/usr/bin/env python
from __future__ import print_function
from distutils.core import setup

from glob import glob
from os import listdir
from os.path import join, isfile

#df = glob(join('data', '*'))
#print(df)

#d = '.'
#pkgs = sorted(o for o in listdir(d) if isfile(join(d,o,'__init__.py')))
# print(pkgs)

descr = 'Structure-driven optimization methods for modular technical systems'

setup(
    name='SDOPT',
    version='0.0-pre-alpha',
    description=descr,
    author='Ali Baharev',
    author_email = 'ali.baharev@gmail.com',
    url='https://sdopt.readthedocs.org',
    license = 'BSD',
    platforms = ['Linux','Mac OSX','Windows','Unix'],
    long_description=descr,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Topic :: Scientific/Engineering :: Mathematics',
    ],
    py_modules=['main'],
    packages=sorted(d for d in listdir('.') if isfile(join('.',d,'__init__.py'))),
    data_files=[('data', glob(join('data', '*')))]
)
