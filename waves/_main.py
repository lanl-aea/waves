"""Internal module implementing the command line utility behavior

Should raise ``RuntimeError`` or a derived class of :class:`waves.exceptions.WAVESError` to allow
:meth:`waves._main.main` to convert stack-trace/exceptions into STDERR message and non-zero exit codes.
"""
import sys
import pathlib
import argparse
import subprocess

from waves import _settings
from waves import __version__
from waves import _parameter_study
from waves import _visualize
from waves import _fetch
from waves.exceptions import WAVESError


_exclude_from_namespace = set(globals().keys())


def main() -> None:
    """This is the main function that performs actions based on command line arguments."""
    parser = get_parser()
    args, unknown = parser.parse_known_args()

    try:
        if args.subcommand == 'docs':
            docs(print_local_path=args.print_local_path)
        elif args.subcommand == 'build':
            build(args.TARGET, scons_args=unknown, max_iterations=args.max_iterations,
                  working_directory=args.working_directory, git_clone_directory=args.git_clone_directory)
        elif args.subcommand == 'fetch':
            root_directory = _settings._modsim_template_directory.parent
            relative_paths = _settings._fetch_subdirectories
            _fetch.main(
                args.subcommand, root_directory, relative_paths, args.destination,
                requested_paths=args.FILE, tutorial=args.tutorial, overwrite=args.overwrite,
                dry_run=args.dry_run, print_available=args.print_available
            )
        elif args.subcommand == 'visualize':
            _visualize.main(
                target=args.TARGET, output_file=args.output_file,
                sconstruct=args.sconstruct, print_graphml=args.print_graphml,
                exclude_list=args.exclude_list, exclude_regex=args.exclude_regex,
                height=args.height, width=args.width, font_size=args.font_size,
                vertical=args.vertical, no_labels=args.no_labels, print_tree=args.print_tree,
                input_file=args.input_file
            )
        elif args.subcommand in _settings._parameter_study_subcommands:
            _parameter_study.parameter_study(
                args.subcommand, args.INPUT_FILE,
                output_file_template=args.OUTPUT_FILE_TEMPLATE,
                output_file=args.OUTPUT_FILE,
                output_file_type=args.output_file_type,
                set_name_template=args.SET_NAME_TEMPLATE,
                previous_parameter_study=args.PREVIOUS_PARAMETER_STUDY,
                overwrite=args.overwrite,
                dryrun=args.dryrun,
                write_meta=args.write_meta
            )
        else:
            parser.print_help()
    except (WAVESError, RuntimeError) as err:
        sys.exit(err)


def get_parser() -> argparse.ArgumentParser:
    """Get parser object for command line options

    :return: parser
    """
    main_description = \
        f"Provides a parameter generator, minimal SCons build wrapper, access to locally packaged HTML " \
         "documentation, and modsim template file generator."
    main_parser = argparse.ArgumentParser(
        description=main_description,
        prog=_settings._project_name_short.lower())

    main_parser.add_argument(
        '-V', '--version',
        action='version',
        version=f'{_settings._project_name_short.upper()} {__version__}')

    subparsers = main_parser.add_subparsers(
        # So args.subcommand will contain the name of the subcommand called
        title="subcommands",
        metavar="{subcommand}",
        dest="subcommand")

    docs_parser = subparsers.add_parser(
        'docs',
         help=f"Open the {_settings._project_name_short.upper()} HTML documentation",
         description=f"Open the packaged {_settings._project_name_short.upper()} HTML documentation in the  " \
                      "system default web browser"
    )
    docs_parser.add_argument('-p', '--print-local-path',
                             action='store_true',
                             help="Print the path to the locally installed documentation index file. " \
                                  "As an alternative to the docs sub-command, open index.html in a web browser " \
                                  "(default: %(default)s)")

    fetch_parser = subparsers.add_parser(
        'fetch',
        help="Fetch and copy WAVES modsim template files and directories",
        description="Fetch and copy WAVES modsim template files and directories. If no ``FILE`` is specified, " \
            "all available files will be created. Directories are recursively copied. ``pathlib.Path`` recursive " \
            "pattern matching is possible. The source path is truncated to use the shortest common file prefix, " \
            "e.g. requesting two files ``common/source/file.1`` and ``common/source/file.2`` will create " \
            "``/destination/file.1`` and ``/destination/file.2``, respectively.",
        parents=[_fetch.get_parser()]
    )

    visualize_parser = subparsers.add_parser(
        "visualize",
        help="Create an SCons project visualization",
        description="Create a visual representation of the directed acyclic graph used by your SCons project.",
        parents=[_visualize.get_parser()]
    )

    build_parser = subparsers.add_parser(
        'build',
        help="Thin SCons wrapper",
        description="Thin SCons wrapper to programmatically re-run SCons until all targets are reported up-to-date."
    )
    build_parser.add_argument("TARGET", nargs="+",
                              help=f"SCons target list")
    build_parser.add_argument("-m", "--max-iterations", type=int, default=5,
                              help="Maximum number of SCons command iterations (default: %(default)s)")
    directory_group = build_parser.add_mutually_exclusive_group()
    directory_group.add_argument("--working-directory", type=str, default=None,
                                 help=argparse.SUPPRESS)
    directory_group.add_argument("-g", "--git-clone-directory", type=str, default=None,
                                  help="Perform a full local git clone operation to the specified directory before " \
                                       "executing the scons command, " \
                                       "``git clone --no-hardlinks ${PWD} ${GIT_CLONE_DIRECTORY}`` " \
                                       "(default: %(default)s)")

    for subcommand in _settings._parameter_study_subcommands:
        subparsers.add_parser(
            subcommand,
            description=_settings._parameter_study_description,
            help=f"Create a {subcommand.replace('_', ' ')} parameter study",
            parents=[_parameter_study.parameter_study_parser()]
        )

    return main_parser


def docs(print_local_path: bool = False) -> None:
    """Open the package HTML documentation in the system default web browser or print the path to the documentation
    index file.

    :param print_local_path: Flag to print the local path to terminal instead of calling the default web browser
    """

    if print_local_path:
        if _settings._installed_docs_index.exists():
            print(_settings._installed_docs_index, file=sys.stdout)
        else:
            # This should only be reached if the package installation structure doesn't match the assumptions in
            # _settings.py. It is used by the Conda build tests as a sign-of-life that the assumptions are correct.
            raise RuntimeError('Could not find package documentation HTML index file')
    else:
        import webbrowser
        webbrowser.open(str(_settings._installed_docs_index))


def build(targets: list, scons_args: list | None = None, max_iterations: int = 5,
          working_directory: str | pathlib.Path | None = None,
          git_clone_directory: str | pathlib.Path | None = None) -> None:
    """Submit an iterative SCons command

    SCons command is re-submitted until SCons reports that the target 'is up to date.' or the iteration count is
    reached.

    :param targets: list of SCons targets (positional arguments)
    :param scons_args: list of SCons arguments
    :param max_iterations: Maximum number of iterations before the iterative loop is terminated
    :param working_directory: Change the SCons command working directory
    :param git_clone_directory: Destination directory for a Git clone operation
    """
    from waves._utilities import tee_subprocess

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
        git_clone_return_code, git_clone_stdout = tee_subprocess(command)
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
            raise RuntimeError(f"Exceeded maximum iterations '{max_iterations}' before finding '{stop_trigger}' "
                                "for every target")
        print(f"\n{_settings._project_name_short.lower()} build iteration {count}: '{' '.join(command)}'\n",
              file=sys.stdout)
        scons_return_code, scons_stdout = tee_subprocess(command, cwd=working_directory)
        if scons_return_code != 0:
            raise RuntimeError(f"command '{' '.join(command)}' failed")
        trigger_count = scons_stdout.count(stop_trigger)


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover


# Limit help() and 'from module import *' behavior to the module's public API
_module_objects = set(globals().keys()) - _exclude_from_namespace
__all__ = [name for name in _module_objects if not name.startswith("_")]
