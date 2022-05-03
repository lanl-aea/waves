#! /usr/bin/env python

import os
import setuptools_scm

# Set project global variables
project_name = 'SCons-simulation'
version = setuptools_scm.get_version() 

# Inherit user's full environment and set project variables
env = Environment(ENV=os.environ.copy(), PROJECT_NAME=project_name.lower(), VERSION=version)

# Add target/build sub-directories
SConscript(dirs='.', variant_dir='build', duplicate=False)
SConscript(dirs='docs', variant_dir='build/docs', exports='env')
