from unittest.mock import patch
from contextlib import nullcontext as does_not_raise

import pytest

from waves import _settings
from waves import _docs


def test_docs():
    # No print. Should call webbrowser.open successfully
    with (
        patch("builtins.print") as mock_print,
        patch("webbrowser.open", return_value=True) as mock_webbrowser_open,
    ):
        _docs.main(_settings._installed_docs_index)
        # Make sure the correct type is passed to webbrowser.open
        mock_webbrowser_open.assert_called_with(str(_settings._installed_docs_index))
        mock_print.assert_not_called()

    # Test the unsuccessful return code of webbrowser.open
    with (
        patch("builtins.print") as mock_print,
        patch("webbrowser.open", return_value=False) as mock_webbrowser_open,
        pytest.raises(RuntimeError, match="Could not open a web browser."),
    ):
        try:
            _docs.main(_settings._installed_docs_index)
        finally:
            mock_webbrowser_open.assert_called_with(str(_settings._installed_docs_index))
            mock_print.assert_not_called()

    # Request print local path. Should print instead of webbrowser open.
    with (
        patch("builtins.print") as mock_print,
        patch("webbrowser.open", return_value=True) as mock_webbrowser_open,
        patch("pathlib.Path.exists", return_value=True),
        does_not_raise(),
    ):
        _docs.main(_settings._installed_docs_index, print_local_path=True)
        mock_webbrowser_open.assert_not_called()
        mock_print.assert_called_once()

    # Test the "unreachable" exit code used as a sign-of-life that the installed package structure assumptions in
    # _settings.py are correct.
    with (
        patch("builtins.print") as mock_print,
        patch("webbrowser.open") as mock_webbrowser_open,
        patch("pathlib.Path.exists", return_value=False),
        pytest.raises(RuntimeError, match="Could not find package documentation HTML index file"),
    ):
        try:
            _docs.main(_settings._installed_docs_index, print_local_path=True)
        finally:
            mock_webbrowser_open.assert_not_called()
            mock_print.assert_not_called()
