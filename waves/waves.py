import argparse
import webbrowser
import pathlib
import sys
import subprocess

from waves import _settings
from waves import __version__


def main():
    """This is the main function that performs actions based on command line arguments.

    :returns: return code
    """
    parser = get_parser()
    args, unknown = parser.parse_known_args()

    if args.subcommand == 'docs':
        open_docs()
    elif args.subcommand == 'build':
        build(args.TARGET, scons_args=unknown, max_iterations=args.max_iterations)
    else:
        parser.print_help()
    return 0


def get_parser():
    """Get parser object for command line options

    :return: parser
    :rtype: ArgumentParser
    """
    main_description = \
        f"Print information about the {_settings._project_name_short.upper()} Conda package and access the " \
         "bundled HTML documentation"
    main_parser = argparse.ArgumentParser(
        description=main_description,
        prog=_settings._project_name_short.lower())

    main_parser.add_argument(
        '-V', '--version',
        action='version',
        version=f'{_settings._project_name_short.upper()} {__version__}')

    subparsers = main_parser.add_subparsers(
        help=f"Specify {_settings._project_name_short.lower()} sub-commands",
        title=f"{_settings._project_name_short} sub-commands",
        description=f"Common {_settings._project_name_short.lower()} sub-commands to specify " \
                    f"{_settings._project_name_short} usage",
        # So args.subcommand will contain the name of the subcommand called
        dest='subcommand')

    docs_parser = argparse.ArgumentParser(add_help=False)
    docs_parser = subparsers.add_parser('docs',
            help=f"Open the {_settings._project_name_short.upper()} HTML documentation",
            description=f"Open the packaged {_settings._project_name_short.upper()} HTML documentation in the  " \
                         "system default web browser",
            parents=[docs_parser])
    docs_parser.add_argument('-p', '--print-local-path',
                             action='version',
                             # Unconventional usage of version argument.
                             # Usage here is to print the docs directory and exit.
                             version=f"{_settings._docs_directory}/index.html",
                             help=f"Print the path to the locally installed documentation index file. " \
                                  f"As an alternative to the docs sub-command, open index.html in a web browser.")

    build_parser = argparse.ArgumentParser(add_help=False)
    build_parser = subparsers.add_parser('build',
        help=f"Thin SCons wrapper",
        description=f"Thin SCons wrapper to programmatically re-run SCons until all targets are reported up-to-date.",
        parents=[build_parser])
    build_parser.add_argument("TARGET", nargs="*",
                              help=f"SCons target list")
    build_parser.add_argument("-m", "--max-iterations", type=int, default=5,
                              help="Maximum number of SCons command iterations")

    return main_parser


def open_docs():
    webbrowser.open(f'{_settings._docs_directory}/index.html')
    return


def build(targets, scons_args=[], max_iterations=5):
    stop_trigger = 'is up to date.'
    scons_command = ['scons']
    scons_command.extend(scons_args)
    if targets:
        scons_command.extend(targets)
    scons_stdout = b"Go boat"
    count = 0
    while stop_trigger not in scons_stdout.decode('utf-8') and count < max_iterations:
        count += 1
        print(f"iteration {count}: '{' '.join(scons_command)}'")
        scons_stdout = subprocess.check_output(scons_command)


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
