#! /usr/bin/env python
import unittest.mock

import numpy
import pandas
import xarray
import waves

from eabm_package import utilities


def test_combine_data():
    """Test the Python 3 Xarray Dataset concatenation utility

    Concatenate real datasets with coordinates representative of a WAVES parameter study workflow
    """
    input_files = ["/mock/parameter_set0/data.h5", "/mock/parameter_set1/data.h5"]
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
        coords={"space": [0], "time": [0, 1, 2], "parameter_sets": ["parameter_set0", "parameter_set1"]},
    )
    xarray_side_effect = [dataset1, dataset2]
    with unittest.mock.patch("xarray.open_dataset", side_effect=xarray_side_effect):
        combined_data = utilities.combine_data(input_files, "/", "parameter_sets")
    assert combined_data.equals(expected)


def test_merge_parameter_study():
    """Test the Python 3 Xarray Dataset and WAVES parameter study merge utility

    Sign-of-life test that a real parameter study object merges correctly with a representative Dataset
    """
    parameter_study = waves.parameter_generators.CartesianProduct(
        {"parameter_1": [1, 2], "parameter_2": [3, 4]}
    ).parameter_study
    combined_data = xarray.Dataset(
        {"variable_name": (("parameter_sets", "space", "time"), numpy.array([[[1, 2, 3]], [[4, 5, 6]]]))},
        coords={"space": [0], "time": [0, 1, 2], "parameter_sets": ["parameter_set0", "parameter_set1"]},
    )
    with unittest.mock.patch("xarray.open_dataset", return_value=parameter_study):
        combined_data = utilities.merge_parameter_study("/mock/path/parameter_study.h5", combined_data)


def test_save_plot():
    """Test the Python 3 Xarray Dataset plotting utility

    Test that the function arguments are unpacked into the correct I/O calls
    """
    combined_data = xarray.Dataset(
        {"variable_name": (("parameter_sets", "space", "time"), numpy.array([[[1, 2, 3]], [[4, 5, 6]]]))},
        coords={"space": [0], "time": [0, 1, 2], "parameter_sets": ["parameter_set0", "parameter_set1"]},
    )
    selection_dict = {"space": 0, "time": 2}
    x_var = "space"
    y_var = "time"
    concat_coord = "parameter_sets"
    output_file = "mock.png"
    with unittest.mock.patch("xarray.Dataset.plot.scatter") as mock_scatter, \
         unittest.mock.patch("matplotlib.pyplot.savefig") as mock_savefig:
        utilities.save_plot(combined_data, x_var, y_var, selection_dict, concat_coord, output_file)
    mock_scatter.assert_called_once_with(x=x_var, y=y_var, hue=concat_coord)
    mock_savefig.assert_called_once_with(output_file)


def test_save_table():
    """Test the Python 3 Xarray Dataset CSV file saving utility

    Test that the function arguments are unpacked into the correct I/O calls
    """
    combined_data = xarray.Dataset(
        {"variable_name": (("parameter_sets", "space", "time"), numpy.array([[[1, 2, 3]], [[4, 5, 6]]]))},
        coords={"space": [0], "time": [0, 1, 2], "parameter_sets": ["parameter_set0", "parameter_set1"]},
    )
    selection_dict = {"space": 0, "time": 2}
    output_file = "mock.csv"
    with unittest.mock.patch("pandas.DataFrame.to_csv") as mock_to_csv:
        utilities.save_table(combined_data, selection_dict, output_file)
    mock_to_csv.assert_called_once_with(output_file)


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
