"""Test WAVES

Test waves.py
"""
import pathlib
from unittest.mock import patch

import pytest

from waves import main
from waves import _settings


@pytest.mark.unittest
def test_main():
    with patch('sys.argv', ['waves.py', 'docs']), \
         patch("waves.main.docs") as mock_docs:
        main.main()
        mock_docs.assert_called()

    target_string = 'dummy.target'
    with patch('sys.argv', ['waves.py', 'build', target_string]), \
         patch("waves.main.build") as mock_build:
        main.main()
        mock_build.assert_called_once()
        mock_build.call_args[0] == [target_string]

    project_directory = 'project_directory'
    with patch('sys.argv', ['waves.py', 'quickstart', project_directory]), \
         patch("waves.fetch.recursive_copy") as mock_recursive_copy:
        main.main()
        mock_recursive_copy.assert_called_once()
        mock_recursive_copy.call_args[0] == [project_directory]


@pytest.mark.unittest
def test_docs():
    with patch('webbrowser.open') as mock_webbrowser_open:
        main.docs()
        # Make sure the correct type is passed to webbrowser.open
        mock_webbrowser_open.assert_called_with(str(_settings._installed_docs_index))

    with patch('webbrowser.open') as mock_webbrowser_open, \
         patch('pathlib.Path.exists', return_value=True):
        return_code = main.docs(print_local_path=True)
        assert return_code == 0
        mock_webbrowser_open.not_called()

    # Test the "unreachable" exit code used as a sign-of-life that the installed package structure assumptions in
    # _settings.py are correct.
    with patch('webbrowser.open') as mock_webbrowser_open, \
         patch('pathlib.Path.exists', return_value=False):
        return_code = main.docs(print_local_path=True)
        assert return_code != 0
        mock_webbrowser_open.not_called()


@pytest.mark.unittest
def test_build():
    with patch('subprocess.check_output', return_value=b"is up to date.") as mock_check_output:
        main.build(['dummy.target'])
        mock_check_output.assert_called_once()

    with patch('subprocess.check_output', return_value=b"is up to date.") as mock_check_output, \
         patch("pathlib.Path.mkdir") as mock_mkdir:
        main.build(['dummy.target'], git_clone_directory='dummy/clone')
        assert mock_check_output.call_count == 2


@pytest.mark.unittest
def test_quickstart():
    # Test the "unreachable" exit code used as a sign-of-life that the installed package structure assumptions in
    # _settings.py are correct.
    with patch("waves.fetch.recursive_copy") as mock_recursive_copy:
        return_code = main.fetch("dummy_subcommand", pathlib.Path("/directory/assumptions/are/wrong"), ["dummy/relative/path"], "/dummy/destination")
        assert return_code != 0
        mock_recursive_copy.assert_not_called()
