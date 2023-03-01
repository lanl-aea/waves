import sys
import shutil
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
    # Gather source and destination lists
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

    # User I/O
    if not overwrite and existing_files:
        print(f"Found conflicting files in destination '{destination}':", file=sys.stderr)
        for path in existing_files:
            print(f"\t{path}", file=sys.stderr)
        return 2
    if dry_run:
        print("Files to create:")
        for path in destination_files:
            print(f"\t{path}", file=sys.stdout)
        return 0

    # Do the work
    for path in destination_dirs:
        path.mkdir(parents=True, exist_ok=True)
    for source, destination in zip(source_files, destination_files):
        shutil.copyfile(source, destination)
    return 0
