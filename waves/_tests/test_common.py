from unittest.mock import Mock, patch

import pytest

from waves._tests import common

test_platform_check_cases = {
    "linux": ("Linux", False, "/", False),
    "windows": ("Windows", True, "C:\\", False),
    "macos": ("Darwin", False, "/", True),
}


@pytest.mark.parametrize(
    ("mock_system", "expected_testing_windows", "expected_root_fs", "expected_testing_macos"),
    test_platform_check_cases.values(),
    ids=test_platform_check_cases.keys(),
)
def test_platform_check(
    mock_system: str, expected_testing_windows: bool, expected_root_fs: str, expected_testing_macos: bool
) -> None:
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


test_check_ci_user_cases = {
    "windows ci user": ("PN2606796$", True),
    "windows ci user without trailing service account character": ("PN2606796", True),
    "macos ci user": ("gitlab-runner", True),
    "player character": ("roppenheimer", False),
}


@pytest.mark.parametrize(
    ("mock_user", "expected"),
    test_check_ci_user_cases.values(),
    ids=test_check_ci_user_cases.keys(),
)
def test_check_ci_user(mock_user: str, expected: bool) -> None:
    with patch("getpass.getuser", return_value=mock_user):
        testing_ci_user = common.check_ci_user()
    assert testing_ci_user is expected
