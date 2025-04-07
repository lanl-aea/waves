import sys
import copy
import pathlib
import warnings
import subprocess
from unittest.mock import patch
from contextlib import nullcontext as does_not_raise

import pytest

from waves import _settings
from waves import _utilities


set_name_substitution = {
    "default behavior": (
        ["@{set_name}lions.txt", "@{set_name}tigers.txt", "bears.txt"],
        "set0",
        {},
        ["set0/lions.txt", "set0/tigers.txt", "bears.txt"],
    ),
    "default behavior: tuple": (
        ("@{set_name}lions.txt", "@{set_name}tigers.txt", "bears.txt"),
        "set0",
        {},
        ["set0/lions.txt", "set0/tigers.txt", "bears.txt"],
    ),
    "default behavior: set": (
        {"@{set_name}lions.txt", "@{set_name}tigers.txt", "bears.txt"},
        "set0",
        {},
        ["set0/lions.txt", "set0/tigers.txt", "bears.txt"],
    ),
    "default behavior: list of pathlib.Path": (
        [pathlib.Path("@{set_name}lions.txt"), pathlib.Path("@{set_name}tigers.txt"), pathlib.Path("bears.txt")],
        "set0",
        {},
        [pathlib.Path("set0/lions.txt"), pathlib.Path("set0/tigers.txt"), pathlib.Path("bears.txt")],
    ),
    "default behavior: list of mixed str and pathlib.Path": (
        ["@{set_name}lions.txt", pathlib.Path("@{set_name}tigers.txt"), pathlib.Path("bears.txt")],
        "set0",
        {},
        ["set0/lions.txt", pathlib.Path("set0/tigers.txt"), pathlib.Path("bears.txt")],
    ),
    "different identifier": (
        ["@{identifier}lions.txt", "@{identifier}tigers.txt", "bears.txt"],
        "set1",
        {"identifier": "identifier"},
        ["set1/lions.txt", "set1/tigers.txt", "bears.txt"],
    ),
    "remove identifier, no suffix": (
        ["@{identifier}lions.txt", "@{identifier}tigers.txt", "bears.txt"],
        "",
        {"identifier": "identifier", "suffix": ""},
        ["lions.txt", "tigers.txt", "bears.txt"],
    ),
    "scalar string, default behavior": (
        "@{set_name}lions.txt",
        "set0",
        {},
        "set0/lions.txt",
    ),
    "scalar pathlib.Path, default behavior": (
        pathlib.Path("@{set_name}lions.txt"),
        "set0",
        {},
        pathlib.Path("set0/lions.txt"),
    ),
    "scalar string, different identifier": (
        "@{identifier}lions.txt",
        "set1",
        {"identifier": "identifier"},
        "set1/lions.txt",
    ),
    "scalar string, remove identifier, no suffix": (
        "@{identifier}lions.txt",
        "",
        {"identifier": "identifier", "suffix": ""},
        "lions.txt",
    ),
    "dictionary": (
        {"key": "value"},
        "set0",
        {},
        {"key": "value"},
    ),
}


@pytest.mark.parametrize(
    "original, replacement, kwargs, expected",
    set_name_substitution.values(),
    ids=set_name_substitution.keys(),
)
def test_set_name_substitution(original, replacement, kwargs, expected):
    default_kwargs = {"identifier": "set_name", "suffix": "/"}
    call_kwargs = copy.deepcopy(default_kwargs)
    call_kwargs.update(kwargs)
    modified = _utilities.set_name_substitution(original, replacement, **call_kwargs)
    if isinstance(expected, (str, pathlib.Path)):
        assert modified == expected
    elif all(isinstance(item, str) for item in expected) or all(isinstance(item, pathlib.Path) for item in expected):
        assert sorted(modified) == sorted(expected)
    else:
        assert modified == expected


quote_spaces_in_path_input = {
    "string, no spaces": (
        "/path/without_space/executable",
        pathlib.Path("/path/without_space/executable"),
    ),
    "string, spaces": (
        "/path/with space/executable",
        pathlib.Path('/path/"with space"/executable'),
    ),
    "pathlib, no spaces": (
        pathlib.Path("/path/without_space/executable"),
        pathlib.Path("/path/without_space/executable"),
    ),
    "pathlib, spaces": (
        pathlib.Path("/path/with space/executable"),
        pathlib.Path('/path/"with space"/executable'),
    ),
    "space in root": (
        pathlib.Path("/path space/with space/executable"),
        pathlib.Path('/"path space"/"with space"/executable'),
    ),
    "relative path": (
        pathlib.Path("path space/without_space/executable"),
        pathlib.Path('"path space"/without_space/executable'),
    ),
    "space in executable": (
        pathlib.Path("path/without_space/executable space"),
        pathlib.Path('path/without_space/"executable space"'),
    ),
}


@pytest.mark.parametrize(
    "path, expected",
    quote_spaces_in_path_input.values(),
    ids=quote_spaces_in_path_input.keys(),
)
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
    "first": (["first", "second"], "first", does_not_raise()),
    "second": (["first", "second"], "second", does_not_raise()),
    "none": (["first", "second"], None, pytest.raises(FileNotFoundError)),
}


@pytest.mark.parametrize(
    "options, found, outcome",
    find_command.values(),
    ids=find_command.keys(),
)
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


def test_find_cubit_bin():
    mock_abspath = pathlib.Path("/mock/path/parent/cubit")
    mock_macos_bin = mock_abspath.parent / "intermediate/MacOS"
    with (
        patch("waves._utilities.find_command", return_value=str(mock_abspath)),
        patch("os.path.realpath", return_value=str(mock_abspath)),
        patch("pathlib.Path.rglob", return_value=[mock_macos_bin]) as mock_rglob,
    ):
        cubit_bin = _utilities.find_cubit_bin(mock_abspath, bin_directory="MacOS")
        mock_rglob.assert_called_once()
    assert cubit_bin == mock_macos_bin


def test_find_cubit_python():
    mock_abspath = pathlib.Path("/mock/path/parent/cubit")
    mock_python = mock_abspath.parent / "bin/python3"
    with (
        patch("waves._utilities.find_command"),
        patch("os.path.realpath", return_value=str(mock_abspath)),
        patch("pathlib.Path.rglob", return_value=[mock_python]) as mock_rglob,
        patch("pathlib.Path.is_file", return_value=True),
        patch("os.access", return_value=True),
    ):
        cubit_python = _utilities.find_cubit_python(mock_abspath)
        assert cubit_python == mock_python

    with (
        patch("waves._utilities.find_command"),
        patch("os.path.realpath", return_value=str(mock_abspath)),
        patch("pathlib.Path.rglob", return_value=[mock_python]) as mock_rglob,
        patch("pathlib.Path.is_file", return_value=False),
        patch("os.access", return_value=True),
        pytest.raises(FileNotFoundError),
    ):
        cubit_python = _utilities.find_cubit_python(mock_abspath)


def test_tee_subprocess():
    with patch("subprocess.Popen") as mock_popen:
        _utilities.tee_subprocess(["dummy"])
    mock_popen.assert_called_once()


return_environment = {
    "no newlines": (
        "command",
        {},
        b"thing1=a\x00thing2=b",
        {"thing1": "a", "thing2": "b"},
    ),
    "newlines": (
        "command",
        {},
        b"thing1=a\nnewline\x00thing2=b",
        {"thing1": "a\nnewline", "thing2": "b"},
    ),
    "extra leading lines": (
        "command",
        {},
        b"command output\nwith newlines\nthing1=a\nnewline\x00thing2=b",
        {"thing1": "a\nnewline", "thing2": "b"},
    ),
    "tcsh": (
        "command",
        {"shell": "tcsh"},
        b"thing1=a\x00thing2=b",
        {"thing1": "a", "thing2": "b"},
    ),
    "no defaults": (
        "command",
        {
            "shell": "different shell",
            "string_option": "different string option",
            "separator": "different separator",
            "environment": "different environment",
        },
        b"thing1=a\x00thing2=b",
        {"thing1": "a", "thing2": "b"},
    ),
}


@pytest.mark.parametrize(
    "command, kwargs, stdout, expected",
    return_environment.values(),
    ids=return_environment.keys(),
)
def test_return_environment(command, kwargs, stdout, expected):
    """
    :param bytes stdout: byte string with null delimited shell environment variables
    :param dict expected: expected dictionary output containing string key:value pairs and preserving newlines
    """
    expected_kwargs = {
        "shell": "bash",
        "string_option": "-c",
        "separator": "&&",
        "environment": "env -0",
    }
    expected_kwargs.update(kwargs)
    expected_command = (
        f"{expected_kwargs['shell']} {expected_kwargs['string_option']} "
        f"\"{command} {expected_kwargs['separator']} {expected_kwargs['environment']}\""
    )

    mock_run_return = subprocess.CompletedProcess(args=command, returncode=0, stdout=stdout)
    with patch("subprocess.run", return_value=mock_run_return) as mock_run:
        environment_dictionary = _utilities.return_environment(command, **kwargs)

    assert environment_dictionary == expected
    mock_run.assert_called_once_with(expected_command, check=True, capture_output=True, shell=True)


cache_environment = {
    # kwargs, cache, overwrite_cache, expected, file_exists
    "no cache": ({}, None, False, False, {"thing1": "a"}, False),
    "no cache, verbose": ({}, None, False, True, {"thing1": "a"}, False),
    "cache exists": ({}, "dummy.yaml", False, False, {"thing1": "a"}, True),
    "cache exists, verbose": ({}, "dummy.yaml", False, True, {"thing1": "a"}, True),
    "cache doesn't exist": ({}, "dummy.yaml", False, False, {"thing1": "a"}, False),
    "overwrite cache": ({}, "dummy.yaml", True, False, {"thing1": "a"}, True),
    "don't overwrite cache": ({}, "dummy.yaml", False, False, {"thing1": "a"}, False),
    "shell override": ({"shell": "tcsh"}, None, False, False, {"thing1": "a"}, False),
}


@pytest.mark.parametrize(
    "kwargs, cache, overwrite_cache, verbose, expected, file_exists",
    cache_environment.values(),
    ids=cache_environment.keys(),
)
def test_cache_environment(kwargs, cache, overwrite_cache, verbose, expected, file_exists):
    return_environment_kwargs = {
        "shell": "bash",
    }
    return_environment_kwargs.update(kwargs)

    with (
        patch("waves._utilities.return_environment", return_value=expected) as return_environment,
        patch("yaml.safe_load", return_value=expected) as yaml_load,
        patch("pathlib.Path.exists", return_value=file_exists),
        patch("yaml.safe_dump") as yaml_dump,
        patch("builtins.open"),
        patch("builtins.print") as mock_print,
    ):
        environment_dictionary = _utilities.cache_environment(
            "dummy command",
            cache=cache,
            overwrite_cache=overwrite_cache,
            verbose=verbose,
            **kwargs,
        )
        if cache and file_exists and not overwrite_cache:
            yaml_load.assert_called_once()
            return_environment.assert_not_called()
        else:
            yaml_load.assert_not_called()
            return_environment.assert_called_once_with("dummy command", **return_environment_kwargs)

        if cache:
            yaml_dump.assert_called_once()

        if verbose:
            mock_print.assert_called_once()
        else:
            mock_print.assert_not_called()
    assert environment_dictionary == expected


def test_cache_environment_exception_handling():
    with (
        patch(
            "waves._utilities.return_environment",
            side_effect=subprocess.CalledProcessError(1, "command", output=b"output"),
        ),
        patch("builtins.print") as mock_print,
        pytest.raises(subprocess.CalledProcessError),
    ):
        try:
            _utilities.cache_environment("dummy command")
        finally:
            mock_print.assert_called_once_with("output", file=sys.stderr)


create_valid_identifier = {
    "leading digit": ("1word", "_1word"),
    "leading space": (" word", "_word"),
    "replace slashes and spaces": ("w o /rd", "w_o__rd"),
    "replace special characters": ("w%o @rd", "w_o__rd"),
}


@pytest.mark.parametrize(
    "identifier, expected",
    create_valid_identifier.values(),
    ids=create_valid_identifier.keys(),
)
def test_create_valid_identifier(identifier, expected) -> None:
    returned = _utilities.create_valid_identifier(identifier)
    assert returned == expected


def test_warn_only_once():

    def test_warning():
        warnings.warn("test warning")

    with warnings.catch_warnings(record=True) as warning_output:
        test_warning()
        test_warning()
        assert len(warning_output) == 1
