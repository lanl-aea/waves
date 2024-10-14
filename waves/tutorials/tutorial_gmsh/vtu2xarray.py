import sys
import pathlib
import argparse

import meshio
import xarray


def main(input_file: pathlib.Path, output_file: pathlib.Path) -> None:
    mesh = meshio.read(input_file)
    coordinate = ["x", "y", "z"]
    components = ["11", "22", "33", "12", "13", "23"]
    point_numbers = list(range(0, len(mesh.points)))
    data_arrays = [xarray.DataArray(
        data=mesh.points,
        dims=["point", "coordinate"],
        coords={"point": point_numbers, "coordinate": coordinate},
        name="original_location"
    )]
    for key, value in mesh.point_data.items():
        if len(value.shape) == 1:
            data_arrays.append(xarray.DataArray(
                data=value,
                dims=["point"],
                coords={"point": point_numbers},
                name=key
            ))
        elif len(value.shape) == 2 and value.shape[1] == len(components):
            data_arrays.append(xarray.DataArray(
                data=value,
                dims=["point", "component"],
                coords={"point": point_numbers, "component": components},
                name=key
            ))
        elif len(value.shape) == 2 and value.shape[1] == len(coordinate):
            data_arrays.append(xarray.DataArray(
                data=value,
                dims=["point", "coordinate"],
                coords={"point": point_numbers, "coordinate": coordinate},
                name=key
            ))
        else:
            raise RuntimeError(f"Do not know how to handle '{key}' data '{value}'")
    data = xarray.merge(data_arrays)
    data.to_netcdf(output_file)


def existing_file(argument):
    path = pathlib.Path(argument)
    if not path.exists():
        raise argparse.ArgumentTypeError(f"file '{path}' does not exist")
    return path


def get_parser():
    script_name = pathlib.Path(__file__)
    prog = f"python {script_name.name} "
    cli_description = "Open a CalculiX-to-VTU output file produced by ``extract.py`` and convert to Xarray"
    parser = argparse.ArgumentParser(description=cli_description, prog=prog)
    parser.add_argument(
        "--input-file",
        type=existing_file,
        required=True,
        help="VTU input file"
    )
    parser.add_argument(
        "--output-file",
        type=pathlib.Path,
        required=True,
        help="Xarray output file"
    )
    return parser


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
    main(
        input_file=args.input_file,
        output_file=args.output_file
    )
