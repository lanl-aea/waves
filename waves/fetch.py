import sys
import shutil
import pathlib


def recursive_copy(directory, overwrite=False, dry_run=False):
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

