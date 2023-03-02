import sys
import shutil
import filecmp
import pathlib

from waves import _settings


def recursive_copy(source, destination, overwrite=False, dry_run=False,
                   exclude_patterns=_settings._fetch_exclude_patterns):
    """Recursively copy source directory into destination directory

    If files exist, report conflicting files and exit with a non-zero return code unless overwrite is specified.

    :param str source: String or pathlike object for the source directory
    :param str destination: String or pathlike object for the destination directory
    :param bool overwrite: Boolean to overwrite any existing files in destination directory
    :param bool dry_run: Print the template destination tree and exit
    :param list exclude_patterns: list of strings to exclude from the source directory tree if the path contains a
        matching string.
    """
    source = pathlib.Path(source).resolve()
    destination = pathlib.Path(destination).resolve()
    if not source.exists():
        # During "waves quickstart" commands, this should only be reached if the package installation structure doesn't
        # match the assumptions in _settings.py. It is used by the Conda build tests as a sign-of-life that the
        # assumptions are correct.
        print(f"Could not find '{source}' source directory", file=sys.stderr)
        return 1

    source_contents = [path for path in source.rglob("*") if not
                       any(map(str(path).__contains__, exclude_patterns))]
    source_dirs = [path for path in source_contents if path.is_dir()]
    source_files = list(set(source_contents) - set(source_dirs))
    if not source_files:
        print(f"Did not find any files in {source}", file=sys.stderr)
        return 1

    destination_dirs = [destination / path.relative_to(source) for path in source_dirs]
    destination_files = [destination / path.relative_to(source) for path in source_files]

    existing_files = [path for path in destination_files if path.exists()]
    copy_tuples = zip(source_files, destination_files)
    if not overwrite and existing_files:
        copy_tuples = [(source_file, destination_file) for source_file, destination_file in copy_tuples if
                       destination_file not in existing_files]
        print(f"Found conflicting files in destination '{destination}'. Use '--overwrite' to replace existing files " \
              f"with files from source '{source}'.", file=sys.stderr)

    # User I/O
    if dry_run:
        print("Files to create:")
        for source_file, destination_file in copy_tuples:
            print(f"\t{destination_file}", file=sys.stdout)
        return 0

    # Do the work if there are any files left to copy
    for source_file, destination_file in copy_tuples:
        # If the source and destination file contents are the same, don't perform unnecessary file I/O
        if not destination_file.exists() or not filecmp.cmp(source_file, destination_file, shallow=False):
            source_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source_file, destination_file)

    return 0
