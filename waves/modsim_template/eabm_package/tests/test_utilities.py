#! /usr/bin/env python
import unittest.mock

import numpy
import pandas
import xarray

from eabm_package import utilities


def test_combine_data():
    input_files = ["/mock/path1/data.h5", "/mock/path2/data.h5"]
    dataset1 = xarray.Dataset(
        {"variable_name": (("space", "time"), numpy.array([[1, 2, 3]]))},
        coords={"space": [0], "time": [0, 1, 2]},
    )
    dataset2 = xarray.Dataset(
        {"variable_name": (("space", "time"), numpy.array([[4, 5, 6]]))},
        coords={"space": [0], "time": [0, 1, 2]},
    )
    expected = xarray.Dataset(
        {"variable_name": (("parameter_sets", "space", "time"), numpy.array([[[1, 2, 3]], [[4, 5, 6]]]))},
        coords={"space": [0], "time": [0, 1, 2], "parameter_sets": ["path1", "path2"]},
    )
    xarray_side_effect = [dataset1, dataset2]
    with unittest.mock.patch("xarray.open_dataset", side_effect=xarray_side_effect):
        combined_data = utilities.combine_data(input_files, "/", "parameter_sets")
    assert combined_data.equals(expected)


def test_csv_files_match():
    data = {
        'DummyLine': [1, 2, 3],
        'SecondDummyLine': [4, 5, 6]
    }
    # Control DataFrame
    control = pandas.DataFrame(data)

    # Identical DataFrame
    identical_copy = control.copy()

    # Different DataFrame
    different_copy = control.copy()
    different_copy.loc[0, 'DummyLine'] = 999

    # Assert that the function returns False when the DataFrames differ
    assert utilities.csv_files_match(control, different_copy) is False

    # Assert that the function returns True when the DataFrames are identical
    assert utilities.csv_files_match(control, identical_copy) is True
