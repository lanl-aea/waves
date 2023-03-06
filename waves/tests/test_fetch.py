import pathlib
from unittest.mock import patch

import pytest

from waves import fetch


@pytest.mark.unittest
def test_conditional_copy():
    # TODO: write conditional copy unit tests. recursive_copy relies on these tests passing.
    pass


@pytest.mark.unittest
def test_recursive_copy():

    # Dummy quickstart tree
    root_directory = pathlib.Path("/path/to/source")
    source_files = [pathlib.Path("dummy.file1"),
                    pathlib.Path("dummy.file2")]
    source_tree = [root_directory / path for path in source_files]
    destination = pathlib.Path("/path/to/destination")
    destination_tree = [destination / path.relative_to(root_directory) for path in source_tree]
    copy_tuples = tuple(zip(source_tree, destination_tree))
    not_found = []
    available_files_output = (source_tree, not_found)

    # Files in destination tree do not exist. Copy the quickstart file tree.
    with patch("waves.fetch.available_files", return_value=available_files_output), \
         patch("waves.fetch.print_list") as mock_print_list, \
         patch("waves.fetch.conditional_copy") as mock_conditional_copy, \
         patch("pathlib.Path.exists", side_effect=[False, False]), \
         patch("filecmp.cmp", return_value=False):
        return_code = fetch.recursive_copy(root_directory.parent, root_directory.name, destination)
        assert return_code == 0
        mock_print_list.assert_not_called()
        mock_conditional_copy.assert_called_once_with(copy_tuples)

    # Files in destination tree do not exist. Only want the first file. Copy the first file..
    with patch("waves.fetch.available_files", return_value=([source_tree[0]], [])), \
         patch("waves.fetch.print_list") as mock_print_list, \
         patch("waves.fetch.conditional_copy") as mock_conditional_copy, \
         patch("pathlib.Path.exists", side_effect=[False, False]), \
         patch("filecmp.cmp", return_value=False):
        return_code = fetch.recursive_copy(source_tree, destination, requested_paths=[source_files[0]])
        assert return_code == 0
        mock_print_list.assert_not_called()
        mock_conditional_copy.assert_called_once_with((copy_tuples[0], ))

    # Files in destination tree do not exist, but dry-run. Print destination file tree.
    with patch("waves.fetch.available_files", return_value=available_files_output), \
         patch("waves.fetch.print_list") as mock_print_list, \
         patch("waves.fetch.conditional_copy") as mock_conditional_copy, \
         patch("pathlib.Path.exists", side_effect=[False, False]), \
         patch("filecmp.cmp", return_value=False):
        return_code = fetch.recursive_copy(root_directory.parent, root_directory.name, destination, dry_run=True)
        assert return_code == 0
        mock_print_list.assert_called_once_with(destination_tree)
        mock_conditional_copy.assert_not_called()

    # Files in destination tree do not exist, but print_available. Print source file tree.
    with patch("waves.fetch.available_files", return_value=available_files_output), \
         patch("waves.fetch.print_list") as mock_print_list, \
         patch("waves.fetch.conditional_copy") as mock_conditional_copy, \
         patch("pathlib.Path.exists", side_effect=[False, False]), \
         patch("filecmp.cmp", return_value=False):
        return_code = fetch.recursive_copy(root_directory.parent, root_directory.name, destination, print_available=True)
        assert return_code == 0
        mock_print_list.assert_called_once_with(source_files)
        mock_conditional_copy.assert_not_called()

    # All files in destination tree do exist. Don't copy the quickstart file tree.
    with patch("waves.fetch.available_files", return_value=available_files_output), \
         patch("waves.fetch.print_list") as mock_print_list, \
         patch("waves.fetch.conditional_copy") as mock_conditional_copy, \
         patch("pathlib.Path.exists", side_effect=[True, True]), \
         patch("filecmp.cmp", return_value=True):
        return_code = fetch.recursive_copy(root_directory.parent, root_directory.name, destination)
        assert return_code == 0  # Don't error out, just remove destination file from the copy list
        mock_print_list.assert_not_called()
        mock_conditional_copy.assert_called_once_with(())

    # Files in destination tree do exist, we want to overwrite contents, and the files differ. Copy the source file.
    with patch("waves.fetch.available_files", return_value=available_files_output), \
         patch("waves.fetch.print_list") as mock_print_list, \
         patch("waves.fetch.conditional_copy") as mock_conditional_copy, \
         patch("pathlib.Path.exists", side_effect=[True, True]), \
         patch("filecmp.cmp", return_value=False):
        return_code = fetch.recursive_copy(root_directory.parent, root_directory.name, destination, overwrite=True)
        assert return_code == 0
        mock_print_list.assert_not_called()
        mock_conditional_copy.assert_called_once_with(copy_tuples)

    # Files in destination tree do exist, we want to overwrite contents, but the files are the same. Don't copy the
    # source file.
    with patch("waves.fetch.available_files", return_value=available_files_output), \
         patch("waves.fetch.print_list") as mock_print_list, \
         patch("waves.fetch.conditional_copy") as mock_conditional_copy, \
         patch("pathlib.Path.exists", side_effect=[True, True]), \
         patch("filecmp.cmp", return_value=True):
        return_code = fetch.recursive_copy(root_directory.parent, root_directory.name, destination, overwrite=True)
        assert return_code == 0
        mock_print_list.assert_not_called()
        mock_conditional_copy.assert_called_once_with(copy_tuples)

    # Files in destination tree do exist, but we want to overwrite contents and dry-run. Print the quickstart file tree.
    with patch("waves.fetch.available_files", return_value=available_files_output), \
         patch("waves.fetch.print_list") as mock_print_list, \
         patch("waves.fetch.conditional_copy") as mock_conditional_copy, \
         patch("pathlib.Path.exists", side_effect=[True, True]), \
         patch("filecmp.cmp", return_value=True):
        return_code = fetch.recursive_copy(root_directory.parent, root_directory.name, destination,
                                           overwrite=True, dry_run=True)
        assert return_code == 0
        mock_print_list.assert_called_once_with(destination_tree)
        mock_conditional_copy.assert_not_called()
