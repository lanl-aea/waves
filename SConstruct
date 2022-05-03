#! /usr/bin/env python

import os
import setuptools_scm

# Set project global variables
project_name = 'SCons-simulation'

# Inherit user's full environment and set project variables
env = Environment(ENV=os.environ.copy(),
                  PROJECT_NAME=project_name.lower(),
                  VERSION=setuptools_scm.get_version(),
                  PROJECT_DIR=Dir('.').abspath)

# Add target/build sub-directories
SConscript(dirs='.', variant_dir='build', duplicate=False)
SConscript(dirs='docs', variant_dir='build/docs', exports='env')
SConscript(dirs='eabm/tutorial_01_geometry', variant_dir='build/eabm/tutorial_01_geometry', exports='env')
