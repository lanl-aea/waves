import os
import shlex
import string
import pathlib
import itertools
import subprocess

import pytest

env = os.environ.copy()
OUTPUT_FOLDER = "--output-folder ${conda_build_artifacts}" if "conda_build_artifacts" in env else ""
CROOT = "--croot ${croot}/recipe-matrix" if "croot" in env else ""
repository_directory = pathlib.Path(os.path.realpath(__file__)).parent.parent

command_template = string.Template(
    "VERSION=$(python -m setuptools_scm) conda mambabuild recipe-matrix --channel fierromechanics " \
    "--channel conda-forge --no-anaconda-upload " \
    "${CROOT} ${OUTPUT_FOLDER} " \
    "--python ${PYTHON_VERSION} --variants \"{'scons':['${SCONS_VERSION}']}\""
)

python_versions = ["3.8", "3.9", "3.10", "3.11", "3.12"]
scons_versions = ["4.6", "4.7"]
conda_build_test_matrix = list(itertools.product(python_versions, scons_versions))


@pytest.mark.parametrize("PYTHON_VERSION, SCONS_VERSION", conda_build_test_matrix)
def test_matrix(PYTHON_VERSION: str, SCONS_VERSION: str) -> None:
    template = command_template
    command = template.safe_substitute({
        "OUTPUT_FOLDER": OUTPUT_FOLDER,
        "CROOT": CROOT,
        "PYTHON_VERSION": PYTHON_VERSION,
        "SCONS_VERSION": SCONS_VERSION
    })
    subprocess.check_output(
        command,
        env=env,
        cwd=repository_directory,
        text=True,
        shell=True,
        stdin=subprocess.DEVNULL,
        start_new_session=True
    )
