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

# Accept command line variables with fall back default values
variables = Variables(None, ARGUMENTS)
variables.Add(
    PathVariable('variant_dir_base',
        help='SCons variant (build) root directory. Relative or absolute path.',
        default='build',
        validator=PathVariable.PathAccept))

# Set project internal variables

# Inherit user's full environment and set project variables
env = Environment(ENV=os.environ.copy(),
                  variables=variables)

# Add project command line variable options to help message
Help(variables.GenerateHelpText(env))

# Set project internal variables and variable substitution dictionaries
project_name = 'WAVES'
documentation_source_dir = 'docs'
waves_source_dir = 'waves'
project_variables = {
    'project_name': project_name,
    'project_dir': Dir('.').abspath,
    'version': version,
    'abaqus_source_dir': 'eabm/abaqus',
    'abaqus_wrapper': str(pathlib.Path(f'{waves_source_dir}/bin/abaqus_wrapper').resolve())
} 
project_substitution_dictionary = dict()
for key, value in project_variables.items():
    env[key] = value
    project_substitution_dictionary[f"@{key}@"] = value

# Build path object for extension and re-use
variant_dir_base = pathlib.Path(env['variant_dir_base'])

# Add documentation target
build_dir = variant_dir_base / documentation_source_dir
SConscript(dirs='.', variant_dir=str(variant_dir_base), exports='documentation_source_dir', duplicate=False)
SConscript(dirs=documentation_source_dir, variant_dir=str(build_dir), exports=['env', 'project_substitution_dictionary'])

# Add pytests
SConscript(dirs=waves_source_dir, exports='env', duplicate=False)

# Add conda build target
# TODO: fix the SCons conda build target and use it instead of hardcoding the conda build commands in .gitlab-ci.yml
# TODO: add a ``--croot`` switch, prefering /scratch/$USER/conda-build when available
# TODO: add a ``--croot`` command line option
package_prefix = f"dist/{project_name.upper()}-{env['version']}"
conda_build_targets = [f"{package_prefix}-py3-none-any.whl", f"{package_prefix}.tar.gz"]
conda_build = env.Command(
    target=conda_build_targets,
    source=['recipe/metal.yaml', 'recipe/conda_build_config.yaml'],
    action='VERSION=$(python -m setuptools_scm) conda build recipe --channel conda-forge --no-anaconda-upload ' \
                                                                  '--croot /tmp/${USER}-conda-build ' \
                                                                  '--output-folder ./conda-build-artifacts')
env.Ignore('dist', conda_build_targets)
env.Alias('conda-build', conda_build)
