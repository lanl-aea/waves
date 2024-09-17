import os
import shlex
import string
import typing
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

fetch_template = string.Template("${waves_command} fetch ${fetch_options} --destination ${temp_directory}")
system_tests = [
    # CLI sign-of-life and help/usage
    ([string.Template("${waves_command} --help")], None),
    ([string.Template("${waves_command} docs --help")], None),
    ([string.Template("${waves_command} fetch --help")], None),
    ([string.Template("${waves_command} visualize --help")], None),
    ([string.Template("${waves_command} build --help")], None),
    ([string.Template("${waves_command} cartesian_product --help")], None),
    ([string.Template("${waves_command} custom_study --help")], None),
    ([string.Template("${waves_command} latin_hypercube --help")], None),
    ([string.Template("${waves_command} sobol_sequence --help")], None),
    ([string.Template("${odb_extract_command} --help")], None),
    # Real fetch operations (on tutorials directory)
    ([fetch_template], "tutorials"),
    # Real visualize operations (on modsim template)
    ([fetch_template, "scons -h", string.Template("${waves_command} visualize nominal --output-file nominal.png")], "modsim_template"),
]
if installed:
    system_tests.append(
        # The HTML docs path doesn't exist in the repository. Can only system test from an installed package.
        ([string.Template("${waves_command} docs --print-local-path")], None),
    )

require_third_party_tests = [
    # Tutorials
    ([fetch_template, "scons rectangle --keep-going"], "tutorials/scons_quickstart"),
    ([fetch_template, "scons rectangle --keep-going"], "tutorials/multi_action_task"),
    ([fetch_template, "scons rectangle --keep-going"], "tutorials/waves_quickstart"),
    ([fetch_template, "scons submit_beam_cae --keep-going"], "tutorials/tutorial_abaqus_cae"),
    ([fetch_template, "scons . --sconstruct=tutorial_00_SConstruct --unconditional-build --print-build-failures"], "--tutorial 0"),
    ([fetch_template, "scons tutorial_01_geometry --sconstruct=tutorial_01_geometry_SConstruct --unconditional-build --print-build-failures"], "--tutorial 1"),
    pytest.param(
        [fetch_template, "scons tutorial_matlab --sconstruct=tutorial_matlab_SConstruct"], "tutorials",
        marks=pytest.mark.skip("Too few licenses to reliably pass")
    ),
    ([fetch_template, "scons tutorial_02_partition_mesh --sconstruct=tutorial_02_partition_mesh_SConstruct --unconditional-build --print-build-failures"], "--tutorial 2"),
    ([fetch_template, "scons tutorial_argparse_types --sconstruct=tutorial_argparse_types_SConstruct --unconditional-build --print-build-failures"], "tutorials"),
    ([fetch_template, "scons tutorial_03_solverprep --sconstruct=tutorial_03_solverprep_SConstruct --unconditional-build --print-build-failures"], "--tutorial 3"),
    ([fetch_template, "scons tutorial_04_simulation --sconstruct=tutorial_04_simulation_SConstruct --unconditional-build --print-build-failures"], "--tutorial 4"),
    ([fetch_template, "scons . --unconditional-build --print-build-failures"], "tutorials/tutorial_cubit"),
    ([fetch_template, "scons . --unconditional-build --print-build-failures"], "tutorials/tutorial_cubit_alternate"),
    ([fetch_template, "scons quinoa-local --unconditional-build --print-build-failures"], "tutorials/tutorial_quinoa"),
    ([fetch_template, "scons tutorial_escape_sequences --sconstruct=tutorial_escape_sequences_SConstruct --solve-cpus=1 --unconditional-build --print-build-failures"], "tutorials"),
    # TODO: Figure out how to authenticate the institutional account without expanding the user credential exposure to
    # AEA Gitlab group members. Until then, the SSH remote execution can't be integration/regression tested.
    pytest.param(
        [fetch_template, "scons tutorial_remote_execution --sconstruct=tutorial_remote_execution_SConstruct --unconditional-build --print-build-failures"], "tutorials",
        marks=pytest.mark.skip("Can't reliably authenticate to the remote server")
    ),
    ([fetch_template, "scons tutorial_sbatch --sconstruct=tutorial_sbatch_SConstruct --unconditional-build --print-build-failures"], "tutorials"),
    ([fetch_template, "scons tutorial_05_parameter_substitution --sconstruct=tutorial_05_parameter_substitution_SConstruct --unconditional-build --print-build-failures"], "--tutorial 5"),
    ([fetch_template, "scons tutorial_06_include_files --sconstruct=tutorial_06_include_files_SConstruct --unconditional-build --print-build-failures"], "--tutorial 6"),
    ([fetch_template, "scons tutorial_07_cartesian_product --sconstruct=tutorial_07_cartesian_product_SConstruct --jobs=4 --unconditional-build --print-build-failures"], "--tutorial 7"),
    ([fetch_template, "scons tutorial_07_latin_hypercube --sconstruct=tutorial_07_latin_hypercube_SConstruct --jobs=4 --unconditional-build --print-build-failures"], "tutorials"),
    ([fetch_template, "scons tutorial_07_sobol_sequence --sconstruct=tutorial_07_sobol_sequence_SConstruct --jobs=4 --unconditional-build --print-build-failures"], "tutorials"),
    ([fetch_template, "scons tutorial_08_data_extraction --sconstruct=tutorial_08_data_extraction_SConstruct --jobs=4 --unconditional-build --print-build-failures"], "--tutorial 8"),
    ([fetch_template, "scons tutorial_09_post_processing --sconstruct=tutorial_09_post_processing_SConstruct --jobs=4 --unconditional-build --print-build-failures"], "--tutorial 9"),
    ([fetch_template, "scons unit_testing --sconstruct=tutorial_10_unit_testing_SConstruct --unconditional-build --print-build-failures"], "--tutorial 10"),
    ([fetch_template, "scons tutorial_sensitivity_study --sconstruct=tutorial_sensitivity_study_SConstruct --jobs=4 --unconditional-build --print-build-failures"], "tutorials"),
    ([fetch_template, "scons datacheck --sconstruct=tutorial_11_regression_testing_SConstruct --jobs=4 --unconditional-build --print-build-failures"], "--tutorial 11"),
    ([fetch_template, "scons tutorial_12_archival --sconstruct=tutorial_12_archival_SConstruct --jobs=4 --unconditional-build --print-build-failures"], "--tutorial 12"),
    ([fetch_template, "chmod +x solver.py", "scons ."], "tutorials/tutorial_writing_builders"),
    ([fetch_template, "scons tutorial_task_reuse --sconstruct=tutorial_task_reuse_SConstruct --jobs=4 --unconditional-build --print-build-failures"], "tutorials"),
    ([fetch_template, "scons tutorial_mesh_convergence --sconstruct=tutorial_mesh_convergence_SConstruct --jobs=4 --unconditional-build --print-build-failures"], "tutorials"),
    ([fetch_template, string.Template("${waves_command} build tutorial_extend_study --max-iterations=4 --sconstruct=tutorial_extend_study_SConstruct --jobs=4")], "tutorials"),
    ([fetch_template, "scons tutorial_part_image --sconstruct=tutorial_part_image_SConstruct --jobs=4 --unconditional-build --print-build-failures"], "tutorials"),
    ([fetch_template, "scons . --jobs=4"], "tutorials/tutorial_ParameterStudySConscript"),
    # ModSim templates
    ([fetch_template, "scons . --jobs=4", string.Template("${waves_command} visualize nominal --output-file nominal.png")], "modsim_template"),
    ([fetch_template, "scons . --jobs=4", string.Template("${waves_command} visualize nominal --output-file nominal.png")], "modsim_template_2")
]


@pytest.mark.systemtest
@pytest.mark.parametrize("commands, fetch_options", system_tests)
def test_system(commands: typing.Iterable[str], fetch_options: typing.Optional[str]) -> None:
    """Fetch and run the tutorial configuration file(s) as system tests in a temporary directory

    Iterates on the command strings in the commands list. Performs string template substitution using keys:

    * ``waves_command``: module namespace variable selected to match installation status
    * ``odb_extract_command``: module namespace variable selected to match installation status
    * ``fetch_options``: test API variable
    * ``temp_directory``: temporary directory created one per test with ``tempfile``

    :param commands: list of command strings for the system test
    :param fetch_options: the fetch arguments for replacement in string templates
    """
    with tempfile.TemporaryDirectory() as temp_directory:
        template_substitution = {
            "waves_command": waves_command,
            "odb_extract_command": odb_extract_command,
            "fetch_options": fetch_options,
            "temp_directory": temp_directory
        }
        for command in commands:
            if isinstance(command, string.Template):
                command = command.substitute(template_substitution)
            command = shlex.split(command)
            subprocess.check_output(command, env=env, cwd=temp_directory, text=True)


@pytest.mark.systemtest
@pytest.mark.require_third_party
@pytest.mark.parametrize("commands, fetch_options", require_third_party_tests)
def test_system_requiring_third_party_software(commands: typing.Iterable[str], fetch_options: typing.Optional[str]) -> None:
    """Pass through wrapper of :meth:`test_system` to allow variations in bulk pytest markers"""
    test_system(commands, fetch_options)
