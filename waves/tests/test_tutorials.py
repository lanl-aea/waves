import os
import sys
import pathlib
import tempfile
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
@pytest.mark.parametrize("command, directory", [
    ("scons . --sconstruct=scons_quickstart_SConstruct", tutorial_directory),
    ("scons . --sconstruct=scons_multiactiontask_SConstruct", tutorial_directory),
    ("scons . --sconstruct=waves_quickstart_SConstruct", tutorial_directory),
    ("scons . --sconstruct=tutorial_00_SConstruct --unconditional-build", tutorial_directory),
    ("scons tutorial_01_geometry --sconstruct=tutorial_01_geometry_SConstruct --unconditional-build", tutorial_directory),
    ("scons tutorial_matlab --sconstruct=tutorial_matlab_SConstruct", tutorial_directory),
    ("scons tutorial_02_partition_mesh --sconstruct=tutorial_02_partition_mesh_SConstruct --unconditional-build", tutorial_directory),
    ("scons tutorial_argparse_types --sconstruct=tutorial_argparse_types_SConstruct --unconditional-build", tutorial_directory),
    ("scons tutorial_03_solverprep --sconstruct=tutorial_03_solverprep_SConstruct --unconditional-build", tutorial_directory),
    ("scons tutorial_04_simulation --sconstruct=tutorial_04_simulation_SConstruct --unconditional-build", tutorial_directory),
    # TODO: Figure out how to load the sierra module without breaking the CI tests. Change ``scons abaqus`` to ``scons .``
    # https://re-git.lanl.gov/aea/python-projects/waves/-/issues/515
    ("scons abaqus --unconditional-build", tutorial_directory / "tutorial_cubit"),
    ("scons tutorial_escape_sequences --sconstruct=tutorial_escape_sequences_SConstruct --solve-cpus=1 --unconditional-build", tutorial_directory),
    ("scons tutorial_builder_post_actions --sconstruct=tutorial_builder_post_actions_SConstruct --unconditional-build", tutorial_directory),
    # TODO: Figure out how to authenticate the institutional account without expanding the user credential exposure to
    # AEA Gitlab group members. Until then, the SSH remote execution can't be integration/regression tested.
    #("scons tutorial_remote_execution --sconstruct=tutorial_remote_execution_SConstruct --unconditional-build", tutorial_directory),
    ("scons tutorial_sbatch --sconstruct=tutorial_sbatch_SConstruct --unconditional-build", tutorial_directory),
    ("scons tutorial_05_parameter_substitution --sconstruct=tutorial_05_parameter_substitution_SConstruct --unconditional-build", tutorial_directory),
    ("scons tutorial_06_include_files --sconstruct=tutorial_06_include_files_SConstruct --unconditional-build", tutorial_directory),
    ("scons tutorial_07_cartesian_product --sconstruct=tutorial_07_cartesian_product_SConstruct --jobs=4 --unconditional-build", tutorial_directory),
    ("scons tutorial_07_latin_hypercube --sconstruct=tutorial_07_latin_hypercube_SConstruct --jobs=4 --unconditional-build", tutorial_directory),
    ("scons tutorial_07_sobol_sequence --sconstruct=tutorial_07_sobol_sequence_SConstruct --jobs=4 --unconditional-build", tutorial_directory),
    ("scons tutorial_08_data_extraction --sconstruct=tutorial_08_data_extraction_SConstruct --jobs=4 --unconditional-build", tutorial_directory),
    ("scons tutorial_09_post_processing --sconstruct=tutorial_09_post_processing_SConstruct --jobs=4 --unconditional-build", tutorial_directory),
    ("scons tutorial_correlation_coefficients --sconstruct=tutorial_correlation_coefficients_SConstruct --jobs=4 --unconditional-build", tutorial_directory),
    ("scons datacheck --sconstruct=tutorial_10_regression_testing_SConstruct --jobs=4 --unconditional-build", tutorial_directory),
    ("scons tutorial_11_archival --sconstruct=tutorial_11_archival_SConstruct --jobs=4 --unconditional-build", tutorial_directory),
    ("scons tutorial_task_reuse --sconstruct=tutorial_task_reuse_SConstruct --jobs=4 --unconditional-build", tutorial_directory),
    ("scons tutorial_mesh_convergence --sconstruct=tutorial_mesh_convergence_SConstruct --jobs=4 --unconditional-build", tutorial_directory),
])
def test_run_tutorial(command, directory):
    """Run the tutorial configuration files as system tests.

    Executes with a ``--build-dir`` temporary directory that is cleaned up after each test execution. The
    ``--build-dir`` command line option must exist for every tutorial configuration.

    :param str command: the full command string for the system test
    :param pathlib.Path directory: the working directory where the command should be executed
    """
    with tempfile.TemporaryDirectory() as temp_directory:
        command = command + f" --build-dir {temp_directory}"
        command = command.split(" ")
        result = subprocess.check_output(command, env=env, cwd=directory).decode('utf-8')
