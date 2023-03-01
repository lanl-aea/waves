import pathlib
from unittest.mock import patch

import pytest

from waves import fetch
from waves import _settings

_settings._installed_quickstart_directory


@pytest.mark.unittest
def test_quickstart():

    # Dummy quickstart tree
    quickstart_tree = [pathlib.Path("dummy.file")]

    # Files in destination tree do not exist. Copy the quickstart file tree.
    with patch("shutil.copyfile") as mock_copyfile, \
         patch("pathlib.Path.mkdir") as mock_mkdir, \
         patch("pathlib.Path.rglob", return_value=quickstart_tree), \
         patch("pathlib.Path.relative_to", return_value=quickstart_tree[0]), \
         patch("pathlib.Path.exists", side_effect=[True, False, False]), \
         patch("filecmp.cmp", return_value=False):
        return_code = fetch.recursive_copy(_settings._installed_quickstart_directory, "/dummy/path")
        assert return_code == 0
        mock_mkdir.assert_not_called()
        mock_copyfile.assert_called_once()

    # Files in destination tree do not exist, but dry run. Print quickstart file tree.
    with patch("shutil.copyfile") as mock_copyfile, \
         patch("pathlib.Path.mkdir") as mock_mkdir, \
         patch("pathlib.Path.rglob", return_value=quickstart_tree), \
         patch("pathlib.Path.relative_to", return_value=quickstart_tree[0]), \
         patch("pathlib.Path.exists", side_effect=[True, False, False]), \
         patch("filecmp.cmp", return_value=False):
        return_code = fetch.recursive_copy(_settings._installed_quickstart_directory, "/dummy/path", dry_run=True)
        assert return_code == 0
        mock_mkdir.assert_not_called()
        mock_copyfile.assert_not_called()

    # Files in destination tree do exist. Don't copy the quickstart file tree.
    with patch("shutil.copyfile") as mock_copyfile, \
         patch("pathlib.Path.mkdir") as mock_mkdir, \
         patch("pathlib.Path.rglob", return_value=quickstart_tree), \
         patch("pathlib.Path.relative_to", return_value=quickstart_tree[0]), \
         patch("pathlib.Path.exists", side_effect=[True, True, True]), \
         patch("filecmp.cmp", return_value=True):
        return_code = fetch.recursive_copy(_settings._installed_quickstart_directory, "/dummy/path")
        assert return_code == 0  # Don't error out, just remove destination file from the copy list
        mock_mkdir.assert_not_called()
        mock_copyfile.assert_not_called()

    # File in destination tree does exist, we want to overwrite contents, and the files differ. Copy the quickstart file tree.
    with patch("shutil.copyfile") as mock_copyfile, \
         patch("pathlib.Path.mkdir") as mock_mkdir, \
         patch("pathlib.Path.rglob", return_value=quickstart_tree), \
         patch("pathlib.Path.relative_to", return_value=quickstart_tree[0]), \
         patch("pathlib.Path.exists", side_effect=[True, True, True]), \
         patch("filecmp.cmp", return_value=False):
        return_code = fetch.recursive_copy(_settings._installed_quickstart_directory, "/dummy/path", overwrite=True)
        assert return_code == 0
        mock_mkdir.assert_not_called()
        mock_copyfile.assert_called_once()

    # File in destination tree does exist, we want to overwrite contents, but the files are the same. Don't copy the
    # source file.
    with patch("shutil.copyfile") as mock_copyfile, \
         patch("pathlib.Path.mkdir") as mock_mkdir, \
         patch("pathlib.Path.rglob", return_value=quickstart_tree), \
         patch("pathlib.Path.relative_to", return_value=quickstart_tree[0]), \
         patch("pathlib.Path.exists", side_effect=[True, True, True]), \
         patch("filecmp.cmp", return_value=True):
        return_code = fetch.recursive_copy(_settings._installed_quickstart_directory, "/dummy/path", overwrite=True)
        assert return_code == 0
        mock_mkdir.assert_not_called()
        mock_copyfile.assert_not_called()

    # Files in destination tree do exist, but we want to overwrite contents and dry run. Print the quickstart file tree.
    with patch("shutil.copyfile") as mock_copyfile, \
         patch("pathlib.Path.mkdir") as mock_mkdir, \
         patch("pathlib.Path.rglob", return_value=quickstart_tree), \
         patch("pathlib.Path.relative_to", return_value=quickstart_tree[0]), \
         patch("pathlib.Path.exists", side_effect=[True, True, True]), \
         patch("filecmp.cmp", return_value=True):
        return_code = fetch.recursive_copy(_settings._installed_quickstart_directory, "/dummy/path", overwrite=True, dry_run=True)
        assert return_code == 0
        mock_mkdir.assert_not_called()
        mock_copyfile.assert_not_called()

    # Test the "unreachable" exit code used as a sign-of-life that the installed package structure assumptions in
    # _settings.py are correct.
    with patch("shutil.copyfile") as mock_copyfile, \
         patch("pathlib.Path.mkdir") as mock_mkdir, \
         patch("pathlib.Path.rglob", return_value=quickstart_tree), \
         patch("pathlib.Path.relative_to", return_value=quickstart_tree[0]), \
         patch("pathlib.Path.exists", side_effect=[False, False, False]), \
         patch("filecmp.cmp", return_value=False):
        return_code = fetch.recursive_copy(_settings._installed_quickstart_directory, "/dummy/path")
        assert return_code != 0
        mock_mkdir.assert_not_called()
        mock_copyfile.assert_not_called()
