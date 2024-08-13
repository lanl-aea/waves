from unittest.mock import patch
from contextlib import nullcontext as does_not_raise

import pytest

from waves import _settings
from waves import _docs


def test_docs():
    with patch('webbrowser.open') as mock_webbrowser_open:
        _docs.main(_settings._installed_docs_index)
        # Make sure the correct type is passed to webbrowser.open
        mock_webbrowser_open.assert_called_with(str(_settings._installed_docs_index))

    with patch('webbrowser.open') as mock_webbrowser_open, \
         patch('pathlib.Path.exists', return_value=True), \
         does_not_raise():
        _docs.main(_settings._installed_docs_index, print_local_path=True)
        mock_webbrowser_open.assert_not_called()

    # Test the "unreachable" exit code used as a sign-of-life that the installed package structure assumptions in
    # _settings.py are correct.
    with patch('webbrowser.open') as mock_webbrowser_open, \
         patch('pathlib.Path.exists', return_value=False), \
         pytest.raises(RuntimeError):
        try:
            _docs.main(_settings._installed_docs_index, print_local_path=True)
        finally:
            mock_webbrowser_open.assert_not_called()
