"""Run the conda-recipe build against a matrix of dependencies."""
import itertools
import os
import pathlib
import string
import subprocess

import pytest

env = os.environ.copy()
OUTPUT_FOLDER = "--output-folder ${conda_build_artifacts}" if "conda_build_artifacts" in env else ""
CROOT = "--croot ${croot}/recipe-matrix" if "croot" in env else ""
repository_directory = pathlib.Path(os.path.realpath(__file__)).parent.parent

command_template = string.Template(
    "VERSION=$(python -m setuptools_scm) conda mambabuild recipe-matrix --channel fierromechanics "
    "--channel conda-forge --no-anaconda-upload "
    "${CROOT} ${OUTPUT_FOLDER} "
    "--python ${python_version} --variants \"{'scons':['${scons_version}']}\""
)

python_versions = ["3.10", "3.11", "3.12", "3.13"]
scons_versions = ["4.6", "4.7", "4.8"]
conda_build_test_matrix = list(itertools.product(python_versions, scons_versions))
conda_build_test_matrix.remove(("3.13", "4.6"))  # SCons 4.6 not available for Python 3.13


@pytest.mark.parametrize(("python_version", "scons_version"), conda_build_test_matrix)
def test_matrix(python_version: str, scons_version: str) -> None:
    """Run the conda-recipe build against a matrix of dependencies.

    :param python_version: the Python version with major and minor version numbers, e.g. "3.10"
    :param scons_version: the SCons version with major and minor version numbers, e.g. "4.6"
    """
    template = command_template
    command = template.safe_substitute(
        {
            "OUTPUT_FOLDER": OUTPUT_FOLDER,
            "CROOT": CROOT,
            "python_version": python_version,
            "scons_version": scons_version,
        }
    )
    subprocess.check_output(
        command,
        env=env,
        cwd=repository_directory,
        text=True,
        shell=True,
        stdin=subprocess.DEVNULL,
        start_new_session=True,
    )
