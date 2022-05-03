#! /usr/bin/env python

import os
import setuptools_scm

# Set project global variables
project_name = 'SCons-simulation'
abaqus_source_dir = 'eabm/abaqus'
variant_dir_base = 'build'

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

# Add top-level SCons script
SConscript(dirs='.', variant_dir=variant_dir_base, duplicate=False)

# Add documentation target
source_dir = 'docs'
build_dir = os.path.join(variant_dir_base, source_dir)
SConscript(dirs=source_dir, variant_dir=build_dir, exports='env')

# Add simulation targets
eabm_simulation_directories = [
    'eabm/tutorial_01_geometry',
    'eabm/tutorial_02_partition_mesh',
    'eabm/tutorial_03_solverprep'
]
for source_dir in eabm_simulation_directories:
    build_dir = os.path.join(variant_dir_base, source_dir)
    SConscript(dirs=source_dir, variant_dir=build_dir, exports='env', duplicate=False)
