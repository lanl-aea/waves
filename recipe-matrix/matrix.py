"""Run the conda-recipe build against a matrix of dependencies."""

import copy
import functools
import itertools
import operator
import os
import pathlib
import string
import subprocess

import pandas
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

package_versions = {
    "python": ["3.10", "3.11", "3.12", "3.13", "3.14"],
    "scons": ["4.6", "4.7", "4.8", "4.9", "4.10"],
}
test_matrix = pandas.DataFrame(list(itertools.product(*package_versions.values())), columns=package_versions.keys())
remove_cases = [
    {"python": "3.13", "scons": "4.6"},
    {"python": "3.14", "scons": "4.6"},
    {"python": "3.14", "scons": "4.7"},
    {"python": "3.14", "scons": "4.8"},
]
remove_index = []
for case in remove_cases:
    conditions = [test_matrix[package] == version for package, version in case.items()]
    remove_index.append(functools.reduce(operator.and_, conditions))
remove_index = functools.reduce(operator.or_, remove_index)
test_matrix = test_matrix[~remove_index]
test_matrix = test_matrix.reset_index(drop=True)
test_identifiers = ["-".join(f"{column}{value}" for column, value in row._asdict().items()) for row in test_matrix.itertuples(index=False)]


@pytest.mark.parametrize(("python_version", "scons_version"), test_matrix.to_numpy(), ids=test_identifiers)
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
        env=test_environment,
        cwd=repository_directory,
        text=True,
        shell=True,
        stdin=subprocess.DEVNULL,
        start_new_session=True,
    )


if __name__ == "__main__":
    pass
