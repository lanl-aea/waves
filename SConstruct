#! /usr/bin/env python

import os
import pathlib

import setuptools_scm
import waves

# TODO: make this available for overwrite from a command line option
variant_dir_base = pathlib.Path('build')

# Set project internal variables
project_name = 'SCons-simulation'
eabm_source_dir = pathlib.Path('eabm')
abaqus_source_dir = eabm_source_dir / 'abaqus'
documentation_source_dir = 'docs'

# Inherit user's full environment and set project variables
env = Environment(ENV=os.environ.copy(),
                  PROJECT_NAME=project_name.lower(),
                  VERSION=setuptools_scm.get_version(),
                  PROJECT_DIR=Dir('.').abspath,
                  ABAQUS_SOURCE_DIR=str(abaqus_source_dir))

# Add custom builders
env.Append(BUILDERS={'AbaqusJournal': waves.abaqus_journal})

# Add top-level SCons script
SConscript(dirs='.', variant_dir=str(variant_dir_base), exports='documentation_source_dir', duplicate=False)

# Add documentation target
source_dir = 'docs'
build_dir = variant_dir_base / source_dir
SConscript(dirs=source_dir, variant_dir=str(build_dir), exports='env')

# Add simulation targets
eabm_simulation_directories = [
    'tutorial_01_geometry',
    'tutorial_02_partition_mesh',
    'tutorial_03_solverprep'
]
for source_dir in eabm_simulation_directories:
    build_dir = variant_dir_base / eabm_source_dir / source_dir
    SConscript(dirs=source_dir, variant_dir=build_dir, exports='env', duplicate=False)
