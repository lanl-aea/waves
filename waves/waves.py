import argparse
import webbrowser
import pathlib
import sys

from waves import _settings
from waves import __version__


def main():
    """This is the main function that performs actions based on command line arguments.
    
    :returns: return code
    """
    parser = get_parser()
    args = parser.parse_args()
    
    if args.subcommand == 'docs':
        open_docs()
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
        title=f"{_settings._project_name_short} commands",
        description=f"Common {_settings._project_name_short.lower()} sub-commands to specify {_settings._project_name_short} usage",
        dest='subcommand')  # so args.subcommand will contain the name of the subcommand called
    
    docs_parser = argparse.ArgumentParser(add_help=False)
    docs_parser = subparsers.add_parser('docs', help=f"Open the {_settings._project_name_short.upper()} HTML documentation",
                                        description=f"Open the packaged {_settings._project_name_short.upper()} HTML documentation in the system default web browser",
                                        parents=[docs_parser])
    docs_parser.add_argument('-p', '--print-local-path',
                             action='version',
                             version=f"{_settings._docs_directory}/index.html",  # unconventional usage of version argument. Usage here is to print the docs directory and exit
                             help=f"Print the path to the locally installed documentation index file. " \
                                  f"As an alternative to the docs sub-command, open index.html in a web browser.")

    return main_parser


def open_docs():
    webbrowser.open(f'{_settings._docs_directory}/index.html')
    return


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
