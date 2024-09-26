import pathlib

import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--system-test-dir",
        action="store",
        type=pathlib.Path,
        default=None,
        help="system test build directory root"
    )


@pytest.fixture
def system_test_directory(request):
    return request.config.getoption("--system-test-dir")
