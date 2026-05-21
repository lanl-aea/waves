"""Run the conda-recipe build against a matrix of dependencies."""

import copy
import itertools
import os
import pathlib
import string
import subprocess

import pytest

environment = os.environ.copy()
OUTPUT_FOLDER = "--output-folder ${conda_build_artifacts}" if "conda_build_artifacts" in environment else ""
repository_directory = pathlib.Path(os.path.realpath(__file__)).parent.parent

command_template = string.Template(
    "VERSION=$(python -m setuptools_scm) rattler-build build --recipe recipe-matrix --channel fierromechanics "
    "--channel conda-forge "
    "--output-dir conda-bld-${test_identifier} "
    '--variant python="${python_version}" --variant scons="${scons_version}"'
)

python_versions = ["3.10", "3.11", "3.12", "3.13", "3.14"]
scons_versions = ["4.6", "4.7", "4.8", "4.9", "4.10"]
conda_build_test_matrix = list(itertools.product(python_versions, scons_versions))
conda_build_test_matrix.remove(("3.13", "4.6"))  # SCons 4.6 not available for Python 3.13
conda_build_test_matrix.remove(("3.14", "4.6"))  # SCons 4.6 not available for Python 3.14
conda_build_test_matrix.remove(("3.14", "4.7"))  # SCons 4.7 not available for Python 3.14
conda_build_test_matrix.remove(("3.14", "4.8"))  # SCons 4.8 not available for Python 3.14


@pytest.mark.parametrize(("python_version", "scons_version"), conda_build_test_matrix)
def test_matrix(request: pytest.FixtureRequest, python_version: str, scons_version: str) -> None:
    """Run the conda-recipe build against a matrix of dependencies.

    :param request: pytest request fixture used to recover the parameterized test ID
    :param python_version: the Python version with major and minor version numbers, e.g. "3.10"
    :param scons_version: the SCons version with major and minor version numbers, e.g. "4.6"
    """
    test_id = request.node.callspec.id
    test_identifier = test_id.replace(" ", "_")
    test_environment = copy.deepcopy(environment)
    test_environment["RATTLER_CACHE_DIR"] = f"rattler-cache-{test_identifier}"

    template = command_template
    command = template.safe_substitute(
        {
            "python_version": python_version,
            "scons_version": scons_version,
            "test_identifier": test_identifier,
        }
    )
    subprocess.check_output(
        command,
        env=environment,
        cwd=repository_directory,
        text=True,
        shell=True,
        stdin=subprocess.DEVNULL,
        start_new_session=True,
    )


if __name__ == "__main__":
    pass
