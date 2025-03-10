#! /usr/bin/env python

import os
import shutil
import pathlib
import platform
import warnings

import setuptools_scm


warnings.filterwarnings(action="ignore", message="tag", category=UserWarning, module="setuptools_scm")

# ========================================================================================================= SETTINGS ===
# Set project meta variables
project_dir = pathlib.Path(Dir(".").abspath)
documentation_source_dir = "docs"
package_source_dir = "waves"
project_name = "waves"
version = setuptools_scm.get_version()
project_variables = {
    "project_dir": project_dir,
    "package_dir": project_dir / package_source_dir,
    "version": version,
    "documentation_pdf": f"{project_name}-{version}.pdf",
    "tutorials_dir": project_dir / "waves/tutorials",
    "modsim_dir": "modsim_package",
    "abaqus_dir": "modsim_package/abaqus",
    "argparse_types_dir": "modsim_package/argparse_types",
    "cubit_dir": "modsim_package/cubit",
    "python_dir": "modsim_package/python",
    "tests_dir": "modsim_package/python/tests",
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
    help="SCons build (variant) root directory. Relative or absolute path. (default: '%default')",
)
AddOption(
    "--ignore-documentation",
    dest="ignore_documentation",
    default=False,
    action="store_true",
    # fmt: off
    help="Boolean to ignore the documentation build, e.g. during Conda package build and testing. Unaffected by the "
         "'--unconditional-build' option. (default: '%default')"
    # fmt: on
)
AddOption(
    "--unconditional-build",
    dest="unconditional_build",
    default=False,
    action="store_true",
    # fmt: off
    help="Boolean to force building of conditionally ignored targets, e.g. if the target's action program is missing "
         "and it would normally be ignored. (default: '%default')"
    # fmt: on
)
# Python optparse appends to the default list instead of overriding. Must implement default/override ourselves.
default_abaqus_commands = [
    "/apps/abaqus/Commands/abq2024",
    "/usr/projects/ea/abaqus/Commands/abq2024",
]
AddOption(
    "--abaqus-command",
    dest="abaqus_command",
    nargs=1,
    type="string",
    action="append",
    metavar="COMMAND",
    help=f"Override for the Abaqus command. Repeat to specify more than one (default: {default_abaqus_commands})",
)
# Python optparse appends to the default list instead of overriding. Must implement default/override ourselves.
default_cubit_commands = [
    "/apps/Cubit-16.16/cubit",
    "/usr/projects/ea/Cubit/Cubit-16.12/cubit",
]
AddOption(
    "--cubit-command",
    dest="cubit_command",
    nargs=1,
    type="string",
    action="append",
    metavar="COMMAND",
    help=f"Override for the Cubit command. Repeat to specify more than one (default: {default_cubit_commands})",
)

# ========================================================================================= CONSTRUCTION ENVIRONMENT ===
# Inherit user's full environment and set project options
env = Environment(
    ENV=os.environ.copy(),
    variant_dir_base=pathlib.Path(GetOption("variant_dir_base")),
    ignore_documentation=GetOption("ignore_documentation"),
    unconditional_build=GetOption("unconditional_build"),
    abaqus_commands=GetOption("abaqus_command"),
    cubit_commands=GetOption("cubit_command"),
)
# Python optparse appends to the default list instead of overriding. Must implement default/override ourselves.
env["abaqus_commands"] = env["abaqus_commands"] if env["abaqus_commands"] is not None else default_abaqus_commands
env["cubit_commands"] = env["cubit_commands"] if env["cubit_commands"] is not None else default_cubit_commands
env["ENV"]["PYTHONDONTWRITEBYTECODE"] = 1

# Empty defaults list to avoid building all simulation targets by default
env.Default()

# Handle OS-aware tee output
system = platform.system().lower()
if system == "windows":  # Assume PowerShell
    env["tee_suffix"] = "$(| Tee-Object -FilePath ${TARGETS[-1].abspath}$)"
else:  # *Nix style tee
    env["tee_suffix"] = "$(2>&1 | tee ${TARGETS[-1].abspath}$)"

# Find required programs for conditional target ignoring
required_programs = ["pytest", "sphinx-build", "latexmk", "flake8", "black", "mypy"]
for program in required_programs:
    absolute_path = env[program.replace("-", "_")] = shutil.which(program, path=env["ENV"]["PATH"])
    print(f"Checking whether '{program}' program exists...{absolute_path}")

# Find tutorial/system test third-party software
# TODO: separate Abaqus/Cubit construction environments for system testing
env["abaqus"] = next(
    (shutil.which(command, path=env["ENV"]["PATH"]) for command in env["abaqus_commands"] if command is not None),
    "abaqus",
)
env["cubit"] = next(
    (shutil.which(command, path=env["ENV"]["PATH"]) for command in env["cubit_commands"] if command is not None),
    "cubit",
)

# Build variable substitution dictionary
project_substitution_dictionary = dict()
for key, value in project_variables.items():
    env[key] = value
    project_substitution_dictionary[f"@{key}@"] = value

# ========================================================================================================== TARGETS ===
# Add documentation target
if not env["ignore_documentation"]:
    build_dir = env["variant_dir_base"] / documentation_source_dir
    source_dir = documentation_source_dir
    SConscript(
        dirs=documentation_source_dir,
        variant_dir=str(build_dir),
        exports={"env": env, "project_substitution_dictionary": project_substitution_dictionary},
    )
else:
    print(f"The 'ignore_documentation' option was set to 'True'. Skipping documentation SConscript file(s)")

# Add pytests, style checks, and static type checking
workflow_configurations = ["pytest", "style", "mypy"]
for workflow in workflow_configurations:
    build_dir = env["variant_dir_base"] / workflow
    SConscript(build_dir.name, variant_dir=build_dir, exports={"env": env}, duplicate=False)

# ============================================================================================= PROJECT HELP MESSAGE ===
# Add aliases to help message so users know what build target options are available
# This must come *after* all expected Alias definitions and SConscript files.
from SCons.Node.Alias import default_ans

alias_help = "\nTarget Aliases:\n"
for alias in default_ans:
    alias_help += f"    {alias}\n"
try:
    # SCons >=4.9.0
    Help(alias_help, append=True, local_only=True)
except TypeError as err:
    try:
        # SCons >=4.6,<4.9.0
        Help(alias_help, append=True, keep_local=True)
    except TypeError as err:
        # SCons <4.6
        Help(alias_help, append=True)
