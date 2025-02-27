import io
import pathlib
from unittest.mock import Mock, patch, mock_open
from contextlib import nullcontext as does_not_raise

import pytest
import yaml

from waves import _parameter_study


def test_read_parameter_schema():
    # Test STDIN/TexIOWrapper read
    input_file = io.TextIOWrapper(io.BytesIO(b"{a: [1], b: [2]}"))
    expected = {"a": [1], "b": [2]}
    with patch("builtins.open", mock_open()) as mock_file:
        parameter_schema = _parameter_study.read_parameter_schema(input_file)
    mock_file.assert_not_called()
    assert parameter_schema == expected

    # Test file read
    input_file = pathlib.Path("dummy.yaml")
    with (
        patch("pathlib.Path.is_file", return_value=True),
        patch("builtins.open", mock_open()) as mock_file,
        patch("yaml.safe_load", return_value=expected),
    ):
        parameter_schema = _parameter_study.read_parameter_schema(input_file)
    mock_file.assert_called_once_with(input_file, "r")
    assert parameter_schema == expected

    # Test RuntimeError on missing file
    with (
        patch("pathlib.Path.is_file", return_value=False),
        patch("builtins.open", mock_open()) as mock_file,
        pytest.raises(RuntimeError),
    ):
        parameter_schema = _parameter_study.read_parameter_schema(input_file)
    mock_file.assert_not_called()

    # Test RuntimeError on missing STDIN and missing file
    with (
        patch("pathlib.Path.is_file", return_value=False),
        patch("builtins.open", mock_open()) as mock_file,
        pytest.raises(RuntimeError),
    ):
        parameter_schema = _parameter_study.read_parameter_schema(None)
    mock_file.assert_not_called()


def test_main():
    # Check the YAML read error and clarification runtime error message
    with (
        patch("waves._parameter_study.read_parameter_schema", side_effect=yaml.parser.ParserError()),
        patch("waves.parameter_generators.ParameterGenerator") as mock_class,
        pytest.raises(RuntimeError),
    ):
        try:
            _parameter_study.main("cartesian_product", "dummy.yaml")
        finally:
            mock_class.assert_not_called()

    # Check correct subcommand/ParameterGenerator class associations
    associations = (
        ("cartesian_product", "CartesianProduct"),
        ("custom_study", "CustomStudy"),
        ("latin_hypercube", "LatinHypercube"),
        ("sobol_sequence", "SobolSequence"),
        ("one_at_a_time", "OneAtATime"),
    )
    for subcommand, generator in associations:
        mock_generator = Mock()
        with (
            patch("waves._parameter_study.read_parameter_schema", return_value={}),
            patch(f"waves.parameter_generators.{generator}", return_value=mock_generator) as mock_class,
            does_not_raise(),
        ):
            _parameter_study.main(subcommand, "dummy.yaml")
            mock_class.assert_called_once()
            mock_generator.write.assert_called_once()
