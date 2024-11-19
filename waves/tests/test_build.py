from unittest.mock import patch

import pytest

from waves import _build


def test_build():
    with patch("waves._utilities.tee_subprocess", return_value=(0, "is up to date.")) as mock_tee_subprocess:
        _build.main(["dummy.target"])
        mock_tee_subprocess.assert_called_once()

    with (
        patch("waves._utilities.tee_subprocess", return_value=(0, "is up to date.")) as mock_tee_subprocess,
        patch("pathlib.Path.mkdir") as mock_mkdir,
    ):
        _build.main(["dummy.target"], git_clone_directory="dummy/clone")
        assert mock_tee_subprocess.call_count == 2

    # Passing an empty targets list should raise a RuntimeError
    with (
        patch("waves._utilities.tee_subprocess", return_value=(0, "is up to date.")) as mock_tee_subprocess,
        patch("pathlib.Path.mkdir") as mock_mkdir,
        pytest.raises(RuntimeError),
    ):
        try:
            _build.main([], git_clone_directory="dummy/clone")
        finally:
            mock_tee_subprocess.assert_not_called()
            mock_mkdir.assert_not_called()

    # Git clone non-zero exit codes should raise a RuntimeError
    with (
        patch("waves._utilities.tee_subprocess", return_value=(1, "some error message")) as mock_tee_subprocess,
        patch("pathlib.Path.mkdir") as mock_mkdir,
        pytest.raises(RuntimeError),
    ):
        try:
            _build.main(["dummy.target"], git_clone_directory="dummy/clone")
        finally:
            mock_mkdir.assert_called_once()

    # If the "is up to date" trigger text is never found, should raise RuntimeError
    max_iterations = 2
    with (
        patch("waves._utilities.tee_subprocess", return_value=(0, "some other message")) as mock_tee_subprocess,
        patch("pathlib.Path.mkdir") as mock_mkdir,
        pytest.raises(RuntimeError),
    ):
        try:
            _build.main(["dummy.target"], git_clone_directory="dummy/clone", max_iterations=max_iterations)
        finally:
            # tee subprocess called once for Git clone and up to max iterations
            mock_tee_subprocess.call_count == max_iterations + 1
            mock_mkdir.assert_called_once()

    # SCons non-zero exit codes should raise a RuntimeError. Don't use git clone feature, so no mkdir and only one
    # subprocess call.
    with (
        patch("waves._utilities.tee_subprocess", return_value=(1, "scons error message")) as mock_tee_subprocess,
        patch("pathlib.Path.mkdir") as mock_mkdir,
        pytest.raises(RuntimeError),
    ):
        try:
            _build.main(["dummy.target"])
        finally:
            mock_tee_subprocess.assert_called_once()
            mock_mkdir.assert_not_called()
