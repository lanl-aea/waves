#!/usr/bin/env python
"""Example for common commercial and research solver behavior and handling

.. warning::

   The solver I/O handling and CLI are *NOT* good behaviors for authors and developers of command line utilities. They
   are intended to be examples of representative types of challenging behaviors to consider when writing SCons builders.

Solver I/O behaviors:

1. Log files are written to the current working directory. Log files are never overwritten and must be cleaned manually.
   Log files are automatically incremented from ``solver.log`` to ``solver.log10``. If no free log file number is found
   and the maximum number of 10 is found, the solver exits with a non-zero exit code.
2. The output file name is built in preferred order: CLI ``--output-file`` argument or the ``--input-file`` argument
   with the replacement extension ``.out``.
3. The implicit and explicit routines write output file(s) based on the requested number of threads. If only one thread
   is requested, the output file name is used. If more than one thread, N, is requested, each thread writes to a
   separately numbered output file 0 to (N-1) as ``output_file.out{number}``.
4. If any output file exists and the overwrite behavior is not requested, the solver exits with a non-zero exit code.

Runtime errors are returned as non-zero exit codes. Internal errors are returned as the appropriate exception.

Exit codes:

1. error loading YAML input file
2. mismatched subcommand and input file routine request
3. output file exists and no overwrite was requested
4. reached max log file integer before finding a free file name
"""
import sys
import typing
import pathlib
import argparse

import yaml


_version = "1.0.0"
_project_name = pathlib.Path(__file__).stem
_project_name_version = f"{_project_name} {_version}"
_output_file_extension = ".out"
_log_file_extension = ".log"
_log_file = pathlib.Path(f"solver{_log_file_extension}")
_cli_description = "Dummy solver with file handling behavior similar to numeric solvers"
_default_solve_cpus = 1


def main():
    """Main function implementing the command line interface and program flow"""
    parser = get_parser()
    subcommand_list = parser._subparsers._group_actions[0].choices.keys()
    args = parser.parse_args()

    if args.subcommand not in subcommand_list:
        parser.print_help()
    else:
        try:
            subcommand = globals()[args.subcommand]
            subcommand(args)
        except RuntimeError as err:
            sys.exit(str(err))


def name_output_file(input_file: pathlib.Path, output_file: pathlib.Path) -> pathlib.Path:
    """Create the output file name from the input file if not specified"""
    if output_file is None:
        output_file = input_file.with_suffix(_output_file_extension)
    output_file = output_file.with_suffix(_output_file_extension)
    return output_file


def name_log_file(log_file: pathlib.Path, max_iterations: int = 10) -> pathlib.Path:
    """Return the first free log file name

    :param log_file: Log file base name
    :param max_iterations: Maximum number of allowable log files

    :raises RuntimeError: if no log file name is free within the max iterations
    """
    log_file = _log_file
    count = 0
    while log_file.exists():
        count = count + 1
        if count > max_iterations:
            message = "Found the maximum number of log files. Please remove old log files and try again."
            raise RuntimeError(message)
        log_file = log_file.with_suffix(f"{_log_file_extension}{count}")
    return log_file


def read_input(input_file: pathlib.Path) -> dict:
    """Return the configuration by reading the input file and handling common errors

    :param input_file: The input YAML file absolute or relative path

    :raises RuntimeError: if the YAML file can not be read
    """
    input_file.resolve()
    if not input_file.is_file():
        raise RuntimeError(f"input file '{input_file}' does not exist")
    with open(input_file, "r") as input_handle:
        try:
            configuration = yaml.safe_load(input_handle)
        except (yaml.parser.ParserError, yaml.scanner.ScannerError) as err:
            message = f"Error loading '{input_file}'. Check the YAML syntax.\nyaml.parser.ParserError: {err}"
            raise RuntimeError(message)
    return configuration


def configure(args: argparse.Namespace) -> dict:
    """Return the configuration with appended executable information

    :param args: The command line argument namespace

    :raises RuntimeError: if the subcommand doesn't match the input file routine
    """
    configuration = read_input(args.input_file)
    if "routine" in configuration and configuration["routine"].lower() != args.subcommand.lower():
        message = f"requested routine '{configuration['routine']}' does not match subcommmand '{args.subcommand}'"
        raise RuntimeError(message)
    configuration["routine"] = args.subcommand.lower()
    configuration["version"] = _project_name_version
    configuration["log_file"] = str(name_log_file(_log_file))
    configuration["output_file"] = str(name_output_file(args.input_file, args.output_file))
    configuration["solve_cpus"] = args.solve_cpus
    configuration["overwrite"] = args.overwrite

    with open(configuration["log_file"], "w+") as log_writer:
        log_writer.write(f"{configuration['version']}\n{configuration['routine']}\n")
        log_writer.write(f"{configuration['log_file']}\n{configuration['output_file']}\n")

    return configuration


def solve_output_files(output_file: pathlib.Path, solve_cpus: int) -> typing.List[pathlib.Path]:
    """Return the solve output file list to match the number of solve cpus

    :param output_file: base name for the output file
    :param solve_cpus: integer number of solve cpus
    """
    if solve_cpus == 1:
        output_files = [output_file]
    else:
        output_files = [
            output_file.with_suffix(f"{_output_file_extension}{solve_cpu}") for solve_cpu in range(solve_cpus)
        ]
    return output_files


def solve(configuration: dict) -> None:
    """Common solve logic because we do not really have separate routines

    :param configuration: The solver configuration

    :raises RuntimeError: if any output file already exists and overwrite is not requested.
    """
    log_file = pathlib.Path(configuration["log_file"])
    output_file = pathlib.Path(configuration["output_file"])
    solve_cpus = configuration["solve_cpus"]
    overwrite = configuration["overwrite"]

    output_files = solve_output_files(output_file, solve_cpus)
    if any([output.exists() for output in output_files]) and not overwrite:
        message = "Output file(s) already exist. Exiting."
        raise RuntimeError(message)

    with open(log_file, "a+") as log_writer:
        for output in output_files:
            with open(output, "w") as output_writer:
                log_writer.write(f"writing: {output}\n")
                output_writer.write(yaml.safe_dump(configuration))


def implicit(args: argparse.Namespace) -> None:
    """Implicit routine

    :param args: The command line argument namespace
    """
    configuration = configure(args)
    solve(configuration)


def explicit(args: argparse.Namespace) -> None:
    """Explicit routine

    :param args: The command line argument namespace
    """
    configuration = configure(args)
    solve(configuration)


def positive_nonzero_int(argument):
    """Type function for argparse - positive, non-zero integers

    :param str argument: string argument from argparse

    :returns: argument
    :rtype: int

    :raises ValueError:

        * The argument can't be cast to int
        * The argument is less than 1
    """
    MINIMUM_VALUE = 1
    try:
        argument = int(argument)
    except ValueError:
        raise argparse.ArgumentTypeError("invalid integer value: '{}'".format(argument))
    if not argument >= MINIMUM_VALUE:
        raise argparse.ArgumentTypeError("invalid positive integer: '{}'".format(argument))
    return argument


def get_parser() -> argparse.ArgumentParser:
    """Return the argparse CLI parser"""
    main_parser = argparse.ArgumentParser(description=_cli_description)
    main_parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=_project_name_version,
    )

    subcommand_parser_parent = argparse.ArgumentParser(add_help=False)
    required_named = subcommand_parser_parent.add_argument_group("required named arguments")
    required_named.add_argument(
        "-i",
        "--input-file",
        type=pathlib.Path,
        required=True,
        help=f"The {_project_name} input file, e.g. ``input_file.yaml``",
    )
    subcommand_parser_parent.add_argument(
        "-o",
        "--output-file",
        type=pathlib.Path,
        default=None,
        required=False,
        # fmt: off
        help=f"The {_project_name} results file. Extension is always replaced with ``{_output_file_extension}``. "
             f"If none is provided, uses the pattern ``input_file{_output_file_extension}``",
        # fmt: on
    )
    subcommand_parser_parent.add_argument(
        "-n",
        "--solve-cpus",
        type=positive_nonzero_int,
        default=_default_solve_cpus,
        required=False,
        help=f"The number of threads to use (default: %(default)s)",
    )
    subcommand_parser_parent.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing output files (default: %(default)s)",
    )

    subparsers = main_parser.add_subparsers(
        # So args.subcommand will contain the name of the subcommand called
        title="subcommands",
        metavar="{subcommand}",
        dest="subcommand",
    )

    subparsers.add_parser(
        "implicit", help=f"Execute the {_project_name} implicit routine", parents=[subcommand_parser_parent]
    )

    subparsers.add_parser(
        "explicit", help=f"Execute the {_project_name} explicit routine", parents=[subcommand_parser_parent]
    )

    return main_parser


if __name__ == "__main__":
    main()
