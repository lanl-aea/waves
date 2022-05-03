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

# Add target/build sub-directories
SConscript(dirs='.', variant_dir=variant_dir_base, duplicate=False)

source_dir = 'docs'
build_dir = os.path.join(variant_dir_base, source_dir)
SConscript(dirs=source_dir, variant_dir=build_dir, exports='env')

source_dir = 'eabm/tutorial_01_geometry'
build_dir = os.path.join(variant_dir_base, source_dir)
SConscript(dirs=source_dir, variant_dir=build_dir, exports='env', duplicate=False)

source_dir = 'eabm/tutorial_02_partition_mesh'
build_dir = os.path.join(variant_dir_base, source_dir)
SConscript(dirs=source_dir, variant_dir=build_dir, exports='env', duplicate=False)
