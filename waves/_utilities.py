"""Internal API module storing project utilities.

Functions that are limited in use to a public API should prefer to raise Python built-in exceptions.

Functions that may be used in a CLI implementation should raise ``RuntimeError`` or a derived class of
:class:`waves.exceptions.WAVESError` to allow the CLI implementation to convert stack-trace/exceptions into STDERR
message and non-zero exit codes.
"""
import os
import shutil
import pathlib
import platform


_exclude_from_namespace = set(globals().keys())


def _quote_spaces_in_path(path: pathlib.Path | str) -> pathlib.Path:
    """Traverse parts of a path and place in double quotes if there are spaces in the part

    >>> import pathlib
    >>> import waves
    >>> path = pathlib.Path("path/directory with space/filename.ext")
    >>> waves.scons_extensions._quote_spaces_in_path(path)
    PosixPath('path/"directory with space"/filename.ext')

    :param path: path to modify as necessary

    :return: Path with parts wrapped in double quotes as necessary
    """
    path = pathlib.Path(path)
    new_path = pathlib.Path(path.root)
    for part in path.parts:
        if " " in part:
            part = f'"{part}"'
        new_path = new_path / part
    return new_path


def search_commands(options: list[str]) -> str | None:
    """Return the first found command in the list of options. Return None if none are found.

    :param list options: executable path(s) to test

    :returns: command absolute path
    """
    command_search = (shutil.which(command) for command in options)
    command_abspath = next((command for command in command_search if command is not None), None)
    return command_abspath


def find_command(options: list[str]) -> str | None:
    """Return first found command in list of options.

    :param options: alternate command options

    :returns: command absolute path

    :raises FileNotFoundError: If no matching command is found
    """
    command_abspath = search_commands(options)
    if command_abspath is None:
        raise FileNotFoundError(f"Could not find any executable on PATH in: {', '.join(options)}")
    return command_abspath


def cubit_os_bin() -> str:
    """Return the OS specific Cubit bin directory name

    Making Cubit importable requires putting the Cubit bin directory on PYTHONPATH. On MacOS, the directory is "MacOS".
    On other systems it is "bin".

    :returns: bin directory name, e.g. "bin" or "MacOS"
    :rtype:
    """
    system = platform.system().lower()
    if system == "darwin":
        bin_directory = "MacOS"
    # TODO: Find the Windows bin directory name, update the function and the test.
    else:
        bin_directory = "bin"
    return bin_directory


def find_cubit_bin(options: list[str], bin_directory: str | None = None) -> pathlib.Path:
    """Provided a few options for the Cubit executable, search for the bin directory.

    Recommend first checking to see if cubit will import.

    :param options: Cubit command options
    :param bin_directory: Cubit's bin directory name. Override the bin directory returned by
        :meth:`waves._utilities.cubit_os_bin`.

    :returns: Cubit bin directory absolute path

    :raise FileNotFoundError: If the Cubit command or bin directory is not found
    """
    if bin_directory is None:
        bin_directory = cubit_os_bin()

    message = "Could not find a Cubit bin directory. Please ensure the Cubit executable is on PATH or provide an " \
              "absolute path to the Cubit executable."

    cubit_command = find_command(options)
    cubit_command = os.path.realpath(cubit_command)
    cubit_bin = pathlib.Path(cubit_command).parent
    if bin_directory in cubit_bin.parts:
        while cubit_bin.name != bin_directory:
            cubit_bin = cubit_bin.parent
    else:
        search = cubit_bin.glob(bin_directory)
        cubit_bin = next((path for path in search if path.name == bin_directory), None)
    if cubit_bin is None:
        raise FileNotFoundError(message)
    return cubit_bin


def tee_subprocess(command: list[str], **kwargs) -> tuple[int, str]:
    """Stream STDOUT to terminal while saving buffer to variable

    :param command: Command to execute provided a list of strings
    :param dict kwargs: Any additional keyword arguments are passed through to subprocess.Popen

    :returns: integer return code, string STDOUT
    """
    from io import StringIO
    import subprocess

    with subprocess.Popen(command, stdout=subprocess.PIPE, bufsize=1, text=True, **kwargs) as process, \
         StringIO() as stdout_buffer:
        for line in process.stdout:
            print(line, end="")
            stdout_buffer.write(line)
        output = stdout_buffer.getvalue()
    return process.returncode, output


# Limit help() and 'from module import *' behavior to the module's public API
_module_objects = set(globals().keys()) - _exclude_from_namespace
__all__ = [name for name in _module_objects if not name.startswith("_")]
