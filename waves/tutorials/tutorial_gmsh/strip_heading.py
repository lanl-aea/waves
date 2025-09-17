"""Strip the heading keyword from an Abaqus input file."""

import argparse
import pathlib
import re


def main(input_file: pathlib.Path, output_file: pathlib.Path) -> None:
    """Strip the heading keyword from an Abaqus input file.

    :param input_file: The Abaqus input file to read
    :param output_file: The Abaqus input file to write
    """
    with input_file.open(mode="r") as read_file:
        read_text = read_file.read()
    write_text = re.sub(
        r"(\*heading.*?)(\*)", r"\2", read_text, count=0, flags=re.MULTILINE | re.IGNORECASE | re.DOTALL
    )
    with output_file.open(mode="w") as write_file:
        write_file.write(write_text)


def get_parser() -> argparse.ArgumentParser:
    """Return the command-line interface parser."""
    script_name = pathlib.Path(__file__)

    prog = f"python {script_name.name} "
    cli_description = "Strip the heading keyword from an Abaqus input file."
    parser = argparse.ArgumentParser(description=cli_description, prog=prog)
    parser.add_argument(
        "--input-file",
        type=pathlib.Path,
        required=True,
    )
    parser.add_argument(
        "--output-file",
        type=pathlib.Path,
        required=True,
    )
    return parser


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
    main(input_file=args.input_file, output_file=args.output_file)
