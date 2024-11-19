import pandas

from modsim_package.python import regression


def test_sort_dataframe():
    data = {
        "time": [0.0, 0.5, 1.0],
        "Column1": [1, 2, 3],
        "Column2": [4, 5, 6],
    }
    control = pandas.DataFrame.from_dict(data)
    unsorted_copy = control[["Column2", "Column1", "time"]]

    sorted_control = regression.sort_dataframe(control, sort_columns=["time"])
    sorted_copy = regression.sort_dataframe(unsorted_copy, sort_columns=["time"])

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
    assert regression.csv_files_match(control, different_copy, sort_columns=["time"]) is False

    # Assert that the function returns True when the DataFrames are identical
    assert regression.csv_files_match(control, identical_copy, sort_columns=["time"]) is True

    # Assert that the function returns True when the sorted DataFrames are identical
    assert regression.csv_files_match(control, unsorted_copy, sort_columns=["time"]) is True
