#!/usr/bin/env python
"""Post-process with data catenation and plotting."""

import argparse
import datetime
import pathlib

import waves
import yaml

import modsim_package.utilities

TODAY = datetime.date.today()
DEFAULT_SELECTION_DICT = {
    "E values": "E22",
    "S values": "S22",
    "elements": 1,
    "step": "Step-1",
    "integration point": 0,
}


def main(
    input_file: pathlib.Path,
    output_file: pathlib.Path,
    group_path: str,
    strain_units: str,
    stress_units: str,
    selection_dict: dict,
):
    """Calculate QOIs for ``input_file`` datasets.

    :param input_file: The input file h5netcdf files containing an Xarray Dataset
    :param output_file: The QOI CSV file name. Relative or absolute path.
    :param group_path: The h5netcdf group path locating the Xarray Dataset in the input files.
    :param strain_units: The independent (x-axis) units
    :param stress_units: The dependent (y-axis) units
    :param selection_dict: Dictionary to define the down selection of data for QOI calculation. Dictionary
        ``key: value`` pairs must match the data variables and coordinates of the expected Xarray Dataset object.
    """
    concat_coord = waves.parameter_generators.SET_COORDINATE_KEY

    # Build single dataset along the "set_name" dimension
    combined_data = modsim_package.utilities.combine_data([input_file], group_path, concat_coord)

    # Add units
    combined_data["E"].attrs["units"] = strain_units
    combined_data["S"].attrs["units"] = stress_units

    # Calculate QOIs
    qoi_data = combined_data.sel(selection_dict).isel({"time": -1}).squeeze()
    strain = waves.qoi.create_qoi(
        name="strain",
        calculated=qoi_data["E"].item(),
        long_name="true strain",
        description=f"true strain tensor component {selection_dict['E values']} from final increment",
        group=qoi_data["set_name"].item(),
        date=TODAY,
        units=strain_units,
    )
    stress = waves.qoi.create_qoi(
        name="stress",
        calculated=qoi_data["S"].item(),
        long_name="true stress",
        description=f"true stress tensor component {selection_dict['S values']} from final increment",
        group=qoi_data["set_name"].item(),
        date=TODAY,
        units=stress_units,
    )
    qoi_set = waves.qoi.create_qoi_set([strain, stress])
    waves.qoi.write_qoi_set_to_csv(qoi_set, output_file)

    # Clean up open files
    combined_data.close()


def get_parser() -> argparse.ArgumentParser:
    """Return parser for CLI options."""
    script_name = pathlib.Path(__file__)
    default_output_file = f"{script_name.name}.csv"
    default_group_path = "RECTANGLE/FieldOutputs/ALL_ELEMENTS"

    prog = f"python {script_name.name} "
    cli_description = "Read Xarray Dataset and calculate QOIs. Save to ``output_file``."
    parser = argparse.ArgumentParser(description=cli_description, prog=prog)
    required_named = parser.add_argument_group("required named arguments")
    required_named.add_argument(
        "-i",
        "--input-file",
        type=pathlib.Path,
        required=True,
        help="The Xarray Dataset file",
    )
    required_named.add_argument(
        "--strain-units",
        type=str,
        required=True,
        help="The strain units string.",
    )
    required_named.add_argument(
        "--stress-units",
        type=str,
        required=True,
        help="The stress units string.",
    )

    parser.add_argument(
        "-o",
        "--output-file",
        type=pathlib.Path,
        default=default_output_file,
        help="The QOI CSV output file (default: %(default)s)",
    )
    parser.add_argument(
        "-g",
        "--group-path",
        type=str,
        default=default_group_path,
        help="The h5py group path to the dataset object (default: %(default)s)",
    )
    parser.add_argument(
        "-s",
        "--selection-dict",
        type=pathlib.Path,
        default=None,
        help=(
            "The YAML formatted dictionary file to define the down selection of data to be plotted. "
            "Dictionary key: value pairs must match the data variables and coordinates of the "
            "expected Xarray Dataset object. If no file is provided, the a default selection dict "
            f"will be used (default: {DEFAULT_SELECTION_DICT})"
        ),
    )

    return parser


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
    if not args.selection_dict:
        selection_dict = DEFAULT_SELECTION_DICT
    else:
        with args.selection_dict.open(mode="r") as input_yaml:
            selection_dict = yaml.safe_load(input_yaml)
    main(
        input_file=args.input_file,
        output_file=args.output_file,
        group_path=args.group_path,
        strain_units=args.strain_units,
        stress_units=args.stress_units,
        selection_dict=selection_dict,
    )
