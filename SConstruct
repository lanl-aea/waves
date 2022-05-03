#! /usr/bin/env python

import os
import pathlib

import setuptools_scm

# Set project global variables
project_name = 'SCons-simulation'
eabm_source_dir = pathlib.Path('eabm')
abaqus_source_dir = eabm_source_dir / 'abaqus'
variant_dir_base = pathlib.Path('build')

# Inherit user's full environment and set project variables
env = Environment(ENV=os.environ.copy(),
                  PROJECT_NAME=project_name.lower(),
                  VERSION=setuptools_scm.get_version(),
                  PROJECT_DIR=Dir('.').abspath,
                  ABAQUS_SOURCE_DIR=str(abaqus_source_dir))

# Custom Builders
abaqus_journal = Builder(
    chdir=1,
    action='abaqus cae -noGui ${SOURCE.abspath} -- ${journal_options} > ${SOURCE.filebase}.log 2>&1')

# Add custom builders
env.Append(BUILDERS={'AbaqusJournal': abaqus_journal})

# Add top-level SCons script
SConscript(dirs='.', variant_dir=str(variant_dir_base), duplicate=False)

# Add documentation target
source_dir = 'docs'
build_dir = os.path.join(str(variant_dir_base), source_dir)
SConscript(dirs=source_dir, variant_dir=build_dir, exports='env')

# Add simulation targets
eabm_simulation_directories = [
    'tutorial_01_geometry',
    'tutorial_02_partition_mesh',
    'tutorial_03_solverprep'
]
for source_dir in eabm_simulation_directories:
    build_dir = os.path.join(str(variant_dir_base), str(eabm_source_dir / source_dir))
    SConscript(dirs=source_dir, variant_dir=build_dir, exports='env', duplicate=False)
