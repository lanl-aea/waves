#!/usr/bin/env python
import sys
import pathlib
import argparse

import pandas
import yaml


def sort_dataframe(dataframe, index_column="time", sort_columns=["time", "set_name"]):
    """Return a sorted dataframe and set an index

    1. sort columns by column name
    2. sort rows by column values ``sort_columns``
    3. set an index

    :returns: sorted and indexed dataframe
    :rtype: pandas.DataFrame
    """
    return dataframe.reindex(sorted(dataframe.columns), axis=1).sort_values(sort_columns).set_index(index_column)


def csv_files_match(current_csv, expected_csv, index_column="time", sort_columns=["time", "set_name"]):
    """Compare two pandas DataFrame objects and determine if they match.

    :param pandas.DataFrame current_csv: Current CSV data of generated plot.
    :param pandas.DataFrame expected_csv: Expected CSV data.

    :returns: True if the CSV files match, False otherwise.
    :rtype: bool
    """
    current = sort_dataframe(current_csv, index_column=index_column, sort_columns=sort_columns)
    expected = sort_dataframe(expected_csv, index_column=index_column, sort_columns=sort_columns)
    try:
        pandas.testing.assert_frame_equal(current, expected)
    except AssertionError as err:
        print(
            f"The CSV regression test failed. Data in expected CSV file and current CSV file do not match.\n{err}",
            file=sys.stderr,
        )
        equal = False
    else:
        equal = True
    return equal


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
    regression_results.update({"CSV comparison": csv_files_match(first_data, second_data)})

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
