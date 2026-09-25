"""Read simulation output, process data, recommend new parameter sets, write updated parameter study."""

import argparse
import copy
import pathlib
import typing

import waves

from modsim_package.python.rectangle_compression_sobol_sequence import parameter_schema


def main(
    input_file: typing.Sequence[pathlib.Path],
    parameter_study_file: pathlib.Path,
    output_file: pathlib.Path | None = None,
) -> None:
    """Read simulation output, process data, recommend new parameter sets, write updated parameter study."""
    set_count = len(input_file)
    if set_count < 8:
        new_schema = copy.deepcopy(parameter_schema())
        new_schema["num_simulations"] = set_count + 2
        new_generator = waves.parameter_generators.SobolSequence(
            new_schema,
            previous_parameter_study=parameter_study_file,
            scramble=False,
        )
        new_generator.write(output_file=output_file)


def get_parser() -> argparse.ArgumentParser:
    """Return parser for CLI options."""
    script_name = pathlib.Path(__file__)

    prog = f"python {script_name.name} "
    cli_description = "Read Xarray Datasets, process data, recommend new parameter sets, write updated parameter study."
    parser = argparse.ArgumentParser(description=cli_description, prog=prog)
    required_named = parser.add_argument_group("required named arguments")
    required_named.add_argument(
        "-i",
        "--input-file",
        nargs="+",
        type=pathlib.Path,
        required=True,
        help="The Xarray Dataset file(s)",
    )
    required_named.add_argument(
        "-p",
        "--parameter-study-file",
        type=pathlib.Path,
        help="An optional h5 file with a WAVES parameter study Xarray Dataset (default: %(default)s)",
    )
    parser.add_argument(
        "-o",
        "--output-file",
        type=pathlib.Path,
        help=("The parameter study with new parameter sets."),
    )
    return parser


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
    main(
        input_files=args.input_file,
        output_file=args.output_file,
        parameter_study_file=args.parameter_study_file,
    )
