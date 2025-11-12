"""Define the project's custom pytest options and CLI extensions."""

import pathlib

import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    """Add the custom pytest options to the pytest command-line parser."""
    parser.addoption(
        "--system-test-dir",
        action="store",
        type=pathlib.Path,
        default=None,
        help="system test build directory root",
    )
    parser.addoption(
        "--keep-system-tests",
        action="store_true",
        default=False,
        help="flag to skip system test directory cleanup",
    )
    parser.addoption(
        "--unconditional-build",
        action="store_true",
        default=False,
        help="pass unconditional build option to system tests",
    )
    parser.addoption(
        "--abaqus-command",
        action="append",
        default=None,
        help="Abaqus command for system test CLI pass through",
    )
    parser.addoption(
        "--cubit-command",
        action="append",
        default=None,
        help="Cubit command for system test CLI pass through",
    )


@pytest.fixture
def system_test_directory(request: pytest.FixtureRequest) -> pathlib.Path:
    """Return the argument of custom pytest ``--system-test-dir`` command-line option."""
    return request.config.getoption("--system-test-dir")


@pytest.fixture
def keep_system_tests(request: pytest.FixtureRequest) -> bool:
    """Return the argument of custom pytest ``--keep-system-tests`` command-line option."""
    return request.config.getoption("--keep-system-tests")


@pytest.fixture
def unconditional_build(request: pytest.FixtureRequest) -> bool:
    """Return the argument of custom pytest ``--unconditional-build`` command-line option."""
    return request.config.getoption("--unconditional-build")


@pytest.fixture
def abaqus_command(request: pytest.FixtureRequest) -> pathlib.Path:
    """Return the argument of custom pytest ``--abaqus-command`` command-line option.

    Returns an empty list if the getopts default ``None`` is provided (no command line argument specified)
    """
    command_list = request.config.getoption("--abaqus-command")
    if command_list is None:
        command_list = []
    return command_list


@pytest.fixture
def cubit_command(request: pytest.FixtureRequest) -> pathlib.Path:
    """Return the argument of custom pytest ``--cubit-command`` command-line option.

    Returns an empty list if the getopts default ``None`` is provided (no command line argument specified)
    """
    command_list = request.config.getoption("--cubit-command")
    if command_list is None:
        command_list = []
    return command_list
