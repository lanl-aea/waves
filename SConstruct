#! /usr/bin/env python

import os
import subprocess
import re

version_regex = r'([0-9]+)\.([0-9]+)\.([0-9]+)(\..*)'
setuptools_scm_stdout = subprocess.check_output('python -m setuptools_scm')
major, minor, micro, dev = re.search(version_regex, setuptools_scm_stdout).groups()

# Set project global variables
project_name = 'SCons-simulation'
version = f"{major}.{minor}.{micro}"
if dev:
    version = f"{version}{dev}"

# Inherit user's full environment and set project variables
env = Environment(ENV=os.environ.copy(), PROJECT_NAME=project_name.lower(), VERSION=version)

# Add target/build sub-directories
SConscript(dirs='.', variant_dir='build', duplicate=False)
SConscript(dirs='docs', variant_dir='build/docs', exports='env')
