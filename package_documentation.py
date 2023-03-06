import os
import shutil
import pathlib

prefix = pathlib.Path(os.getenv("PREFIX")).resolve()
sp_dir = pathlib.Path(os.getenv("SP_DIR")).resolve()
pkg_name = os.getenv("PKG_NAME")

man_path = pathlib.Path("build/docs/man").resolve()
html_path_external = pathlib.Path("build/docs/html").resolve()
html_path_internal = pathlib.Path("build/docs/html-internal").resolve()
html_path = html_path_external if html_path_external.exists() else html_path_internal
# TODO: figure out the setuptools and setuptools_scm solution for including data files
quickstart_path = pathlib.Path("quickstart").resolve()
tutorials_path = pathlib.Path("tutorials").resolve()
# FIXME: setuptools claims that these should be included by default, but they aren't
readme_path = pathlib.Path("README.rst").resolve()
pyproject = pathlib.Path("pyproject.toml").resolve()

new_paths = [
    (prefix / "share/man/man1", man_path),
    (prefix / "man/man1", man_path),
    (sp_dir / pkg_name / "docs", html_path),
    (sp_dir / pkg_name / "quickstart", quickstart_path),
    (sp_dir / pkg_name / "tutorials", tutorials_path),
    (sp_dir / pkg_name / "README.rst", readme_path),
    (sp_dir / pkg_name / "pyproject.toml", pyproject),
]
for destination, source in new_paths:
    assert source.exists()
    print(f"Copying '{source}' to '{destination}'...")
    if destination.is_file():
        shutil.copy2(source, destination, follow_symlinks=True)
    else:
        destination.mkdir(parents=True, exist_ok=True)
        shutil.copytree(source, destination, symlinks=False, dirs_exist_ok=True)
