#! /usr/bin/env python

import pathlib

# Inherit the parent construction environment
Import("env")

# Limit list of source files to allow Conda build test to avoid copying waves source code and test off the installed
# waves package
waves_source_list = [
    "pyproject.toml",
]

pytest_command = "PYTHONDONTWRITEBYTECODE=1 pytest --junitxml=${TARGETS[0].name}"
target = ["test_results.xml"]
if env["coverage_report"]:
    pytest_command += " --cov --cov-report term --cov-report xml:${TARGETS[1].name}"
    target.append("coverage.xml")
pytest_node = env.Command(
    target=target,
    source=waves_source_list,
    action=pytest_command)
alias_list = env.Alias("pytest", pytest_node)
# Always run pytests in place of a complete source list
env.AlwaysBuild(pytest_node)

# System tests *must* be run in serial because they all try to write to the same sconsign file
systemtest_command = "PYTHONDONTWRITEBYTECODE=1 pytest -n0 -m systemtest --junitxml=${TARGETS[0].name} --cache-clear"
target = ["systemtest_results.xml"]
source = waves_source_list + [str(pathlib.Path("waves/tests/test_tutorials.py"))]
systemtest_node = env.Command(
    target=target,
    source=source,
    action=systemtest_command)
alias_list = env.Alias("systemtest", systemtest_node)
env.AlwaysBuild(systemtest_node)

# Return the alias list to SConstruct for help message output
Return("alias_list")
