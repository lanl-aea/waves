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

# ========================================================================================================= SETTINGS ===
# Variables normally found in a project's root settings.py file(s)
_program_name = pathlib.Path(__file__).stem
cartesian_product_subcommand = 'cartesian_product'
custom_study_subcommand = 'custom_study'
latin_hypercube_subcommand = 'latin_hypercube'
sobol_sequence_subcommand = 'sobol_sequence'


# =========================================================================================== COMMAND LINE INTERFACE ===
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

    # Required positional option
    parent_parser = ArgumentParser(add_help=False)
    parent_parser.add_argument('INPUT_FILE', nargs='?', type=argparse.FileType('r'),
                               default=(None if sys.stdin.isatty() else sys.stdin),
                               help=f"YAML formatted parameter study schema file (default: STDIN)")

    # Mutually exclusive output file options
    output_file_group = parent_parser.add_mutually_exclusive_group()
    output_file_group.add_argument('-o', '--output-file-template',
                                   default=None, dest='OUTPUT_FILE_TEMPLATE',
                                   help=f"Output file template. May contain pathseps for an absolute or relative " \
                                        f"path template. May contain ``{parameter_generators.template_placeholder}`` " \
                                        f"set number placeholder in the file basename but not in the path. " \
                                        f"If the placeholder is not found, it will be " \
                                        f"appended to the template string. (default: %(default)s)")
    output_file_group.add_argument('-f', '--output-file',
                                   default=None, dest='OUTPUT_FILE',
                                   help=f"Output file name. May contain pathseps for an absolute or relative path. " \
                                         "Output file is overwritten if the content of the file has changed. " \
                                         "(default: %(default)s)")

    # Optional keyword options
    parent_parser.add_argument('-t', '--output-file-type',
                               default='yaml',
                               choices=['yaml', 'h5'],
                               help="Output file type (default: %(default)s)")
    parent_parser.add_argument('-s', '--set-name-template',
                               default='parameter_set@number', dest='SET_NAME_TEMPLATE',
                               help="Parameter set name template. Overridden by ``output_file_template``, " \
                                    "if provided (default: %(default)s)")
    parent_parser.add_argument('-p', '--previous-parameter-study',
                               default=None, dest='PREVIOUS_PARAMETER_STUDY',
                               help="A relative or absolute file path to a previously created parameter study Xarray " \
                                    "Dataset (default: %(default)s)")
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
        dest='subcommand')

    cartesian_product_parser = subparsers.add_parser(
        cartesian_product_subcommand,
        description=generator_description,
        help='Cartesian product generator',
        parents=[parent_parser]
    )

    custom_study_parser = subparsers.add_parser(
        custom_study_subcommand,
        description=generator_description,
        help='Custom study generator',
        parents=[parent_parser]
    )

    latin_hypercube_parser = subparsers.add_parser(
        latin_hypercube_subcommand,
        description=f"{generator_description} The 'h5' output is the only output type that contains both the " \
                    "parameter samples and quantiles.",
        help='Latin hypercube generator',
        parents=[parent_parser]
    )

    sobol_sequence_parser = subparsers.add_parser(
        sobol_sequence_subcommand,
        description=f"{generator_description} The 'h5' output is the only output type that contains both the " \
                    "parameter samples and quantiles.",
        help='Sobol sequence generator',
        parents=[parent_parser]
    )

    subparser_dictionary = {
        cartesian_product_subcommand: cartesian_product_parser,
        custom_study_subcommand: custom_study_parser,
        latin_hypercube_subcommand: latin_hypercube_parser,
        sobol_sequence_subcommand: sobol_sequence_parser
    }

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
    output_file_template = args.OUTPUT_FILE_TEMPLATE
    output_file = args.OUTPUT_FILE
    output_file_type = args.output_file_type
    set_name_template = args.SET_NAME_TEMPLATE
    previous_parameter_study = args.PREVIOUS_PARAMETER_STUDY
    overwrite = args.overwrite
    dryrun = args.dryrun
    debug = args.debug
    write_meta = args.write_meta

    if debug:
        print(f"subcommand               = {subcommand}")
        print(f"input_file               = {input_file}")
        print(f"output_file_template     = {output_file_template}")
        print(f"output_file              = {output_file}")
        print(f"output_file_type         = {output_file_type}")
        print(f"set_name_template        = {set_name_template}")
        print(f"previous_parameter_study = {previous_parameter_study}")
        print(f"overwrite                = {overwrite}")
        print(f"write_meta               = {write_meta}")
        return 0

    # Read the input stream
    # TODO: Handle input file outside of argparse
    # https://re-git.lanl.gov/aea/python-projects/waves/-/issues/72
    parameter_schema = yaml.safe_load(input_file)
    input_file.close()

    # Retrieve and instantiate the subcommand class
    available_parameter_generators = {
        cartesian_product_subcommand: parameter_generators.CartesianProduct,
        custom_study_subcommand: parameter_generators.CustomStudy,
        latin_hypercube_subcommand: parameter_generators.LatinHypercube,
        sobol_sequence_subcommand: parameter_generators.SobolSequence
    }
    parameter_generator = \
        available_parameter_generators[subcommand](
            parameter_schema,
            output_file_template=output_file_template,
            output_file=output_file,
            output_file_type=output_file_type,
            set_name_template=set_name_template,
            previous_parameter_study=previous_parameter_study,
            overwrite=overwrite,
            dryrun=dryrun,
            debug=debug,
            write_meta=write_meta
        )

    # Build the parameter study.
    parameter_generator.write()

    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
