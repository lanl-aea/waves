import os
import stat
import argparse
import webbrowser
import pathlib
import sys
import subprocess
import shutil

from waves import _settings
from waves import __version__
from waves import visualize


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
        return_code = quickstart(args.PROJECT_DIRECTORY, overwrite=args.overwrite, dry_run=args.dry_run)
    elif args.subcommand == 'visualize':
        return_code = visualization(target=args.TARGET[0], output_file=args.output_file,
                                project_directory=args.project_directory, print_graphml=args.print_graphml)
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
        f"Provides a minimal SCons build wrapper, access to locally packaged HTML " \
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
        dest='subcommand')

    docs_parser = argparse.ArgumentParser(add_help=False)
    docs_parser = subparsers.add_parser('docs',
            help=f"Open the {_settings._project_name_short.upper()} HTML documentation",
            description=f"Open the packaged {_settings._project_name_short.upper()} HTML documentation in the  " \
                         "system default web browser",
            parents=[docs_parser])
    docs_parser.add_argument('-p', '--print-local-path',
                             action='store_true',
                             help="Print the path to the locally installed documentation index file. " \
                                  "As an alternative to the docs sub-command, open index.html in a web browser " \
                                  "(default: %(default)s)")

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
        nargs="?",
        help="Directory for new project template. Unless ``--overwrite`` is specified, the directory must not " \
             "contain conflicting filenames. (default: PWD).",
        type=pathlib.Path,
        default=pathlib.Path().cwd())
    quickstart_parser.add_argument("--overwrite",
        action="store_true",
        help="Overwrite any existing files (default: %(default)s).")
    quickstart_parser.add_argument("--dry-run",
        action="store_true",
        help="Print the files that would be created and exit (default: %(default)s).")

    visualize_parser = argparse.ArgumentParser(add_help=False)
    visualize_parser = subparsers.add_parser('visualize',
        help="Create an SCons-WAVES project visualization",
        description="Create a visual representation of the directed acyclic graph used by your SCons-WAVES project ",
        parents=[visualize_parser])
    visualize_parser.add_argument("TARGET", nargs="+", help=f"SCons target")
    visualize_parser.add_argument("-p", "--project-directory", type=str, default=str(pathlib.Path().cwd()),
        help='path to SConstruct file')
    visualize_parser.add_argument("-o", "--output-file", type=str, metavar='waves_visualization.svg',
        help='path to output file')
    visualize_parser.add_argument("-g", "--print-graphml", dest='print_graphml', action='store_true',
        help='print the visualization in graphml format')

    return main_parser


def docs(print_local_path=False):

    if print_local_path:
        if _settings._installed_docs_index.exists():
            print(_settings._installed_docs_index, file=sys.stdout)
        else:
            # This should only be reached if the package installation structure doesn't match the assumptions in
            # _settings.py. It is used by the Conda build tests as a sign-of-life that the assumptions are correct.
            print('Could not find package documentation HTML index file', file=sys.stderr)
            return 1
    else:
        webbrowser.open(str(_settings._installed_docs_index))
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
    scons_command = [_settings._scons_command]
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


def quickstart(directory, overwrite=False, dry_run=False):
    """Copy project quickstart template files into directory

    Copies from the project quickstart tree to the directory. If files exist, report conflicting files and exit with a
    non-zero return code unless overwrite is specified.

    :param str directory: String or pathlike object for the new template directory destination
    :param bool overwrite: Boolean to overwrite any existing files in directory destination
    :param bool dry_run: Print the template destination tree and exit
    """

    # Gather source and destination lists
    directory = pathlib.Path(directory).resolve()
    if not _settings._installed_quickstart_directory.exists():
        # This should only be reached if the package installation structure doesn't match the assumptions in
        # _settings.py. It is used by the Conda build tests as a sign-of-life that the assumptions are correct.
        print(f"Could not find {_settings._project_name_short} quickstart directory", file=sys.stderr)
        return 1
    exclude_strings = ["__pycache__", ".pyc", ".sconf_temp", ".sconsign.dblite", "config.log"]
    quickstart_contents = [path for path in _settings._installed_quickstart_directory.rglob("*") if not
                           any(map(str(path).__contains__, exclude_strings))]
    quickstart_dirs = [path for path in quickstart_contents if path.is_dir()]
    quickstart_files = list(set(quickstart_contents) - set(quickstart_dirs))
    if not quickstart_files:
        print(f"Did not find any quickstart files or directories in {_settings._installed_quickstart_directory}",
              file=sys.stderr)
        return 1
    directory_dirs = [directory / path.relative_to(_settings._installed_quickstart_directory)
                      for path in quickstart_dirs]
    directory_files = [directory / path.relative_to(_settings._installed_quickstart_directory)
                       for path in quickstart_files]
    existing_files = [path for path in directory_files if path.exists()]

    # User I/O
    print(f"{_settings._project_name_short} Quickstart", file=sys.stdout)
    print(f"Project root path: '{directory}'", file=sys.stdout)
    if not overwrite and existing_files:
        print(f"Found conflicting files in destination '{directory}':", file=sys.stderr)
        for path in existing_files:
            print(f"\t{path}", file=sys.stderr)
        return 2
    if dry_run:
        print("Files to create:")
        for path in directory_files:
            print(f"\t{path}", file=sys.stdout)
        return 0

    # Do the work
    for path in directory_dirs:
        path.mkdir(parents=True, exist_ok=True)
    for source, destination in zip(quickstart_files, directory_files):
        shutil.copyfile(source, destination)
    return 0


def visualization(target, project_directory, output_file=None, print_graphml=False):
    """Visualize the directed acyclic graph created by a WAVES/SCons build

    Uses matplotlib and networkx to build out an acyclic directed graph showing the relationships of the various
    dependencies using boxes and arrows. The visualization can be saved as an svg and graphml output can be printed
    as well.

    :param str target: String specifying an SCons target
    :param str project_directory: Directory where the WAVES/SCons project can be found
    :param str output_file: File for saving the visualization
    :param bool print_graphml: Whether to print the graph in graphml format
    """
    scons_command = [_settings._scons_command, target]
    scons_command.extend(_settings._scons_visualize_arguments)
    scons_stdout = subprocess.check_output(scons_command, cwd=project_directory)
    tree_output = scons_stdout.decode("utf-8").split('\n')
    tree_dict = visualize.parse_output(tree_output)

    if print_graphml:
        print(tree_dict['graphml'])
    visualize.visualize(tree_dict, output_file)
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
