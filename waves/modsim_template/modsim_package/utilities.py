"""Python 3 utilities not compatible with Abaqus Python 2"""

import sys
import typing
import pathlib

import yaml
import waves
import pandas
import xarray
import matplotlib.pyplot


def combine_data(input_files, group_path, concat_coord):
    """Combine input data files into one dataset

    :param list input_files: list of path-like or file-like objects pointing to h5netcdf files
        containing Xarray Datasets
    :param str group_path: The h5netcdf group path locating the Xarray Dataset in the input files.
    :param str concat_coord: Name of dimension

    :returns: Combined data
    :rtype: xarray.DataArray
    """
    paths = [pathlib.Path(input_file).resolve() for input_file in input_files]
    data_generator = (
        xarray.open_dataset(path, group=group_path, engine="h5netcdf").assign_coords({concat_coord: path.parent.name})
        for path in paths
    )
    combined_data = xarray.concat(data_generator, concat_coord)
    combined_data.close()

    return combined_data


def merge_parameter_study(parameter_study_file, combined_data):
    """Merge parameter study to existing dataset

    :param str parameter_study_file: path-like or file-like object containing the parameter study dataset. Assumes the
        h5netcdf file contains only a single dataset at the root group path, .e.g. ``/``.
    :param xarray.DataArray combined_data: XArray Dataset that will be merged.

    :returns: Combined data
    :rtype: xarray.DataArray
    """
    parameter_study = xarray.open_dataset(parameter_study_file, engine="h5netcdf")
    combined_data = combined_data.merge(parameter_study)
    parameter_study.close()
    return combined_data


def save_plot(combined_data, x_var, y_var, selection_dict, concat_coord, output_file):
    """Save scatter plot with given x and y labels

    :param xarray.DataArray combined_data: XArray Dataset that will be plotted.
    :param str x_var: The independent (x-axis) variable key name for the Xarray Dataset "data variable"
    :param str y_var: The dependent (y-axis) variable key name for the Xarray Dataset "data variable"
    :param dict selection_dict: Dictionary to define the down selection of data to be plotted. Dictionary ``key: value``
        pairs must match the data variables and coordinates of the expected Xarray Dataset object.
    :param str concat_coord: Name of dimension for which you want multiple lines plotted.
    :param str output_file: The plot file name. Relative or absolute path.
    """
    # Plot
    combined_data.sel(selection_dict).plot.scatter(x=x_var, y=y_var, hue=concat_coord)
    matplotlib.pyplot.title(None)
    matplotlib.pyplot.savefig(output_file)


def save_table(combined_data, selection_dict, output_file):
    """Save csv table

    :param xarray.DataArray combined_data: XArray Dataset to be written as a CSV.
    :param dict selection_dict: Dictionary to define the down selection of data to be plotted. Dictionary ``key: value``
        pairs must match the data variables and coordinates of the expected Xarray Dataset object.
    :param str output_file: The CSV file name. Relative or absolute path.
    """
    combined_data.sel(selection_dict).to_dataframe().to_csv(output_file)


def sort_dataframe(dataframe, index_column="time", sort_columns=["time", "set_name"]):
    """Return a sorted dataframe and set an index

    1. sort columns by column name
    2. sort rows by column values ``sort_columns``
    3. set an index

    :returns: sorted and indexed dataframe
    :rtype: pandas.DataFrame
    """
    return dataframe.reindex(sorted(dataframe.columns), axis=1).sort_values(sort_columns).set_index(index_column)


def csv_files_match(current_csv, expected_csv, index_column="time", sort_columns=["time", "set_name"]):
    """Compare two pandas DataFrame objects and determine if they match.

    :param pandas.DataFrame current_csv: Current CSV data of generated plot.
    :param pandas.DataFrame expected_csv: Expected CSV data.

    :returns: True if the CSV files match, False otherwise.
    :rtype: bool
    """
    current = sort_dataframe(current_csv, index_column=index_column, sort_columns=sort_columns)
    expected = sort_dataframe(expected_csv, index_column=index_column, sort_columns=sort_columns)
    try:
        pandas.testing.assert_frame_equal(current, expected)
    except AssertionError as err:
        print(
            f"The CSV regression test failed. Data in expected CSV file and current CSV file do not match.\n{err}",
            file=sys.stderr,
        )
        equal = False
    else:
        equal = True
    return equal


def write_study_definition(
    study_definition: typing.Union[waves.parameter_generators.ParameterGenerator, dict],
    path: pathlib.Path,
    alias: str,
) -> None:
    """Write parameter study definition files to path

    Calls parameter generator write function or writes a YAML dictionary

    :param study_definition: Parameter study definition. WAVES parameter generator or dictionary.
    :param path: Output directory
    :param alias: Parameter study dictionary file name
    """
    if isinstance(study_definition, waves.parameter_generators.ParameterGenerator):
        study_definition.write()
    elif isinstance(study_definition, dict):
        study_path = path / f"{alias}.yaml"
        study_path.parent.mkdir(parents=True, exist_ok=True)
        with open(study_path, "w") as study_file:
            study_file.write(yaml.safe_dump(study_definition))
