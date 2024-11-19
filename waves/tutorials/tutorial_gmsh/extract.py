import re
import sys
import pathlib
import argparse

import ccx2paraview.ccx2paraview


required_input_file_suffix = ".frd"
default_output_format = "vtu"


def main(input_file: pathlib.Path, output_format: str = default_output_format) -> None:
    """Convert CalculiX FRD results file to Paraview VTK file with ccx2paraview

    :param input_file: The CalculiX FRD file to read
    :param output_format: The ParaView output format: 'vtu' or 'vtk'
    """
    if not input_file.suffix == required_input_file_suffix:
        sys.exit(f"Input file '{input_file}' must have suffix '{required_input_file_suffix}'")
    if not input_file.is_file():
        sys.exit(f"No such file '{input_file}' found")
    converter = ccx2paraview.ccx2paraview.Converter(str(input_file), [output_format])
    converter.run()


def get_parser():
    script_name = pathlib.Path(__file__)

    prog = f"python {script_name.name} "
    cli_description = "Convert CalculiX FRD results file to Paraview VTK file with ccx2paraview"
    parser = argparse.ArgumentParser(description=cli_description, prog=prog)
    parser.add_argument(
        "--input-file",
        type=pathlib.Path,
        required=True,
    )
    parser.add_argument(
        "--output-format",
        type=str,
        choices=["vtu", "vtk"],
        default=default_output_format,
    )
    return parser


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
    main(
        input_file=args.input_file,
        output_format=args.output_format,
    )
