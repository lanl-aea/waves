#! /usr/bin/env python

import os
import pathlib

import setuptools_scm
import waves

# Variables required when WAVES is not installed as a package
# TODO: (1) Separate EABM and WAVES definitions
waves_source_dir = pathlib.Path('waves')
abaqus_wrapper = waves_source_dir / 'bin/abaqus_wrapper'
abaqus_wrapper = abaqus_wrapper.resolve()

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
                  ABAQUS_SOURCE_DIR=str(abaqus_source_dir),
                  # TODO: (1) Separate EABM and WAVES definitions
                  abaqus_wrapper=str(abaqus_wrapper))

# Add custom builders
env.Append(BUILDERS={'AbaqusJournal': waves.abaqus_journal(),
                     'AbaqusSolver': waves.abaqus_solver()})

# Add top-level SCons script
SConscript(dirs='.', variant_dir=str(variant_dir_base), exports='documentation_source_dir', duplicate=False)

# Add documentation target
build_dir = variant_dir_base / documentation_source_dir
SConscript(dirs=documentation_source_dir, variant_dir=str(build_dir), exports='env')

# Add simulation targets
eabm_simulation_directories = [
    'tutorial_01_geometry',
    'tutorial_02_partition_mesh',
    'tutorial_03_solverprep'
]
for source_dir in eabm_simulation_directories:
    build_dir = variant_dir_base / eabm_source_dir / source_dir
    SConscript(dirs=source_dir, variant_dir=build_dir, exports='env', duplicate=False)
