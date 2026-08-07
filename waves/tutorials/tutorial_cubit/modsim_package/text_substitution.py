"""Search and replace simple text substitutions in text files."""

import argparse
import pathlib
import re
import shutil


def main(input_file: pathlib.Path, output_file: pathlib.Path, pattern: str, replacement: str) -> None:
    """Search and replace simple text substitutions in text files.

    :param input_file: input file to read for text substitutions
    :param output_file: output file to write with text substitutions
    :param pattern: Python re module's ``re.sub`` search pattern regex
    :param replacement: Python re module's ``re.sub`` replacment string
    """
    # Avoid modifying the contents or timestamp on the input file.
    # Required to get conditional re-builds with a build system such as GNU Make, CMake, or SCons
    if input_file != output_file:
        shutil.copyfile(input_file, output_file)

    with input_file.open(mode="r") as infile:
        text = infile.read()
    updated_text = re.sub(pattern, replacement, text)
    with output_file.open(mode="w") as outfile:
        outfile.write(updated_text)


def get_parser() -> argparse.ArgumentParser:
    """Return the command-line interface parser."""
    script_name = pathlib.Path(__file__)
    prog = f"python {script_name.name} "
    cli_description = "Search and replace simple text substitutions in text files."
    parser = argparse.ArgumentParser(description=cli_description, prog=prog)
    parser.add_argument(
        "--input-file", required=True, type=pathlib.Path, help="The input file to read for text substitutions"
    )
    parser.add_argument(
        "--output-file", required=True, type=pathlib.Path, help="The output file to write with text substitutions"
    )
    parser.add_argument(
        "--pattern", required=True, type=str, help="The Python re module's ``re.sub`` search pattern regex"
    )
    parser.add_argument(
        "--replacement", required=True, type=str, help="The Python re module's ``re.sub`` replacement string"
    )
    return parser


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
    main(
        input_file=args.input_file,
        output_file=args.output_file,
        pattern=args.pattern,
        replacement=args.replacement,
    )
