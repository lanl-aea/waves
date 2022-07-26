#!/usr/bin/env python
"""stress strain comparison"""

import sys
import argparse
import pathlib


def main(input_files, output_file):
    return 0


def get_parser():
    script_name = pathlib.Path(__file__)
    default_output_file = script_name.stem

    prog = f"python {script_name.name} "
    cli_description = "Read Xarray Datasets and plot stress-strain comparisons. Save to ``output_file``.pdf."
    parser = argparse.ArgumentParser(description=cli_description,
                                     prog=prog)
    parser.add_argument('-i', '--input-files', nargs='+',
                        help="The Xarray Dataset file(s)")
    parser.add_argument('-o', '--output-file', type=str, default=default_output_file,
                        help="The output file for for the stress-strain comparison plot, e.g. ``output_file``.pdf")
    return parser


if __name__ == "__main__":
    parser = get_parser()
    args, unknown = parser.parse_known_args()
    sys.exit(main(input_files=args.input_files,
                  output_file=args.output_file))
