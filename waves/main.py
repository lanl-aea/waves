import sys
import pathlib
import argparse
import subprocess

from waves import _settings
from waves import __version__
from waves import _parameter_study


_exclude_from_namespace = set(globals().keys())


def main() -> int:
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
        root_directory = _settings._modsim_template_directory.parent
        relative_paths = _settings._fetch_subdirectories
        return_code = fetch(args.subcommand, root_directory, relative_paths, args.destination,
                            requested_paths=args.FILE, tutorial=args.tutorial, overwrite=args.overwrite,
                            dry_run=args.dry_run, print_available=args.print_available)
    elif args.subcommand == 'quickstart':
        root_directory = _settings._modsim_template_directory.parent
        relative_paths = [_settings._modsim_template_directory.name]
        return_code = fetch(args.subcommand, root_directory, relative_paths, args.destination,
                            overwrite=args.overwrite, dry_run=args.dry_run)
    elif args.subcommand == 'visualize':
        return_code = visualization(target=args.TARGET, output_file=args.output_file,
                                    sconstruct=args.sconstruct, print_graphml=args.print_graphml,
                                    exclude_list=args.exclude_list, exclude_regex=args.exclude_regex,
                                    height=args.height, width=args.width, font_size=args.font_size,
                                    vertical=args.vertical, no_labels=args.no_labels, print_tree=args.print_tree,
                                    input_file=args.input_file)
    elif args.subcommand in _settings._parameter_study_subcommands:
        return_code = _parameter_study.parameter_study(
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

    if return_code:
        return return_code
    else:
        return 0


def get_parser() -> argparse.ArgumentParser:
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
        title="subcommands",
        metavar="{subcommand}",
        dest="subcommand")

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

    fetch_parser = argparse.ArgumentParser(add_help=False)
    fetch_parser = subparsers.add_parser('fetch',
        help="Fetch and copy WAVES modsim template files and directories",
        description="Fetch and copy WAVES modsim template files and directories. If no ``FILE`` is specified, " \
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
    fetch_parser.add_argument("--tutorial",
        help="Fetch all necessary files for specified tutorial. Appends to the positional FILE requests.",
        type=int,
        choices=_settings._tutorial_paths.keys())
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
        help="Path to output image file with an extension supported by matplotlib, e.g. 'visualization.svg' " \
             "(default: %(default)s)")
    visualize_parser.add_argument("--height", type=int, default=12,
        help="Height of visualization in inches if being saved to a file (default: %(default)s)")
    visualize_parser.add_argument("--width", type=int, default=36,
        help="Width of visualization in inches if being saved to a file (default: %(default)s)")
    visualize_parser.add_argument("--font-size", type=int, default=_settings._visualize_default_font_size,
        help="Font size of file names in points (default: %(default)s)")
    visualize_parser.add_argument("-e", "--exclude-list", nargs="*", default=_settings._visualize_exclude,
        help="If a node starts or ends with one of these string literals, do not visualize it (default: %(default)s)")
    visualize_parser.add_argument("-r", "--exclude-regex", type=str,
        help="If a node matches this regular expression, do not visualize it (default: %(default)s)")
    print_group = visualize_parser.add_mutually_exclusive_group()
    print_group.add_argument("-g", "--print-graphml", dest="print_graphml", action="store_true",
        help="Print the visualization in graphml format (default: %(default)s)")
    print_group.add_argument("--print-tree", action="store_true",
        help="Print the output of the scons tree command to the screen (default: %(default)s)")
    visualize_parser.add_argument("--vertical", action="store_true",
        help="Display the graph in a vertical layout (default: %(default)s)")
    visualize_parser.add_argument("-n", "--no-labels", action="store_true",
        help="Create visualization without labels on the nodes (default: %(default)s)")
    visualize_parser.add_argument("--input-file", type=str,
        help="Path to text file with output from scons tree command (default: %(default)s). Scons target must "
             "still be specified and must be present in the input file.")

    quickstart_parser = argparse.ArgumentParser(add_help=False)
    quickstart_parser = subparsers.add_parser('quickstart',
        description="Create an WAVES project template from the rectangle compression simulation found in " \
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

    for subcommand in _settings._parameter_study_subcommands:
        subparsers.add_parser(
            subcommand,
            description=_settings._parameter_study_description,
            help=f"Create a {subcommand.replace('_', ' ')} parameter study",
            parents=[_parameter_study.parameter_study_parser()]
        )

    return main_parser


def docs(print_local_path: bool = False) -> int:
    """Open the package HTML documentation in the system default web browser or print the path to the documentation
    index file.

    :param print_local_path: Flag to print the local path to terminal instead of calling the default web browser

    :returns: return code
    """

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


def build(targets: list, scons_args: list | None = None, max_iterations: int = 5,
          working_directory: str | pathlib.Path | None = None,
          git_clone_directory: str | pathlib.Path | None = None) -> int:
    """Submit an iterative SCons command

    SCons command is re-submitted until SCons reports that the target 'is up to date.' or the iteration count is
    reached. If multiple targets are submitted, they are executed sequentially in the order provided.

    :param targets: list of SCons targets (positional arguments)
    :param scons_args: list of SCons arguments
    :param max_iterations: Maximum number of iterations before the iterative loop is terminated
    :param working_directory: Change the SCons command working directory
    :param git_clone_directory: Destination directory for a Git clone operation

    :returns: return code
    """
    from waves._utilities import tee_subprocess

    if not scons_args:
        scons_args = []
    if not targets:
        print("At least one target must be provided", file=sys.stderr)
        return 1
    if git_clone_directory:
        current_directory = pathlib.Path().cwd().resolve()
        git_clone_directory = pathlib.Path(git_clone_directory).resolve()
        git_clone_directory.mkdir(parents=True, exist_ok=True)
        working_directory = str(git_clone_directory)
        command = ["git", "clone", "--no-hardlinks", str(current_directory), working_directory]
        git_clone_return_code, git_clone_stdout = tee_subprocess(command)
        if git_clone_return_code != 0:
            print(f"command '{' '.join(command)}' failed", file=sys.stderr)
            return 3
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
            print(f"Exceeded maximum iterations '{max_iterations}' before finding '{stop_trigger}' for every target",
                  file=sys.stderr)
            return 2
        print(f"\n{_settings._project_name_short.lower()} build iteration {count}: '{' '.join(command)}'\n",
              file=sys.stdout)
        scons_return_code, scons_stdout = tee_subprocess(command, cwd=working_directory)
        if scons_return_code != 0:
            print(f"command '{' '.join(command)}' failed", file=sys.stderr)
            return 3
        trigger_count = scons_stdout.count(stop_trigger)

    return 0


def fetch(subcommand: str, root_directory: str | pathlib.Path, relative_paths: list[str | pathlib.Path],
          destination: str | pathlib.Path, requested_paths: list[str | pathlib.Path] | None = None,
          tutorial: int | None = None, overwrite: bool = False, dry_run: bool = False, print_available: bool = False) -> int:
    """Thin wrapper on :meth:`waves.fetch.recursive_copy` to provide subcommand specific behavior and STDOUT/STDERR

    Recursively copy requested paths from root_directory/relative_paths directories into destination directory using
    the shortest possible shared source prefix.

    If files exist, report conflicting files and exit with a non-zero return code unless overwrite is specified.

    :param subcommand: name of the subcommand to report in STDOUT
    :param root_directory: String or pathlike object for the root_directory directory
    :param relative_paths: List of string or pathlike objects describing relative paths to search for in
        root_directory
    :param destination: String or pathlike object for the destination directory
    :param requested_paths: list of relative path-like objects that subset the files found in the
        ``root_directory`` ``relative_paths``
    :param tutorial: Integer to fetch all necessary files for the specified tutorial number
    :param overwrite: Boolean to overwrite any existing files in destination directory
    :param dry_run: Print the destination tree and exit. Short circuited by ``print_available``
    :param print_available: Print the available source files and exit. Short circuits ``dry_run``

    :returns: return code
    """
    if not requested_paths:
        requested_paths = []
    if not root_directory.is_dir():
        # During "waves quickstart/fetch" sub-command(s), this should only be reached if the package installation
        # structure doesn't match the assumptions in _settings.py. It is used by the Conda build tests as a
        # sign-of-life that the installed directory assumptions are correct.
        print(f"Could not find '{root_directory}' directory", file=sys.stderr)
        return 1

    from waves import _fetch

    print(f"{_settings._project_name_short} {subcommand}", file=sys.stdout)
    print(f"Destination directory: '{destination}'", file=sys.stdout)
    return_code = _fetch.recursive_copy(root_directory, relative_paths, destination, requested_paths=requested_paths,
                                       tutorial=tutorial, overwrite=overwrite, dry_run=dry_run,
                                       print_available=print_available)

    return return_code


def visualization(target: str, sconstruct: str | pathlib.Path, exclude_list: list[str], exclude_regex: str,
                  output_file: str | pathlib.Path | None = None, print_graphml: bool = False,
                  height: int = _settings._visualize_default_height, width: int = _settings._visualize_default_width,
                  font_size: int = _settings._visualize_default_font_size, vertical: bool = False,
                  no_labels: bool = False, print_tree: bool = False,
                  input_file: str | pathlib.Path | None = None) -> int:
    """Visualize the directed acyclic graph created by a SCons build

    Uses matplotlib and networkx to build out an acyclic directed graph showing the relationships of the various
    dependencies using boxes and arrows. The visualization can be saved as an svg and graphml output can be printed
    as well.

    :param target: String specifying an SCons target
    :param sconstruct: Path to an SConstruct file or parent directory
    :param exclude_list: exclude nodes starting with strings in this list (e.g. /usr/bin)
    :param exclude_regex: exclude nodes that match this regular expression
    :param output_file: File for saving the visualization
    :param print_graphml: Whether to print the graph in graphml format
    :param height: Height of visualization if being saved to a file
    :param width: Width of visualization if being saved to a file
    :param font_size: Font size of node labels
    :param vertical: Specifies a vertical layout of graph instead of the default horizontal layout
    :param no_labels: Don't print labels on the nodes of the visualization
    :param print_tree: Print the text output of the scons --tree command to the screen
    :param input_file: Path to text file storing output from scons tree command

    :returns: return code
    """
    from waves import _visualize
    sconstruct = pathlib.Path(sconstruct).resolve()
    if not sconstruct.is_file():
        sconstruct = sconstruct / "SConstruct"
    if not sconstruct.exists() and not input_file:
        print(f"\t{sconstruct} does not exist.", file=sys.stderr)
        return 1
    tree_output = ""
    if input_file:
        input_file = pathlib.Path(input_file)
        if not input_file.exists():
            print(f"\t{input_file} does not exist.", file=sys.stderr)
            return 1
        else:
            tree_output = input_file.read_text()
    else:
        scons_command = [_settings._scons_command, target, f"--sconstruct={sconstruct.name}"]
        scons_command.extend(_settings._scons_visualize_arguments)
        scons_stdout = subprocess.check_output(scons_command, cwd=sconstruct.parent)
        tree_output = scons_stdout.decode("utf-8")
    if print_tree:
        print(tree_output)
        return 0
    tree_dict = _visualize.parse_output(tree_output.split('\n'), exclude_list=exclude_list, exclude_regex=exclude_regex)
    if not tree_dict['nodes']:  # If scons tree or input_file is not in the expected format the nodes will be empty
        print(f"Unexpected SCons tree format or missing target. Use SCons "
              f"options '{' '.join(_settings._scons_visualize_arguments)}' or "
              f"the ``visualize --print-tree`` option to generate the input file.", file=sys.stderr)
        return 1

    if print_graphml:
        print(tree_dict['graphml'], file=sys.stdout)
        return 0
    _visualize.visualize(tree_dict, output_file, height, width, font_size, vertical, no_labels)


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover


# Limit help() and 'from module import *' behavior to the module's public API
_module_objects = set(globals().keys()) - _exclude_from_namespace
__all__ = [name for name in _module_objects if not name.startswith("_")]
