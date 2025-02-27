"""Internal API module implementing the parameter study subcommand(s) behavior.

Thin CLI wrapper around :meth:`waves.parameter_generators` classes

Should raise ``RuntimeError`` or a derived class of :class:`waves.exceptions.WAVESError` to allow the CLI implementation
to convert stack-trace/exceptions into STDERR message and non-zero exit codes.
"""

import io
import sys
import typing
import pathlib
import argparse

import yaml

from waves import _settings
from waves import parameter_generators


_exclude_from_namespace = set(globals().keys())


def get_parser() -> argparse.ArgumentParser:
    """Return a 'no-help' parser for the parameter study subcommand(s)

    :return: parser
    """
    # Required positional option
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        "INPUT_FILE",
        nargs="?",
        default=(None if sys.stdin.isatty() else sys.stdin),
        help="YAML formatted parameter study schema file (default: STDIN)",
    )

    # Mutually exclusive output file options
    output_file_group = parser.add_mutually_exclusive_group()
    output_file_group.add_argument(
        "-o",
        "--output-file-template",
        default=_settings._default_output_file_template,
        dest="OUTPUT_FILE_TEMPLATE",
        # fmt: off
        help="Output file template. May contain pathseps for an absolute or relative "
             f"path template. May contain the ``{_settings._template_placeholder}`` "
             "set number placeholder in the file basename but not in the path. "
             "If the placeholder is not found, it will be "
             "appended to the template string. Output files are overwritten if the "
             "content of the file has changed or if ``overwrite`` is True "
             "(default: %(default)s)",
        # fmt: on
    )
    output_file_group.add_argument(
        "-f",
        "--output-file",
        default=_settings._default_output_file,
        dest="OUTPUT_FILE",
        # fmt: off
        help=f"Output file name. May contain pathseps for an absolute or relative path. "
              "Output file is overwritten if the content of the file has changed or if "
              "``overwrite`` is True (default: %(default)s)",
        # fmt: on
    )

    # Optional keyword options
    parser.add_argument(
        "-t",
        "--output-file-type",
        default=_settings._default_output_file_type_cli,
        choices=_settings._allowable_output_file_types,
        help="Output file type (default: %(default)s)",
    )
    parser.add_argument(
        "-s",
        "--set-name-template",
        default=_settings._default_set_name_template,
        dest="SET_NAME_TEMPLATE",
        # fmt: off
        help="Parameter set name template. Overridden by ``output_file_template``, "
             "if provided (default: %(default)s)",
        # fmt: on
    )
    parser.add_argument(
        "-p",
        "--previous-parameter-study",
        default=_settings._default_previous_parameter_study,
        dest="PREVIOUS_PARAMETER_STUDY",
        # fmt: off
        help="A relative or absolute file path to a previously created parameter study Xarray "
             "Dataset (default: %(default)s)",
        # fmt: on
    )
    parser.add_argument(
        "--require-previous-parameter-study",
        action="store_true",
        help="Raise a ``RuntimeError`` if the previous parameter study file is missing (default: %(default)s)",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing output files (default: %(default)s)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print contents of new parameter study output files to STDOUT and exit (default: %(default)s)",
    )
    parser.add_argument(
        "--write-meta",
        action="store_true",
        # fmt: off
        help="Write a meta file named 'parameter_study_meta.txt' containing the parameter set file names "
             "(default: %(default)s)",
        # fmt: on
    )

    return parser


def read_parameter_schema(input_file: typing.Union[str, pathlib.Path, io.TextIOWrapper, None]) -> dict:
    """Read a YAML dictionary from STDIN or a file

    :param input_file: STDIN stream or file path

    :returns: dictionary

    :raises RuntimeError: if not STDIN and the file name does not exist
    """
    if input_file is None:
        raise RuntimeError("Require an input file path or a YAML formatted string on STDIN")
    if isinstance(input_file, io.TextIOWrapper):
        parameter_schema = yaml.safe_load(input_file)
    else:
        input_file = pathlib.Path(input_file)
        if not input_file.is_file():
            raise RuntimeError(f"File '{input_file}' does not exist.")
        with open(input_file, "r") as input_handle:
            parameter_schema = yaml.safe_load(input_handle)
    return parameter_schema


def main(
    subcommand: str,
    input_file: typing.Union[str, pathlib.Path, io.TextIOWrapper, None],
    output_file_template: typing.Optional[str] = _settings._default_output_file_template,
    output_file: typing.Optional[str] = _settings._default_output_file,
    output_file_type: _settings._allowable_output_file_typing = _settings._default_output_file_type_cli,
    set_name_template: str = _settings._default_set_name_template,
    previous_parameter_study: typing.Optional[str] = _settings._default_previous_parameter_study,
    require_previous_parameter_study: bool = _settings._default_require_previous_parameter_study,
    overwrite: bool = _settings._default_overwrite,
    dry_run: bool = _settings._default_dry_run,
    write_meta: bool = _settings._default_write_meta,
) -> None:
    """Build parameter studies

    :param str subcommand: parameter study type to build
    :param str input_file: path to YAML formatted parameter study schema file
    :param str output_file_template: output file template name
    :param str output_file: relative or absolute output file path
    :param str output_file_type: yaml or h5
    :param str set_name_template: parameter set name string template. May contain '@number' for the set number.
    :param str previous_parameter_study: relative or absolute path to previous parameter study file
    :param bool overwrite: overwrite all existing parameter set file(s)
    :param bool dry_run: print what files would have been written, but do no work
    :param bool write_meta: write a meta file name 'parameter_study_meta.txt' containing the parameter set file path(s)
    """
    try:
        parameter_schema = read_parameter_schema(input_file)
    except yaml.parser.ParserError as err:
        raise RuntimeError(f"Error loading '{input_file}'. Check the YAML syntax.\nyaml.parser.ParserError: {err}")

    # Retrieve and instantiate the subcommand class
    available_parameter_generators = {
        _settings._cartesian_product_subcommand: parameter_generators.CartesianProduct,
        _settings._custom_study_subcommand: parameter_generators.CustomStudy,
        _settings._latin_hypercube_subcommand: parameter_generators.LatinHypercube,
        _settings._sobol_sequence_subcommand: parameter_generators.SobolSequence,
        _settings._one_at_a_time_subcommand: parameter_generators.OneAtATime,
    }
    parameter_generator = available_parameter_generators[subcommand](
        parameter_schema,
        output_file_template=output_file_template,
        output_file=output_file,
        output_file_type=output_file_type,
        set_name_template=set_name_template,
        previous_parameter_study=previous_parameter_study,
        require_previous_parameter_study=require_previous_parameter_study,
        overwrite=overwrite,
        write_meta=write_meta,
    )

    # Build the parameter study.
    parameter_generator.write(dry_run=dry_run)


# Limit help() and 'from module import *' behavior to the module's public API
_module_objects = set(globals().keys()) - _exclude_from_namespace
__all__ = [name for name in _module_objects if not name.startswith("_")]
