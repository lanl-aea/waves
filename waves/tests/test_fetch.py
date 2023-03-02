import pathlib
from unittest.mock import patch

import pytest

from waves import fetch

@pytest.mark.unittest
def test_quickstart():

    # Dummy quickstart tree
    root_directory = pathlib.Path("/path/to/source")
    quickstart_tree = [root_directory / "dummy.file"]
    destination = pathlib.Path("/path/to/destination")
    destination_tree = [destination / path.relative_to(root_directory) for path in quickstart_tree]
    not_found = []
    available_files_output = (quickstart_tree, not_found)

    # Files in destination tree do not exist. Copy the quickstart file tree.
    with patch("shutil.copyfile") as mock_copyfile, \
         patch("pathlib.Path.mkdir") as mock_mkdir, \
         patch("waves.fetch.available_files", return_value=available_files_output), \
         patch("waves.fetch.print_list") as mock_print_list, \
         patch("pathlib.Path.exists", side_effect=[False, False]), \
         patch("filecmp.cmp", return_value=False):
        return_code = fetch.recursive_copy(root_directory.parent, root_directory.name, destination)
        assert return_code == 0
        mock_print_list.assert_not_called()
        mock_mkdir.assert_called_once()
        mock_copyfile.assert_called_once()

    # Files in destination tree do not exist, but dry-run. Print destination file tree.
    with patch("shutil.copyfile") as mock_copyfile, \
         patch("pathlib.Path.mkdir") as mock_mkdir, \
         patch("waves.fetch.available_files", return_value=available_files_output), \
         patch("waves.fetch.print_list") as mock_print_list, \
         patch("pathlib.Path.exists", side_effect=[False, False]), \
         patch("filecmp.cmp", return_value=False):
        return_code = fetch.recursive_copy(root_directory.parent, root_directory.name, destination, dry_run=True)
        assert return_code == 0
        mock_print_list.assert_called_once_with(destination_tree)
        mock_mkdir.assert_not_called()
        mock_copyfile.assert_not_called()

    # Files in destination tree do not exist, but print_available. Print source file tree.
    with patch("shutil.copyfile") as mock_copyfile, \
         patch("pathlib.Path.mkdir") as mock_mkdir, \
         patch("waves.fetch.available_files", return_value=available_files_output), \
         patch("waves.fetch.print_list") as mock_print_list, \
         patch("pathlib.Path.exists", side_effect=[False, False]), \
         patch("filecmp.cmp", return_value=False):
        return_code = fetch.recursive_copy(root_directory.parent, root_directory.name, destination, print_available=True)
        assert return_code == 0
        mock_print_list.assert_called_once_with(quickstart_tree)
        mock_mkdir.assert_not_called()
        mock_copyfile.assert_not_called()

    # All files in destination tree do exist. Don't copy the quickstart file tree.
    with patch("shutil.copyfile") as mock_copyfile, \
         patch("pathlib.Path.mkdir") as mock_mkdir, \
         patch("waves.fetch.available_files", return_value=available_files_output), \
         patch("waves.fetch.print_list") as mock_print_list, \
         patch("pathlib.Path.exists", side_effect=[True, True]), \
         patch("filecmp.cmp", return_value=True):
        return_code = fetch.recursive_copy(root_directory.parent, root_directory.name, destination)
        assert return_code == 0  # Don't error out, just remove destination file from the copy list
        mock_print_list.assert_not_called()
        mock_mkdir.assert_not_called()
        mock_copyfile.assert_not_called()

    # File in destination tree does exist, we want to overwrite contents, and the files differ. Copy the source file.
    with patch("shutil.copyfile") as mock_copyfile, \
         patch("pathlib.Path.mkdir") as mock_mkdir, \
         patch("waves.fetch.available_files", return_value=available_files_output), \
         patch("waves.fetch.print_list") as mock_print_list, \
         patch("pathlib.Path.exists", side_effect=[True, True]), \
         patch("filecmp.cmp", return_value=False):
        return_code = fetch.recursive_copy(root_directory.parent, root_directory.name, destination, overwrite=True)
        assert return_code == 0
        mock_print_list.assert_not_called()
        mock_mkdir.assert_called_once()
        mock_copyfile.assert_called_once()

    # File in destination tree does exist, we want to overwrite contents, but the files are the same. Don't copy the
    # source file.
    with patch("shutil.copyfile") as mock_copyfile, \
         patch("pathlib.Path.mkdir") as mock_mkdir, \
         patch("waves.fetch.available_files", return_value=available_files_output), \
         patch("waves.fetch.print_list") as mock_print_list, \
         patch("pathlib.Path.exists", side_effect=[True, True]), \
         patch("filecmp.cmp", return_value=True):
        return_code = fetch.recursive_copy(root_directory.parent, root_directory.name, destination, overwrite=True)
        assert return_code == 0
        mock_print_list.assert_not_called()
        mock_mkdir.assert_not_called()
        mock_copyfile.assert_not_called()

    # Files in destination tree do exist, but we want to overwrite contents and dry-run. Print the quickstart file tree.
    with patch("shutil.copyfile") as mock_copyfile, \
         patch("pathlib.Path.mkdir") as mock_mkdir, \
         patch("waves.fetch.available_files", return_value=available_files_output), \
         patch("waves.fetch.print_list") as mock_print_list, \
         patch("pathlib.Path.exists", side_effect=[True, True]), \
         patch("filecmp.cmp", return_value=True):
        return_code = fetch.recursive_copy(root_directory.parent, root_directory.name, destination,
                                           overwrite=True, dry_run=True)
        assert return_code == 0
        mock_print_list.assert_called_once_with(destination_tree)
        mock_mkdir.assert_not_called()
        mock_copyfile.assert_not_called()
