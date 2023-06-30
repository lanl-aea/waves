import os
import sys
import pathlib
import subprocess

import pytest

from waves import _settings


tutorial_directory = _settings._installed_tutorials_directory

env = os.environ.copy()
# If executing in repository, add package to PYTHONPATH
if _settings._repository_tutorials_directory == tutorial_directory:
    package_parent_path = tutorial_directory.parent
    key = "PYTHONPATH"
    if key in env:
        env[key] = f"{package_parent_path}:{env[key]}"
    else:
        env[key] = f"{package_parent_path}"

@pytest.mark.systemtest
@pytest.mark.parametrize("command", [
    "scons . --sconstruct=scons_quickstart_SConstruct --keep-going",
    "scons . --sconstruct=scons_multiactiontask_SConstruct --keep-going",
    "scons . --sconstruct=waves_quickstart_SConstruct --keep-going",
    "scons . --sconstruct=tutorial_00_SConstruct --keep-going --unconditional-build",
    "scons . --sconstruct=tutorial_01_geometry_SConstruct --keep-going --unconditional-build",
    "scons . --sconstruct=tutorial_matlab_SConstruct --keep-going",
    "scons . --sconstruct=tutorial_02_partition_mesh_SConstruct --keep-going --unconditional-build",
    "scons . --sconstruct=tutorial_argparse_types_SConstruct --keep-going --unconditional-build",
    "scons . --sconstruct=tutorial_03_solverprep_SConstruct --keep-going --unconditional-build",
    "scons . --sconstruct=tutorial_04_simulation_SConstruct --keep-going --unconditional-build",
    "scons . --sconstruct=tutorial_cubit_SConstruct --keep-going --unconditional-build",
    "scons . --sconstruct=tutorial_escape_sequences_SConstruct --solve-cpus=1 --keep-going --unconditional-build",
    "scons . --sconstruct=tutorial_builder_post_actions_SConstruct --keep-going --unconditional-build",
    # TODO: Figure out how to authenticate the institutional account without expanding the user credential exposure to
    # AEA Gitlab group members. Until then, the SSH remote execution can't be integration/regression tested.
    #"scons . --sconstruct=tutorial_remote_execution_SConstruct --keep-going --unconditional-build",
    "scons . --sconstruct=tutorial_sbatch_SConstruct --keep-going --unconditional-build",
    "scons . --sconstruct=tutorial_05_parameter_substitution_SConstruct --keep-going --unconditional-build",
    "scons . --sconstruct=tutorial_06_include_files_SConstruct --keep-going --unconditional-build",
    "scons . --sconstruct=tutorial_07_cartesian_product_SConstruct --jobs=4 --keep-going --unconditional-build",
    "scons . --sconstruct=tutorial_07_latin_hypercube_SConstruct --jobs=4 --keep-going --unconditional-build",
    "scons . --sconstruct=tutorial_07_sobol_sequence_SConstruct --jobs=4 --keep-going --unconditional-build",
    "scons . --sconstruct=tutorial_08_data_extraction_SConstruct --jobs=4 --keep-going --unconditional-build",
    "scons . --sconstruct=tutorial_09_post_processing_SConstruct --jobs=4 --keep-going --unconditional-build",
    "scons datacheck --sconstruct=tutorial_10_regression_testing_SConstruct --jobs=4 --keep-going --unconditional-build",
    "scons . --sconstruct=tutorial_11_archival_SConstruct --jobs=4 --keep-going --unconditional-build",
    "scons . --sconstruct=tutorial_task_reuse_SConstruct --jobs=4 --keep-going --unconditional-build",
    "scons . --sconstruct=tutorial_mesh_convergence_SConstruct --jobs=4 --keep-going --unconditional-build",
])
def test_run_tutorial(command):
    command = command.split(" ")
    result = subprocess.check_output(command, env=env, cwd=tutorial_directory).decode('utf-8')
