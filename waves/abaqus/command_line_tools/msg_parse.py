#! /usr/bin/env python

"""Extracts data from an Abaqus msg file.
Parses passed in msg file and writes the output to a yaml file

.. moduleauthor:: Prabhu S. Khalsa <pkhalsa@lanl.gov>
"""

import sys
from datetime import datetime
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from pathlib import Path

from waves.abaqus import abaqus_file_parser
from waves.abaqus import _settings


def get_parser():
    """Get parser object for command line options

    :return: argument parser
    :rtype: parser
    """
    _program_name = Path(__file__).stem
    example = f''' Example: >> {_program_name} sample.msg\n '''
    parser = ArgumentParser(description=__doc__.split('..')[0],  # Don't include module author part of doc string
                            formatter_class=ArgumentDefaultsHelpFormatter, epilog=example, prog=_program_name)
    parser.add_argument(nargs=1,
                        dest='msg_file',
                        type=str,
                        help='msg file for parsing data',
                        metavar='sample.msg')
    parser.add_argument('-o', '--output-file',
                        dest='output_file',
                        type=str,
                        help='file for printing output',
                        metavar='sample.yaml')
    parser.add_argument('-s', '--write-summary',
                        action="store_true",
                        dest='write_summary_table',
                        default=False,
                        help='Write a summary of the data in a table')
    parser.add_argument('-a', '--write-all',
                        action="store_true",
                        dest='write_all',
                        default=False,
                        help='Write the parsed data in an organized format that is also easy to visually parse')
    parser.add_argument('-y', '--write-yaml',
                        action="store_true",
                        dest='write_yaml',
                        default=True,
                        help='Write the parsed data into a yaml file')
    return parser


def main():
    args = get_parser().parse_args()

    # Handle arguments
    msg_file = args.msg_file[0]
    path_msg_file = Path(msg_file)
    if not path_msg_file.exists():
        print(f'{msg_file} does not exist.')
        raise SystemExit(-1)
    output_file = args.output_file
    if not output_file:
        output_file = path_msg_file.with_suffix('')
    path_output_file = Path(output_file)

    # Parse output of msg file
    parsed_msg = abaqus_file_parser.MsgFileParser(msg_file)

    if args.write_yaml:
        output_file = file_exists(path_output_file.with_suffix(_settings._default_yaml_extension))
        parsed_msg.write_yaml(output_file)
    if args.write_all:
        output_file = file_exists(path_output_file.with_suffix(_settings._default_parsed_extension))
        parsed_msg.write_all(output_file)
    if args.write_summary_table:
        output_file = file_exists(path_output_file.with_suffix('.summary'))
        parsed_msg.write_summary_table(output_file)

    return 0

def file_exists(output_file):
    """Check if file exists and add time stamp to file name if it does

    :param pathlib.Path output_file: Name of file to check
    :return: new file name
    :rtype: pathlib.Path
    """
    if output_file.exists():
        time_stamp = datetime.now().strftime(_settings._default_timestamp_format)
        file_suffix = output_file.suffix
        new_output_file = f"{str(output_file.with_suffix(''))}_{time_stamp}{file_suffix}"
        print(f'{output_file} already exists. Will use {new_output_file} instead.')
        return str(new_output_file)
    else:
        return str(output_file)

if __name__ == '__main__':
    sys.exit(main())  # pragma: no cover
