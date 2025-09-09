"""OS agnostic search for files with a specified shebang"""

# TODO: Remove custom python script if/when black supports magic file type searches
# https://github.com/psf/black/issues/491

import re
import typing
import pathlib
import argparse


default_shebang = "#!.*python"


def get_parser():
    script_name = pathlib.Path(__file__)
    prog = f"python {script_name.name} "
    parser = argparse.ArgumentParser(description="OS agnostic search for files with a specified shebang", prog=prog)
    parser.add_argument(
        "PATH",
        type=pathlib.Path,
        nargs="+",
    )
    parser.add_argument(
        "--shebang",
        type=str,
        default=default_shebang,
        help="Shebang text to search for on the first line of the file(s) (default %(default)s)",
    )
    parser.add_argument(
        "--exclude-dir",
        nargs="+",
        type=str,
        default=("build", "install", "conda-environment", "conda-pkgs", "pip-build-test"),
        help="Directories to exclude from search (default %(default)s)",
    )
    return parser


def recurse_files(paths: typing.Iterable[pathlib.Path], exclude_dir: typing.Iterable[str]) -> list[pathlib.Path]:
    """Recursively search provided path(s) and return list of files that aren't symlinks

    :param paths: list of paths to search

    :returns: list of file paths
    """
    files = []
    for path in paths:
        if path.is_file() and not path.is_symlink():
            files.append(path)
        elif path.is_dir():
            files.extend(
                [
                    path
                    for path in path.rglob("*")
                    if path.is_file()
                    and not path.is_symlink()
                    and not any(exclude in str(path) for exclude in exclude_dir)
                ]
            )
        else:
            pass
    return files


def find_shebang(path: pathlib.Path, shebang: str = default_shebang) -> None:
    """Print path if the file contains the shebang on the first line

    :param path: file to check for shebang
    :param shebang: shebang regular expression to look for
    """
    with open(path) as infile:
        try:
            first_line = infile.readline()
            if re.match(shebang, first_line):
                print(path)
        except UnicodeDecodeError:
            pass


def main():
    parser = get_parser()
    args = parser.parse_args()
    files = recurse_files(args.PATH, args.exclude_dir)
    files.sort()
    for path in files:
        find_shebang(path, args.shebang)


if __name__ == "__main__":
    main()
