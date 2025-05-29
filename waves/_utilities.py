"""Internal API module storing project utilities.

Functions that are limited in use to a public API should prefer to raise Python built-in exceptions.

Functions that may be used in a CLI implementation should raise ``RuntimeError`` or a derived class of
:class:`waves.exceptions.WAVESError` to allow the CLI implementation to convert stack-trace/exceptions into STDERR
message and non-zero exit codes.
"""

import os
import re
import sys
import shutil
import string
import typing
import pathlib
import platform
import warnings
import subprocess

import yaml

from waves import _settings


_exclude_from_namespace = set(globals().keys())


class _AtSignTemplate(string.Template):
    """Use the CMake '@' delimiter in a Python 'string.Template' to avoid clashing with bash variable syntax"""

    delimiter = _settings._template_delimiter


def set_name_substitution(
    original: typing.Union[typing.Iterable[typing.Union[str, pathlib.Path]], str, pathlib.Path],
    replacement: str,
    identifier: str = "set_name",
    suffix: str = "/",
) -> typing.Union[typing.List[typing.Union[str, pathlib.Path]], str, pathlib.Path]:
    """Replace ``@identifier`` with replacement text in a list of strings and pathlib Path objects

    If the original is not a string, Path, or an iterable of strings and Paths, return without modification.

    :param original: List of strings
    :param replacement: substitution string for the identifier
    :param identifier: template identifier to replace, e.g. ``@identifier`` becomes ``replacement``
    :param suffix: to insert after the replacement text

    :returns: string or list of strings with identifier replacements
    """
    mapping = {identifier: f"{replacement}{suffix}"}
    if isinstance(original, str):
        return _AtSignTemplate(original).safe_substitute(mapping)
    elif isinstance(original, pathlib.Path):
        return pathlib.Path(_AtSignTemplate(str(original)).safe_substitute(mapping))
    elif isinstance(original, (list, set, tuple)) and all(isinstance(item, (str, pathlib.Path)) for item in original):
        modified = list()
        for node in original:
            try:
                modified.append(_AtSignTemplate(node).safe_substitute(mapping))
            except TypeError:
                modified.append(pathlib.Path(_AtSignTemplate(str(node)).safe_substitute(mapping)))
        return modified
    else:
        return original


def _quote_spaces_in_path(path: typing.Union[str, pathlib.Path]) -> pathlib.Path:
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


def search_commands(options: typing.Iterable[str]) -> typing.Optional[str]:
    """Return the first found command in the list of options. Return None if none are found.

    :param list options: executable path(s) to test

    :returns: command absolute path
    """
    command_search = (shutil.which(command) for command in options)
    command_abspath = next((command for command in command_search if command is not None), None)
    return command_abspath


def find_command(options: typing.Iterable[str]) -> str:
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


def find_cubit_bin(options: typing.Iterable[str], bin_directory: typing.Optional[str] = None) -> pathlib.Path:
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

    message = (
        "Could not find a Cubit bin directory. Please ensure the Cubit executable is on PATH or provide an "
        "absolute path to the Cubit executable."
    )

    cubit_command = find_command(options)
    cubit_command = os.path.realpath(cubit_command)
    cubit_bin = pathlib.Path(cubit_command).parent
    if bin_directory in cubit_bin.parts:
        while cubit_bin.name != bin_directory:
            cubit_bin = cubit_bin.parent
    else:
        search = cubit_bin.rglob(bin_directory)
        try:
            cubit_bin = next((path for path in search if path.name == bin_directory))
        except StopIteration:
            raise FileNotFoundError(message)
    return cubit_bin


def find_cubit_python(options: typing.Iterable[str], python_command: str = "python3*") -> pathlib.Path:
    """Provided a few options for the Cubit executable, search for the Cubit Python interpreter.

    Recommend first checking to see if cubit will import.

    :param options: Cubit command options
    :param python_command: Cubit's Python executable file basename or ``pathlib.Path.rglob`` pattern

    :returns: Cubit Python intepreter executable absolute path

    :raise FileNotFoundError: If the Cubit command or Cubit Python interpreter is not found
    """
    message = (
        "Could not find a Cubit Python interpreter. Please ensure the Cubit executable is on PATH or provide "
        "an absolute path to the Cubit executable."
    )

    cubit_command = find_command(options)
    cubit_command = os.path.realpath(cubit_command)
    cubit_parent = pathlib.Path(cubit_command).parent
    search = cubit_parent.rglob(python_command)
    try:
        cubit_python = next((path for path in search if path.is_file() and os.access(path, os.X_OK)))
    except StopIteration:
        raise FileNotFoundError(message)
    return cubit_python


def tee_subprocess(command: typing.List[str], **kwargs) -> typing.Tuple[int, str]:
    """Stream STDOUT to terminal while saving buffer to variable

    :param command: Command to execute provided a list of strings
    :param dict kwargs: Any additional keyword arguments are passed through to subprocess.Popen

    :returns: integer return code, string STDOUT
    """
    from io import StringIO
    import subprocess

    with (
        subprocess.Popen(command, stdout=subprocess.PIPE, bufsize=1, text=True, **kwargs) as process,
        StringIO() as stdout_buffer,
    ):
        for line in process.stdout:
            print(line, end="")
            stdout_buffer.write(line)
        output = stdout_buffer.getvalue()
    return process.returncode, output


def return_environment(
    command: str,
    shell: str = "bash",
    string_option: str = "-c",
    separator: str = "&&",
    environment: str = "env -0",
) -> dict:
    """Run a shell command and return the shell environment as a dictionary

    .. code-block::

       {shell} {string_option} "{command} {separator} {environment}"

    .. warning::

       The method may fail if the command produces stdout that does not terminate in a newline. Redirect command output
       away from stdout if this causes problems, e.g. ``command = 'command > /dev/null && command two > /dev/null'`` in
       most shells.

    :param command: the shell command to execute
    :param shell: the shell to use when executing command by absolute or relative path
    :param string_option: the shell's option to execute a string command
    :param separator: the shell's command separator, e.g. ``;`` or ``&&``.
    :param environment: environment command to print environment on STDOUT with null terminated seperators

    :returns: shell environment dictionary

    :raises subprocess.CalledProcessError: When the shell command returns a non-zero exit status
    """
    result = subprocess.run(
        f'{shell} {string_option} "{command} {separator} {environment}"',
        check=True,
        capture_output=True,
        shell=True,
    )
    stdout = result.stdout.decode()
    variables = stdout.split("\x00")
    first_key, first_value = variables[0].rsplit("=", 1)
    if "\n" in first_key:
        first_key = first_key.rsplit("\n")[-1]
    variables[0] = f"{first_key}={first_value}"

    environment = dict()
    for line in variables:
        if line != "":
            key, value = line.split("=", 1)
            environment[key] = value

    return environment


def cache_environment(
    command: str,
    shell: str = "bash",
    cache: typing.Optional[typing.Union[str, pathlib.Path]] = None,
    overwrite_cache: bool = False,
    verbose: bool = False,
) -> dict:
    """Retrieve cached environment dictionary or run a shell command to generate environment dictionary

    .. warning::

       Currently assumes a nix flavored shell: sh, bash, zsh, csh, tcsh. May work with any shell supporting command
       construction as below.

       .. code-block::

          {shell} -c "{command} && env -0"

       The method may fail if the command produces stdout that does not terminate in a newline. Redirect command output
       away from stdout if this causes problems, e.g. ``command = 'command > /dev/null && command two > /dev/null'`` in
       most shells.

    If the environment is created successfully and a cache file is requested, the cache file is *always* written. The
    ``overwrite_cache`` behavior forces the shell ``command`` execution, even when the cache file is present. If the
    ``command`` fails (raising a ``subprocess.CalledProcessError``) the captured output is printed to STDERR before
    re-raising the exception.

    :param command: the shell command to execute
    :param shell: the shell to use when executing command by absolute or relative path
    :param cache: absolute or relative path to read/write a shell environment dictionary. Will be written as YAML
        formatted file regardless of extension.
    :param overwrite_cache: Ignore previously cached files if they exist.
    :param verbose: Print SCons configuration-like action messages when True

    :returns: shell environment dictionary

    :raises subprocess.CalledProcessError: Print the captured output and re-raise exception when the shell command
        returns a non-zero exit status.
    """
    if cache:
        cache = pathlib.Path(cache).resolve()

    if cache and cache.exists() and not overwrite_cache:
        if verbose:
            print(f"Sourcing the shell environment from cached file '{cache}' ...")
        with open(cache, "r") as cache_file:
            environment = yaml.safe_load(cache_file)
    else:
        if verbose:
            print(f"Sourcing the shell environment with command '{command}' ...")
        try:
            environment = return_environment(command, shell=shell)
        except subprocess.CalledProcessError as err:
            print(err.output.decode(), file=sys.stderr)
            raise err

    if cache:
        with open(cache, "w") as cache_file:
            yaml.safe_dump(environment, cache_file)

    return environment


def create_valid_identifier(identifier: str) -> str:
    """Create a valid Python identifier from an arbitray string by replacing invalid characters with underscores

    :param identifier: String to convert to valid Python identifier
    """
    return re.sub(r"\W|^(?=\d)", "_", identifier)


def warn_only_once(function):
    """Decorator to suppress warnings raised by successive function calls

    :param function: The function to wrap

    :returns: function wrapped in the warning suppression logic
    """
    function.already_warned = False

    def wrapper(*args, **kwargs):
        """Wrapper logic for the function warning suppression

        :param args: all positional arguments passed through to wrapped function
        :param kwargs: all keyword arguments passed through to wrapped function
        """
        with warnings.catch_warnings(record=function.already_warned):
            function.already_warned = True
            return function(*args, **kwargs)

    return wrapper


# Limit help() and 'from module import *' behavior to the module's public API
_module_objects = set(globals().keys()) - _exclude_from_namespace
__all__ = [name for name in _module_objects if not name.startswith("_")]
