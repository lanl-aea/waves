import pathlib


def _quote_spaces_in_path(path):
    """Traverse parts of a path and place in double quotes if there are spaces in the part

    >>> import pathlib
    >>> import waves
    >>> path = pathlib.Path("path/directory with space/filename.ext")
    >>> waves.scons_extensions._quote_spaces_in_path(path)
    PosixPath('path/"directory with space"/filename.ext')

    :param pathlib.Path path: path to modify as necessary

    :return: Path with parts wrapped in double quotes as necessary
    :rtype: pathlib.Path
    """
    path = pathlib.Path(path)
    new_path = pathlib.Path(path.root)
    for part in path.parts:
        if " " in part:
            part = f'"{part}"'
        new_path = new_path / part
    return new_path
