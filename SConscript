#! /usr/bin/env python

import pathlib

# Inherit the parent construction environment
Import("env")

# Limit list of source files to allow Conda build-test to test off the installed package
pytest_source_list = [
    "pyproject.toml",
]

pytest_command = "PYTHONDONTWRITEBYTECODE=1 pytest --junitxml=${TARGETS[0].abspath}"
target = ["test_results.xml"]

# TODO: Remove the "program_operations" logic when the race conditions on test_program_operations are fixed
coverage = ""
program_operations_coverage = ""
coverage_command = ""
if env["coverage_report"]:
    coverage = "--cov"
    program_operations_coverage = "--cov --cov-append"
    target.append("coverage.xml")
    coverage_command = "coverage xml"

pytest_node = env.Command(
    target=target,
    source=pytest_source_list,
    # TODO: Revert to a single, simple "pytest_command" when the race conditions on test_program_operations are fixed
    action=[
        "${pytest_command} -vvv -m 'not programoperations and not systemtest' ${coverage}",
        "${pytest_command} -vvv -m 'programoperations' ${program_operations_coverage}",
        "${coverage_command}"
    ],
    pytest_command=pytest_command,
    coverage=coverage,
    program_operations_coverage=program_operations_coverage,
    coverage_command=coverage_command
)
env.Alias("pytest", pytest_node)
# Always run pytests in place of a complete source list
env.AlwaysBuild(pytest_node)

target = ["systemtest_results.xml"]
source = pytest_source_list + [str(pathlib.Path("waves/tests/test_systemtest.py"))]
systemtest_node = env.Command(
    target=target,
    source=source,
    action=[
        "${pytest_command} -v --no-showlocals -n 4 -m systemtest --tb=short --cache-clear"
    ],
    pytest_command=pytest_command,
)
env.Alias("systemtest", systemtest_node)
env.AlwaysBuild(systemtest_node)

# Collector alias to build all regression tasks
env.Alias('regression', pytest_node + systemtest_node)
