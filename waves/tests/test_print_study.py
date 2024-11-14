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
    safe_load = {"ints": [1, 2, 3], "floats": [10., 20., 30.]}
    table = pandas.DataFrame(safe_load)
    table.index.name = _settings._set_coordinate_key
    study_xarray = xarray.Dataset.from_dataframe(table)

    with patch("pathlib.Path.is_file", return_value=False), \
         patch("builtins.print") as mock_print, \
         patch("builtins.open", mock_open(read_data="")), \
         patch("yaml.safe_load", return_value={}), \
         pytest.raises(RuntimeError):
        _print_study.main(pathlib.Path("badpath.yaml"))
        mock_print.assert_not_called()

    with patch("pathlib.Path.is_file", return_value=True), \
         patch("builtins.print") as mock_print, \
         patch("builtins.open", mock_open(read_data=read_data)), \
         patch("yaml.safe_load", return_value=safe_load), \
         does_not_raise():
        _print_study.main(pathlib.Path("goodpath.yaml"))
        mock_print.assert_called_once()

    with patch("pathlib.Path.is_file", return_value=True), \
         patch("builtins.print") as mock_print, \
         patch("builtins.open", mock_open(read_data=read_data)), \
         patch("yaml.safe_load", side_effect=UnicodeDecodeError("utf-8", b"", 0, 1, "invalid start byte")), \
         patch("xarray.open_dataset", return_value=study_xarray), \
         does_not_raise():
        _print_study.main(pathlib.Path("goodpath.h5"))
        mock_print.assert_called_once()
