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

