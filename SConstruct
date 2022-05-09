#! /usr/bin/env python

import os
import pathlib
import warnings

import setuptools_scm

# Ignore the version warning message associated with 'x.y.z+dev' Git tags
warnings.filterwarnings(action='ignore',
                        message='tag',
                        category=UserWarning,
                        module='setuptools_scm')

# Versioning is more complicated than ``setuptools_scm.get_version()`` to allow us to build and run tests in the Conda
# package directory, where setuptools_scm can't version from Git. This logic is reveresed from the waves.__init__
# logic. We do this to re-use SCons build target commands during Conda packaging to avoid hard coding target commands in
# the Conda recipe. This is not necessary in an EABM project definition.
try:
    version = setuptools_scm.get_version()
except LookupError:
    try:
        from importlib.metadata import version, PackageNotFoundError
        version = version("waves")
    except PackageNotFoundError:
        from waves import _version
        version = _version.version

# Variables required when WAVES is not installed as a package
waves_source_dir = pathlib.Path('waves')
abaqus_wrapper = waves_source_dir / 'bin/abaqus_wrapper'
abaqus_wrapper = abaqus_wrapper.resolve()

# TODO: make this available for overwrite from a command line option
# https://re-git.lanl.gov/kbrindley/scons-simulation/-/issues/25
variant_dir_base = pathlib.Path('build')

# Set project internal variables
project_name = 'WAVES'
eabm_source_dir = pathlib.Path('eabm')
abaqus_source_dir = eabm_source_dir / 'abaqus'
documentation_source_dir = 'docs'

# Inherit user's full environment and set project variables
env = Environment(ENV=os.environ.copy(),
                  PROJECT_NAME=project_name.lower(),
                  VERSION=version,
                  PROJECT_DIR=Dir('.').abspath,
                  ABAQUS_SOURCE_DIR=str(abaqus_source_dir),
                  abaqus_wrapper=str(abaqus_wrapper))

# Add top-level SCons script
SConscript(dirs='.', variant_dir=str(variant_dir_base), exports='documentation_source_dir', duplicate=False)

# Add documentation target
build_dir = variant_dir_base / documentation_source_dir
SConscript(dirs=documentation_source_dir, variant_dir=str(build_dir), exports='env')

# Add pytests
SConscript(dirs=str(waves_source_dir), exports='env', duplicate=False)

# Add conda build target
# TODO: fix the SCons conda build target and use it instead of hardcoding the conda build commands in .gitlab-ci.yml
# TODO: add a ``--croot`` switch, prefering /scratch/$USER/conda-build when available
# TODO: add a ``--croot`` command line option
package_prefix = f"dist/{project_name.upper()}-{env['VERSION']}"
conda_build_targets = [f"{package_prefix}-py3-none-any.whl", f"{package_prefix}.tar.gz"]
conda_build = env.Command(
    target=conda_build_targets,
    source=['recipe/metal.yaml', 'recipe/conda_build_config.yaml'],
    action='VERSION=$(python -m setuptools_scm) conda build recipe --channel conda-forge --no-anaconda-upload ' \
                                                                  '--croot /tmp/${USER}-conda-build ' \
                                                                  '--output-folder ./conda-build-artifacts')
env.Ignore('dist', conda_build_targets)
env.Alias('conda-build', conda_build)
