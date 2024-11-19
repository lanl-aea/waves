import pathlib

import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--system-test-dir",
        action="store",
        type=pathlib.Path,
        default=None,
        help="system test build directory root",
    )
    parser.addoption(
        "--unconditional-build",
        action="store_true",
        default=False,
        help="pass unconditional build option to sytem tests",
    )


@pytest.fixture
def system_test_directory(request):
    return request.config.getoption("--system-test-dir")


@pytest.fixture
def unconditional_build(request):
    return request.config.getoption("--unconditional-build")
