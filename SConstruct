#! /usr/bin/env python

import os
import setuptools_scm

# Set project global variables
project_name = 'SCons-simulation'
abaqus_source_dir = 'eabm/abaqus'

# Inherit user's full environment and set project variables
env = Environment(ENV=os.environ.copy(),
                  PROJECT_NAME=project_name.lower(),
                  VERSION=setuptools_scm.get_version(),
                  PROJECT_DIR=Dir('.').abspath,
                  ABAQUS_SOURCE_DIR=abaqus_source_dir)

# Custom Builders
abaqus_journal = Builder(
    chdir=1,
    action='abaqus cae -noGui ${SOURCE.abspath} -- ${journal_options} > ${SOURCE.filebase}.log 2>&1')

# Add custom builders
env.Append(BUILDERS={'AbaqusJournal': abaqus_journal})

# Add target/build sub-directories
SConscript(dirs='.', variant_dir='build', duplicate=False)
SConscript(dirs='docs', variant_dir='build/docs', exports='env')
SConscript(dirs='eabm/tutorial_01_geometry', variant_dir='build/eabm/tutorial_01_geometry', exports='env', duplicate=False)
