#! /usr/bin/env python

"""Extracts data from an Abaqus odb file.
Calls odbreport feature of Abaqus, parses resultant file, and creates output file.

.. moduleauthor:: Prabhu Khalsa <pkhalsa@lanl.gov>
"""

import sys
import json
import yaml
import select
import re
import shlex
import subprocess
from datetime import datetime
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from pathlib import Path
from shutil import which

# Local modules
from waves.abaqus import abaqus_file_parser
from waves.abaqus import _settings

def get_parser():
    """Get parser object for command line options

    :return: argument parser
    :rtype: parser
    """
    example = f''' Example: >> {Path(__file__).stem} sample.odb\n '''
    parser = ArgumentParser(description=__doc__.split('..')[0],  # Don't include module author part of doc string
                            formatter_class=ArgumentDefaultsHelpFormatter, epilog=example)
    parser.add_argument(nargs=1,
                        dest='input_file',
                        type=str,
                        help='odb or odbreport file for extracting data',
                        metavar='sample.odb')
    parser.add_argument('-o', '--output-file',
                        dest='output_file',
                        type=str,
                        help='file for printing output',
                        metavar='sample.h5')
    parser.add_argument('-f', '--output-file-type',
                        dest='output_type',
                        choices=['yaml', 'json', 'h5'],
                        type=str,
                        default='h5',
                        help='Type of file in which to store output data',
                        metavar='h5')
    parser.add_argument('-r', '--odb-report-args',
                        dest='odb_report_args',
                        type=str,
                        help='arguments to give to the odbreport command',
                        metavar='"step=step1 results"')
    parser.add_argument('-a', '--abaqus-command',
                        dest='abaqus_command',
                        type=str,
                        default=_settings._default_abaqus_command,
                        help='Abaqus command to use',
                        metavar='/path/to/abaqus')
    parser.add_argument('-d', '--delete-report-file',
                        action="store_true",
                        dest='delete_report_file',
                        default=False,
                        help='Delete after parsing the file created by the odbreport command')
    parser.add_argument('-v', '--verbose',
                        action="store_true",
                        dest='verbose',
                        default=False,
                        help='Print all messages')
    return parser


def main():
    args = get_parser().parse_args()

    # Handle arguments
    input_file = args.input_file[0]
    path_input_file = Path(input_file)
    odbreport_file = False
    if not path_input_file.exists():
        log_critical(f'{input_file} does not exist.')
    if path_input_file.suffix != '.odb':
        log_warning(f'{input_file} is not an odb file. File will be assumed to be an odbreport file.')
        odbreport_file = True
    file_base_name = str(path_input_file.with_suffix(''))
    output_file = args.output_file
    if not output_file:  # If no output file given, use the name and path of odb file, but change the extension
        output_file = f'{file_base_name}.{args.output_type}'
    path_output_file = Path(output_file)
    file_suffix = path_output_file.suffix.replace('.', '')
    if file_suffix != args.output_type:  # If file ends in different extension than requested output
        output_file = str(path_output_file.with_suffix(f'.{args.output_type}'))  # Change extension
        log_warning(f'Output specified as {args.output_type}, but output file extension is {file_suffix}. '
                       f'Changing output file extension. Output file name {output_file}')
        file_suffix = args.output_type
    odb_report_args = args.odb_report_args
    job_name = file_base_name
    time_stamp = datetime.now().strftime(_settings._default_timestamp_format)
    if not odb_report_args:
        odb_report_args = f'job={job_name} odb={input_file} all mode=CSV blocked'
    else:
        if 'odb=' in odb_report_args or 'job=' in odb_report_args:
            log_warning(f'Argument to odbreport cannot include odb or job. Will use default odbreport arguments.')
            odb_report_args = f'job={job_name} odb={input_file} all mode=CSV blocked'
    if path_output_file.exists():
        new_output_file = f"{str(path_output_file.with_suffix(''))}_{time_stamp}.{file_suffix}"
        log_warning(f'{output_file} already exists. Will use {new_output_file} instead.')
        output_file = new_output_file

    if 'odbreport' in odb_report_args:
        odb_report_args = odb_report_args.replace('odbreport', '')
    if 'odb=' not in odb_report_args:
        odb_report_args = f'odb={input_file} {odb_report_args.strip()}'
    if 'job=' not in odb_report_args:
        odb_report_args = f'job={job_name} {odb_report_args.strip()}'
    if 'blocked' not in odb_report_args:
        odb_report_args = f'{odb_report_args.strip()} blocked'
    if 'invariants' in odb_report_args:
        odb_report_args = odb_report_args.replace('invariants', '')
    if 'mode' not in odb_report_args:
        odb_report_args = f'{odb_report_args.strip()} mode=CSV'
    # use regex that ignores case to replace 'html' or 'HTML' with 'CSV'
    odb_report_args = re.sub('(?i)' + re.escape('html'), lambda m: 'CSV', odb_report_args)

    abaqus_base_command = which(args.abaqus_command)
    if not abaqus_base_command:
        abaqus_base_command = _settings._default_abaqus_command  # try 'abaqus' anyway

    abaqus_command = f'{abaqus_base_command} odbreport {odb_report_args}'

    if odbreport_file:
        job_name = path_input_file
        call_odbreport = False
    else:
        job_name = f'{file_base_name}{_settings._default_odbreport_extension}'
        call_odbreport = True
    if Path(job_name).exists() and not odbreport_file:
        call_odbreport = False  # Don't call odbreport again if the report file already exists
        print(f"Report file {job_name} already exists, would you like to use this file?")
        i, o, e = select.select([sys.stdin], [], [], 15)  # Wait 15 seconds for user input
        if i:
            answer = sys.stdin.readline().strip()
            if answer[:1].lower() != 'y':
                call_odbreport = True  # If user input is not yes, run odbreport again
    if call_odbreport:
        # Call odbreport
        output, return_code, error_code = run_external(abaqus_command)
        if return_code != 0:
            log_critical(f'Abaqus odbreport command failed to execute. {error_code}')
        if not Path(job_name).exists():
            log_critical(f'{job_name} does not exist.')

    if args.output_type == 'h5':  # If the dataset isn't empty
        try:
            abaqus_file_parser.OdbReportFileParser(job_name, 'extract', output_file, time_stamp)
        except (IndexError, ValueError) as e:  # Index error is reached if a line is split and the line is empty (i.e. file is empty), ValueError is reached if a string is found where an integer is expected
            log_critical(f'{job_name} could not be parsed. Please check if file is in expected format. {e}')
    else:
        parsed_odb = None
        # Parse output of odbreport
        try:
            parsed_odb = abaqus_file_parser.OdbReportFileParser(job_name, 'odb').parsed
        except (IndexError, ValueError) as e:  # Index error is reached if a line is split and the line is empty (i.e. file is empty)
            log_critical(f'{job_name} could not be parsed. Please check if file is in expected format. {e}')

        # Write parsed output
        if args.output_type == 'json':
            with open(output_file, 'w') as f:
                json.dump(parsed_odb, f, indent=4)
        elif args.output_type == 'yaml':
            with open(output_file, 'w') as f:
                yaml.safe_dump(parsed_odb, f)  # With safe_dump, tuples are converted to lists

    if args.delete_report_file:
        Path(job_name).unlink(missing_ok=True)  # Remove odbreport file, don't raise exception if it doesn't exist
    return 0

def run_external(cmd, env=None, stdout_file=None):
    """
    Execute an external command and get its exitcode, stdout and stderr.

    :param str cmd: command line command to run
    :param dict env: environment mapping for new process
    :param str stdout_file: file to pipe STDOUT
    :returns: output, return_code, error_code
    """
    args = shlex.split(cmd, posix=(os.name == 'posix'))
    proc = subprocess.Popen(args, stdin=subprocess.DEVNULL, stdout=stdout_file, stderr=subprocess.PIPE, env=env)
    out, error_code = proc.communicate()
    exit_code = proc.returncode
    return exit_code, out, error_code

def log_warning(verbose, message):
    """
    Log a message to the screen

    :param bool verbose: Whether to print or not
    :param bool message: message to print
    """
    if verbose:
        print(message)

def log_critical(message):
    """
    Log a message to the screen and exit

    :param bool verbose: Whether to print or not
    :param bool message: message to print
    """
    print(message)
    raise SystemExit(-1)


if __name__ == '__main__':
    sys.exit(main())  # pragma: no cover
