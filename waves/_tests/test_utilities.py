import contextlib
import copy
import pathlib
import subprocess
import sys
import typing
import warnings
from unittest.mock import patch

import pytest

from waves import _utilities

does_not_raise = contextlib.nullcontext()

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
    ("original", "replacement", "kwargs", "expected"),
    set_name_substitution.values(),
    ids=set_name_substitution.keys(),
)
def test_set_name_substitution(
    # Function returns unhandled objects unchanged. Test must accept typing.Any.
    original: list[str | pathlib.Path] | str | pathlib.Path | typing.Any,  # noqa: ANN401
    replacement: str,
    kwargs: dict,
    # Function returns unhandled objects unchanged. Test must accept typing.Any.
    expected: list[str | pathlib.Path] | str | pathlib.Path | typing.Any,  # noqa: ANN401
) -> None:
    default_kwargs = {"identifier": "set_name", "suffix": "/"}
    call_kwargs = copy.deepcopy(default_kwargs)
    call_kwargs.update(kwargs)
    modified = _utilities.set_name_substitution(original, replacement, **call_kwargs)
    if isinstance(expected, str | pathlib.Path):
        assert modified == expected
    elif all(isinstance(item, str) for item in expected) or all(isinstance(item, pathlib.Path) for item in expected):
        # Assertion logic designed for expected types. Ignore type of actual return value, ``modified``.
        assert sorted(modified) == sorted(expected)  # type: ignore[arg-type]
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
    ("path", "expected"),
    quote_spaces_in_path_input.values(),
    ids=quote_spaces_in_path_input.keys(),
)
def test_quote_spaces_in_path(path: str | pathlib.Path, expected: pathlib.Path) -> None:
    assert _utilities._quote_spaces_in_path(path) == expected


def test_search_commands() -> None:
    """Test :meth:`waves._utilities.search_command`."""
    with patch("shutil.which", return_value=None):
        command_abspath = _utilities.search_commands(["notfound"])
        assert command_abspath is None

    with patch("shutil.which", return_value="found"):
        command_abspath = _utilities.search_commands(["found"])
        assert command_abspath == "found"


find_command = {
    "first": (["first", "second"], "first", does_not_raise),
    "second": (["first", "second"], "second", does_not_raise),
    "none": (["first", "second"], None, pytest.raises(FileNotFoundError)),
}


@pytest.mark.parametrize(
    ("options", "found", "outcome"),
    find_command.values(),
    ids=find_command.keys(),
)
def test_find_command(
    options: list[str], found: str | None, outcome: contextlib.nullcontext | pytest.RaisesExc
) -> None:
    """Test :meth:`waves._utilities.find_command`."""
    with patch("waves._utilities.search_commands", return_value=found), outcome:
        command_abspath = _utilities.find_command(options)
        assert command_abspath == found


def test_cubit_os_bin() -> None:
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


def test_find_cubit_bin() -> None:
    mock_abspath = pathlib.Path("/mock/path/parent/cubit")
    mock_macos_bin = mock_abspath.parent / "intermediate/MacOS"
    with (
        patch("waves._utilities.find_command", return_value=str(mock_abspath)),
        patch("os.path.realpath", return_value=str(mock_abspath)),
        patch("pathlib.Path.rglob", return_value=[mock_macos_bin]) as mock_rglob,
    ):
        cubit_bin = _utilities.find_cubit_bin([str(mock_abspath)], bin_directory="MacOS")
        mock_rglob.assert_called_once()
    assert cubit_bin == mock_macos_bin


def test_find_cubit_python() -> None:
    mock_abspath = pathlib.Path("/mock/path/parent/cubit")
    mock_python = mock_abspath.parent / "bin/python3"
    with (
        patch("waves._utilities.find_command"),
        patch("os.path.realpath", return_value=str(mock_abspath)),
        patch("pathlib.Path.rglob", return_value=[mock_python]),
        patch("pathlib.Path.is_file", return_value=True),
        patch("os.access", return_value=True),
    ):
        cubit_python = _utilities.find_cubit_python([str(mock_abspath)])
        assert cubit_python == mock_python

    with (
        patch("waves._utilities.find_command"),
        patch("os.path.realpath", return_value=str(mock_abspath)),
        patch("pathlib.Path.rglob", return_value=[mock_python]),
        patch("pathlib.Path.is_file", return_value=False),
        patch("os.access", return_value=True),
        pytest.raises(FileNotFoundError),
    ):
        cubit_python = _utilities.find_cubit_python([str(mock_abspath)])


def test_tee_subprocess() -> None:
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
    ("command", "kwargs", "stdout", "expected"),
    return_environment.values(),
    ids=return_environment.keys(),
)
def test_return_environment(command: str, kwargs: dict, stdout: bytes, expected: dict[str, str]) -> None:
    """Test :func:`waves._utilities.return_environment`.

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
        f'"{command} {expected_kwargs["separator"]} {expected_kwargs["environment"]}"'
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
    ("kwargs", "cache", "overwrite_cache", "verbose", "expected", "file_exists"),
    cache_environment.values(),
    ids=cache_environment.keys(),
)
def test_cache_environment(
    kwargs: dict, cache: str | None, overwrite_cache: bool, verbose: bool, expected: dict[str, str], file_exists: bool
) -> None:
    return_environment_kwargs = {
        "shell": "bash",
    }
    return_environment_kwargs.update(kwargs)

    with (
        patch("waves._utilities.return_environment", return_value=expected) as return_environment,
        patch("yaml.safe_load", return_value=expected) as yaml_load,
        patch("pathlib.Path.exists", return_value=file_exists),
        patch("yaml.safe_dump") as yaml_dump,
        patch("pathlib.Path.open"),
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


def test_cache_environment_exception_handling() -> None:
    with (
        patch(
            "waves._utilities.return_environment",
            side_effect=subprocess.CalledProcessError(1, "command", output=b"output"),
        ),
        patch("builtins.print") as mock_print,
        pytest.raises(subprocess.CalledProcessError),
    ):
        _utilities.cache_environment("dummy command")
    mock_print.assert_called_once_with("output", file=sys.stderr)


create_valid_identifier = {
    "leading digit": ("1word", "_1word"),
    "leading space": (" word", "_word"),
    "replace slashes and spaces": ("w o /rd", "w_o__rd"),
    "replace special characters": ("w%o @rd", "w_o__rd"),
}


@pytest.mark.parametrize(
    ("identifier", "expected"),
    create_valid_identifier.values(),
    ids=create_valid_identifier.keys(),
)
def test_create_valid_identifier(identifier: str, expected: str) -> None:
    returned = _utilities.create_valid_identifier(identifier)
    assert returned == expected


def test_warn_only_once() -> None:
    def test_warning() -> None:
        warnings.warn("test warning")

    with warnings.catch_warnings(record=True) as warning_output:
        test_warning()
        test_warning()
        assert len(warning_output) == 1


get_abaqus_restart_extensions_input = {
    "standard_1": (
        "standard",
        1,
        (".odb", ".prt", ".mdl", ".sim", ".stt", ".res"),
        does_not_raise,
    ),
    "STANDARD_1": (
        "STANDARD",
        1,
        (".odb", ".prt", ".mdl", ".sim", ".stt", ".res"),
        does_not_raise,
    ),
    "standard_2": (
        "standard",
        2,
        (".odb", ".prt", ".mdl.0", ".mdl.1", ".sim", ".stt.0", ".stt.1", ".res"),
        does_not_raise,
    ),
    "standard_11": (
        "standard",
        11,
        (
            ".odb",
            ".prt",
            ".mdl.0",
            ".mdl.1",
            ".mdl.2",
            ".mdl.3",
            ".mdl.4",
            ".mdl.5",
            ".mdl.6",
            ".mdl.7",
            ".mdl.8",
            ".mdl.9",
            ".mdl.10",
            ".sim",
            ".stt.0",
            ".stt.1",
            ".stt.2",
            ".stt.3",
            ".stt.4",
            ".stt.5",
            ".stt.6",
            ".stt.7",
            ".stt.8",
            ".stt.9",
            ".stt.10",
            ".res",
        ),
        does_not_raise,
    ),
    "explicit_1": (
        "explicit",
        1,
        (".odb", ".prt", ".mdl", ".sim", ".stt", ".res", ".abq", ".pac", ".sel"),
        does_not_raise,
    ),
    "EXPLICIT_1": (
        "EXPLICIT",
        1,
        (".odb", ".prt", ".mdl", ".sim", ".stt", ".res", ".abq", ".pac", ".sel"),
        does_not_raise,
    ),
    "explicit_2": (
        "explicit",
        2,
        (".odb", ".prt", ".mdl", ".sim", ".stt", ".res", ".abq", ".pac", ".sel"),
        does_not_raise,
    ),
    "explicit_11": (
        "explicit",
        11,
        (".odb", ".prt", ".mdl", ".sim", ".stt", ".res", ".abq", ".pac", ".sel"),
        does_not_raise,
    ),
    "stahnduurd": (
        "stahnduurd",
        2,
        None,
        pytest.raises(ValueError, match="Unknown solver type: 'stahnduurd'"),
    ),
}


@pytest.mark.parametrize(
    ("solver", "processes", "expected", "outcome"),
    get_abaqus_restart_extensions_input.values(),
    ids=get_abaqus_restart_extensions_input.keys(),
)
def test_get_abaqus_restart_extensions(
    solver: str,
    processes: int,
    expected: tuple[str] | None,
    outcome: contextlib.nullcontext | pytest.RaisesExc,
) -> None:
    with outcome:
        # Test cases include intentional bad argument types. Do not perform static type checks.
        extensions = _utilities._get_abaqus_restart_extensions(
            solver=solver,  # type: ignore[arg-type]
            processes=processes,
        )
        assert extensions == expected
