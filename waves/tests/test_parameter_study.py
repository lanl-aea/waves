import io
import pathlib
from unittest.mock import patch, mock_open

import pytest

from waves import _parameter_study


@pytest.mark.unittest
def test_read_parameter_schema():
    # Test STDIN/TexIOWrapper read
    input_file = io.TextIOWrapper(io.BytesIO(b"{a: [1], b: [2]}"))
    expected = {"a": [1], "b": [2]}
    with patch('builtins.open', mock_open()) as mock_file:
        parameter_schema = _parameter_study.read_parameter_schema(input_file)
    mock_file.assert_not_called()
    assert parameter_schema == expected

    # Test file read
    input_file = pathlib.Path("dummy.yaml")
    with patch("pathlib.Path.is_file", return_value=True), \
         patch('builtins.open', mock_open()) as mock_file, \
         patch('yaml.safe_load', return_value=expected):
        parameter_schema = _parameter_study.read_parameter_schema(input_file)
    mock_file.assert_called_once_with(input_file, "r")
    assert parameter_schema == expected

    # Test RuntimeError on missing file
    with patch("pathlib.Path.is_file", return_value=False), \
         patch('builtins.open', mock_open()) as mock_file, \
         pytest.raises(RuntimeError):
        parameter_schema = _parameter_study.read_parameter_schema(input_file)
    mock_file.assert_not_called()

    # Test RuntimeError on missing STDIN and missing file
    with patch("pathlib.Path.is_file", return_value=False), \
         patch('builtins.open', mock_open()) as mock_file, \
         pytest.raises(RuntimeError):
        parameter_schema = _parameter_study.read_parameter_schema(None)
    mock_file.assert_not_called()
