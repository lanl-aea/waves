#! /usr/bin/env python

"""Extracts data from an Abaqus sta file.
Parses passed in sta file and writes the output to a yaml file

.. moduleauthor:: Prabhu S. Khalsa <pkhalsa@lanl.gov>
"""

from datetime import datetime
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from pathlib import Path

# Local modules
from waves.abaqus import abaqus_file_parser
from waves.abaqus import _settings

def get_parser():
    """Get parser object for command line options

    :return: argument parser
    :rtype: parser
    """
    example = f''' Example: >> python {Path(__file__).name} sample.sta\n '''
    parser = ArgumentParser(description=__doc__.split('..')[0],  # Don't include module author part of doc string
                            formatter_class=ArgumentDefaultsHelpFormatter, epilog=example)
    parser.add_argument(nargs=1,
                        dest='sta_file',
                        type=str,
                        help='sta file for parsing data',
                        metavar='sample.sta')
    parser.add_argument('-o', '--output-file',
                        dest='output_file',
                        type=str,
                        help='file for printing output',
                        metavar='sample.yaml')
    parser.add_argument('-v', '--verbose',
                        action="store_true",
                        dest='verbose',
                        default=False,
                        help='Print messages to screen')
    return parser


def main():
    args = get_parser().parse_args()

    # Handle arguments
    sta_file = args.sta_file[0]
    path_sta_file = Path(sta_file)
    if not path_sta_file.exists():
        print(f'{sta_file} does not exist.')
        raise SystemExit(-1)
    output_file = args.output_file
    if not output_file:
        output_file = path_sta_file.with_suffix(_settings._default_yaml_extension)
    path_output_file = Path(output_file)
    if path_output_file.exists():
        time_stamp = datetime.now().strftime(_settings._default_timestamp_format)
        file_suffix = path_output_file.suffix
        new_output_file = f"{str(path_output_file.with_suffix(''))}_{time_stamp}{file_suffix}"
        print(f'{output_file} already exists. Will use {new_output_file} instead.')
        output_file = new_output_file

    # Parse output of sta file
    parsed_sta = abaqus_file_parser.StaFileParser(sta_file)
    # Write to yaml file
    parsed_sta.write_yaml(output_file)

    return 0

