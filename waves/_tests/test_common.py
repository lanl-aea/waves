from unittest.mock import patch

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
    with patch("platform.system", return_value=mock_system):
        testing_windows, root_fs, testing_macos = common.platform_check()
    assert testing_windows == expected_testing_windows
    assert root_fs == expected_root_fs
    assert testing_macos == expected_testing_macos
