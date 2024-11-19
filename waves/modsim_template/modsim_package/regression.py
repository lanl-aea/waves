#!/usr/bin/env python
import sys
import pathlib
import argparse

import pandas
import yaml

import modsim_package.utilities


def main(
    first_file: pathlib.Path,
    second_file: pathlib.Path,
    output_file: pathlib.Path,
) -> None:
    """Compare CSV files and return an error code if they differ

    :param first_file: path-like or file-like object containing the first CSV dataset
    :param second_file: path-like or file-like object containing the second CSV dataset
    """
    regression_results = {}

    # CSV regression file comparison
    first_data = pandas.read_csv(first_file)
    second_data = pandas.read_csv(second_file)
    regression_results.update({"CSV comparison": modsim_package.utilities.csv_files_match(first_data, second_data)})

    with open(output_file, "w") as output:
        output.write(yaml.safe_dump(regression_results))

    if len(regression_results.values()) < 1 or not all(regression_results.values()):
        sys.exit("One or more regression tests failed")


def get_parser() -> argparse.ArgumentParser:
    """Return parser for CLI options

    All options should use the double-hyphen ``--option VALUE`` syntax to avoid clashes with the Abaqus option syntax,
    including flag style arguments ``--flag``. Single hyphen ``-f`` flag syntax often clashes with the Abaqus command
    line options and should be avoided.

    :returns: parser
    :rtype:
    """
    script_name = pathlib.Path(__file__)
    default_output_file = f"{script_name.stem}.yaml"

    prog = f"python {script_name.name} "
    cli_description = "Compare CSV files and return an error code if they differ"
    parser = argparse.ArgumentParser(description=cli_description, prog=prog)
    parser.add_argument(
        "FIRST_FILE",
        type=pathlib.Path,
        help="First CSV file for comparison",
    )
    parser.add_argument(
        "SECOND_FILE",
        type=pathlib.Path,
        help="Second CSV file for comparison",
    )
    parser.add_argument(
        "--output-file",
        type=pathlib.Path,
        default=default_output_file,
        help="Regression test pass/fail list",
    )
    return parser


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
    main(
        args.FIRST_FILE,
        args.SECOND_FILE,
        args.output_file,
    )
