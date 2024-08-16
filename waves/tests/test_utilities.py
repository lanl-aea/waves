import pathlib
import subprocess
from unittest.mock import patch
from contextlib import nullcontext as does_not_raise

import pytest

from waves import _settings
from waves import _utilities


set_name_substitution = {
    "default identifier": (
        ["@{set_name}lions.txt", "@{set_name}tigers.txt", "bears.txt"],
        "set0",
        "set_name",
        "/",
        ["set0/lions.txt", "set0/tigers.txt", "bears.txt"]
    ),
    "different identifier": (
        ["@{identifier}lions.txt", "@{identifier}tigers.txt", "bears.txt"],
        "set1",
        "identifier",
        "/",
        ["set1/lions.txt", "set1/tigers.txt", "bears.txt"]
    ),
    "remove identifier, no suffix": (
        ["@{identifier}lions.txt", "@{identifier}tigers.txt", "bears.txt"],
        "",
        "identifier",
        "",
        ["lions.txt", "tigers.txt", "bears.txt"]
    ),
}


@pytest.mark.parametrize("sources, replacement, identifier, suffix, expected",
                         set_name_substitution.values(),
                         ids=set_name_substitution.keys())
def test_set_name_substitution(sources, replacement, identifier, suffix, expected):
    replaced_sources = _utilities.set_name_substitution(sources, replacement, identifier=identifier, suffix=suffix)
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


def test_find_cubit_bin():
    mock_abspath = pathlib.Path("/mock/path/parent/cubit")
    mock_macos_bin = mock_abspath.parent / "intermediate/MacOS"
    with patch("waves._utilities.find_command", return_value=str(mock_abspath)), \
         patch("os.path.realpath", return_value=str(mock_abspath)), \
         patch("pathlib.Path.rglob", return_value=[mock_macos_bin]) as mock_rglob:
        cubit_bin = _utilities.find_cubit_bin(mock_abspath, bin_directory="MacOS")
        mock_rglob.assert_called_once()
    assert cubit_bin == mock_macos_bin


def test_find_cubit_python():
    mock_abspath = pathlib.Path("/mock/path/parent/cubit")
    mock_python = mock_abspath.parent / "bin/python3"
    with patch("waves._utilities.find_command"), \
         patch("os.path.realpath", return_value=str(mock_abspath)), \
         patch("pathlib.Path.rglob", return_value=[mock_python]) as mock_rglob, \
         patch("pathlib.Path.is_file", return_value=True), \
         patch("os.access", return_value=True):
        cubit_python = _utilities.find_cubit_python(mock_abspath)
    assert cubit_python == mock_python


def test_tee_subprocess():
    with patch("subprocess.Popen") as mock_popen:
        _utilities.tee_subprocess(['dummy'])
    mock_popen.assert_called_once()


shell_redirect = {
    "default kwargs": (
        {}, _settings._sh_redirect_string
    ),
    "no defaults": (
        {
         "redirect_dictionary": {},
         "redirect_fallback": "different redirect fall back"
        },
        "different redirect fall back"
    ),
    "default fall back": (
        {"shell": "unknown shell"}, _settings._sh_redirect_string
    ),
    "tcsh": (
        {"shell": "tcsh"}, _settings._csh_redirect_string
    ),
    "requested redirect": (
        {"redirect": "different redirect"}, "different redirect"
    ),
}


@pytest.mark.parametrize("kwargs, expected_string",
                         shell_redirect.values(),
                         ids=shell_redirect.keys())
def test_shell_redirect(kwargs, expected_string):
    redirect = _utilities.shell_redirect(**kwargs)
    assert redirect == expected_string


return_environment = {
    "no newlines": (
        "command", {}, b"thing1=a\x00thing2=b", {"thing1": "a", "thing2": "b"}
    ),
    "newlines": (
        "command", {}, b"thing1=a\nnewline\x00thing2=b", {"thing1": "a\nnewline", "thing2": "b"}
    ),
    "tcsh": (
        "command", {"shell": "tcsh"},
        b"thing1=a\x00thing2=b", {"thing1": "a", "thing2": "b"}
    ),
    "no defaults": (
        "command",
        {
         "shell": "different shell",
         "redirect": "different redirect",
         "string_option": "different string option",
         "separator": "different separator",
         "environment": "different environment",
         "redirect_dictionary": {},
         "redirect_fallback": "different redirect fallback"
        },
        b"thing1=a\x00thing2=b", {"thing1": "a", "thing2": "b"}
    ),
}


@pytest.mark.parametrize("command, kwargs, stdout, expected",
                         return_environment.values(),
                         ids=return_environment.keys())
def test_return_environment(command, kwargs, stdout, expected):
    """
    :param bytes stdout: byte string with null delimited shell environment variables
    :param dict expected: expected dictionary output containing string key:value pairs and preserving newlines
    """
    redirect_kwargs = {key: kwargs[key] for key in ["shell", "redirect", "redirect_dictionary", "redirect_fallback"]
                       if key in kwargs}
    expected_kwargs = {
        "shell": "bash",
        "redirect": _utilities.shell_redirect(**redirect_kwargs),
        "string_option": "-c",
        "separator": "&&",
        "environment": "env -0",
        "redirect_dictionary": _settings._redirect_strings,
        "redirect_fallback": _settings._sh_redirect_string
    }
    expected_kwargs.update(kwargs)
    expected_command = \
        [expected_kwargs["shell"], expected_kwargs["string_option"],
         f"{command} {expected_kwargs['redirect']} " \
         f"{expected_kwargs['separator']} {expected_kwargs['environment']}"]

    mock_run_return = subprocess.CompletedProcess(args=command, returncode=0, stdout=stdout)
    with patch("subprocess.run", return_value=mock_run_return) as mock_run:
        environment_dictionary = _utilities.return_environment(command, **kwargs)

    assert environment_dictionary == expected
    mock_run.assert_called_once_with(
        expected_command, check=True, capture_output=True
    )


cache_environment = {
        # cache,       overwrite_cache, expected,        file_exists
    "no cache":
        (None,         False,           {"thing1": "a"}, False),
    "cache exists":
        ("dummy.yaml", False,           {"thing1": "a"}, True),
    "cache doesn't exist":
        ("dummy.yaml", False,           {"thing1": "a"}, False),
    "overwrite cache":
        ("dummy.yaml", True,            {"thing1": "a"}, True),
    "don't overwrite cache":
        ("dummy.yaml", False,           {"thing1": "a"}, False)
}


@pytest.mark.parametrize("cache, overwrite_cache, expected, file_exists",
                         cache_environment.values(),
                         ids=cache_environment.keys())
def test_cache_environment(cache, overwrite_cache, expected, file_exists):
    with patch("waves._utilities.return_environment", return_value=expected) as return_environment, \
         patch("yaml.safe_load", return_value=expected) as yaml_load, \
         patch("pathlib.Path.exists", return_value=file_exists), \
         patch("yaml.safe_dump") as yaml_dump, \
         patch("builtins.open"):
        environment_dictionary = _utilities.cache_environment("dummy command", cache=cache,
                                                              overwrite_cache=overwrite_cache)
        if cache and file_exists and not overwrite_cache:
            yaml_load.assert_called_once()
            return_environment.assert_not_called()
        else:
            yaml_load.assert_not_called()
            return_environment.assert_called_once()
        if cache:
            yaml_dump.assert_called_once()
    assert environment_dictionary == expected
