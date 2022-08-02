import argparse
import webbrowser
import pathlib
import sys

# Local modules
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
    main_parser = argparse.ArgumentParser(
        description=f"{_settings._project_name_short} version: {__version__}",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog=_settings._project_name_short.lower())

    main_parser.add_argument(
        '-V', '--version',
        action='version',
        version=f'{_settings._project_name_short} {__version__}')
    
    subparsers = main_parser.add_subparsers(
        help=f"Specify {_settings._project_name_short.lower()} command",
        title=f"{_settings._project_name_short} commands",
        description=f"Common {_settings._project_name_short.lower()} commands to specify {_settings._project_name_short} usage",
        dest='subcommand')  # so args.subcommand will contain the name of the subcommand called
    
    docs_parser = argparse.ArgumentParser(add_help=False)
    docs_parser = subparsers.add_parser('docs', help=f"Open {_settings._project_name_short.upper()} HTML documentation",
                                        description=f"Open the packaged {_settings._project_name_short.upper()} HTML documentation in the system default web browser",
                                        parents=[docs_parser])
    docs_parser.add_argument('-p', '--print-local-path',
                             action='version',
                             version=f"{_settings._docs_directory}/index.html",  # unconventional usage of version argument. Usage here is to print the docs directory and exit
                             help=f"print the path to the locally installed documentation index file. " \
                                  f"As an alternative to the docs subcommand, open index.html in a web browser.")

    return main_parser


def open_docs():
    webbrowser.open(f'{_settings._docs_directory}/index.html')
    return


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
