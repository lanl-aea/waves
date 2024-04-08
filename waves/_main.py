"""Internal module implementing the command line utility behavior

Should raise ``RuntimeError`` or a derived class of :class:`waves.exceptions.WAVESError` to allow
:meth:`waves._main.main` to convert stack-trace/exceptions into STDERR message and non-zero exit codes.
"""
import sys
import pathlib
import argparse

from waves import _settings
from waves import __version__
from waves import _docs
from waves import _fetch
from waves import _visualize
from waves import _build
from waves import _parameter_study
from waves.exceptions import WAVESError


_exclude_from_namespace = set(globals().keys())


def main() -> None:
    """This is the main function that performs actions based on command line arguments."""
    parser = get_parser()
    args, unknown = parser.parse_known_args()

    try:
        if args.subcommand == "docs":
            _docs.main(print_local_path=args.print_local_path)
        elif args.subcommand == "fetch":
            root_directory = _settings._modsim_template_directory.parent
            relative_paths = _settings._fetch_subdirectories
            _fetch.main(
                args.subcommand, root_directory, relative_paths, args.destination,
                requested_paths=args.FILE, tutorial=args.tutorial, overwrite=args.overwrite,
                dry_run=args.dry_run, print_available=args.print_available
            )
        elif args.subcommand == "visualize":
            _visualize.main(
                target=args.TARGET, output_file=args.output_file,
                sconstruct=args.sconstruct, print_graphml=args.print_graphml,
                exclude_list=args.exclude_list, exclude_regex=args.exclude_regex,
                height=args.height, width=args.width, font_size=args.font_size,
                vertical=args.vertical, no_labels=args.no_labels, print_tree=args.print_tree,
                input_file=args.input_file
            )
        elif args.subcommand == "build":
            _build.main(
                args.TARGET, scons_args=unknown, max_iterations=args.max_iterations,
                working_directory=args.working_directory, git_clone_directory=args.git_clone_directory
        )
        elif args.subcommand in _settings._parameter_study_subcommands:
            _parameter_study.main(
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
        "-V", "--version",
        action="version",
        version=f"{_settings._project_name_short.upper()} {__version__}")

    subparsers = main_parser.add_subparsers(
        # So args.subcommand will contain the name of the subcommand called
        title="subcommands",
        metavar="{subcommand}",
        dest="subcommand")

    subparsers.add_parser(
        "docs",
         help=f"Open the {_settings._project_name_short.upper()} HTML documentation",
         description=f"Open the packaged {_settings._project_name_short.upper()} HTML documentation in the  " \
                      "system default web browser",
        parents=[_docs.get_parser()]
    )

    subparsers.add_parser(
        "fetch",
        help="Fetch and copy WAVES modsim template files and directories",
        description="Fetch and copy WAVES modsim template files and directories. If no ``FILE`` is specified, " \
            "all available files will be created. Directories are recursively copied. ``pathlib.Path`` recursive " \
            "pattern matching is possible. The source path is truncated to use the shortest common file prefix, " \
            "e.g. requesting two files ``common/source/file.1`` and ``common/source/file.2`` will create " \
            "``/destination/file.1`` and ``/destination/file.2``, respectively.",
        parents=[_fetch.get_parser()]
    )

    subparsers.add_parser(
        "visualize",
        help="Create an SCons project visualization",
        description="Create a visual representation of the directed acyclic graph used by your SCons project.",
        parents=[_visualize.get_parser()]
    )

    subparsers.add_parser(
        "build",
        help="Thin SCons wrapper",
        description="Thin SCons wrapper to programmatically re-run SCons until all targets are reported up-to-date.",
        parents=[_build.get_parser()]
    )

    for subcommand in _settings._parameter_study_subcommands:
        subparsers.add_parser(
            subcommand,
            description=_settings._parameter_study_description,
            help=f"Create a {subcommand.replace('_', ' ')} parameter study",
            parents=[_parameter_study.get_parser()]
        )

    return main_parser


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover


# Limit help() and 'from module import *' behavior to the module's public API
_module_objects = set(globals().keys()) - _exclude_from_namespace
__all__ = [name for name in _module_objects if not name.startswith("_")]
