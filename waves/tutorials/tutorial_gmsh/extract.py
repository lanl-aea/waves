import re
import pathlib
import argparse

import ccx2paraview.ccx2paraview


def main(input_file: pathlib.Path, output_formats: list) -> None:
    """Convert CalculiX FRD results file to Paraview VTK file with ccx2paraview

    :param input_file: The CalculiX FRD file to read
    :param output_formats: The ParaView output format(s): 'vtu', 'vtk', or both
    """
    converter = ccx2paraview.ccx2paraview.Converter(str(input_file), output_formats)
    converter.run()


def get_parser():
    script_name = pathlib.Path(__file__)

    prog = f"python {script_name.name} "
    cli_description = "Convert CalculiX FRD results file to Paraview VTK file with ccx2paraview"
    parser = argparse.ArgumentParser(description=cli_description, prog=prog)
    parser.add_argument(
        "--input-file",
        type=pathlib.Path,
        required=True
    )
    parser.add_argument(
        "--output-formats",
        type=str,
        nargs="+",
        default=["vtu"],
        required=True
    )
    return parser


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
    main(
        input_file=args.input_file,
        output_formats=args.output_formats
    )
