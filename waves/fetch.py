import sys
import shutil
import filecmp
import pathlib

from waves import _settings


def available_files(root_directory, relative_paths):
    """Build a list of files at ``relative_paths`` with respect to the root ``root_directory`` directory

    Returns a list of absolute paths and a list of any relative paths that were not found.

    :param str root_directory: Relative or absolute root path to search. Relative paths are converted to absolute paths with
        respect to the current working directory before searching.
    :param list relative_paths: Relative paths to search for. Directories are searched recursively for files.

    :returns: available_files, not_found
    :rtype: tuple of lists
    """
    root_directory = pathlib.Path(root_directory).resolve()

    available_files = []
    not_found = []
    for path in relative_paths:
        absolute_path = root_directory / path
        if absolute_path.is_file():
            available_files.extend(absolute_path)
        elif absolute_path.is_dir():
            file_list = [path for path in absolute_path.rglob("*") if path.is_file()]
            available_files.extend(file_list)
        else:
            not_found.extend(path)
    return available_files, not_found


def recursive_copy(root_directory, relative_paths, destination, overwrite=False, dry_run=False,
                   exclude_patterns=_settings._fetch_exclude_patterns):
    """Recursively copy root_directory directory into destination directory

    If files exist, report conflicting files and exit with a non-zero return code unless overwrite is specified.

    :param str root_directory: String or pathlike object for the root_directory directory
    :param str destination: String or pathlike object for the destination directory
    :param bool overwrite: Boolean to overwrite any existing files in destination directory
    :param bool dry_run: Print the template destination tree and exit
    :param list exclude_patterns: list of strings to exclude from the root_directory directory tree if the path contains a
        matching string.
    """
    root_directory = pathlib.Path(root_directory).resolve()
    destination = pathlib.Path(destination).resolve()
    if not root_directory.exists():
        # During "waves quickstart" commands, this should only be reached if the package installation structure doesn't
        # match the assumptions in _settings.py. It is used by the Conda build tests as a sign-of-life that the
        # assumptions are correct.
        print(f"Could not find '{root_directory}' directory", file=sys.stderr)
        return 1

    source_files, not_found = available_files(root_directory, relative_paths)
    source_files = [path for path in source_files if not any(map(str(path).__contains__, exclude_patterns))]
    if not source_files:
        print(f"Did not find any files in '{root_directory}'", file=sys.stderr)
        return 1

    destination_files = [destination / path.relative_to(root_directory) for path in source_files]

    existing_files = [path for path in destination_files if path.exists()]
    copy_tuples = zip(source_files, destination_files)
    if not overwrite and existing_files:
        copy_tuples = [(source_file, destination_file) for source_file, destination_file in copy_tuples if
                       destination_file not in existing_files]
        print(f"Found conflicting files in destination '{destination}'. Use '--overwrite' to replace existing files " \
              f"with files from '{root_directory}'.", file=sys.stderr)

    # User I/O
    if dry_run:
        print("Files to create:")
        for source_file, destination_file in copy_tuples:
            print(f"\t{destination_file}", file=sys.stdout)
        return 0

    # Do the work if there are any files left to copy
    for source_file, destination_file in copy_tuples:
        # If the root_directory and destination file contents are the same, don't perform unnecessary file I/O
        if not destination_file.exists() or not filecmp.cmp(source_file, destination_file, shallow=False):
            destination_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source_file, destination_file)

    return 0
