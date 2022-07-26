#!/usr/bin/env python
"""stress strain comparison"""

import sys
import argparse
import pathlib

import xarray
import matplotlib.pyplot


def main(input_files, output_file, group_path):
    # TODO: Move dataset meta script assumptions to CLI
    select_dict = {"LE values": "LE22", "S values": "S22", "elements": 1, "step": "Step-1"}
    x_var = "LE"
    x_units = "mm/mm"
    y_var = "S"
    y_units = "MPa"
    concat_coord = "parameter_sets"

    # Build single dataset along the "parameter_sets" dimension
    paths = [pathlib.Path(input_file).resolve() for input_file in input_files]
    data_generator = (xarray.open_dataset(path, group=group_path).sel(select_dict).assign_coords({concat_coord:
                          path.parent.name}) for path in paths)
    combined_data = xarray.concat(data_generator, concat_coord)

    # Add units
    combined_data[x_var].attrs["units"] = x_units
    combined_data[y_var].attrs["units"] = y_units

    # Plot
    combined_data.plot.scatter(x_var, y_var, hue=concat_coord)
    matplotlib.pyplot.savefig(output_file)

    # Clean up open files
    combined_data.close()

    return 0


def get_parser():
    script_name = pathlib.Path(__file__)
    default_output_file = script_name.stem
    default_group_path = "SINGLE_ELEMENT/FieldOutputs/ALL"

    prog = f"python {script_name.name} "
    cli_description = "Read Xarray Datasets and plot stress-strain comparisons as a function of parameter set name. " \
                      " Save to ``output_file``."
    parser = argparse.ArgumentParser(description=cli_description,
                                     prog=prog)
    parser.add_argument("-i", "--input-files", nargs="+",
                        help="The Xarray Dataset file(s)")
    parser.add_argument("-o", "--output-file", type=str, default=default_output_file,
                        help="The output file for the stress-strain comparison plot with extension, " \
                             "e.g. ``output_file.pdf``. Extension must be supported by matplotlib.")
    parser.add_argument("-g", "--group-path", type=str, default=default_group_path,
                        help="The h5py group path to the dataset object (default: %(default)s)")
    return parser


if __name__ == "__main__":
    parser = get_parser()
    args, unknown = parser.parse_known_args()
    sys.exit(main(input_files=args.input_files,
                  output_file=args.output_file,
                  group_path=args.group_path))
