"""Internal API module implementing the parameter study subcommand(s) behavior.

Thin CLI wrapper around :meth:`waves.parameter_generators` classes

Should raise ``RuntimeError`` or a derived class of :class:`waves.exceptions.WAVESError` to allow the CLI implementation
to convert stack-trace/exceptions into STDERR message and non-zero exit codes.
"""

import argparse
import io
import pathlib
import sys

import yaml

from waves import _settings, parameter_generators

_exclude_from_namespace = set(globals().keys())


def get_parser() -> argparse.ArgumentParser:
    """Return a 'no-help' parser for the parameter study subcommand(s).

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
        "-f",
        "--output-file",
        type=pathlib.Path,
        default=_settings._default_output_file,
        dest="OUTPUT_FILE",
        help=(
            "Write a single parameter study file at this absolute or relative path. "
            "Output file is overwritten if the content of the file has changed or if "
            "``overwrite`` is True (default: %(default)s)"
        ),
    )
    output_file_group.add_argument(
        "-o",
        "--output-directory",
        type=pathlib.Path,
        default=None,
        dest="OUTPUT_DIRECTORY",
        help=(
            "Write one output file per parameter set in the directory at this absolute or relative"
            " path. Filenames are based on the set name and output file type,"
            " ``{output_directory}/{set_name}.{output_file_type}``."
            " Output file is overwritten if the content of the file has changed or if "
            " ``overwrite`` is True (default: %(default)s)"
        ),
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
        help=(
            "Parameter set name template. Overridden by ``output_file_template``, if provided (default: %(default)s)"
        ),
    )
    parser.add_argument(
        "-p",
        "--previous-parameter-study",
        type=pathlib.Path,
        default=_settings._default_previous_parameter_study,
        dest="PREVIOUS_PARAMETER_STUDY",
        help=(
            "A relative or absolute file path to a previously created parameter study Xarray "
            "Dataset (default: %(default)s)"
        ),
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
        "--meta-file",
        type=pathlib.Path,
        dest="META_FILE",
        help=("Write a meta file containing the parameter set file absolute path(s) (default: %(default)s)"),
    )

    return parser


def read_parameter_schema(input_file: str | pathlib.Path | io.TextIOWrapper | None) -> dict:
    """Read a YAML dictionary from STDIN or a file.

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
        with pathlib.Path(input_file).open(mode="r") as input_handle:
            parameter_schema = yaml.safe_load(input_handle)
    return parameter_schema


def main(
    subcommand: str,
    input_file: str | pathlib.Path | io.TextIOWrapper | None,
    output_file: str | None = None,
    output_directory: str | None = None,
    output_file_type: _settings._allowable_output_file_typing = "yaml",
    set_name_template: str = _settings._default_set_name_template,
    previous_parameter_study: str | None = None,
    require_previous_parameter_study: bool = False,
    overwrite: bool = False,
    dry_run: bool = False,
    meta_file: str | None = None,
) -> None:
    """Build parameter studies.

    :param str subcommand: parameter study type to build
    :param str input_file: path to YAML formatted parameter study schema file
    :param output_file: Write a single parameter study file at this absolute or relative path.
    :param output_directory: Write one output file per parameter set in the directory at this absolute or relative
        path. Filenames are based on the set name and output file type,
        ``{output_directory}/{set_name}.{output_file_type}``.
    :param output_file_type: Output file syntax or type. Options are: 'yaml', 'h5'.
    :param str set_name_template: parameter set name string template. May contain '@number' for the set number.
    :param str previous_parameter_study: relative or absolute path to previous parameter study file
    :param overwrite: Overwrite existing output files
    :param dry_run: Print contents of new or overwritten parameter study output file(s) to STDOUT and exit.
    :param meta_file: Write a meta file at this absolute or relative path containing the parameter set file names, one
        per line. Useful for command line execution with build systems that require an explicit file list for target
        creation.
    """
    try:
        parameter_schema = read_parameter_schema(input_file)
    except yaml.parser.ParserError as err:
        raise RuntimeError(
            f"Error loading '{input_file}'. Check the YAML syntax.\nyaml.parser.ParserError: {err}"
        ) from err

    # Retrieve and instantiate the subcommand class
    available_parameter_generators = {
        _settings._cartesian_product_subcommand: parameter_generators.CartesianProduct,
        _settings._custom_study_subcommand: parameter_generators.CustomStudy,
        _settings._latin_hypercube_subcommand: parameter_generators.LatinHypercube,
        _settings._sobol_sequence_subcommand: parameter_generators.SobolSequence,
        _settings._one_at_a_time_subcommand: parameter_generators.OneAtATime,
    }
    parameter_generator = available_parameter_generators[subcommand](  # type: ignore[abstract]
        parameter_schema,
        set_name_template=set_name_template,
        previous_parameter_study=previous_parameter_study,
        require_previous_parameter_study=require_previous_parameter_study,
    )

    # Build the parameter study.
    parameter_generator.write(
        output_file=output_file,
        output_directory=output_directory,
        output_file_type=output_file_type,
        overwrite=overwrite,
        dry_run=dry_run,
        meta_file=meta_file,
    )


# Limit help() and 'from module import *' behavior to the module's public API
_module_objects = set(globals().keys()) - _exclude_from_namespace
__all__ = [name for name in _module_objects if not name.startswith("_")]
