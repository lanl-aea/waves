#!/usr/bin/env python
"""parameter_study - Python based generator of parameter studies"""

__author__ = 'Kyle Brindley <kbrindley@lanl.gov>'

import argparse
from argparse import ArgumentParser
import pathlib
import sys

import yaml

from waves import __version__
from waves import parameter_generators

#========================================================================================================== SETTINGS ===
# Variables normally found in a project's root settings.py file(s)
_program_name = pathlib.Path(__file__).stem
cartesian_product_subcommand = 'cartesian_product'

#============================================================================================ COMMAND LINE INTERFACE ===
def get_parser(return_subparser_dictionary=False):
    """Get parser object for command line options

    :return: argument parser
    :rtype: parser
    """
    main_description = "Generates parameter studies in various output formats."
    generator_description = \
        "Writes parameter study to STDOUT by default. If an output file template " \
        "is specified, output one file per parameter set if and only if that parameter " \
        "set's file doesn't already exist. The overwrite option will overwrite all " \
        "parameter set files. The dry run option will print a list of files and contents " \
        "that would have been  written."
    main_parser = ArgumentParser(description=main_description,
                                 prog=_program_name,
                                 epilog=f"author(s): {__author__}")
    main_parser.add_argument('-V', '--version',
                             action='version',
                             version=f"{_program_name} {__version__}")

    parent_parser = ArgumentParser(add_help=False)
    parent_parser.add_argument('INPUT_FILE', nargs='?', type=argparse.FileType('r'),
                               default=(None if sys.stdin.isatty() else sys.stdin),
                               help=f"Parameter study configuration file (default: STDIN)")
    parent_parser.add_argument('-o', '--output-file-template',
                               default=None, dest='OUTPUT_FILE_TEMPLATE',
                               help=f"Output file template. May contain '{parameter_generators.template_placeholder} " \
                                    f"placeholder for the set number. If the placeholder is not found, it will be " \
                                    f"appended to the template string. (default: %(default)s)")
    parent_parser.add_argument('--overwrite', action='store_true',
                               help=f"Overwrite existing output files (default: %(default)s)")
    parent_parser.add_argument('--dryrun', action='store_true',
                               help=f"Print contents of new parameter study output files to STDOUT and exit " \
                                    f"(default: %(default)s)")
    parent_parser.add_argument('--debug', action='store_true',
                               help="Print internal variables to STDOUT and exit (default: %(default)s)")
    parent_parser.add_argument('--write-meta', action='store_true',
                               help="Write a meta file named 'parameter_study_meta.txt' containing the " \
                                    "parameter set file names (default: %(default)s)")

    subparsers = main_parser.add_subparsers(
        help=f"Specify which parameter study generator to use",
        title="subcommands",
        description=f"Available parameter study generators",
        dest='subcommand')

    cartesian_product_parser = subparsers.add_parser(cartesian_product_subcommand, description=generator_description,
                                                     help='Cartesian product generator',
                                                     parents=[parent_parser])

    subparser_dictionary = {cartesian_product_subcommand: cartesian_product_parser}

    if return_subparser_dictionary:
        return subparser_dictionary
    else:
        return main_parser

# ============================================================================================= PARAMETER STUDY MAIN ===
def main():
    """
    Build parameter studies

    :returns: return code
    """

    # Console scripts must parse arguments outside of __main__
    parser = get_parser()
    subparser_dictionary = get_parser(return_subparser_dictionary=True)
    args = parser.parse_args()

    # Set variables from CLI argparse output
    subcommand = args.subcommand
    if not subcommand:
        parser.print_usage()
        return 0
    input_file = args.INPUT_FILE
    if not input_file:
        subparser_dictionary[subcommand].print_usage()
        return 0
    # TODO: accept an output file template and manage file writeability outside argparse
    # May require and additional --output-dir option and otherwise assume PWD
    # https://re-git.lanl.gov/aea/python-projects/waves/-/issues/79
    output_file_template = args.OUTPUT_FILE_TEMPLATE
    overwrite = args.overwrite
    dryrun = args.dryrun
    debug = args.debug
    write_meta = args.write_meta

    if debug:
        print(f"subcommand           = {subcommand}")
        print(f"input_file           = {input_file}")
        print(f"output_file_template = {output_file_template}")
        print(f"overwrite            = {overwrite}")
        print(f"write_meta           = {write_meta}")
        return 0

    # Clean the output file template if specified
    if output_file_template:
        output_file_template = pathlib.Path(args.OUTPUT_FILE_TEMPLATE).name

    # Read the input stream
    # TODO: Handle input file outside of argparse
    # https://re-git.lanl.gov/aea/python-projects/waves/-/issues/72
    parameter_schema = yaml.safe_load(input_file)
    input_file.close()

    # Retrieve and instantiate the subcommand class
    available_parameter_generators = \
        {cartesian_product_subcommand: parameter_generators.CartesianProduct}
    parameter_generator = \
        available_parameter_generators[subcommand](parameter_schema, output_file_template,
                                                   overwrite, dryrun, debug, write_meta)

    # Build the parameter study
    parameter_generator.generate()
    parameter_generator.write()

    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
