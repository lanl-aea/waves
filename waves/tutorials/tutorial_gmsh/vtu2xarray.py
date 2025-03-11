import sys
import typing
import pathlib
import argparse
import warnings

import meshio
import xarray


def main(
    input_file: pathlib.Path,
    output_file: pathlib.Path,
    mesh_file: typing.Optional[pathlib.Path] = None,
) -> None:
    """Read VTU file provided by ``ccx2paraview`` and write an Xarray H5 file

    Assumes

    1. Nodes are numbered sequentially from one in the CalculiX input file
    2. Nodes will be converted to zero index by ``meshio``

    :param input_file: VTU file created by ``ccx2paraview``
    :param output_file: Xarray H5 output file
    :param mesh_file: CalculiX input file containing node sets
    """
    results = meshio.read(input_file)
    coordinate = ["x", "y", "z"]
    components = ["11", "22", "33", "12", "13", "23"]
    point_numbers = list(range(0, len(results.points)))
    data_arrays = [
        xarray.DataArray(
            data=results.points,
            dims=["point", "coordinate"],
            coords={"point": point_numbers, "coordinate": coordinate},
            name="original_location",
        )
    ]
    for key, value in results.point_data.items():
        if len(value.shape) == 1:
            data_arrays.append(
                xarray.DataArray(
                    data=value,
                    dims=["point"],
                    coords={"point": point_numbers},
                    name=key,
                )
            )
        elif len(value.shape) == 2 and value.shape[1] == len(components):
            data_arrays.append(
                xarray.DataArray(
                    data=value,
                    dims=["point", "component"],
                    coords={"point": point_numbers, "component": components},
                    name=key,
                )
            )
        elif len(value.shape) == 2 and value.shape[1] == len(coordinate):
            data_arrays.append(
                xarray.DataArray(
                    data=value,
                    dims=["point", "coordinate"],
                    coords={"point": point_numbers, "coordinate": coordinate},
                    name=key,
                )
            )
        else:
            warnings.warn(
                f"Do not know how to handle '{key}' data '{value}'. "
                "Data variable will not be saved in the xarray dataset"
            )

    # TODO: Find a better way to add the node set information
    if mesh_file is not None and mesh_file.is_file():
        mesh = meshio.read(mesh_file)
        for key, value in mesh.point_sets.items():
            data_arrays.append(
                xarray.DataArray(
                    data=value,
                    dims=[f"{key}_nodes"],
                    name=key,
                )
            )

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
    cli_description = "Open a CalculiX-to-VTU output file produced by ``ccx2paraview`` and convert to Xarray"
    parser = argparse.ArgumentParser(description=cli_description, prog=prog)
    parser.add_argument(
        "--input-file",
        type=existing_file,
        required=True,
        help="VTU input file",
    )
    parser.add_argument(
        "--output-file",
        type=pathlib.Path,
        required=True,
        help="Xarray output file",
    )
    parser.add_argument(
        "--mesh-file",
        type=existing_file,
        help="CalculiX input file. When provided, try to merge the point/node sets with the results VTU file.",
    )
    return parser


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
    main(
        input_file=args.input_file,
        output_file=args.output_file,
        mesh_file=args.mesh_file,
    )
