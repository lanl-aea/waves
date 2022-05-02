#! /usr/bin/env python

import os

# Set project global variables
project_name = 'SCons-simulation'
# TODO: recover from Git tags. Probably using Python setuptools_scm.
VERSION='0.1.1+dev'

# Inherit user's full environment and set project variables
env = Environment(ENV=os.environ.copy(), PROJECT_NAME=project_name.lower(), VERSION=VERSION)

# Add target/build sub-directories
SConscript(dirs='.', variant_dir='build', duplicate=False)
SConscript(dirs='docs', variant_dir='build/docs')
