#! /usr/bin/env python

"""Extracts data from an Abaqus odb file.
Calls odbreport feature of Abaqus, parses resultant file, and creates output file.
Most simulation data lives in a group path following the instance and set name, e.g.
/INSTANCE/FieldOutputs/ELEMENT_SET, and can be accessed with xarray as
xarray.open_dataset("sample.h5", group="/INSTANCE/FieldOutputs/ELEMENT_SET"). You can view all group paths with
h5ls -r sample.h5. Additional ODB information is available in the /odb group path. The /xarray/Dataset group path
contains a list of group paths that contain an xarray dataset.

.. code-block::
   :caption: Format of HDF5 file

   /                 # Top level group required in all hdf5 files
   /<instance name>/ # Groups containing data of each instance found in an odb
       FieldOutputs/      # Group with multiple xarray datasets for each field output
           <field name>/  # Group with datasets containing field output data for a specified set or surface
                          # If no set or surface is specified, the <field name> will be 'ALL_NODES' or 'ALL_ELEMENTS'
       HistoryOutputs/    # Group with multiple xarray datasets for each history output
           <region name>/ # Group with datasets containing history output data for specified history region name
                          # If no history region name is specified, the <region name> will be 'ALL NODES'
       Mesh/              # Group written from an xarray dataset with all mesh information for this instance
   /<instance name>_Assembly/ # Group containing data of assembly instance found in an odb
       Mesh/              # Group written from an xarray dataset with all mesh information for this instance
   /odb/             # Catch all group for data found in the odbreport file not already organized by instance
       info/              # Group with datasets that mostly give odb meta-data like name, path, etc.
       jobData/           # Group with datasets that contain additional odb meta-data
       rootAssembly/      # Group with datasets that match odb file organization per Abaqus documentation
       sectionCategories/ # Group with datasets that match odb file organization per Abaqus documentation
   /xarray/          # Group with a dataset that lists the location of all data written from xarray datasets

"""

import os
import re
import sys
import json
import yaml
import shlex
import select
from shutil import which
from pathlib import Path
from subprocess import run
from datetime import datetime
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

from waves._abaqus import _settings
from waves._abaqus import abaqus_file_parser
from waves._utilities import _quote_spaces_in_path


_exclude_from_namespace = set(globals().keys())


def get_parser():
    """Get parser object for command line options

    :return: argument parser
    :rtype: parser
    """
    _program_name = Path(__file__).stem
    example = f''' Example: >> {_program_name} sample.odb\n '''
    parser = ArgumentParser(description=__doc__, formatter_class=ArgumentDefaultsHelpFormatter, epilog=example,
                            prog=_program_name)
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
                        help='Arguments to give to the odbreport command. Require the ``option=value`` interface style.',
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


def odb_extract(input_file,
                output_file,
                output_type='h5',
                odb_report_args=None,
                abaqus_command=_settings._default_abaqus_command,
                delete_report_file=False,
                verbose=False):
    """The odb_extract Abaqus data extraction tool. Most users should use the associated command line interface.

    .. warning::

       ``odb_extract`` *requires* Abaqus arguments for ``odb_report_args`` in the form of ``option=value``, e.g.
       ``step=step_name``.

    :param list input_file: A list of ``*.odb`` files to extract. Current implementation only supports extraction on the
        first file in the list.
    :param str output_file: The output file name to extract to. Extension should match on of the supported output types.
    :param str output_type: Output file type. Defaults to ``h5``. Options are: ``h5``, ``yaml``, ``json``.
    :param str odb_report_args: String of command line options to pass to ``abaqus odbreport``.
    :param str abaqus_command: The abaqus command name or absolute path to the Abaqus exectuble.
    :param bool delete_report_file: Boolean to delete the intermediate Abaqus generated report file after producing the
        ``output_file``.
    :param bool verbose: Boolean to print more verbose messages
    """

    # Handle arguments
    input_file = input_file[0]
    path_input_file = Path(input_file)
    odbreport_file = False
    if not path_input_file.exists():
        sys.exit(f'{input_file} does not exist.')
    if path_input_file.suffix != '.odb':
        print_warning(verbose, f'{input_file} is not an odb file. File will be assumed to be an odbreport file.')
        odbreport_file = True
    file_base_name = str(path_input_file.with_suffix(''))
    if not output_file:  # If no output file given, use the name and path of odb file, but change the extension
        output_file = f'{file_base_name}.{output_type}'
    path_output_file = Path(output_file)
    file_suffix = path_output_file.suffix.replace('.', '')
    if file_suffix != output_type:  # If file ends in different extension than requested output
        output_file = str(path_output_file.with_suffix(f'.{output_type}'))  # Change extension
        print_warning(verbose, f'Output specified as {output_type}, but output file extension is {file_suffix}. '
                       f'Changing output file extension. Output file name {output_file}')
        file_suffix = output_type

    time_stamp = datetime.now().strftime(_settings._default_timestamp_format)
    job_name = path_output_file.with_suffix('.csv')
    if path_output_file.exists():
        new_output_file = f"{str(path_output_file.with_suffix(''))}_{time_stamp}.{file_suffix}"
        print_warning(verbose, f'{output_file} already exists. Will use {new_output_file} instead.')
        output_file = new_output_file

    odb_report_args = get_odb_report_args(odb_report_args, input_file, job_name, verbose)

    abaqus_base_command = which(abaqus_command)
    if not abaqus_base_command:
        abaqus_base_command = _settings._default_abaqus_command  # try 'abaqus' anyway

    abaqus_command = f'{abaqus_base_command} odbreport {odb_report_args}'

    if odbreport_file:
        job_name = path_input_file
        call_odbreport = False
    else:
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
        return_code, output, error_code = run_external(abaqus_command)
        if return_code != 0:
            sys.exit(f"Abaqus odbreport command failed to execute. Abaqus output: '{output}'")
        if not Path(job_name).exists():
            sys.exit(f'{job_name} does not exist.')

    if output_type == 'h5':  # If the dataset isn't empty
        try:
            abaqus_file_parser.OdbReportFileParser(job_name, 'extract', output_file, time_stamp).parse(h5_file=output_file)
        except (IndexError, ValueError) as e:  # Index error is reached if a line is split and the line is empty (i.e. file is empty), ValueError is reached if a string is found where an integer is expected
            sys.exit(f'{job_name} could not be parsed. Please check if file is in expected format. {e}')
    else:
        parsed_odb = None
        # Parse output of odbreport
        try:
            parsed_odb = abaqus_file_parser.OdbReportFileParser(job_name, 'odb').parsed
        except (IndexError, ValueError) as e:  # Index error is reached if a line is split and the line is empty (i.e. file is empty)
            sys.exit(f'{job_name} could not be parsed. Please check if file is in expected format. {e}')

        # Write parsed output
        if output_type == 'json':
            with open(output_file, 'w') as f:
                json.dump(parsed_odb, f, indent=4)
        elif output_type == 'yaml':
            with open(output_file, 'w') as f:
                yaml.safe_dump(parsed_odb, f)  # With safe_dump, tuples are converted to lists

    if delete_report_file:
        Path(job_name).unlink(missing_ok=True)  # Remove odbreport file, don't raise exception if it doesn't exist
    return 0


def get_odb_report_args(odb_report_args, input_file, job_name, verbose):
    """
    Generates odb_report arguments

    :param str odb_report_args: String of command line options to pass to ``abaqus odbreport``.
    :param Path input_file: ``.odb`` file.
    :param Path job_name: Report file.
    :param bool verbose: Boolean to print more verbose messages
    """
    input_file = _quote_spaces_in_path(input_file)
    job_name = _quote_spaces_in_path(job_name)
    odb_report_args = odb_report_args
    if not odb_report_args:
        odb_report_args = f"job={job_name.with_suffix('')} odb={input_file} all mode=CSV blocked"
    else:
        if 'odb=' in odb_report_args or 'job=' in odb_report_args:
            print_warning(verbose,
                          f'Argument to odbreport cannot include odb or job. Will use default odbreport arguments.')
            odb_report_args = f"job={job_name.with_suffix('')} odb={input_file} all mode=CSV blocked"

    if 'odbreport' in odb_report_args:
        odb_report_args = odb_report_args.replace('odbreport', '')
    if 'odb=' not in odb_report_args:
        odb_report_args = f'odb={input_file} {odb_report_args.strip()}'
    if 'job=' not in odb_report_args:
        odb_report_args = f"job={job_name.with_suffix('')} {odb_report_args.strip()}"
    if 'blocked' not in odb_report_args:
        odb_report_args = f'{odb_report_args.strip()} blocked'
    if 'invariants' in odb_report_args:
        odb_report_args = odb_report_args.replace('invariants', '')
    if 'mode=' not in odb_report_args:
        odb_report_args = f'{odb_report_args.strip()} mode=CSV'
    # use regex that ignores case to replace 'html' or 'HTML' with 'CSV'
    odb_report_args = re.sub('(?i)' + re.escape('html'), lambda m: 'CSV', odb_report_args)
    return odb_report_args


def run_external(cmd):
    """
    Execute an external command and get its exitcode, stdout and stderr.

    :param str cmd: command line command to run
    :returns: output, return_code, error_code
    """
    args = shlex.split(cmd, posix=(os.name == 'posix'))
    p = run(args, capture_output=True)
    return p.returncode, p.stdout.decode(), p.stderr.decode()


def print_warning(verbose, message):
    """
    Log a message to the screen

    :param bool verbose: Whether to print or not
    :param str message: message to print
    """
    if verbose:
        print(message, file=sys.stderr)


def main():
    args = get_parser().parse_args()  # pragma: no cover
    sys.exit(odb_extract(args.input_file,
                         args.output_file,
                         args.output_type,
                         args.odb_report_args,
                         args.abaqus_command,
                         args.delete_report_file,
                         args.verbose,
            ))  # pragma: no cover


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover


# Limit help() and 'from module import *' behavior to the module's public API
_module_objects = set(globals().keys()) - _exclude_from_namespace
__all__ = [name for name in _module_objects if not name.startswith("_")]
