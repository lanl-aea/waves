import unittest.mock

import numpy
import pandas
import xarray
from waves.parameter_generators import SET_COORDINATE_KEY
from waves.parameter_generators import CartesianProduct

from modsim_package import utilities


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
        {"variable_name": ((SET_COORDINATE_KEY, "space", "time"), numpy.array([[[1, 2, 3]], [[4, 5, 6]]]))},
        coords={"space": [0], "time": [0, 1, 2], SET_COORDINATE_KEY: ["parameter_set0", "parameter_set1"]},
    )
    xarray_side_effect = [dataset1, dataset2]
    with unittest.mock.patch("xarray.open_dataset", side_effect=xarray_side_effect):
        combined_data = utilities.combine_data(input_files, "/", SET_COORDINATE_KEY)
    assert combined_data.equals(expected)


def test_merge_parameter_study():
    """Test the Python 3 Xarray Dataset and WAVES parameter study merge utility

    Sign-of-life test that a real parameter study object merges correctly with a representative Dataset
    """
    parameter_study = CartesianProduct({"parameter_1": [1, 2], "parameter_2": [3, 4]}).parameter_study
    combined_data = xarray.Dataset(
        {"variable_name": ((SET_COORDINATE_KEY, "space", "time"), numpy.array([[[1, 2, 3]], [[4, 5, 6]]]))},
        coords={"space": [0], "time": [0, 1, 2], SET_COORDINATE_KEY: ["parameter_set0", "parameter_set1"]},
    )
    with unittest.mock.patch("xarray.open_dataset", return_value=parameter_study):
        combined_data = utilities.merge_parameter_study("/mock/path/parameter_study.h5", combined_data)


def test_save_plot():
    """Test the Python 3 Xarray Dataset plotting utility

    Test that the function arguments are unpacked into the correct I/O calls
    """
    combined_data = xarray.Dataset(
        {"variable_name": ((SET_COORDINATE_KEY, "space", "time"), numpy.array([[[1, 2, 3]], [[4, 5, 6]]]))},
        coords={"space": [0], "time": [0, 1, 2], SET_COORDINATE_KEY: ["parameter_set0", "parameter_set1"]},
    )
    selection_dict = {"space": 0, "time": 2}
    x_var = "space"
    y_var = "time"
    concat_coord = SET_COORDINATE_KEY
    output_file = "mock.png"
    with (
        unittest.mock.patch("xarray.Dataset.plot.scatter") as mock_scatter,
        unittest.mock.patch("matplotlib.pyplot.savefig") as mock_savefig,
    ):
        utilities.save_plot(combined_data, x_var, y_var, selection_dict, concat_coord, output_file)
    mock_scatter.assert_called_once_with(x=x_var, y=y_var, hue=concat_coord)
    mock_savefig.assert_called_once_with(output_file)


def test_save_table():
    """Test the Python 3 Xarray Dataset CSV file saving utility

    Test that the function arguments are unpacked into the correct I/O calls
    """
    combined_data = xarray.Dataset(
        {"variable_name": ((SET_COORDINATE_KEY, "space", "time"), numpy.array([[[1, 2, 3]], [[4, 5, 6]]]))},
        coords={"space": [0], "time": [0, 1, 2], SET_COORDINATE_KEY: ["parameter_set0", "parameter_set1"]},
    )
    selection_dict = {"space": 0, "time": 2}
    output_file = "mock.csv"
    with unittest.mock.patch("pandas.DataFrame.to_csv") as mock_to_csv:
        utilities.save_table(combined_data, selection_dict, output_file)
    mock_to_csv.assert_called_once_with(output_file)


def test_sort_dataframe():
    data = {
        "time": [0.0, 0.5, 1.0],
        "Column1": [1, 2, 3],
        "Column2": [4, 5, 6],
    }
    control = pandas.DataFrame.from_dict(data)
    unsorted_copy = control[["Column2", "Column1", "time"]]

    sorted_control = utilities.sort_dataframe(control, sort_columns=["time"])
    sorted_copy = utilities.sort_dataframe(unsorted_copy, sort_columns=["time"])

    pandas.testing.assert_frame_equal(sorted_control, sorted_copy)


def test_csv_files_match():
    data = {
        "time": [0.0, 0.5, 1.0],
        "Column1": [1, 2, 3],
        "Column2": [4, 5, 6],
    }
    # Control DataFrame
    control = pandas.DataFrame.from_dict(data)

    # Identical DataFrame
    identical_copy = control.copy()
    unsorted_copy = control[["time", "Column2", "Column1"]]

    # Different DataFrame
    different_copy = control.copy()
    different_copy.loc[0, "Column1"] = 999

    # Assert that the function returns False when the DataFrames differ
    assert utilities.csv_files_match(control, different_copy, sort_columns=["time"]) is False

    # Assert that the function returns True when the DataFrames are identical
    assert utilities.csv_files_match(control, identical_copy, sort_columns=["time"]) is True

    # Assert that the function returns True when the sorted DataFrames are identical
    assert utilities.csv_files_match(control, unsorted_copy, sort_columns=["time"]) is True
