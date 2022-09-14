import argparse
import webbrowser
import pathlib
import sys
import subprocess
import shutil

from waves import _settings
from waves import __version__


def main():
    """This is the main function that performs actions based on command line arguments.

    :returns: return code
    """
    return_code = None
    parser = get_parser()
    args, unknown = parser.parse_known_args()

    if args.subcommand == 'docs':
        return_code = docs(print_local_path=args.print_local_path)
    elif args.subcommand == 'build':
        return_code = build(args.TARGET, scons_args=unknown, max_iterations=args.max_iterations,
                            working_directory=args.working_directory, git_clone_directory=args.git_clone_directory)
    elif args.subcommand == 'quickstart':
        return_code = quickstart(args.PROJECT_DIRECTORY)
    else:
        parser.print_help()

    if return_code:
        return return_code
    else:
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
                             action='store_true',
                             help=f"Print the path to the locally installed documentation index file. " \
                                  f"As an alternative to the docs sub-command, open index.html in a web browser.")

    build_parser = argparse.ArgumentParser(add_help=False)
    build_parser = subparsers.add_parser('build',
        help="Thin SCons wrapper",
        description="Thin SCons wrapper to programmatically re-run SCons until all targets are reported up-to-date.",
        parents=[build_parser])
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
                                       "(default: %(default)s).")

    quickstart_parser = argparse.ArgumentParser(add_help=False)
    quickstart_parser = subparsers.add_parser('quickstart',
        help="Create an SCons-WAVES project template",
        description="Create an SCons-WAVES project template from the single element compression simulation found in " \
                    "the WAVES tutorials.",
        parents=[quickstart_parser])
    quickstart_parser.add_argument("PROJECT_DIRECTORY",
        nargs='?',
        help="Directory for new project template (default: PWD).",
        type=pathlib.Path,
        default=pathlib.Path().cwd())


    return main_parser


def docs(print_local_path=False):

    if print_local_path:
        if _settings._installed_docs_index.exists():
            print(_settings._installed_docs_index, file=sys.stdout)
        else:
            # This should only be reached if the package installation structure doesn't match the assumptions in
            # _settings.py. It is used by the Conda build tests as a sign-of-life that the assumptions are correct.
            print('Could not find package documentation HTML index file')
            return 1
    else:
        webbrowser.open(_settings._installed_docs_index)
    return 0


def build(targets, scons_args=[], max_iterations=5, working_directory=None, git_clone_directory=None):
    """Submit an iterative SCons command

    SCons command is re-submitted until SCons reports that the target 'is up to date.' or the iteration count is
    reached. If multiple targets are submitted, they are executed sequentially in the order provided.

    :param list targets: list of SCons targets (positional arguments)
    :param list scons_args: list of SCons arguments
    :param int max_iterations: maximum number of iterations before the iterative loop is terminated
    :param str working_directory: Change the SCons command working directory
    """
    if not targets:
        print("At least one target must be provided", file=sys.stderr)
        return 1
    if git_clone_directory:
        current_directory = pathlib.Path().cwd().resolve()
        git_clone_directory = pathlib.Path(git_clone_directory).resolve()
        git_clone_directory.mkdir(parents=True, exist_ok=True)
        working_directory = str(git_clone_directory)
        command = ["git", "clone", "--no-hardlinks", str(current_directory), working_directory]
        git_clone_stdout = subprocess.check_output(command)
    stop_trigger = "is up to date."
    scons_command = ["scons"]
    scons_command.extend(scons_args)
    for target in targets:
        scons_stdout = b"Go boat"
        count = 0
        command = scons_command + [target]
        while stop_trigger not in scons_stdout.decode("utf-8"):
            count += 1
            if count > max_iterations:
                print(f"Exceeded maximum iterations '{max_iterations}' before finding '{stop_trigger}'", file=sys.stderr)
                return 2
            print(f"iteration {count}: '{' '.join(command)}'", file=sys.stdout)
            scons_stdout = subprocess.check_output(command, cwd=working_directory)

    return 0


def quickstart(directory=''):

    # User I/O
    print(f"{_settings._project_name_short} Quickstart", file=sys.stdout)
    directory = pathlib.Path(directory).resolve()
    # TODO: future versions can be more subtle and only error out when directory content filenames clash with the
    # quickstart files.
    if directory.exists() and any(directory.iterdir()):
        print(f"Project root path: '{directory}' exists and is non-empty. Please specify an empty or new directory.",
              file=sys.stderr)
        return 1
    else:
        print(f"Project root path: '{directory}'", file=sys.stdout)
    if _settings._installed_quickstart_directory.exists():
        quickstart_contents = list(_settings._installed_quickstart_directory.iterdir())
        print("Copying the following to project root path: ", file=sys.stdout)
        [print(f"\t{item}", file=sys.stdout) for item in quickstart_contents]
    else:
        # This should only be reached if the package installation structure doesn't match the assumptions in
        # _settings.py. It is used by the Conda build tests as a sign-of-life that the assumptions are correct.
        print('Could not find package quickstart directory')
        return 1

    # Do the work
    shutil.copytree(_settings._installed_quickstart_directory, directory)


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
