#!/usr/bin/env python
"""stress strain comparison"""

import sys
import argparse
import pathlib

import xarray


def main(input_files, output_file):
    # TODO: Move dataset meta script assumptions to CLI
    group = "SINGLE_ELEMENT/FieldOutputs/ALL"
    select_dict = {"LE values": "LE22", "S values": "S22", "elements": 1, "step": "Step-1"}

    paths = [pathlib.Path(input_file).resolve() for input_file in input_files]
    data_generator = (xarray.open_dataset(path, group=group).sel(select_dict).assign_coords({"parameter_sets":
                          path.parent.name}) for path in paths)
    combined_data = xarray.concat(data_generator, "parameter_sets")

    # Clean up open files
    for datarray in dataarrays:
        dataarray.close()

    return 0


def get_parser():
    script_name = pathlib.Path(__file__)
    default_output_file = script_name.stem

    prog = f"python {script_name.name} "
    cli_description = "Read Xarray Datasets and plot stress-strain comparisons. Save to ``output_file``.pdf."
    parser = argparse.ArgumentParser(description=cli_description,
                                     prog=prog)
    parser.add_argument("-i", "--input-files", nargs="+",
                        help="The Xarray Dataset file(s)")
    parser.add_argument("-o", "--output-file", type=str, default=default_output_file,
                        help="The output file for for the stress-strain comparison plot, e.g. ``output_file``.pdf")
    return parser


if __name__ == "__main__":
    parser = get_parser()
    args, unknown = parser.parse_known_args()
    sys.exit(main(input_files=args.input_files,
                  output_file=args.output_file))
