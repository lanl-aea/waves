import os
import shlex
import string
import pathlib
import subprocess

import pytest

env = os.environ.copy()
repository_directory = pathlib.Path(os.path.realpath(__file__)).parent.parent

command_template = string.Template(
    "VERSION=$(python -m setuptools_scm) conda mambabuild recipe-matrix --channel fierromechanics " \
    "--channel conda-forge --no-anaconda-upload --croot ${croot}/recipe-matrix " \
    "--output-folder ${conda_artifacts_directory} " \
    "--python ${PYTHON_VERSION} --variants {'scons':['${SCONS_VERSION}']}"
)

python_versions = ["3.11", "3.12"]
scons_versions = ["4.6", "4.7"]
conda_build_test_matrix = list(itertools.product(python_versions, scons_versions))


@pytest.mark.parametrize("PYTHON_VERSION, SCONS_VERSION", conda_build_test_matrix)
def test_matrix(PYTHON_VERSION: str, SCONS_VERSION: str) -> None:
    template = command_template
    command = template.safe_substitute({"PYTHON_VERSION": PYTHON_VERSION, "SCONS_VERSION": SCONS_VERSION})
    subprocess.check_output(command, env=env, cwd=repository_directory, text=True, shell=True)
