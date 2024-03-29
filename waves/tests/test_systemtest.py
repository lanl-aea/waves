import os
import string
import pathlib
import tempfile
import subprocess
from importlib.metadata import version, PackageNotFoundError

import pytest

from waves import _settings


tutorial_directory = _settings._tutorials_directory
env = os.environ.copy()
waves_command = "waves"
odb_extract_command = "odb_extract"

# If executing in repository, add package to PYTHONPATH
try:
    version("waves")
    installed = True
except PackageNotFoundError:
    installed = False

if not installed:
    waves_command = "python -m waves._main"
    odb_extract_command = "python -m waves._abaqus.odb_extract"
    package_parent_path = _settings._project_root_abspath.parent
    key = "PYTHONPATH"
    if key in env:
        env[key] = f"{package_parent_path}:{env[key]}"
    else:
        env[key] = f"{package_parent_path}"

fetch_tutorials = string.Template("${waves_command} fetch tutorials --destination ${temp_directory}")
system_tests = [
    # CLI sign-of-life and help/usage
    ([f"{waves_command} --help"], "."),
    ([f"{waves_command} docs --help"], "."),
    ([f"{waves_command} fetch --help"], "."),
    ([f"{waves_command} visualize --help"], "."),
    ([f"{waves_command} build --help"], "."),
    ([f"{waves_command} cartesian_product --help"], "."),
    ([f"{waves_command} custom_study --help"], "."),
    ([f"{waves_command} latin_hypercube --help"], "."),
    ([f"{waves_command} sobol_sequence --help"], "."),
    ([f"{odb_extract_command} --help"], "."),
    # Tutorials
    ([string.Template("${waves_command} fetch tutorials/scons_quickstart --destination ${temp_directory}"), "scons rectangle --keep-going"], "."),
    ([string.Template("${waves_command} fetch tutorials/multi_action_task --destination ${temp_directory}"), "scons rectangle --keep-going"], "."),
    ([string.Template("${waves_command} fetch tutorials/waves_quickstart --destination ${temp_directory}"), "scons rectangle --keep-going"], "."),
    ([fetch_tutorials, "scons . --sconstruct=tutorial_00_SConstruct --unconditional-build --print-build-failures"], "."),
    ([fetch_tutorials, "scons tutorial_01_geometry --sconstruct=tutorial_01_geometry_SConstruct --unconditional-build --print-build-failures"], "."),
    ([fetch_tutorials, "scons tutorial_matlab --sconstruct=tutorial_matlab_SConstruct"], "."),
    ([fetch_tutorials, "scons tutorial_02_partition_mesh --sconstruct=tutorial_02_partition_mesh_SConstruct --unconditional-build --print-build-failures"], "."),
    ([fetch_tutorials, "scons tutorial_argparse_types --sconstruct=tutorial_argparse_types_SConstruct --unconditional-build --print-build-failures"], "."),
    ([fetch_tutorials, "scons tutorial_03_solverprep --sconstruct=tutorial_03_solverprep_SConstruct --unconditional-build --print-build-failures"], "."),
    ([fetch_tutorials, "scons tutorial_04_simulation --sconstruct=tutorial_04_simulation_SConstruct --unconditional-build --print-build-failures"], "."),
    ([string.Template("${waves_command} fetch tutorials/tutorial_cubit --destination ${temp_directory}"), "scons . --unconditional-build --print-build-failures"], "."),
    ([string.Template("${waves_command} fetch tutorials/tutorial_quinoa --destination ${temp_directory}"), "scons quinoa-local --unconditional-build --print-build-failures"], "."),
    ([fetch_tutorials, "scons tutorial_escape_sequences --sconstruct=tutorial_escape_sequences_SConstruct --solve-cpus=1 --unconditional-build --print-build-failures"], "."),
    ([fetch_tutorials, "scons tutorial_builder_post_actions --sconstruct=tutorial_builder_post_actions_SConstruct --unconditional-build --print-build-failures"], "."),
    # TODO: Figure out how to authenticate the institutional account without expanding the user credential exposure to
    # AEA Gitlab group members. Until then, the SSH remote execution can't be integration/regression tested.
    #([fetch_tutorials, "scons tutorial_remote_execution --sconstruct=tutorial_remote_execution_SConstruct --unconditional-build --print-build-failures"], "."),
    ([fetch_tutorials, "scons tutorial_sbatch --sconstruct=tutorial_sbatch_SConstruct --unconditional-build --print-build-failures"], "."),
    ([fetch_tutorials, "scons tutorial_05_parameter_substitution --sconstruct=tutorial_05_parameter_substitution_SConstruct --unconditional-build --print-build-failures"], "."),
    ([fetch_tutorials, "scons tutorial_06_include_files --sconstruct=tutorial_06_include_files_SConstruct --unconditional-build --print-build-failures"], "."),
    ([fetch_tutorials, "scons tutorial_07_cartesian_product --sconstruct=tutorial_07_cartesian_product_SConstruct --jobs=4 --unconditional-build --print-build-failures"], "."),
    ([fetch_tutorials, "scons tutorial_07_latin_hypercube --sconstruct=tutorial_07_latin_hypercube_SConstruct --jobs=4 --unconditional-build --print-build-failures"], "."),
    ([fetch_tutorials, "scons tutorial_07_sobol_sequence --sconstruct=tutorial_07_sobol_sequence_SConstruct --jobs=4 --unconditional-build --print-build-failures"], "."),
    ([fetch_tutorials, "scons tutorial_08_data_extraction --sconstruct=tutorial_08_data_extraction_SConstruct --jobs=4 --unconditional-build --print-build-failures"], "."),
    ([fetch_tutorials, "scons tutorial_09_post_processing --sconstruct=tutorial_09_post_processing_SConstruct --jobs=4 --unconditional-build --print-build-failures"], "."),
    ([fetch_tutorials, "scons unit_testing --sconstruct=tutorial_10_unit_testing_SConstruct --unconditional-build --print-build-failures"], "."),
    ([fetch_tutorials, "scons tutorial_sensitivity_study --sconstruct=tutorial_sensitivity_study_SConstruct --jobs=4 --unconditional-build --print-build-failures"], "."),
    ([fetch_tutorials, "scons datacheck --sconstruct=tutorial_11_regression_testing_SConstruct --jobs=4 --unconditional-build --print-build-failures"], "."),
    ([fetch_tutorials, "scons tutorial_12_archival --sconstruct=tutorial_12_archival_SConstruct --jobs=4 --unconditional-build --print-build-failures"], "."),
    ([fetch_tutorials, "scons tutorial_task_reuse --sconstruct=tutorial_task_reuse_SConstruct --jobs=4 --unconditional-build --print-build-failures"], "."),
    ([fetch_tutorials, "scons tutorial_mesh_convergence --sconstruct=tutorial_mesh_convergence_SConstruct --jobs=4 --unconditional-build --print-build-failures"], "."),
    ([fetch_tutorials, f"{waves_command} build tutorial_extend_study --max-iterations=4 --sconstruct=tutorial_extend_study_SConstruct --jobs=4"], "."),
]
if installed:
    system_tests.append(
        # The HTML docs path doesn't exist in the repository. Can only system test from an installed package.
        ([fetch_tutorials, f"{waves_command} docs --print-local-path"], "."),
    )


@pytest.mark.systemtest
@pytest.mark.parametrize("commands, directory", system_tests)
def test_run_tutorial(commands: list[str], directory: str) -> None:
    """Fetch and run the tutorial configuration file(s) as system tests in a temporary directory

    :param str command: the full command string for the system test
    :param pathlib.Path directory: the directory relative to the tutorials directory where the command should be
        executed
    """
    with tempfile.TemporaryDirectory() as temp_directory:
        for command in commands:
            run_directory = pathlib.Path(temp_directory) / directory
            if isinstance(command, string.Template):
                command = command.substitute({"temp_directory": temp_directory, "waves_command": waves_command})
            command = command.split(" ")
            subprocess.check_output(command, env=env, cwd=run_directory).decode("utf-8")


@pytest.mark.systemtest
def test_modsim_template() -> None:
    """Fetch and run the modsim template as a system test in a temporary directory"""
    with tempfile.TemporaryDirectory() as temp_directory:
        command = f"{waves_command} fetch modsim_template --destination {temp_directory}"
        command = command.split(" ")
        subprocess.check_output(command, env=env, cwd=temp_directory).decode("utf-8")

        command = "scons . --jobs=4"
        command = command.split(" ")
        subprocess.check_output(command, env=env, cwd=temp_directory).decode("utf-8")

        output_file = pathlib.Path(temp_directory) / "nominal.svg"
        command = f"{waves_command} visualize nominal --output-file {output_file}"
        command = command.split(" ")
        subprocess.check_output(command, env=env, cwd=temp_directory).decode("utf-8")
