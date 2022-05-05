#!/usr/bin/env python
"""
parameter_study - Python based generator of parameter studies

.. moduleauthor:: Kyle Brindley <kbrindley@lanl.gov>
"""

from abc import ABC, abstractmethod
import argparse
from argparse import ArgumentParser
import pathlib
import string
import sys
import itertools

import yaml

#========================================================================================================== SETTINGS ===
# Files normally found in a project's root settings.py, __init__.py, or configuration.py file(s)
# Assign some hard coded script specific meta data
__version__ = '0.1.2'
__author__ = 'Kyle Brindley <kbrindley@lanl.gov>'
PROJECT_NAME_SHORT = 'parameter_study'
template_delimiter = '@'


class AtSignTemplate(string.Template):
    delimiter = template_delimiter


template_placeholder = f"{template_delimiter}number"
default_output_file_template = AtSignTemplate(f'parameter_set{template_placeholder}')
parameter_study_meta_file = "parameter_study_meta.txt"

#============================================================================================ COMMAND LINE INTERFACE ===
def get_parser():
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
                                 prog=PROJECT_NAME_SHORT,
                                 epilog=f"author(s): {__author__}")
    main_parser.add_argument('-V', '--version',
                             action='version',
                             version=f"{PROJECT_NAME_SHORT} {__version__}")

    parent_parser = ArgumentParser(add_help=False)
    parent_parser.add_argument('INPUT_FILE', nargs='?', type=argparse.FileType('r'),
                               default=sys.stdin,
                               help=f"Parameter study configuration file (default: STDIN)")
    parent_parser.add_argument('-o', '--output-file-template',
                               default=None, dest='OUTPUT_FILE_TEMPLATE',
                               help=f"Output file template. May contain '{template_placeholder}' placeholder for " \
                                    f"the set number. If the placeholder is not found, it will be appended to the " \
                                    f"template string. (default: %(default)s)")
    parent_parser.add_argument('--overwrite', action='store_true',
                               help=f"Overwrite existing output files (default: %(default)s)")
    parent_parser.add_argument('--dryrun', action='store_true',
                               help=f"Print contents of new parameter study output files to STDOUT and exit " \
                                    f"(default: %(default)s)")
    parent_parser.add_argument('--debug', action='store_true',
                               help=f"Print internal variables to STDOUT and exit (default: False)")

    subparsers = main_parser.add_subparsers(
        help=f"Specify which parameter study generator to use",
        title="subcommands",
        description=f"Available parameter study generators",
        dest='subcommand')

    cartesian_product_parser = subparsers.add_parser('cartesian_product', description=generator_description,
                                                     help='Cartesian product generator',
                                                     parents=[parent_parser])

    return main_parser


# ========================================================================================== PARAMETER STUDY CLASSES ===

class ParameterGenerator(ABC):
    """Abstract base class for internal parameter study generators

    :param str parameter_schema: The loaded parameter study schema file contents
    :param list output_file_template: Output file name template
    :param bool overwrite: Overwrite existing output files
    :param bool dryrun: Print contents of new parameter study output files to STDOUT and exit
    :param bool debug: Print internal variables to STDOUT and exit
    """
    def __init__(self, parameter_schema, output_file_template, overwrite, dryrun, debug):
        self.parameter_schema = parameter_schema
        self.output_file_template = output_file_template
        self.overwrite = overwrite
        self.dryrun = dryrun
        self.debug = debug

        self.default_template = default_output_file_template
        self.provided_template = False
        if self.output_file_template:
            if not f'{template_placeholder}' in self.output_file_template:
                self.output_file_template = f"{self.output_file_template}{template_placeholder}"
            self.output_file_template = AtSignTemplate(self.output_file_template)
            self.provided_template = True
        else:
            self.output_file_template = self.default_template

    @abstractmethod
    def validate(self):
        """Process parameter study input to verify schema

        :returns: validated_schema
        :rtype: bool
        """
        pass

    @abstractmethod
    def generate(self):
        """Generate the parameter study definition

        Must set:
        * ``self.parameter_study``
        """
        pass

    def write(self):
        """Write the parameter study to STDOUT or an output file.

        If printing to STDOUT, print all parameter sets together. If printing to files, don't overwrite existing files.
        If overwrite is specified, overwrite all parameter set files. If a dry run is requested print file-content
        associations for files that would have been written.
        """
        self.write_meta()
        for parameter_set_file, text in self.parameter_study.items():
            # If no output file template is provided, print to stdout
            if not self.provided_template:
                sys.stdout.write(f"{parameter_set_file.name}:\n{text}")
            # If overwrite is specified or if file doesn't exist
            elif self.overwrite or not parameter_set_file.is_file():
                # If dry run is specified, print the files that would have been written to stdout
                if self.dryrun:
                    sys.stdout.write(f"{parameter_set_file.absolute()}:\n{text}")
                else:
                    with open(parameter_set_file, 'w') as outfile:
                        outfile.write(text)

    def write_meta(self):
        """Write the parameter study meta data file.

        The parameter study meta file is always overwritten. It should *NOT* be used to determine if the parameter study
        target or dependee is out-of-date.
        """
        # TODO: Don't write meta for STDOUT output stream
        # Always overwrite the meta data file to ensure that *all* parameter file names are included.
        with open(f'{parameter_study_meta_file}', 'w') as meta_file:
            for parameter_set_file in self.parameter_study.keys():
                meta_file.write(f"{parameter_set_file.name}\n")


class CartesianProduct(ParameterGenerator):
    """Builds a cartesian product parameter study

    :param str parameter_schema: The loaded parameter study schema file contents
    :param list output_file_template: Output file name template
    :param bool overwrite: Overwrite existing output files
    :param bool dryrun: Print contents of new parameter study output files to STDOUT and exit
    :param bool debug: Print internal variables to STDOUT and exit
    """

    def validate(self):
        # TODO: Settle on an input file schema and validation library
        # https://re-git.lanl.gov/kbrindley/cmake-simulation/-/issues/69
        return True

    def generate(self):
        parameter_names = list(self.parameter_schema.keys())
        parameter_sets = list(itertools.product(*self.parameter_schema.values()))
        parameter_set_names = []
        parameter_set_text = []
        # TODO: Separate the parameter study object from the output file syntax
        # https://re-git.lanl.gov/kbrindley/cmake-simulation/-/issues/36
        for number, parameter_set in enumerate(parameter_sets):
            template = self.output_file_template
            parameter_set_names.append(template.substitute({'number': number}))
            text = ''
            for name, value in zip(parameter_names, parameter_set):
                text = f'{text}set({name} "{value}")\n'
            parameter_set_text.append(text)
        self.parameter_study = {pathlib.Path(set_name): set_text for set_name, set_text in
                                zip(parameter_set_names, parameter_set_text)}


# ============================================================================================= PARAMETER STUDY MAIN ===
def main():
    """
    Build parameter studies

    :returns: return code
    """

    # Console scripts must parse arguments outside of __main__
    parser = get_parser()
    args = parser.parse_args()

    # Set variables from CLI argparse output
    subcommand = args.subcommand
    input_file = args.INPUT_FILE
    # TODO: accept an output file template and manage file writeability outside argparse
    # May require and additional --output-dir option and otherwise assume PWD
    # https://re-git.lanl.gov/kbrindley/cmake-simulation/-/issues/33
    output_file_template = args.OUTPUT_FILE_TEMPLATE
    overwrite = args.overwrite
    dryrun = args.dryrun
    debug = args.debug

    if debug:
        print(f"subcommand           = {subcommand}")
        print(f"input_file           = {input_file}")
        print(f"output_file_template = {output_file_template}")
        print(f"overwrite            = {overwrite}")
        return 0

    # Clean the output file template if specified
    if output_file_template:
        output_file_tempalte = pathlib.Path(args.OUTPUT_FILE_TEMPLATE).name

    # Read the input stream
    # TODO: Handle input file outside of argparse
    # https://re-git.lanl.gov/kbrindley/cmake-simulation/-/issues/32
    parameter_schema = yaml.safe_load(input_file)
    input_file.close()

    # Retrieve the subcommand class
    # TODO: Move parameter study class(es) to a separate module file. Will change the class creation technique
    available_parameter_generators = \
        {'cartesian_product': CartesianProduct}
    parameter_generator = \
        available_parameter_generators[subcommand](parameter_schema, output_file_template, overwrite, dryrun, debug)

    # Build the parameter study
    if not parameter_generator.validate():
        print("Parameter schema validation failed. Please review the input file for syntax errors")
        return 1
    parameter_generator.generate()
    parameter_generator.write()

    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
