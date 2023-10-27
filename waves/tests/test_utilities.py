import pathlib

import pytest

from waves import _utilities

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


@pytest.mark.unittest
@pytest.mark.parametrize("path, expected",
                         quote_spaces_in_path_input.values(),
                         ids=quote_spaces_in_path_input.keys())
def test_quote_spaces_in_path(path, expected):
    assert _utilities._quote_spaces_in_path(path) == expected
