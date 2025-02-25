import sys
import pathlib
from unittest.mock import Mock
from unittest.mock import patch, call
from contextlib import nullcontext as does_not_raise

import pytest

from waves import _fetch
from waves import _settings
from waves.exceptions import ChoicesError
from waves._tests.common import platform_check


testing_windows, root_fs, testing_macos = platform_check()

if testing_windows:
    root_directory = pathlib.Path("C:/path/to/source")
    destination = pathlib.Path("C:/path/to/destination")
else:
    root_directory = pathlib.Path("/path/to/source")
    destination = pathlib.Path("/path/to/destination")
source_files = [pathlib.Path("dummy.file1"), pathlib.Path("dummy.file2")]

one_file_source_tree = [root_directory / source_files[0]]
one_file_destination_tree = [destination / source_files[0]]
one_file_copy_tuples = ((one_file_source_tree[0], one_file_destination_tree[0]),)

two_file_source_tree = [root_directory / path for path in source_files]
two_file_destination_tree = [destination / path for path in source_files]


def test_fetch():
    # Test the "unreachable" exit code used as a sign-of-life that the installed package structure assumptions in
    # _settings.py are correct.
    with (
        patch("waves._fetch.recursive_copy") as mock_recursive_copy,
        pytest.raises(RuntimeError),
    ):
        try:
            _fetch.main(
                "dummy_subcommand",
                pathlib.Path("/directory/assumptions/are/wrong"),
                ["dummy/relative/path"],
                "/dummy/destination",
            )
        finally:
            mock_recursive_copy.assert_not_called()


def test_fetch_settings():
    """Check that the implemented tutorial settings and the static type hints are consistent.

    The type hints and implemented integer checks are forced to be consistent in the fetch module, but the type hints
    ``typing.Literal`` can't be built from the settings tutorial path dictionary keys. Unit test to avoid out-of-sync
    programmatic errors between settings variables.
    """
    assert tuple(_settings._tutorial_paths.keys()) == _settings._allowable_tutorial_numbers


conditional_copy_input = {
    "one new file": (  # File does not exist
        one_file_copy_tuples,
        [False],
        [False],
        one_file_copy_tuples[0],
    ),
    "one different file": (  # File does exist, but it's different from the source file
        one_file_copy_tuples,
        [True],
        [False],
        one_file_copy_tuples[0],
    ),
    "one identical file": (  # File exists and is identical to source file
        one_file_copy_tuples,
        [True],
        [True],
        None,
    ),
    "one missing (different) file": (  # File doesn't exist and is identical to source file. Should never actually occur
        one_file_copy_tuples,
        [False],
        [True],
        one_file_copy_tuples[0],
    ),
}


@pytest.mark.parametrize(
    "copy_tuples, exists_side_effect, filecmp_side_effect, copyfile_call",
    conditional_copy_input.values(),
    ids=conditional_copy_input.keys(),
)
def test_conditional_copy(copy_tuples, exists_side_effect, filecmp_side_effect, copyfile_call):
    with (
        patch("pathlib.Path.exists", side_effect=exists_side_effect),
        patch("filecmp.cmp", side_effect=filecmp_side_effect),
        patch("pathlib.Path.mkdir") as mock_mkdir,
        patch("shutil.copyfile") as mock_copyfile,
    ):
        _fetch.conditional_copy(copy_tuples)
        if copyfile_call:
            mock_mkdir.assert_called_once()
            mock_copyfile.assert_called_once_with(*copyfile_call)
        else:
            mock_copyfile.assert_not_called()


available_files_input = {
    "one file, str": (
        "/path/to/source",
        "dummy.file1",
        [True],
        [False],
        [],
        one_file_source_tree,
        [],
        None,
    ),
    "one file, list": (
        "/path/to/source",
        ["dummy.file1"],
        [True],
        [False],
        [],
        one_file_source_tree,
        [],
        None,
    ),
    "one file, not found": (
        "/path/to/source",
        ["dummy.file1"],
        [False],
        [False],
        [[]],
        [],
        ["dummy.file1"],
        "dummy.file1",
    ),
    "two files": (
        "/path/to/source",
        ["dummy.file2", "dummy.file1"],
        [True, True],
        [],
        [],
        two_file_source_tree,
        [],
        None,
    ),
    "one directory, one file": (
        "/path/to",
        "source",
        [False, True],
        [True],
        [one_file_source_tree],
        one_file_source_tree,
        [],
        "*",
    ),
    "one directory, two files": (
        "/path/to",
        "source",
        [False, True, True],
        [True],
        [two_file_source_tree],
        two_file_source_tree,
        [],
        "*",
    ),
    "two files, rglob pattern": (
        "/path/to/source",
        ["dummy.file*"],
        [False, True, True],
        [False],
        [two_file_source_tree],
        two_file_source_tree,
        [],
        "dummy.file*",
    ),
}


@pytest.mark.parametrize(
    "root_directory, relative_paths, is_file_side_effect, is_dir_side_effect, rglob_side_effect, expected_files, expected_missing, mock_rglob_argument",  # noqa: E501
    available_files_input.values(),
    ids=available_files_input.keys(),
)
def test_available_files(
    root_directory,
    relative_paths,
    is_file_side_effect,
    is_dir_side_effect,
    rglob_side_effect,
    expected_files,
    expected_missing,
    mock_rglob_argument,
):
    with (
        patch("pathlib.Path.is_file", side_effect=is_file_side_effect),
        patch("pathlib.Path.is_dir", side_effect=is_dir_side_effect),
        patch("pathlib.Path.rglob", side_effect=rglob_side_effect) as mock_rglob,
    ):
        available_files, not_found = _fetch.available_files(root_directory, relative_paths)
        assert available_files == expected_files
        assert not_found == expected_missing
        if mock_rglob_argument:
            mock_rglob.assert_called_once_with(mock_rglob_argument)
        else:
            mock_rglob.assert_not_called()


build_source_files_input = {
    "one file not matched": (
        "/path/to/source",
        ["dummy.file1"],
        ["notamatch"],
        (one_file_source_tree, []),
        one_file_source_tree,
    ),
    "one file matched": (
        "/path/to/source",
        ["dummy.file1"],
        ["dummy"],
        (one_file_source_tree, []),
        [],
    ),
    "two files, one matched": (
        "/path/to/source",
        ["dummy.file1", "matched"],
        ["matched"],
        ([one_file_source_tree[0], pathlib.Path("/path/to/source/matched")], []),
        one_file_source_tree,
    ),
}


@pytest.mark.parametrize(
    "root_directory, relative_paths, exclude_patterns, available_files_side_effect, expected_source_files",
    build_source_files_input.values(),
    ids=build_source_files_input.keys(),
)
def test_build_source_files(
    root_directory, relative_paths, exclude_patterns, available_files_side_effect, expected_source_files
):
    with patch("waves._fetch.available_files", return_value=available_files_side_effect):
        source_files, not_found = _fetch.build_source_files(
            root_directory, relative_paths, exclude_patterns=exclude_patterns
        )
        assert source_files == expected_source_files


expected_path = root_directory
longest_common_path_prefix_input = {
    "no list": ([], expected_path, pytest.raises(RuntimeError)),
    "one file, str": (str(one_file_source_tree[0]), expected_path, pytest.raises(ValueError)),
    "one file, path": (one_file_source_tree[0], expected_path, pytest.raises(TypeError)),
    "one file, list": (one_file_source_tree, expected_path, does_not_raise()),
    "two files": (two_file_source_tree, expected_path, does_not_raise()),
}


@pytest.mark.parametrize(
    "file_list, expected_path, outcome",
    longest_common_path_prefix_input.values(),
    ids=longest_common_path_prefix_input.keys(),
)
def test_longest_common_path_prefix(file_list, expected_path, outcome):
    with outcome:
        try:
            path_prefix = _fetch.longest_common_path_prefix(file_list)
            assert path_prefix == expected_path
        finally:
            pass


build_destination_files_input = {
    "two files, one exists": (
        "/path/to/destination",
        two_file_source_tree,
        [False, True],
        two_file_destination_tree,
        [two_file_destination_tree[1]],
    )
}


@pytest.mark.parametrize(
    "destination, requested_paths, exists_side_effect, expected_destination_files, expected_existing_files",
    build_destination_files_input.values(),
    ids=build_destination_files_input.keys(),
)
def test_build_destination_files(
    destination, requested_paths, exists_side_effect, expected_destination_files, expected_existing_files
):
    with patch("pathlib.Path.exists", side_effect=exists_side_effect):
        destination_files, existing_files = _fetch.build_destination_files(destination, requested_paths)
        assert destination_files == expected_destination_files
        assert existing_files == expected_existing_files


build_copy_tuples_input = {
    "two files, one exists, overwrite": (
        "/path/to/destination",
        two_file_source_tree,
        True,
        (two_file_destination_tree, [two_file_destination_tree[1]]),
        list(zip(two_file_source_tree, two_file_destination_tree)),
    ),
    "two files, one exists, no overwrite": (
        "/path/to/destination",
        two_file_source_tree,
        False,
        (two_file_destination_tree, [two_file_destination_tree[1]]),
        list(zip([two_file_source_tree[0]], [two_file_destination_tree[0]])),
    ),
}


@pytest.mark.parametrize(
    "destination, requested_paths_resolved, overwrite, build_destination_files_side_effect, expected_copy_tuples",
    build_copy_tuples_input.values(),
    ids=build_copy_tuples_input.keys(),
)
def test_build_copy_tuples(
    destination, requested_paths_resolved, overwrite, build_destination_files_side_effect, expected_copy_tuples
):
    with patch("waves._fetch.build_destination_files", return_value=build_destination_files_side_effect):
        copy_tuples = _fetch.build_copy_tuples(destination, requested_paths_resolved, overwrite=overwrite)
        assert copy_tuples == expected_copy_tuples


def test_print_list():
    test_list = ["one", "two"]

    # Default arugments
    with patch("builtins.print") as mock_print:
        _fetch.print_list(test_list)
        mock_print.assert_has_calls(
            [
                call("\tone", file=sys.stdout),
                call("\ttwo", file=sys.stdout),
            ]
        )

    nondefault_args = {"prefix": " ", "stream": sys.stderr}
    with patch("builtins.print") as mock_print:
        _fetch.print_list(test_list, **nondefault_args)
        mock_print.assert_has_calls(
            [
                call(" one", file=sys.stderr),
                call(" two", file=sys.stderr),
            ]
        )


@pytest.mark.parametrize(
    "root_directory, source_files, source_tree, destination_tree, tutorial",
    [
        (root_directory, source_files, two_file_source_tree, two_file_destination_tree, None),
        (root_directory, source_files, two_file_source_tree, two_file_destination_tree, 6),
    ],
)
def test_recursive_copy(root_directory, source_files, source_tree, destination_tree, tutorial):

    # Dummy modsim_template tree
    copy_tuples = list(zip(source_tree, destination_tree))
    not_found = []
    available_files_output = (source_tree, not_found)
    single_file_requested = ([source_tree[0]], not_found)
    bad_file_requests = [pathlib.Path("notfound")]
    bad_file_requested = ([], bad_file_requests)

    # Files in destination tree do not exist. Copy the modsim_template file tree.
    with (
        patch("waves._fetch.build_source_files", return_value=available_files_output),
        patch("waves._fetch.print_list") as mock_print_list,
        patch("waves._fetch.conditional_copy") as mock_conditional_copy,
        patch("pathlib.Path.exists", side_effect=[False, False]),
        patch("filecmp.cmp", return_value=False),
        does_not_raise(),
    ):
        _fetch.recursive_copy(root_directory.parent, root_directory.name, destination)
        mock_print_list.assert_not_called()
        mock_conditional_copy.assert_called_once_with(copy_tuples)

    # Files in destination tree do not exist. Only want the first file. Copy the first file..
    with (
        patch("waves._fetch.build_source_files", side_effect=[available_files_output, single_file_requested]),
        patch("waves._fetch.print_list") as mock_print_list,
        patch("waves._fetch.conditional_copy") as mock_conditional_copy,
        patch("pathlib.Path.exists", side_effect=[False, False]),
        patch("filecmp.cmp", return_value=False),
        does_not_raise(),
    ):
        _fetch.recursive_copy(
            root_directory.parent, root_directory.name, destination, requested_paths=[source_files[0]]
        )
        mock_print_list.assert_not_called()
        mock_conditional_copy.assert_called_once_with([copy_tuples[0]])

    # Files in destination tree do not exist, but dry-run. Print destination file tree.
    with (
        patch("waves._fetch.build_source_files", return_value=available_files_output),
        patch("waves._fetch.print_list") as mock_print_list,
        patch("waves._fetch.conditional_copy") as mock_conditional_copy,
        patch("pathlib.Path.exists", side_effect=[False, False]),
        patch("filecmp.cmp", return_value=False),
        does_not_raise(),
    ):
        _fetch.recursive_copy(root_directory.parent, root_directory.name, destination, dry_run=True)
        mock_print_list.assert_called_once_with(destination_tree)
        mock_conditional_copy.assert_not_called()

    # Files in destination tree do not exist, but print_available. Print source file tree.
    with (
        patch("waves._fetch.build_source_files", return_value=available_files_output),
        patch("waves._fetch.print_list") as mock_print_list,
        patch("waves._fetch.conditional_copy") as mock_conditional_copy,
        patch("pathlib.Path.exists", side_effect=[False, False]),
        patch("filecmp.cmp", return_value=False),
        does_not_raise(),
    ):
        _fetch.recursive_copy(root_directory.parent, root_directory.name, destination, print_available=True)
        mock_print_list.assert_called_once_with(source_files)
        mock_conditional_copy.assert_not_called()

    # All files in destination tree do exist. Don't copy the modsim_template file tree.
    # Don't error out, just remove destination file from the copy list
    with (
        patch("waves._fetch.build_source_files", return_value=available_files_output),
        patch("waves._fetch.print_list") as mock_print_list,
        patch("waves._fetch.conditional_copy") as mock_conditional_copy,
        patch("pathlib.Path.exists", side_effect=[True, True]),
        patch("filecmp.cmp", return_value=True),
        does_not_raise(),
    ):
        _fetch.recursive_copy(root_directory.parent, root_directory.name, destination)
        mock_print_list.assert_not_called()
        mock_conditional_copy.assert_called_once_with([])

    # Files in destination tree do exist, we want to overwrite contents, and the files differ. Copy the source file.
    with (
        patch("waves._fetch.build_source_files", return_value=available_files_output),
        patch("waves._fetch.print_list") as mock_print_list,
        patch("waves._fetch.conditional_copy") as mock_conditional_copy,
        patch("pathlib.Path.exists", side_effect=[True, True]),
        patch("filecmp.cmp", return_value=False),
        does_not_raise(),
    ):
        _fetch.recursive_copy(root_directory.parent, root_directory.name, destination, overwrite=True)
        mock_print_list.assert_not_called()
        mock_conditional_copy.assert_called_once_with(copy_tuples)

    # Files in destination tree do exist, we want to overwrite contents, but the files are the same. Don't copy the
    # source file.
    with (
        patch("waves._fetch.build_source_files", return_value=available_files_output),
        patch("waves._fetch.print_list") as mock_print_list,
        patch("waves._fetch.conditional_copy") as mock_conditional_copy,
        patch("pathlib.Path.exists", side_effect=[True, True]),
        patch("filecmp.cmp", return_value=True),
        does_not_raise(),
    ):
        _fetch.recursive_copy(root_directory.parent, root_directory.name, destination, overwrite=True)
        mock_print_list.assert_not_called()
        mock_conditional_copy.assert_called_once_with(copy_tuples)

    # Files in destination tree do exist, but we want to overwrite contents and dry-run.
    # Print the modsim_template file tree.
    with (
        patch("waves._fetch.build_source_files", return_value=available_files_output),
        patch("waves._fetch.print_list") as mock_print_list,
        patch("waves._fetch.conditional_copy") as mock_conditional_copy,
        patch("pathlib.Path.exists", side_effect=[True, True]),
        patch("filecmp.cmp", return_value=True),
        does_not_raise(),
    ):
        _fetch.recursive_copy(root_directory.parent, root_directory.name, destination, overwrite=True, dry_run=True)
        mock_print_list.assert_called_once_with(destination_tree)
        mock_conditional_copy.assert_not_called()

    # Testing tutorial argument behavior..
    with (
        patch("waves._fetch.build_source_files", return_value=available_files_output),
        patch("waves._fetch.print_list") as mock_print_list,
        patch("waves._fetch.extend_requested_paths") as mock_extend,
        patch("waves._fetch.conditional_copy"),
        patch("pathlib.Path.exists", side_effect=[False, False]),
        patch("filecmp.cmp", return_value=False),
        does_not_raise(),
    ):
        _fetch.recursive_copy(root_directory.parent, root_directory.name, destination, tutorial=tutorial)
        mock_print_list.assert_not_called()
        if tutorial is not None:
            mock_extend.assert_called_once()
        else:
            mock_extend.assert_not_called()

    # Requested source files do not exist or do not resolve
    with (
        patch("waves._fetch.build_source_files", side_effect=[available_files_output, bad_file_requested]),
        patch("waves._fetch.print_list") as mock_print_list,
        patch("waves._fetch.conditional_copy") as mock_conditional_copy,
        patch("pathlib.Path.exists", side_effect=[False, False]),
        patch("filecmp.cmp", return_value=False),
        pytest.raises(RuntimeError),
    ):
        try:
            _fetch.recursive_copy(
                root_directory.parent,
                root_directory.name,
                destination,
                requested_paths=bad_file_requests,
            )
        finally:
            mock_print_list.assert_not_called()
            mock_conditional_copy.assert_not_called()


def test_extend_requested_paths():
    # Testing accepted tutorial keys
    for tutorial_num in _settings._tutorial_paths.keys():
        mock_list = Mock()
        _fetch.extend_requested_paths(mock_list, tutorial_num)
        assert mock_list.extend.call_count == tutorial_num + 1

    # testing key that does not exist
    with pytest.raises(ChoicesError):
        _fetch.extend_requested_paths([], "shouldRaiseError")
