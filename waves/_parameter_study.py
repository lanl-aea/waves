"""Thin CLI wrapper around :meth:`waves.parameter_generators` classes"""

import argparse
import sys
import typing

import yaml

from waves import _settings
from waves import parameter_generators


def parameter_study_parser() -> argparse.ArgumentParser:
    # Required positional option
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('INPUT_FILE', nargs='?', default=(None if sys.stdin.isatty() else sys.stdin),
                        help=f"YAML formatted parameter study schema file (default: STDIN)")

    # Mutually exclusive output file options
    output_file_group = parser.add_mutually_exclusive_group()
    output_file_group.add_argument('-o', '--output-file-template',
                                   default=parameter_generators._default_output_file_template, dest='OUTPUT_FILE_TEMPLATE',
                                   help=f"Output file template. May contain pathseps for an absolute or relative " \
                                        f"path template. May contain ``{parameter_generators._template_placeholder}`` " \
                                        f"set number placeholder in the file basename but not in the path. " \
                                        f"If the placeholder is not found, it will be " \
                                        f"appended to the template string. Output files are overwritten if the "
                                        f"content of the file has changed or if ``overwrite`` is True "
                                        f"(default: %(default)s)")
    output_file_group.add_argument('-f', '--output-file',
                                   default=parameter_generators._default_output_file, dest='OUTPUT_FILE',
                                   help=f"Output file name. May contain pathseps for an absolute or relative path. " \
                                         "Output file is overwritten if the content of the file has changed or if " \
                                         "``overwrite`` is True (default: %(default)s)")

    # Optional keyword options
    parser.add_argument('-t', '--output-file-type',
                               default=parameter_generators._default_output_file_type,
                               choices=parameter_generators._allowable_output_file_types,
                               help="Output file type (default: %(default)s)")
    parser.add_argument('-s', '--set-name-template',
                               default=parameter_generators._default_set_name_template, dest='SET_NAME_TEMPLATE',
                               help="Parameter set name template. Overridden by ``output_file_template``, " \
                                    "if provided (default: %(default)s)")
    parser.add_argument('-p', '--previous-parameter-study',
                               default=parameter_generators._default_previous_parameter_study, dest='PREVIOUS_PARAMETER_STUDY',
                               help="A relative or absolute file path to a previously created parameter study Xarray " \
                                    "Dataset (default: %(default)s)")
    parser.add_argument('--overwrite', action='store_true',
                               help=f"Overwrite existing output files (default: %(default)s)")
    parser.add_argument('--dryrun', action='store_true',
                               help=f"Print contents of new parameter study output files to STDOUT and exit " \
                                    f"(default: %(default)s)")
    parser.add_argument('--write-meta', action='store_true',
                               help="Write a meta file named 'parameter_study_meta.txt' containing the " \
                                    "parameter set file names (default: %(default)s)")
    return parser


def parameter_study(subcommand: str,
                    input_file_path: str,
                    output_file_template: str = parameter_generators._default_output_file_template,
                    output_file: str = parameter_generators._default_output_file,
                    output_file_type: typing.Literal["yaml", "h5"] = parameter_generators._default_output_file_type,
                    set_name_template: str = parameter_generators._default_set_name_template,
                    previous_parameter_study: str = parameter_generators._default_previous_parameter_study,
                    overwrite: bool = parameter_generators._default_overwrite,
                    dryrun: bool = parameter_generators._default_dryrun,
                    write_meta: bool = parameter_generators._default_write_meta) -> int:
    """Build parameter studies

    :param str subcommand: parameter study type to build
    :param str input_file_path: path to YAML formatted parameter study schema file
    :param str output_file_template: output file template name
    :param str output_file: relative or absolute output file path
    :param str output_file_type: yaml or h5
    :param str set_name_template: parameter set name string template. May contain '@number' for the set number.
    :param str previous_parameter_study: relative or absolute path to previous parameter study file
    :param bool overwrite: overwrite all existing parameter set file(s)
    :param bool dryrun: print what files would have been written, but do no work
    :param bool write_meta: write a meta file name 'parameter_study_meta.txt' containing the parameter set file path(s)

    :returns: return code
    """

    # Read the input stream
    with open(input_file_path, 'r') as input_file:
        parameter_schema = yaml.safe_load(input_file)

    # Retrieve and instantiate the subcommand class
    available_parameter_generators = {
        _settings._cartesian_product_subcommand: parameter_generators.CartesianProduct,
        _settings._custom_study_subcommand: parameter_generators.CustomStudy,
        _settings._latin_hypercube_subcommand: parameter_generators.LatinHypercube,
        _settings._sobol_sequence_subcommand: parameter_generators.SobolSequence
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
            write_meta=write_meta
        )

    # Build the parameter study.
    parameter_generator.write()

    return 0
