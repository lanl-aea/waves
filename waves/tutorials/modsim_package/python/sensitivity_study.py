#!/usr/bin/env python
"""Example of catenating WAVES parameter study results and definition"""

import sys
import yaml
import pathlib
import argparse

import pandas
import xarray
import matplotlib.pyplot
import numpy
import seaborn
import SALib.analyze.delta
from waves.parameter_generators import SET_COORDINATE_KEY

from modsim_package.python.rectangle_compression_sensitivity_study import parameter_schema


default_selection_dict = {
    "E values": "E22",
    "S values": "S22",
    "elements": 1,
    "step": "Step-1",
    "time": 1.0,
    "integration point": 0,
}


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


def main(input_files, output_file, group_path, selection_dict, parameter_study_file=None):
    """Catenate ``input_files`` datasets along the ``set_name`` dimension and plot selected data.

    Merges the parameter study results datasets with the parameter study definition dataset, where the parameter study
    dataset file is assumed to be written by a WAVES parameter generator.

    :param list input_files: list of path-like or file-like objects pointing to h5netcdf files containing Xarray
        Datasets
    :param str output_file: The correlation coefficients plot file name. Relative or absolute path.
    :param str group_path: The h5netcdf group path locating the Xarray Dataset in the input files.
    :param dict selection_dict: Dictionary to define the down selection of data to be plotted. Dictionary ``key: value``
        pairs must match the data variables and coordinates of the expected Xarray Dataset object.
    :param str parameter_study_file: path-like or file-like object containing the parameter study dataset. Assumes the
        h5netcdf file contains only a single dataset at the root group path, .e.g. ``/``.
    """
    output_file = pathlib.Path(output_file)
    output_csv = output_file.with_suffix(".csv")
    output_yaml = output_file.with_suffix(".yaml")
    concat_coord = SET_COORDINATE_KEY

    # Build single dataset along the "set_name" dimension
    combined_data = combine_data(input_files, group_path, concat_coord)

    # Merge WAVES parameter study if provided
    combined_data = merge_parameter_study(parameter_study_file, combined_data)

    # Correlation coefficients
    correlation_data = combined_data.sel(selection_dict).to_array().to_pandas().transpose()
    seaborn.pairplot(correlation_data, corner=True)
    matplotlib.pyplot.savefig(output_file)

    correlation_matrix = numpy.corrcoef(correlation_data.to_numpy(), rowvar=False)
    correlation_coefficients = pandas.DataFrame(
        correlation_matrix, index=correlation_data.columns, columns=correlation_data.columns
    )
    correlation_coefficients.to_csv(output_csv)

    # Sensitivity analysis
    stress = combined_data.sel(selection_dict)["S"].to_numpy()
    inputs = combined_data.sel(selection_dict)[["width", "height"]].to_array().transpose().to_numpy()
    sensitivity = SALib.analyze.delta.analyze(parameter_schema()["problem"], inputs, stress)
    sensitivity_yaml = {}
    for key, value in sensitivity.items():
        if isinstance(value, numpy.ndarray):
            value = value.tolist()
        sensitivity_yaml[key] = value
    with open(output_yaml, "w") as output:
        output.write(yaml.safe_dump(sensitivity_yaml))

    # Clean up open files
    combined_data.close()


def get_parser():
    script_name = pathlib.Path(__file__)
    default_output_file = f"{script_name.stem}.pdf"
    default_group_path = "RECTANGLE/FieldOutputs/ALL_ELEMENTS"
    default_parameter_study_file = None

    prog = f"python {script_name.name} "
    cli_description = (
        "Read Xarray Datasets and plot correlation coefficients as a function of parameter set name. "
        " Save to ``output_file``."
    )
    parser = argparse.ArgumentParser(description=cli_description, prog=prog)
    required_named = parser.add_argument_group("required named arguments")
    required_named.add_argument(
        "-i",
        "--input-file",
        nargs="+",
        required=True,
        help="The Xarray Dataset file(s)",
    )
    required_named.add_argument(
        "-p",
        "--parameter-study-file",
        type=str,
        default=default_parameter_study_file,
        help="An optional h5 file with a WAVES parameter study Xarray Dataset " "(default: %(default)s)",
    )

    parser.add_argument(
        "-o",
        "--output-file",
        type=str,
        default=default_output_file,
        # fmt: off
        help="The output file for the correlation coefficients plot with extension, "
             "e.g. ``output_file.pdf``. Extension must be supported by matplotlib. File stem is also "
             "used for the CSV table output, e.g. ``output_file.csv``, and sensitivity results, e.g. "
             "``output_file.yaml``. (default: %(default)s)",
        # fmt: off
    )
    parser.add_argument(
        "-g",
        "--group-path",
        type=str,
        default=default_group_path,
        help="The h5py group path to the dataset object (default: %(default)s)",
    )
    parser.add_argument(
        "-s",
        "--selection-dict",
        type=str,
        default=None,
        # fmt: off
        help="The YAML formatted dictionary file to define the down selection of data to be plotted. "
             "Dictionary key: value pairs must match the data variables and coordinates of the "
             "expected Xarray Dataset object. If no file is provided, the a default selection dict "
             f"will be used (default: {default_selection_dict})",
        # fmt: on
    )

    return parser


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
    if not args.selection_dict:
        selection_dict = default_selection_dict
    else:
        with open(args.selection_dict, "r") as input_yaml:
            selection_dict = yaml.safe_load(input_yaml)
    sys.exit(
        main(
            input_files=args.input_file,
            output_file=args.output_file,
            group_path=args.group_path,
            selection_dict=selection_dict,
            parameter_study_file=args.parameter_study_file,
        )
    )
