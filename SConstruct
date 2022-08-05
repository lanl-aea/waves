#! /usr/bin/env python

import os
import pathlib

# ========================================================================================================= SETTINGS ===
# Set project meta variables
documentation_source_dir = 'docs'
package_source_dir = 'waves'
project_variables = {
    'project_dir': Dir('.').abspath,
    'build_wrapper': 'waves/bin/waves_build_wrapper',
    'eabm_dir': 'eabm',
    'abaqus_dir': 'eabm_package/abaqus',
    'cubit_dir': 'eabm_package/cubit',
    'python_dir': 'eabm_package/python',
    'tutorial_01_dir': 'tutorial_01_geometry',
    'tutorial_02_dir': 'tutorial_02_partition_mesh',
    'tutorial_03_dir': 'tutorial_03_solverprep',
    'tutorial_04_dir': 'tutorial_04_simulation',
    'tutorial_05_dir': 'tutorial_05_parameter_substitution',
    'tutorial_06_dir': 'tutorial_06_include_files',
    'tutorial_07_cp_dir': 'tutorial_07_cartesian_product',
    'tutorial_07_lh_dir': 'tutorial_07_latin_hypercube',
    'tutorial_08_dir': 'tutorial_08_data_extraction',
    'tutorial_09_dir': 'tutorial_09_post_processing',
    'tutorial_10_dir': 'tutorial_10_regression_testing',
    'tutorial_cubit_dir': 'tutorial_cubit'
}

# ============================================================================================= COMMAND LINE OPTIONS ===
AddOption(
    "--build-dir",
    dest="variant_dir_base",
    default="build",
    nargs=1,
    type="string",
    action="store",
    metavar="DIR",
    help="SCons build (variant) root directory. Relative or absolute path. (default: '%default')"
)
AddOption(
    "--ignore-documentation",
    dest="ignore_documentation",
    default=False,
    action="store_true",
    help="Boolean to ignore the documentation build, e.g. during Conda package build and testing. Unaffected by the " \
         "'--unconditional-build' option. (default: '%default')"
)
AddOption(
    "--unconditional-build",
    dest="unconditional_build",
    default=False,
    action="store_true",
    help="Boolean to force building of conditionally ignored targets, e.g. if the target's action program is missing" \
            " and it would normally be ignored. (default: '%default')"
)

# ========================================================================================= CONSTRUCTION ENVIRONMENT ===
# Inherit user's full environment and set project options
env = Environment(ENV=os.environ.copy(),
                  variant_dir_base=GetOption("variant_dir_base"),
                  ignore_documentation=GetOption("ignore_documentation"),
                  unconditional_build=GetOption("unconditional_build"))

# Find required programs for conditional target ignoring
required_programs = ['sphinx-build']
conf = env.Configure()
for program in required_programs:
    env[program.replace('-', '_')] = conf.CheckProg(program)
conf.Finish()

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
# This must come *after* all expected Alias definitions and SConscript files.
try:
    # Recover from SCons configuration
    from SCons.Node.Alias import default_ans
    alias_list = default_ans
except ImportError:
    # Fall back to manually constructed alias list(s)
    alias_list = docs_aliases + pytest_aliases
alias_help = "\nTarget Aliases:\n"
for alias in alias_list:
    alias_help += f"    {alias}\n"
Help(alias_help, append=True)
