#!/usr/bin/env python
"""Example of catenating WAVES parameter study results and definition"""

import sys
import argparse
import pathlib

import xarray
import matplotlib.pyplot


def main(input_files, output_file, group_path, x_var, x_units, y_var, y_units, parameter_study_file=None):
    """Catenate ``input_files`` datasets along the ``parameter_sets`` dimension and plot selected data.

    Optionally merges the parameter study results datasets with the parameter study definition dataset, where the
    parameter study dataset file is assumed to be written by a WAVES parameter generator. Currently assumes the selected
    data as harcoded dictionary

    .. code-block::

       select_dict = {"LE values": "LE22", "S values": "S22", "elements": 1, "step": "Step-1"}

    :param list input_files: list of path-like or file-like objects pointing to h5netcdf files containing XArray Datasets
    :param str output_file: The plot file name. Relative or absolute path.
    :param str group_path: The h5netcdf group path locating the XArray Dataset in the input files.
    :param str x_var: The independent (x-axis) variable key name for the XArray Dataset "data variable"
    :param str x_units: The independent (x-axis) units
    :param str y_var: The dependent (y-axis) variable key name for the XArray Dataset "data variable"
    :param str y_units: The dependent (y-axis) units
    :param str parameter_study_file: path-like or file-like object containing the parameter study dataset. Assumes the
        h5netcdf file contains only a single dataset at the root group path, .e.g. ``/``.
    """
    # TODO: Move dataset meta script assumptions to CLI
    select_dict = {"LE values": "LE22", "S values": "S22", "elements": 1, "step": "Step-1"}
    concat_coord = "parameter_sets"

    # Build single dataset along the "parameter_sets" dimension
    paths = [pathlib.Path(input_file).resolve() for input_file in input_files]
    data_generator = (xarray.open_dataset(path, group=group_path).assign_coords({concat_coord:
                          path.parent.name}) for path in paths)
    combined_data = xarray.concat(data_generator, concat_coord)

    # Add units
    combined_data[x_var].attrs["units"] = x_units
    combined_data[y_var].attrs["units"] = y_units

    # Open and merge WAVES parameter study if provided
    if parameter_study_file:
        parameter_study = xarray.open_dataset(parameter_study_file)
        combined_data = combined_data.merge(parameter_study)

    # Write results dataset to stdout for tutorial demonstration
    print(combined_data)

    # Plot
    combined_data.sel(select_dict).plot.scatter(x_var, y_var, hue=concat_coord)
    matplotlib.pyplot.savefig(output_file)

    # Clean up open files
    combined_data.close()
    if parameter_study_file:
        parameter_study.close()

    return 0


def get_parser():
    script_name = pathlib.Path(__file__)
    default_output_file = f"{script_name.stem}.pdf"
    default_group_path = "SINGLE_ELEMENT/FieldOutputs/ALL"
    default_x_var = "LE"
    default_y_var = "S"
    default_parameter_study_file = None

    prog = f"python {script_name.name} "
    cli_description = "Read Xarray Datasets and plot stress-strain comparisons as a function of parameter set name. " \
                      " Save to ``output_file``."
    parser = argparse.ArgumentParser(description=cli_description,
                                     prog=prog)
    required_named = parser.add_argument_group('required named arguments')
    required_named.add_argument("-i", "--input-file", nargs="+", required=True,
                                help="The Xarray Dataset file(s)")
    required_named.add_argument("--x-units", type=str, required=True,
                                help="The dependent (x-axis) units string.")
    required_named.add_argument("--y-units", type=str, required=True,
                                help="The independent (y-axis) units string.")

    parser.add_argument("-o", "--output-file", type=str, default=default_output_file,
                        help="The output file for the stress-strain comparison plot with extension, " \
                             "e.g. ``output_file.pdf``. Extension must be supported by matplotlib. " \
                             "(default: %(default)s)")
    parser.add_argument("-g", "--group-path", type=str, default=default_group_path,
                        help="The h5py group path to the dataset object (default: %(default)s)")
    parser.add_argument("-x", "--x-var", type=str, default=default_x_var,
                        help="The independent (x-axis) variable name (default: %(default)s)")
    parser.add_argument("-y", "--y-var", type=str, default=default_y_var,
                        help="The dependent (y-axis) variable name (default: %(default)s)")
    parser.add_argument("-p", "--parameter-study-file", type=str, default=default_parameter_study_file,
                        help="An optional h5 file with a WAVES parameter study XArray Dataset (default: %(default)s)")

    return parser


if __name__ == "__main__":
    parser = get_parser()
    args, unknown = parser.parse_known_args()
    sys.exit(main(input_files=args.input_file,
                  output_file=args.output_file,
                  group_path=args.group_path,
                  x_var=args.x_var,
                  x_units=args.x_units,
                  y_var=args.y_var,
                  y_units=args.y_units,
                  parameter_study_file=args.parameter_study_file))
