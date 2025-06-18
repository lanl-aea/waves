from unittest.mock import patch, Mock

import pytest

from waves._tests import common


test_platform_check_cases = {
    "linux": ("Linux", False, "/", False),
    "windows": ("Windows", True, "C:\\", False),
    "macos": ("Darwin", False, "/", True),
}


@pytest.mark.parametrize(
    "mock_system, expected_testing_windows, expected_root_fs, expected_testing_macos",
    test_platform_check_cases.values(),
    ids=test_platform_check_cases.keys(),
)
def test_platform_check(mock_system, expected_testing_windows, expected_root_fs, expected_testing_macos):
    windows_path_mock = Mock()
    windows_path_mock.drive = "C:"
    with (
        patch("platform.system", return_value=mock_system),
        patch("pathlib.Path.resolve", return_value=windows_path_mock),
    ):
        testing_windows, root_fs, testing_macos = common.platform_check()
    assert testing_windows == expected_testing_windows
    assert root_fs == expected_root_fs
    assert testing_macos == expected_testing_macos
