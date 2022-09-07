"""Test WAVES

Test waves.py
""" 

import pytest
from unittest.mock import patch

from waves import waves

@pytest.mark.unittest
def test_open_docs():
    with patch('webbrowser.open') as mock_webbrowser_open:
        waves.open_docs()
        mock_webbrowser_open.assert_called()

@pytest.mark.unittest
def test_main():
    with patch('sys.argv', ['waves.py', 'docs']), \
         patch("waves.waves.open_docs") as mock_open_docs:
        waves.main()
        mock_open_docs.assert_called()

    target_string = 'dummy.target'
    with patch('sys.argv', ['waves.py', 'build', target_string]), \
         patch("waves.waves.build") as mock_build:
        waves.main()
        mock_build.assert_called_once()
        mock_build.call_args[0] == [target_string]
