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
OUTPUT_FOLDER = "--output-dir ${conda_build_artifacts}" if "conda_build_artifacts" in environment else ""
repository_directory = pathlib.Path(os.path.realpath(__file__)).parent.parent

command_template = string.Template(
    "VERSION=$(python -m setuptools_scm) rattler-build build --recipe recipe-matrix --channel fierromechanics "
    "--channel conda-forge "
    "--output-dir conda-bld-${test_identifier} "
    "--env-isolation conda-build "
    '--variant python="${python_version}" --variant scons="${scons_version}"'
)

package_versions = {
    "python": ["3.10", "3.11", "3.12", "3.13", "3.14"],
    "scons": ["4.6", "4.7", "4.8", "4.9", "4.10"],
}
remove_cases = [
    {"python": "3.13", "scons": "4.6"},
    {"python": "3.14", "scons": "4.6"},
    {"python": "3.14", "scons": "4.7"},
    {"python": "3.14", "scons": "4.8"},
]


def return_test_matrix(package_versions: dict[str : list[str]], remove_cases: dict[str, str]) -> pandas.DataFrame:
    """Construct a full factorial test matrix.

    :param package_version: ``{package [version1, version2, ...]}`` pairs for the full factorial
    :param remove_cases: ``{package: version, package2: version}`` rows to remove from the full factorial

    :returns: Pandas DataFrame where the index is the string catenation of package names and versions
    """
    test_matrix = pandas.DataFrame(list(itertools.product(*package_versions.values())), columns=package_versions.keys())
    remove_index_case = []
    for case in remove_cases:
        conditions = [test_matrix[package] == version for package, version in case.items()]
        remove_index_case.append(functools.reduce(operator.and_, conditions))
    remove_indices = functools.reduce(operator.or_, remove_index_case)
    test_matrix = test_matrix[~remove_indices]
    test_matrix = test_matrix.reset_index(drop=True)
    test_identifiers = [
        "-".join(f"{column}{value}" for column, value in row._asdict().items())
        for row in test_matrix.itertuples(index=False)
    ]
    test_matrix.index = test_identifiers
    return test_matrix


test_matrix = return_test_matrix(package_versions, remove_cases)


@pytest.mark.parametrize(("python_version", "scons_version"), test_matrix.to_numpy(), ids=test_matrix.index)
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
