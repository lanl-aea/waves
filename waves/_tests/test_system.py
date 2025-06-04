"""System test wrapper for executing shell commands with pytest results reporting

Test are constructed as a list of strings or string templates to run as shell commands. Success is defined as a shell 0
return code.

All tests should be marked ``pytest.mark.systemtest`` (handled in the test function markers).

All tests that require a third-party software unavailable on conda-forge should be marked as
``pytest.mark.require_third_party``.

All tests should use string template substitution instead of f-strings, if possible. See :meth:`test_system` for
available substitutions.
"""

import os
import re
import sys
import shlex
import shutil
import string
import typing
import inspect
import pathlib
import tempfile
import subprocess
from importlib.metadata import version, PackageNotFoundError

import pytest

from waves import _settings
from waves import _utilities
from waves._tests.common import platform_check


testing_windows, root_fs, testing_macos = platform_check()
# TODO: Fix HPC CI system tests that run TeXLive
# https://re-git.lanl.gov/aea/python-projects/waves/-/issues/891
testing_hpc = shutil.which("sbatch") is not None
python_313_or_above = sys.version_info >= (3, 13)

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
    pytest.param([string.Template("${waves_command} --help")], None, marks=[pytest.mark.cli]),
    pytest.param([string.Template("${waves_command} docs --help")], None, marks=[pytest.mark.cli]),
    pytest.param([string.Template("${waves_command} fetch --help")], None, marks=[pytest.mark.cli]),
    pytest.param([string.Template("${waves_command} fetch --print-available")], None, marks=[pytest.mark.cli]),
    pytest.param([string.Template("${waves_command} visualize --help")], None, marks=[pytest.mark.cli]),
    pytest.param([string.Template("${waves_command} build --help")], None, marks=[pytest.mark.cli]),
    pytest.param([string.Template("${waves_command} cartesian_product --help")], None, marks=[pytest.mark.cli]),
    pytest.param([string.Template("${waves_command} custom_study --help")], None, marks=[pytest.mark.cli]),
    pytest.param([string.Template("${waves_command} latin_hypercube --help")], None, marks=[pytest.mark.cli]),
    pytest.param([string.Template("${waves_command} sobol_sequence --help")], None, marks=[pytest.mark.cli]),
    pytest.param([string.Template("${waves_command} one_at_a_time --help")], None, marks=[pytest.mark.cli]),
    pytest.param([string.Template("${waves_command} print_study --help")], None, marks=[pytest.mark.cli]),
    pytest.param([string.Template("${waves_command} qoi --help")], None, marks=[pytest.mark.cli]),
    pytest.param([string.Template("${waves_command} qoi accept --help")], None, marks=[pytest.mark.cli]),
    pytest.param([string.Template("${waves_command} qoi diff --help")], None, marks=[pytest.mark.cli]),
    pytest.param([string.Template("${waves_command} qoi check --help")], None, marks=[pytest.mark.cli]),
    pytest.param([string.Template("${waves_command} qoi aggregate --help")], None, marks=[pytest.mark.cli]),
    pytest.param([string.Template("${waves_command} qoi report --help")], None, marks=[pytest.mark.cli]),
    pytest.param([string.Template("${waves_command} qoi archive --help")], None, marks=[pytest.mark.cli]),
    pytest.param([string.Template("${waves_command} qoi plot-archive --help")], None, marks=[pytest.mark.cli]),
    pytest.param([string.Template("${odb_extract_command} --help")], None, marks=[pytest.mark.cli]),
    pytest.param(
        [string.Template("${waves_command} docs --print-local-path")],
        None,
        marks=[
            pytest.mark.cli,
            pytest.mark.skipif(not installed, reason="The HTML docs path only exists in the as-installed package"),
        ],
    ),
    # Real fetch operations and file I/O
    ([fetch_template], "tutorials"),
    pytest.param(
        [
            fetch_template,
            "scons -h",
            string.Template("${waves_command} visualize rectangle_compression-nominal --output-file nominal.png"),
        ],
        "modsim_template",
        marks=[pytest.mark.scons],
        id="modsim_template_visualize_operations",
    ),
    pytest.param(
        [
            fetch_template,
            string.Template("scons html ${unconditional_build} --jobs=4 ${abaqus_command}"),
        ],
        "modsim_template",
        marks=[
            pytest.mark.scons,
            pytest.mark.sphinx,
            pytest.mark.skipif(testing_windows, reason="Windows handles symlinks in repository poorly"),
            pytest.mark.skip(reason="Fragile system test is a regular cause of false negatives"),
        ],
        id="modsim_template_scons_html",
    ),
    pytest.param(
        [
            fetch_template,
            string.Template("scons html ${unconditional_build} --jobs=4 ${abaqus_command}"),
        ],
        "modsim_template_2",
        marks=[
            pytest.mark.scons,
            pytest.mark.sphinx,
            pytest.mark.skipif(testing_windows, reason="Windows handles symlinks in repository poorly"),
            pytest.mark.skip(reason="Fragile system test is a regular cause of false negatives"),
        ],
        id="modsim_template_2_scons_html",
    ),
    pytest.param(
        [fetch_template, "scons . --jobs=4"],
        "tutorials/tutorial_ParameterStudySConscript",
        marks=[pytest.mark.scons],
    ),
    pytest.param(
        [fetch_template, "scons . --jobs=4"],
        "tutorials/tutorial_ParameterStudyTask",
        marks=[pytest.mark.scons],
    ),
    pytest.param(
        [fetch_template, "scons . --jobs=4"],
        "tutorials/tutorial_ParameterStudyWrite",
        marks=[pytest.mark.scons],
    ),
    pytest.param(
        [fetch_template, "scons ."],
        "tutorials/tutorial_writing_builders",
        marks=[pytest.mark.scons],
    ),
    pytest.param(
        [fetch_template, string.Template("scons . --waves-command='${waves_command}'")],
        "tutorials/tutorial_qoi",
        marks=[pytest.mark.scons],
        id="tutorial_qoi",
    ),
]

require_third_party_system_tests = [
    # Tutorials
    pytest.param(
        [fetch_template, string.Template("scons rectangle ${unconditional_build} ${abaqus_command}")],
        "tutorials/scons_quickstart",
        marks=[pytest.mark.require_third_party, pytest.mark.scons, pytest.mark.abaqus],
    ),
    pytest.param(
        [fetch_template, string.Template("scons rectangle ${unconditional_build} ${abaqus_command}")],
        "tutorials/multi_action_task",
        marks=[
            pytest.mark.require_third_party,
            pytest.mark.scons,
            pytest.mark.abaqus,
            pytest.mark.skipif(testing_windows, reason="Windows handles symlinks in repository poorly"),
        ],
    ),
    pytest.param(
        [
            fetch_template,
            string.Template("scons nominal mesh_convergence ${unconditional_build} ${abaqus_command}"),
            string.Template("${waves_command} print_study build/parameter_studies/mesh_convergence.h5"),
        ],
        "tutorials/waves_quickstart",
        marks=[pytest.mark.require_third_party, pytest.mark.scons, pytest.mark.abaqus],
    ),
    pytest.param(
        [
            fetch_template,
            string.Template("scons nominal mesh_convergence ${unconditional_build}"),
            string.Template("${waves_command} print_study build/parameter_studies/mesh_convergence.h5"),
        ],
        "tutorials/tutorial_gmsh",
        marks=[pytest.mark.require_third_party, pytest.mark.scons, pytest.mark.gmsh, pytest.mark.calculix],
    ),
    pytest.param(
        [
            fetch_template,
            string.Template("scons submit_beam_cae ${unconditional_build} ${abaqus_command}"),
        ],
        "tutorials/tutorial_abaqus_cae",
        marks=[pytest.mark.require_third_party, pytest.mark.scons, pytest.mark.abaqus],
    ),
    pytest.param(
        [
            fetch_template,
            string.Template(
                "scons . --sconstruct=tutorial_00_SConstruct ${unconditional_build} --print-build-failures ${abaqus_command}"  # noqa: E501
            ),
        ],
        "--tutorial 0",
        marks=[pytest.mark.require_third_party, pytest.mark.scons],
    ),
    pytest.param(
        [
            fetch_template,
            string.Template(
                "scons tutorial_01_geometry --sconstruct=tutorial_01_geometry_SConstruct ${unconditional_build} --print-build-failures ${abaqus_command}"  # noqa: E501
            ),
        ],
        "--tutorial 1",
        marks=[pytest.mark.require_third_party, pytest.mark.scons, pytest.mark.abaqus],
    ),
    pytest.param(
        [fetch_template, "scons tutorial_matlab --sconstruct=tutorial_matlab_SConstruct"],
        "tutorials",
        marks=[
            pytest.mark.require_third_party,
            pytest.mark.scons,
            pytest.mark.matlab,
            pytest.mark.skip("Too few licenses to reliably pass"),
        ],
    ),
    pytest.param(
        [
            fetch_template,
            string.Template(
                "scons tutorial_02_partition_mesh --sconstruct=tutorial_02_partition_mesh_SConstruct ${unconditional_build} --print-build-failures ${abaqus_command}"  # noqa: E501
            ),
        ],
        "--tutorial 2",
        marks=[pytest.mark.require_third_party, pytest.mark.scons, pytest.mark.abaqus],
    ),
    pytest.param(
        [
            fetch_template,
            string.Template(
                "scons tutorial_argparse_types --sconstruct=tutorial_argparse_types_SConstruct ${unconditional_build} --print-build-failures ${abaqus_command}"  # noqa: E501
            ),
        ],
        "tutorials",
        marks=[pytest.mark.require_third_party, pytest.mark.scons, pytest.mark.abaqus],
    ),
    pytest.param(
        [
            fetch_template,
            string.Template(
                "scons tutorial_03_solverprep --sconstruct=tutorial_03_solverprep_SConstruct ${unconditional_build} --print-build-failures ${abaqus_command}"  # noqa: E501
            ),
        ],
        "--tutorial 3",
        marks=[pytest.mark.require_third_party, pytest.mark.scons, pytest.mark.abaqus],
    ),
    pytest.param(
        [
            fetch_template,
            string.Template(
                "scons tutorial_04_simulation --sconstruct=tutorial_04_simulation_SConstruct ${unconditional_build} --print-build-failures ${abaqus_command}"  # noqa: E501
            ),
        ],
        "--tutorial 4",
        marks=[pytest.mark.require_third_party, pytest.mark.scons, pytest.mark.abaqus],
    ),
    pytest.param(
        [
            fetch_template,
            string.Template(
                "scons abaqus ${unconditional_build} --print-build-failures ${abaqus_command} ${cubit_command}"  # noqa: E501
            ),
        ],
        "tutorials/tutorial_cubit",
        marks=[
            pytest.mark.require_third_party,
            pytest.mark.scons,
            pytest.mark.abaqus,
            pytest.mark.cubit,
            pytest.mark.skipif(
                testing_macos or testing_windows, reason="Cannot reliably skip '.' target on CI servers missing Cubit"
            ),
        ],
    ),
    pytest.param(
        [
            fetch_template,
            string.Template(
                "scons fierro ${unconditional_build} --print-build-failures ${abaqus_command} ${cubit_command}"  # noqa: E501
            ),
        ],
        "tutorials/tutorial_cubit",
        marks=[
            pytest.mark.require_third_party,
            pytest.mark.scons,
            pytest.mark.cubit,
            pytest.mark.fierro,
            pytest.mark.skipif(
                testing_macos or testing_windows, reason="Cannot reliably skip '.' target on CI servers missing Cubit"
            ),
        ],
    ),
    pytest.param(
        [
            fetch_template,
            string.Template(
                "scons sierra ${unconditional_build} --print-build-failures ${abaqus_command} ${cubit_command}"  # noqa: E501
            ),
        ],
        "tutorials/tutorial_cubit",
        marks=[
            pytest.mark.require_third_party,
            pytest.mark.scons,
            pytest.mark.cubit,
            pytest.mark.sierra,
            # Remove sierra python version skip when ci server has a sierra vesrion compatible with python 3.13
            # https://re-git.lanl.gov/aea/python-projects/waves/-/issues/844
            pytest.mark.skipif(
                python_313_or_above, reason="Sierra verison on CI server is incompatible with Python 3.13"
            ),
            pytest.mark.skipif(
                testing_macos or testing_windows, reason="Cannot reliably skip '.' target on CI servers missing Cubit"
            ),
        ],
    ),
    pytest.param(
        [
            fetch_template,
            string.Template(
                "scons abaqus ${unconditional_build} --print-build-failures ${abaqus_command} ${cubit_command}"  # noqa: E501
            ),
        ],
        "tutorials/tutorial_cubit_alternate",
        marks=[
            pytest.mark.require_third_party,
            pytest.mark.scons,
            pytest.mark.abaqus,
            pytest.mark.cubit,
            pytest.mark.skipif(
                testing_macos or testing_windows, reason="Cannot reliably skip '.' target on CI servers missing Cubit"
            ),
            # TODO: Remove this skip when Cubit python interpretter search is fixed
            # https://re-git.lanl.gov/aea/python-projects/waves/-/issues/917
            pytest.mark.skipif(testing_hpc, reason="Cubit Python interpretter search fails on HPC"),
        ],
    ),
    pytest.param(
        [
            fetch_template,
            string.Template(
                "scons fierro ${unconditional_build} --print-build-failures ${abaqus_command} ${cubit_command}"  # noqa: E501
            ),
        ],
        "tutorials/tutorial_cubit_alternate",
        marks=[
            pytest.mark.require_third_party,
            pytest.mark.scons,
            pytest.mark.cubit,
            pytest.mark.fierro,
            pytest.mark.skipif(
                testing_macos or testing_windows, reason="Cannot reliably skip '.' target on CI servers missing Cubit"
            ),
            # TODO: Remove this skip when Cubit python interpretter search is fixed
            # https://re-git.lanl.gov/aea/python-projects/waves/-/issues/917
            pytest.mark.skipif(testing_hpc, reason="Cubit Python interpretter search fails on HPC"),
        ],
    ),
    pytest.param(
        [
            fetch_template,
            string.Template(
                "scons sierra ${unconditional_build} --print-build-failures ${abaqus_command} ${cubit_command}"  # noqa: E501
            ),
        ],
        "tutorials/tutorial_cubit_alternate",
        marks=[
            pytest.mark.require_third_party,
            pytest.mark.scons,
            pytest.mark.cubit,
            pytest.mark.sierra,
            # Remove sierra python version skip when ci server has a sierra vesrion compatible with python 3.13
            # https://re-git.lanl.gov/aea/python-projects/waves/-/issues/844
            pytest.mark.skipif(
                python_313_or_above, reason="Sierra verison on CI server is incompatible with Python 3.13"
            ),
            pytest.mark.skipif(
                testing_macos or testing_windows, reason="Cannot reliably skip '.' target on CI servers missing Cubit"
            ),
            # TODO: Remove this skip when Cubit python interpretter search is fixed
            # https://re-git.lanl.gov/aea/python-projects/waves/-/issues/917
            pytest.mark.skipif(testing_hpc, reason="Cubit Python interpretter search fails on HPC"),
        ],
    ),
    pytest.param(
        [
            fetch_template,
            string.Template(
                "scons quinoa-local ${unconditional_build} --print-build-failures ${cubit_command}"  # noqa: E501
            ),
        ],
        "tutorials/tutorial_quinoa",
        marks=[pytest.mark.require_third_party, pytest.mark.scons, pytest.mark.cubit, pytest.mark.quinoa],
    ),
    pytest.param(
        [
            fetch_template,
            string.Template(
                "scons tutorial_escape_sequences --sconstruct=tutorial_escape_sequences_SConstruct --solve-cpus=1 ${unconditional_build} --print-build-failures ${abaqus_command}"  # noqa: E501
            ),
        ],
        "tutorials",
        marks=[pytest.mark.require_third_party, pytest.mark.scons, pytest.mark.abaqus],
    ),
    # TODO: Figure out how to authenticate the institutional account without expanding the user credential exposure to
    # AEA Gitlab group members. Until then, the SSH remote execution can't be integration/regression tested.
    pytest.param(
        [
            fetch_template,
            string.Template(
                "scons tutorial_remote_execution --sconstruct=tutorial_remote_execution_SConstruct ${unconditional_build} --print-build-failures ${abaqus_command}"  # noqa: E501
            ),
        ],
        "tutorials",
        marks=[
            pytest.mark.require_third_party,
            pytest.mark.scons,
            pytest.mark.abaqus,
            pytest.mark.skip("Can't reliably authenticate to the remote server"),
        ],
    ),
    pytest.param(
        [
            fetch_template,
            string.Template(
                "scons tutorial_sbatch --sconstruct=tutorial_sbatch_SConstruct ${unconditional_build} --print-build-failures ${abaqus_command}"  # noqa: E501
            ),
        ],
        "tutorials",
        marks=[pytest.mark.require_third_party, pytest.mark.scons, pytest.mark.abaqus],
    ),
    pytest.param(
        [
            fetch_template,
            string.Template(
                "scons tutorial_05_parameter_substitution --sconstruct=tutorial_05_parameter_substitution_SConstruct ${unconditional_build} --print-build-failures ${abaqus_command}"  # noqa: E501
            ),
        ],
        "--tutorial 5",
        marks=[pytest.mark.require_third_party, pytest.mark.scons, pytest.mark.abaqus],
    ),
    pytest.param(
        [
            fetch_template,
            string.Template(
                "scons tutorial_06_include_files --sconstruct=tutorial_06_include_files_SConstruct ${unconditional_build} --print-build-failures ${abaqus_command}"  # noqa: E501
            ),
        ],
        "--tutorial 6",
        marks=[pytest.mark.require_third_party, pytest.mark.scons, pytest.mark.abaqus],
    ),
    pytest.param(
        [
            fetch_template,
            string.Template(
                "scons tutorial_07_cartesian_product --sconstruct=tutorial_07_cartesian_product_SConstruct --jobs=4 ${unconditional_build} --print-build-failures ${abaqus_command}"  # noqa: E501
            ),
        ],
        "--tutorial 7",
        marks=[pytest.mark.require_third_party, pytest.mark.scons, pytest.mark.abaqus],
        id="tutorial_07_cartesian_product",
    ),
    pytest.param(
        [
            fetch_template,
            string.Template(
                "scons tutorial_07_latin_hypercube --sconstruct=tutorial_07_latin_hypercube_SConstruct --jobs=4 ${unconditional_build} --print-build-failures ${abaqus_command}"  # noqa: E501
            ),
        ],
        "tutorials",
        marks=[pytest.mark.require_third_party, pytest.mark.scons, pytest.mark.abaqus],
    ),
    pytest.param(
        [
            fetch_template,
            string.Template(
                "scons tutorial_07_sobol_sequence --sconstruct=tutorial_07_sobol_sequence_SConstruct --jobs=4 ${unconditional_build} --print-build-failures ${abaqus_command}"  # noqa: E501
            ),
        ],
        "tutorials",
        marks=[pytest.mark.require_third_party, pytest.mark.scons, pytest.mark.abaqus],
    ),
    pytest.param(
        [
            fetch_template,
            string.Template(
                "scons tutorial_07_one_at_a_time --sconstruct=tutorial_07_one_at_a_time_SConstruct --jobs=3 ${unconditional_build} --print-build-failures ${abaqus_command}"  # noqa: E501
            ),
        ],
        "tutorials one at a time",
        marks=[pytest.mark.require_third_party, pytest.mark.scons, pytest.mark.abaqus],
    ),
    pytest.param(
        [
            fetch_template,
            string.Template(
                "scons tutorial_08_data_extraction --sconstruct=tutorial_08_data_extraction_SConstruct --jobs=4 ${unconditional_build} --print-build-failures ${abaqus_command}"  # noqa: E501
            ),
        ],
        "--tutorial 8",
        marks=[pytest.mark.require_third_party, pytest.mark.scons, pytest.mark.abaqus],
    ),
    pytest.param(
        [
            fetch_template,
            string.Template(
                "scons tutorial_09_post_processing --sconstruct=tutorial_09_post_processing_SConstruct --jobs=4 ${unconditional_build} --print-build-failures ${abaqus_command}"  # noqa: E501
            ),
        ],
        "--tutorial 9",
        marks=[pytest.mark.require_third_party, pytest.mark.scons, pytest.mark.abaqus],
    ),
    pytest.param(
        [
            fetch_template,
            string.Template(
                "scons unit_testing --sconstruct=tutorial_10_unit_testing_SConstruct ${unconditional_build} --print-build-failures ${abaqus_command}"  # noqa: E501
            ),
        ],
        "--tutorial 10",
        marks=[pytest.mark.require_third_party, pytest.mark.scons, pytest.mark.abaqus],
    ),
    pytest.param(
        [
            fetch_template,
            string.Template(
                "scons tutorial_sensitivity_study --sconstruct=tutorial_sensitivity_study_SConstruct --jobs=4 ${unconditional_build} --print-build-failures ${abaqus_command}"  # noqa: E501
            ),
        ],
        "tutorials",
        marks=[pytest.mark.require_third_party, pytest.mark.scons, pytest.mark.abaqus],
    ),
    pytest.param(
        [
            fetch_template,
            string.Template(
                "scons datacheck --sconstruct=tutorial_11_regression_testing_SConstruct --jobs=4 ${unconditional_build} --print-build-failures ${abaqus_command}"  # noqa: E501
            ),
        ],
        "--tutorial 11",
        marks=[pytest.mark.require_third_party, pytest.mark.scons, pytest.mark.abaqus],
    ),
    pytest.param(
        [
            fetch_template,
            string.Template(
                "scons tutorial_12_archival --sconstruct=tutorial_12_archival_SConstruct --jobs=4 ${unconditional_build} --print-build-failures ${abaqus_command}"  # noqa: E501
            ),
        ],
        "--tutorial 12",
        marks=[pytest.mark.require_third_party, pytest.mark.scons, pytest.mark.abaqus],
    ),
    pytest.param(
        [
            fetch_template,
            string.Template(
                "scons tutorial_abaqus_pseudo_builder --sconstruct=tutorial_abaqus_pseudo_builder_SConstruct --jobs=4 ${unconditional_build} --print-build-failures ${abaqus_command}"  # noqa: E501
            ),
        ],
        "tutorials",
        marks=[pytest.mark.require_third_party, pytest.mark.scons, pytest.mark.abaqus],
    ),
    pytest.param(
        [
            fetch_template,
            string.Template(
                "scons tutorial_task_reuse --sconstruct=tutorial_task_reuse_SConstruct --jobs=4 ${unconditional_build} --print-build-failures ${abaqus_command}"  # noqa: E501
            ),
        ],
        "tutorials",
        marks=[pytest.mark.require_third_party, pytest.mark.scons, pytest.mark.abaqus],
    ),
    pytest.param(
        [
            fetch_template,
            string.Template(
                "scons tutorial_mesh_convergence --sconstruct=tutorial_mesh_convergence_SConstruct --jobs=4 ${unconditional_build} --print-build-failures ${abaqus_command}"  # noqa: E501
            ),
        ],
        "tutorials",
        marks=[pytest.mark.require_third_party, pytest.mark.scons, pytest.mark.abaqus],
    ),
    pytest.param(
        [
            fetch_template,
            string.Template(
                "${waves_command} build tutorial_extend_study --max-iterations=4 --sconstruct=tutorial_extend_study_SConstruct --jobs=4 ${abaqus_command}"  # noqa: E501
            ),
        ],
        "tutorials",
        marks=[pytest.mark.require_third_party, pytest.mark.scons, pytest.mark.abaqus],
    ),
    pytest.param(
        [
            fetch_template,
            string.Template(
                "scons tutorial_part_image --sconstruct=tutorial_part_image_SConstruct --jobs=4 ${unconditional_build} --print-build-failures ${abaqus_command}"  # noqa: E501
            ),
        ],
        "tutorials",
        marks=[pytest.mark.require_third_party, pytest.mark.scons, pytest.mark.abaqus],
    ),
    # ModSim templates
    pytest.param(
        [
            fetch_template,
            # TODO: return to testing ``.`` all targets if/when system tests are less fragile
            string.Template(
                "scons --jobs=4 ${unconditional_build} --print-build-failures ${abaqus_command}"
                " datacheck"
                " rectangle_compression-nominal-datacheck"
                " rectangle_compression-nominal-images"
                " rectangle_compression-nominal"
                " rectangle_compression-nominal-archive"
                " rectangle_compression-mesh_convergence-datacheck"
                " rectangle_compression-mesh_convergence-images"
                " rectangle_compression-mesh_convergence"
                " rectangle_compression-mesh_convergence-archive"
                " unit_testing"
            ),
            string.Template(
                "${waves_command} visualize rectangle_compression-nominal --output-file nominal.png ${abaqus_command}"  # noqa: E501
            ),
            string.Template(
                "${waves_command} print_study build/rectangle_compression-mesh_convergence/mesh_convergence.h5"
            ),
        ],
        "modsim_template",
        marks=[
            pytest.mark.require_third_party,
            pytest.mark.scons,
            pytest.mark.sphinx,
            pytest.mark.abaqus,
            pytest.mark.skipif(
                testing_macos or testing_windows, reason="Cannot reliably skip '.' target on CI servers missing Abaqus"
            ),
            pytest.mark.skipif(testing_windows, reason="Windows handles symlinks in repository poorly"),
            # TODO: Fix HPC CI system tests that run TeXLive
            # https://re-git.lanl.gov/aea/python-projects/waves/-/issues/891
            pytest.mark.skipif(testing_hpc, reason="HPC CI server fails TeXLive PDF builds"),
        ],
        id="modsim_template_full",
    ),
    pytest.param(
        [
            fetch_template,
            # TODO: return to testing ``.`` all targets if/when system tests are less fragile
            string.Template(
                "scons --jobs=4 ${unconditional_build} --print-build-failures ${abaqus_command}"
                " datacheck"
                " rectangle_compression-nominal-datacheck"
                " rectangle_compression-nominal-images"
                " rectangle_compression-nominal"
                " rectangle_compression-nominal-archive"
                " rectangle_compression-mesh_convergence-datacheck"
                " rectangle_compression-mesh_convergence-images"
                " rectangle_compression-mesh_convergence"
                " rectangle_compression-mesh_convergence-archive"
                " unit_testing"
            ),
            string.Template(
                "${waves_command} visualize rectangle_compression-nominal --output-file nominal.png ${abaqus_command}"  # noqa: E501
            ),
            string.Template(
                "${waves_command} print_study build/parameter_studies/rectangle_compression-mesh_convergence.h5"
            ),
        ],
        "modsim_template_2",
        marks=[
            pytest.mark.require_third_party,
            pytest.mark.scons,
            pytest.mark.sphinx,
            pytest.mark.abaqus,
            pytest.mark.skipif(
                testing_macos or testing_windows, reason="Cannot reliably skip '.' target on CI servers missing Abaqus"
            ),
            pytest.mark.skipif(testing_windows, reason="Windows handles symlinks in repository poorly"),
            # TODO: Fix HPC CI system tests that run TeXLive
            # https://re-git.lanl.gov/aea/python-projects/waves/-/issues/891
            pytest.mark.skipif(testing_hpc, reason="HPC CI server fails TeXLive PDF builds"),
        ],
        id="modsim_template_2_full",
    ),
]


@pytest.mark.systemtest
@pytest.mark.parametrize("commands, fetch_options", system_tests + require_third_party_system_tests)
def test_system(
    system_test_directory: typing.Optional[pathlib.Path],
    keep_system_tests: bool,
    unconditional_build: bool,
    abaqus_command: typing.Optional[pathlib.Path],
    cubit_command: typing.Optional[pathlib.Path],
    request: pytest.FixtureRequest,
    commands: typing.Iterable[str],
    fetch_options: typing.Optional[str],
) -> None:
    """Run shell commands as system tests in a temporary directory.

    Test directory name is constructed from test ID string, with character replacements to create a valid Python
    identifier as a conservative estimate of a valid directory name. Failed tests persist on disk.

    Iterates on the command strings in the commands list. Performs string template substitution using keys:

    * ``waves_command``: module namespace variable selected to match installation status
    * ``odb_extract_command``: module namespace variable selected to match installation status
    * ``fetch_options``: test API variable
    * ``temp_directory``: temporary directory created one per test with ``tempfile``
    * ``unconditional_build``: pass through CLI argument string for the tutorial/system test SConstruct option of the
        same name
    * ``abaqus_command``: pass through CLI argument string for tutorial/system test SConstruct option of the same name
    * ``cubit_command``: pass through CLI argument string for tutorial/system test SConstruct option of the same name

    Accepts custom pytest CLI options to re-direct the temporary system test root directory away from ``$TMPDIR`` and
    specify third-party software executables as

    .. code-block::

       pytest --system-test-dir=/my/systemtest/output --abaqus-command /my/system/abaqus --cubit-command /my/system/cubit

    An optional ``--keep-system-tests`` flag can be added to avoid temporary directory cleanup, e.g. to keep the test
    artifacts in the ``--systemt-test-dir`` for troubleshooting.

    :param system_test_directory: custom pytest decorator defined in conftest.py
    :param keep_system_tests: custom pytest decorator defined in conftest.py
    :param unconditional_build: custom pytest decorator defined in conftest.py
    :param abaqus_command: string absolute path to Abaqus executable
    :param cubit_command: string absolute path to Cubit executable
    :param request: pytest decorator with test case meta data
    :param commands: list of command strings for the system test
    :param fetch_options: the fetch arguments for replacement in string templates
    """
    module_name = pathlib.Path(__file__).stem
    test_id = request.node.callspec.id
    test_prefix = _utilities.create_valid_identifier(test_id)
    test_prefix = f"{module_name}.{test_prefix}."

    if system_test_directory is not None:
        system_test_directory.mkdir(parents=True, exist_ok=True)

    # TODO: Move to common test utility VVV
    # Naive move to waves/_tests/common.py resulted in every test failing with FileNotFoundError.
    # Probably tempfile is handling some scope existence that works when inside the function but not when it's outside.
    kwargs = {}
    temporary_directory_inspection = inspect.getfullargspec(tempfile.TemporaryDirectory)
    temporary_directory_arguments = temporary_directory_inspection.args + temporary_directory_inspection.kwonlyargs
    if "ignore_cleanup_errors" in temporary_directory_arguments and system_test_directory is not None:
        kwargs.update({"ignore_cleanup_errors": True})
    if keep_system_tests:
        if "delete" in temporary_directory_arguments:
            kwargs.update({"delete": False})
        else:
            print(
                "``--keep-system-tests`` requested, but Python version does not support ``delete=False`` in"
                " tempfile.TemporaryDirectory. System test directories will be deleted on cleanup.",
                file=sys.stderr,
            )
    temp_directory = tempfile.TemporaryDirectory(dir=system_test_directory, prefix=test_prefix, **kwargs)
    temp_path = pathlib.Path(temp_directory.name)
    temp_path.mkdir(parents=True, exist_ok=True)
    # Move to common test utility ^^^
    template_substitution = {
        "waves_command": waves_command,
        "odb_extract_command": odb_extract_command,
        "fetch_options": fetch_options,
        "temp_directory": temp_path,
        "unconditional_build": "--unconditional-build" if unconditional_build else "",
        "abaqus_command": f"--abaqus-command={abaqus_command}" if abaqus_command is not None else "",
        "cubit_command": f"--cubit-command={cubit_command}" if cubit_command is not None else "",
    }
    try:
        for command in commands:
            if isinstance(command, string.Template):
                command = command.substitute(template_substitution)
            # TODO: Find a better way to split ``--waves-command='python -m waves._main'`` correctly for Windows
            if "--waves-command" in command:
                command_list = shlex.split(command, posix=True)
            else:
                command_list = shlex.split(command, posix=not testing_windows)
            subprocess.check_output(command_list, env=env, cwd=temp_path, text=True)
    except Exception as err:
        raise err
    else:
        if not keep_system_tests:
            temp_directory.cleanup()
