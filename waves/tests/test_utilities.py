import pathlib
from unittest.mock import patch
from contextlib import nullcontext as does_not_raise

import pytest

from waves import _utilities


set_name_substitution = {
    "default pattern": (
        ["@{set_name}lions.txt", "@{set_name}tigers.txt", "bears.txt"],
        "set0",
        "set_name",
        "/",
        ["set0/lions.txt", "set0/tigers.txt", "bears.txt"]
    ),
    "different pattern": (
        ["@{pattern}lions.txt", "@{pattern}tigers.txt", "bears.txt"],
        "set1",
        "pattern",
        "/",
        ["set1/lions.txt", "set1/tigers.txt", "bears.txt"]
    ),
    "remove pattern, no postfix": (
        ["@{pattern}lions.txt", "@{pattern}tigers.txt", "bears.txt"],
        "",
        "pattern",
        "",
        ["lions.txt", "tigers.txt", "bears.txt"]
    ),
}


@pytest.mark.parametrize("sources, replacement, pattern, postfix, expected",
                         set_name_substitution.values(),
                         ids=set_name_substitution.keys())
def test_set_name_substitution(sources, replacement, pattern, postfix, expected):
    replaced_sources = _utilities.set_name_substitution(sources, replacement, pattern=pattern, postfix=postfix)
    assert replaced_sources == expected


quote_spaces_in_path_input = {
    "string, no spaces": (
        "/path/without_space/executable",
        pathlib.Path("/path/without_space/executable")
    ),
    "string, spaces": (
        "/path/with space/executable",
        pathlib.Path("/path/\"with space\"/executable")
    ),
    "pathlib, no spaces": (
        pathlib.Path("/path/without_space/executable"),
        pathlib.Path("/path/without_space/executable")
    ),
    "pathlib, spaces": (
        pathlib.Path("/path/with space/executable"),
        pathlib.Path("/path/\"with space\"/executable")
    ),
    "space in root": (
        pathlib.Path("/path space/with space/executable"),
        pathlib.Path("/\"path space\"/\"with space\"/executable")
    ),
    "relative path": (
        pathlib.Path("path space/without_space/executable"),
        pathlib.Path("\"path space\"/without_space/executable")
    ),
    "space in executable": (
        pathlib.Path("path/without_space/executable space"),
        pathlib.Path("path/without_space/\"executable space\"")
    )
}


@pytest.mark.parametrize("path, expected",
                         quote_spaces_in_path_input.values(),
                         ids=quote_spaces_in_path_input.keys())
def test_quote_spaces_in_path(path, expected):
    assert _utilities._quote_spaces_in_path(path) == expected


def test_search_commands():
    """Test :meth:`waves._utilities.search_command`"""
    with patch("shutil.which", return_value=None) as shutil_which:
        command_abspath = _utilities.search_commands(["notfound"])
        assert command_abspath is None

    with patch("shutil.which", return_value="found") as shutil_which:
        command_abspath = _utilities.search_commands(["found"])
        assert command_abspath == "found"


find_command = {
    "first": (
        ["first", "second"], "first", does_not_raise()
    ),
    "second": (
        ["first", "second"], "second", does_not_raise()
    ),
    "none": (
        ["first", "second"], None, pytest.raises(FileNotFoundError)
    ),
}


@pytest.mark.parametrize("options, found, outcome",
                         find_command.values(),
                         ids=find_command.keys())
def test_find_command(options, found, outcome):
    """Test :meth:`waves._utilities.find_command`"""
    with patch("waves._utilities.search_commands", return_value=found), outcome:
        try:
            command_abspath = _utilities.find_command(options)
            assert command_abspath == found
        finally:
            pass


def test_cubit_os_bin():
    with patch("platform.system", return_value="Darwin"):
        bin_directory = _utilities.cubit_os_bin()
        assert bin_directory == "MacOS"

    with patch("platform.system", return_value="Linux"):
        bin_directory = _utilities.cubit_os_bin()
        assert bin_directory == "bin"

    # TODO: Find the Windows bin directory name, update the function and the test.
    with patch("platform.system", return_value="Windows"):
        bin_directory = _utilities.cubit_os_bin()
        assert bin_directory == "bin"


def test_tee_subprocess():
    with patch("subprocess.Popen") as mock_popen:
        _utilities.tee_subprocess(['dummy'])
    mock_popen.assert_called_once()
