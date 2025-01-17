"""Internal API module implementing the ``print_study`` subcommand behavior.

Should raise ``RuntimeError`` or a derived class of :class:`waves.exceptions.WAVESError` to allow the CLI implementation
to convert stack-trace/exceptions into STDERR message and non-zero exit codes.
"""

import sys
import pathlib
import argparse

from waves import _settings

import yaml
import pandas
import xarray


_exclude_from_namespace = set(globals().keys())


def get_parser() -> argparse.ArgumentParser:
    """Return a 'no-help' parser for the print_study subcommand

    :return: parser
    """
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        "PARAMETER_STUDY_FILE",
        type=pathlib.Path,
        help="Parameter study relative or absolute path",
    )
    return parser


def main(parameter_study_file: pathlib.Path) -> None:
    """Open and print a WAVES parameter study file as a table

    :param parameter_study_file: The parameter study file to open

    :raises RuntimeError: If one or more files fails to open
    """
    if not parameter_study_file.is_file():
        raise RuntimeError(f"'{parameter_study_file}' does not exist or is not a file.")
    try:
        with open(parameter_study_file) as infile:
            study = yaml.safe_load(infile)
            table = pandas.DataFrame(study).T
            table.index.name = _settings._set_coordinate_key
    except UnicodeDecodeError as err:
        from waves.parameter_generators import _open_parameter_study

        study = _open_parameter_study(parameter_study_file)
        table = study.to_pandas()
    except Exception as err:
        raise RuntimeError(f"'{parameter_study_file}' failed to open with: '{err}'")
    print(f"{table.sort_values(_settings._set_coordinate_key)}")


# Limit help() and 'from module import *' behavior to the module's public API
_module_objects = set(globals().keys()) - _exclude_from_namespace
__all__ = [name for name in _module_objects if not name.startswith("_")]
