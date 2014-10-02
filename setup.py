#!/usr/bin/env python
from __future__ import print_function
from distutils.core import setup

from os import listdir
from os.path import join, isfile

descr = 'Structure-driven optimization methods for modular technical systems'

topdir = join('.','sdopt')

pkgs = ['sdopt'] + sorted('sdopt.'+d for d in listdir(topdir) 
                             if isfile(join(topdir,d,'__init__.py')))

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
    packages=pkgs,
    package_data={'sdopt.datagen': [join('data','*')]},
)
