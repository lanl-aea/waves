#! /usr/bin/env python

import os
import pathlib

from waves._settings import _project_name_short, _abaqus_wrapper

# ========================================================================================================= SETTINGS ===
# Set project meta variables
documentation_source_dir = 'docs'
package_source_dir = _project_name_short.lower()
project_variables = {
    'project_dir': Dir('.').abspath,
    'abaqus_wrapper': str(_abaqus_wrapper),
    'eabm_dir': 'eabm',
    'abaqus_dir': 'source/abaqus'
}

# =========================================================================================== COMMAND LINE VARIABLES ===
# Accept command line variables with fall back default values
variables = Variables(None, ARGUMENTS)
variables.AddVariables(
    PathVariable('variant_dir_base',
        help='SCons variant (build) root directory. Relative or absolute path.',
        default='build',
        validator=PathVariable.PathAccept),
    BoolVariable('conditional_ignore',
        help="Boolean to conditionally ignore targets, e.g. if the action's program is missing.",
        default=True),
    BoolVariable('ignore_documentation',
        help="Boolean to ignore the documentation build, e.g. during Conda package build and testing.",
        default=False))

# ========================================================================================= CONSTRUCTION ENVIRONMENT ===
# Inherit user's full environment and set project variables
env = Environment(ENV=os.environ.copy(),
                  variables=variables)

# Find required programs for conditional target ignoring
required_programs = ['sphinx-build']
conf = env.Configure()
for program in required_programs:
    env[program.replace('-', '_')] = conf.CheckProg(program)
conf.Finish()

# Add project command line variable options to help message
Help(variables.GenerateHelpText(env))

# Build variable substitution dictionary
project_substitution_dictionary = dict()
for key, value in project_variables.items():
    env[key] = value
    project_substitution_dictionary[f"@{key}@"] = value

# ======================================================================================= SCONSTRUCT LOCAL VARIABLES ===
# Build path object for extension and re-use
variant_dir_base = pathlib.Path(env['variant_dir_base'])

# ========================================================================================================== TARGETS ===
# Add documentation target
if not env['ignore_documentation']:
    build_dir = variant_dir_base / documentation_source_dir
    SConscript(dirs='.', variant_dir=str(variant_dir_base), exports='documentation_source_dir', duplicate=False)
    docs_aliases = SConscript(dirs=documentation_source_dir,
                              variant_dir=str(build_dir),
                              exports=['env', 'project_substitution_dictionary'])
else:
    print(f"The 'ignore_documentation' option was set to 'True'. Skipping documentation SConscript file(s)")
    docs_aliases = []

# Add pytests
pytest_aliases = SConscript(dirs=package_source_dir, exports='env', duplicate=False)

# ============================================================================================= PROJECT HELP MESSAGE ===
# Add aliases to help message so users know what build target options are available
# TODO: recover alias list from SCons variable instead of constructing manually
# https://re-git.lanl.gov/kbrindley/waves/-/issues/33
alias_list = docs_aliases + pytest_aliases
alias_help = "\nTarget Aliases:\n"
for alias in alias_list:
    alias_help += f"    {alias}\n"
Help(alias_help)
