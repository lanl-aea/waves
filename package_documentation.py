import os
import shutil
import pathlib

prefix = pathlib.Path(os.getenv("PREFIX")).resolve()
sp_dir = pathlib.Path(os.getenv("SP_DIR")).resolve()
pkg_name = os.getenv("PKG_NAME")

man_path = pathlib.Path("build/docs/man").resolve()
html_path = pathlib.Path("build/docs/html-github").resolve()
quickstart_path = pathlib.Path("quickstart").resolve()

new_paths = [
    (prefix / "share/man/man1", man_path),
    (prefix / "man/man1", man_path),
    (sp_dir / pkg_name / "docs", html_path),
    (sp_dir / pkg_name / "quickstart", quickstart_path)
]
for destination, source in new_paths:
    destination.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, destination, symlinks=False, dirs_exist_ok=True)
