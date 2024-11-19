"""Internal API module implementing the ``build`` subcommand behavior.

Should raise ``RuntimeError`` or a derived class of :class:`waves.exceptions.WAVESError` to allow the CLI implementation
to convert stack-trace/exceptions into STDERR message and non-zero exit codes.
"""

import sys
import typing
import pathlib
import argparse

from waves import _settings
from waves import _utilities


_exclude_from_namespace = set(globals().keys())


def get_parser() -> argparse.ArgumentParser:
    """Return a 'no-help' parser for the build subcommand

    :return: parser
    """
    parser = argparse.ArgumentParser(add_help=False)

    parser.add_argument(
        "TARGET",
        nargs="+",
        help=f"SCons target(s)",
    )
    parser.add_argument(
        "-m",
        "--max-iterations",
        type=int,
        default=5,
        help="Maximum number of SCons command iterations (default: %(default)s)",
    )

    directory_group = parser.add_mutually_exclusive_group()
    directory_group.add_argument(
        "--working-directory",
        type=str,
        default=None,
        help=argparse.SUPPRESS,
    )
    directory_group.add_argument(
        "-g",
        "--git-clone-directory",
        type=str,
        default=None,
        # fmt: off
        help="Perform a full local git clone operation to the specified directory before executing the scons "
             "command, ``git clone --no-hardlinks ${PWD} ${GIT_CLONE_DIRECTORY}`` (default: %(default)s)",
        # fmt: on
    )

    return parser


def main(
    targets: list,
    scons_args: typing.Optional[list] = None,
    max_iterations: int = 5,
    working_directory: typing.Union[str, pathlib.Path, None] = None,
    git_clone_directory: typing.Union[str, pathlib.Path, None] = None,
) -> None:
    """Submit an iterative SCons command

    SCons command is re-submitted until SCons reports that the target 'is up to date.' or the iteration count is
    reached.

    :param targets: list of SCons targets (positional arguments)
    :param scons_args: list of SCons arguments
    :param max_iterations: Maximum number of iterations before the iterative loop is terminated
    :param working_directory: Change the SCons command working directory
    :param git_clone_directory: Destination directory for a Git clone operation
    """

    if not scons_args:
        scons_args = []
    if not targets:
        raise RuntimeError("At least one target must be provided")
    if git_clone_directory:
        current_directory = pathlib.Path().cwd().resolve()
        git_clone_directory = pathlib.Path(git_clone_directory).resolve()
        git_clone_directory.mkdir(parents=True, exist_ok=True)
        working_directory = str(git_clone_directory)
        command = ["git", "clone", "--no-hardlinks", str(current_directory), working_directory]
        git_clone_return_code, git_clone_stdout = _utilities.tee_subprocess(command)
        if git_clone_return_code != 0:
            raise RuntimeError(f"command '{' '.join(command)}' failed")
    stop_trigger = "is up to date."
    scons_command = [_settings._scons_command]
    scons_command.extend(scons_args)
    command = scons_command + targets

    scons_stdout = "Go boat"
    trigger_count = 0
    count = 0
    while trigger_count < len(targets):
        count += 1
        if count > max_iterations:
            raise RuntimeError(
                f"Exceeded maximum iterations '{max_iterations}' before finding '{stop_trigger}' " "for every target"
            )
        print(
            f"\n{_settings._project_name_short.lower()} build iteration {count}: '{' '.join(command)}'\n",
            file=sys.stdout,
        )
        scons_return_code, scons_stdout = _utilities.tee_subprocess(command, cwd=working_directory)
        if scons_return_code != 0:
            raise RuntimeError(f"command '{' '.join(command)}' failed")
        trigger_count = scons_stdout.count(stop_trigger)


# Limit help() and 'from module import *' behavior to the module's public API
_module_objects = set(globals().keys()) - _exclude_from_namespace
__all__ = [name for name in _module_objects if not name.startswith("_")]
