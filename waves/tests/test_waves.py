"""Test WAVES

Test waves.py
"""
from unittest.mock import patch

import pytest

from waves import waves


@pytest.mark.unittest
def test_docs():
    with patch('webbrowser.open') as mock_webbrowser_open:
        waves.docs()
        mock_webbrowser_open.assert_called()

    with patch('webbrowser.open') as mock_webbrowser_open, \
         patch('pathlib.Path.exists', return_value=True):
        return_code = waves.docs(print_local_path=True)
        assert return_code == 0
        mock_webbrowser_open.not_called()

    with patch('webbrowser.open') as mock_webbrowser_open, \
         patch('pathlib.Path.exists', return_value=False):
        return_code = waves.docs(print_local_path=True)
        assert return_code != 0
        mock_webbrowser_open.not_called()


@pytest.mark.unittest
def test_main():
    with patch('sys.argv', ['waves.py', 'docs']), \
         patch("waves.waves.docs") as mock_docs:
        waves.main()
        mock_docs.assert_called()

    target_string = 'dummy.target'
    with patch('sys.argv', ['waves.py', 'build', target_string]), \
         patch("waves.waves.build") as mock_build:
        waves.main()
        mock_build.assert_called_once()
        mock_build.call_args[0] == [target_string]


@pytest.mark.unittest
def test_build():
    with patch('subprocess.check_output', return_value=b"is up to date.") as mock_check_output:
        waves.build(['dummy.target'])
        mock_check_output.assert_called_once()

    with patch('subprocess.check_output', return_value=b"is up to date.") as mock_check_output:
        waves.build(['dummy.target'], git_clone_directory='dummy/clone')
        assert mock_check_output.call_count == 2
