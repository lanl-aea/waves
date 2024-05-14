from unittest.mock import patch

import pytest

from waves import _build


def test_build():
    with patch('waves._utilities.tee_subprocess', return_value=(0, "is up to date.")) as mock_tee_subprocess:
        _build.main(['dummy.target'])
        mock_tee_subprocess.assert_called_once()

    with patch('waves._utilities.tee_subprocess', return_value=(0, "is up to date.")) as mock_tee_subprocess, \
         patch("pathlib.Path.mkdir") as mock_mkdir:
        _build.main(['dummy.target'], git_clone_directory='dummy/clone')
        assert mock_tee_subprocess.call_count == 2
