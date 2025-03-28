import os
import sys
import shutil
import pathlib
import argparse


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--prefix",
        type=pathlib.Path,
        default=None,
        help=(
            "Installation environment prefix. "
            "If 'None', will try to use environment variable 'PREFIX' (default: %(default)s)",
        ),
    )
    parser.add_argument(
        "--sp-dir",
        type=pathlib.Path,
        default=None,
        help=(
            "Installation environment site-packages full path, including prefix. "
            "If 'None', will try to use environment variable 'SP_DIR' (default: %(default)s)"
        ),
    )
    parser.add_argument(
        "--pkg-name",
        default=None,
        help="Package name. If 'None', will try to use environment variable 'PKG_NAME' (default: %(default)s)",
    )
    parser.add_argument(
        "--man-page",
        type=pathlib.Path,
        default=pathlib.Path("build/docs/man/waves.1"),
        help="Path to man page (default: %(default)s)",
    )
    return parser


def validate_input(prefix, sp_dir, pkg_name):
    """Validate arguments and raise exceptions when

    :raises RuntimeError: prefix, sp_dir, or pkg_name are None or empty
    :raises FileNotFoundError: prefix or sp_dir directories do not exist
    """
    if not prefix:
        raise RuntimeError("PREFIX not specified or not found in the environment variable 'PREFIX'")
    if not prefix.is_dir():
        raise FileNotFoundError("PREFIX '{prefix}' is not a directory")
    if not sp_dir:
        raise RuntimeError("SP_DIR not specified or not found in the environment variable 'SP_DIR'")
    if not sp_dir.is_dir():
        raise FileNotFoundError("SP_DIR '{sp_dir}' is not a directory")
    if not pkg_name:
        raise RuntimeError("PKG_NAME not specified or not found in the environment variable 'PKG_NAME'")


def copy_paths(destination, source):
    """Copy files and recursively copy directories

    :raises FileNotFoundError: if source does not exist
    """
    if not source.exists():
        raise FileNotFoundError(f"'{source}' does not exist")
    print(f"Copying '{source}' to '{destination}'...")
    if source.is_file():
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination, follow_symlinks=True)
    else:
        destination.mkdir(parents=True, exist_ok=True)
        shutil.copytree(
            source,
            destination,
            symlinks=False,
            dirs_exist_ok=True,
            ignore=shutil.ignore_patterns(".doctrees", "*.doctree", ".buildinfo"),
        )


def main():
    parser = get_parser()
    args = parser.parse_args()

    prefix = args.prefix if args.prefix is not None else pathlib.Path(os.getenv("PREFIX")).resolve()
    sp_dir = args.sp_dir if args.sp_dir is not None else pathlib.Path(os.getenv("SP_DIR")).resolve()
    pkg_name = args.pkg_name if args.pkg_name is not None else os.getenv("PKG_NAME")

    validate_input(prefix, sp_dir, pkg_name)

    man_page = args.man_page.resolve()
    html_path_external = pathlib.Path("build/docs/html").resolve()
    html_path_internal = pathlib.Path("build/docs/html-internal").resolve()
    html_path = html_path_external if html_path_external.exists() else html_path_internal
    # TODO: figure out the setuptools and setuptools_scm solution for including data files
    # FIXME: setuptools claims that these should be included by default, but they aren't
    readme_path = pathlib.Path("README.rst").resolve()
    pyproject = pathlib.Path("pyproject.toml").resolve()

    new_paths = [
        (prefix / "share/man/man1", man_page),
        (prefix / "man/man1", man_page),
        (sp_dir / pkg_name / "docs", html_path),
        (sp_dir / pkg_name / "README.rst", readme_path),
        (sp_dir / pkg_name / "pyproject.toml", pyproject),
    ]
    for destination, source in new_paths:
        try:
            copy_paths(destination, source)
        except (RuntimeError, FileNotFoundError) as err:
            sys.exit(err)


if __name__ == "__main__":
    main()  # pragma: no cover
