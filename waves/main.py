import argparse
import pathlib
import sys
import subprocess

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
    elif args.subcommand == 'fetch':
        root_directory = _settings._installed_quickstart_directory.parent
        relative_paths = _settings._fetch_subdirectories
        return_code = fetch(args.subcommand, root_directory, relative_paths, args.destination, requested_paths=args.FILE,
                            overwrite=args.overwrite, dry_run=args.dry_run, print_available=args.print_available)
    elif args.subcommand == 'quickstart':
        root_directory = _settings._installed_quickstart_directory.parent
        relative_paths = [_settings._installed_quickstart_directory.name]
        return_code = fetch(args.subcommand, root_directory, relative_paths, args.destination,
                            overwrite=args.overwrite, dry_run=args.dry_run)
    elif args.subcommand == 'visualize':
        return_code = visualization(target=args.TARGET, output_file=args.output_file,
                                    sconstruct=args.sconstruct, print_graphml=args.print_graphml,
                                    exclude_list=args.exclude_list, exclude_regex=args.exclude_regex, 
                                    height=args.height, width=args.width)
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
                                       "(default: %(default)s)")

    quickstart_parser = argparse.ArgumentParser(add_help=False)
    quickstart_parser = subparsers.add_parser('quickstart',
        help="Create an SCons-WAVES project template",
        description="Create an SCons-WAVES project template from the single element compression simulation found in " \
                    "the WAVES tutorials.",
        parents=[quickstart_parser])
    quickstart_parser.add_argument("destination",
        nargs="?",
        help="Destination directory. Unless ``--overwrite`` is specified, conflicting file names in the " \
             "destination will not be copied. (default: PWD)",
        type=pathlib.Path,
        default=pathlib.Path().cwd())
    quickstart_parser.add_argument("--overwrite",
        action="store_true",
        help="Overwrite any existing files (default: %(default)s)")
    quickstart_parser.add_argument("--dry-run",
        action="store_true",
        help="Print the destination tree and exit (default: %(default)s)")

    fetch_parser = argparse.ArgumentParser(add_help=False)
    fetch_parser = subparsers.add_parser('fetch',
        help="Fetch and copy SCons-WAVES modsim template files and directories",
        description="Fetch and copy SCons-WAVES modsim template files and directories. If no ``FILE`` is specified, " \
            "all available files will be created. Directories are recursively copied. ``pathlib.Path`` recursive " \
            "pattern matching is possible. The source path is truncated to use the shortest common file prefix, " \
            "e.g. requesting two files ``common/source/file.1`` and ``common/source/file.2`` will create " \
            "``/destination/file.1`` and ``/destination/file.2``, respectively.",
        parents=[fetch_parser])
    fetch_parser.add_argument("FILE", nargs="*",
                              help=f"modsim template file or directory")
    fetch_parser.add_argument("--destination",
        help="Destination directory. Unless ``--overwrite`` is specified, conflicting file names in the " \
             "destination will not be copied. (default: PWD)",
        type=pathlib.Path,
        default=pathlib.Path().cwd())
    fetch_parser.add_argument("--overwrite",
        action="store_true",
        help="Overwrite any existing files (default: %(default)s)")
    fetch_parser.add_argument("--dry-run",
        action="store_true",
        help="Print the destination tree and exit (default: %(default)s)")
    fetch_parser.add_argument("--print-available",
        action="store_true",
        help="Print available modsim template files and exit (default: %(default)s)")

    visualize_parser = argparse.ArgumentParser(add_help=False)
    visualize_parser = subparsers.add_parser("visualize",
        help="Create an SCons project visualization",
        description="Create a visual representation of the directed acyclic graph used by your SCons project ",
        parents=[visualize_parser])
    visualize_parser.add_argument("TARGET", help=f"SCons target")
    visualize_parser.add_argument("--sconstruct", type=str, default="SConstruct",
        help="Path to SConstruct file (default: %(default)s)")
    visualize_parser.add_argument("-o", "--output-file", type=str,
        help="Path to output image file with an extension supported by matplotlib, e.g. 'visualization.svg' (default: %(default)s)")
    visualize_parser.add_argument("--height", type=int, default=12,
        help="Height of visualization in inches if being saved to a file (default: %(default)s)")
    visualize_parser.add_argument("--width", type=int, default=36,
        help="Width of visualization in inches if being saved to a file (default: %(default)s)")
    visualize_parser.add_argument("-e", "--exclude-list", nargs="*", default=_settings._visualize_exclude,
        help="If a node starts or ends with one of these string literals, do not visualize it (default: %(default)s)")
    visualize_parser.add_argument("-r", "--exclude-regex", type=str,
        help="If a node matches this regular expression, do not visualize it (default: %(default)s)")
    visualize_parser.add_argument("-g", "--print-graphml", dest="print_graphml", action="store_true",
        help="Print the visualization in graphml format (default: %(default)s)")

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
        import webbrowser
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


def fetch(subcommand, root_directory, relative_paths, destination, requested_paths=[],
          overwrite=False, dry_run=False, print_available=False):
    """Thin wrapper on :meth:`waves.fetch.recursive_copy` to provide subcommand specific behavior and STDOUT/STDERR

    Recursively copy requested paths from root_directory/relative_paths directories into destination directory using
    the shortest possible shared source prefix.

    If files exist, report conflicting files and exit with a non-zero return code unless overwrite is specified.

    :param str subcommand: name of the subcommand to report in STDOUT
    :param str root_directory: String or pathlike object for the root_directory directory
    :param list relative_paths: List of string or pathlike objects describing relative paths to search for in
        root_directory
    :param str destination: String or pathlike object for the destination directory
    :param list requested_paths: list of relative path-like objects that subset the files found in the
        ``root_directory`` ``relative_paths``
    :param bool overwrite: Boolean to overwrite any existing files in destination directory
    :param bool dry_run: Print the destination tree and exit. Short circuited by ``print_available``
    :param bool print_available: Print the available source files and exit. Short circuits ``dry_run``
    """
    if not root_directory.is_dir():
        # During "waves quickstart/fetch" sub-command(s), this should only be reached if the package installation structure
        # doesn't match the assumptions in _settings.py. It is used by the Conda build tests as a sign-of-life that the
        # installed directory assumptions are correct.
        print(f"Could not find '{root_directory}' directory", file=sys.stderr)
        return 1
    from waves import fetch
    print(f"{_settings._project_name_short} {subcommand}", file=sys.stdout)
    print(f"Destination directory: '{destination}'", file=sys.stdout)
    return_code = fetch.recursive_copy(root_directory, relative_paths, destination, requested_paths=requested_paths,
                                       overwrite=overwrite, dry_run=dry_run, print_available=print_available)
    return return_code


def visualization(target, sconstruct, exclude_list, exclude_regex, output_file=None, print_graphml=False,
                  height=_settings._visualize_default_height, width=_settings._visualize_default_width):
    """Visualize the directed acyclic graph created by a SCons build

    Uses matplotlib and networkx to build out an acyclic directed graph showing the relationships of the various
    dependencies using boxes and arrows. The visualization can be saved as an svg and graphml output can be printed
    as well.

    :param str target: String specifying an SCons target
    :param str sconstruct: Path to an SConstruct file or parent directory
    :param list exclude_list: exclude nodes starting with strings in this list (e.g. /usr/bin)
    :param str exclude_regex: exclude nodes that match this regular expression
    :param str output_file: File for saving the visualization
    :param bool print_graphml: Whether to print the graph in graphml format
    :param int height: Height of visualization if being saved to a file
    :param int width: Width of visualization if being saved to a file
    """
    from waves import visualize
    sconstruct = pathlib.Path(sconstruct).resolve()
    if not sconstruct.is_file():
        sconstruct = sconstruct / "SConstruct"
    if not sconstruct.exists():
        print(f"\t{sconstruct} does not exist.", file=sys.stderr)
        return 1
    scons_command = [_settings._scons_command, target, f"--sconstruct={sconstruct.name}"]
    scons_command.extend(_settings._scons_visualize_arguments)
    scons_stdout = subprocess.check_output(scons_command, cwd=sconstruct.parent)
    tree_output = scons_stdout.decode("utf-8").split('\n')
    tree_dict = visualize.parse_output(tree_output, exclude_list=exclude_list, exclude_regex=exclude_regex)

    if print_graphml:
        print(tree_dict['graphml'], file=sys.stdout)
    visualize.visualize(tree_dict, output_file, height, width)
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
