import pathlib
from unittest.mock import patch, mock_open
from contextlib import nullcontext as does_not_raise

import pytest
import pandas
import xarray

from waves import _settings
from waves import _print_study


def test_print_study():
    read_data = "ints: [1, 2, 3]\nfloats: [10., 20., 30]\n"
    safe_load = {"ints": [1, 2, 3], "floats": [10.0, 20.0, 30.0]}
    table = pandas.DataFrame(safe_load)
    table.index.name = _settings._set_coordinate_key
    study_xarray = xarray.Dataset.from_dataframe(table)

    # Test the pathlib file search exception
    with (
        patch("pathlib.Path.is_file", return_value=False),
        patch("builtins.print") as mock_print,
        patch("builtins.open", mock_open(read_data="")),
        patch("yaml.safe_load", return_value={}),
        pytest.raises(RuntimeError),
    ):
        try:
            _print_study.main(pathlib.Path("badpath.yaml"))
        finally:
            mock_print.assert_not_called()

    # Test an unexpected YAML exception not associated with trying to read an H5 file
    with (
        patch("pathlib.Path.is_file", return_value=True),
        patch("builtins.print") as mock_print,
        patch("builtins.open", mock_open(read_data="")),
        patch("yaml.safe_load", side_effect=Exception()),
        pytest.raises(RuntimeError),
    ):
        try:
            _print_study.main(pathlib.Path("notayamlfile.h5"))
        finally:
            mock_print.assert_not_called()

    # Test the YAML read behavior
    with (
        patch("pathlib.Path.is_file", return_value=True),
        patch("builtins.print") as mock_print,
        patch("builtins.open", mock_open(read_data=read_data)),
        patch("yaml.safe_load", return_value=safe_load),
        does_not_raise(),
    ):
        try:
            _print_study.main(pathlib.Path("goodpath.yaml"))
        finally:
            mock_print.assert_called_once()

    # Test the Xarray read behavior
    with (
        patch("pathlib.Path.is_file", return_value=True),
        patch("builtins.print") as mock_print,
        patch("builtins.open", mock_open(read_data=read_data)),
        patch("yaml.safe_load", side_effect=UnicodeDecodeError("utf-8", b"", 0, 1, "invalid start byte")),
        patch("waves.parameter_generators._open_parameter_study", return_value=study_xarray),
        does_not_raise(),
    ):
        try:
            _print_study.main(pathlib.Path("goodpath.h5"))
        finally:
            mock_print.assert_called_once()
