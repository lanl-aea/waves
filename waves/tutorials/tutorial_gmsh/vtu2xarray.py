import typing
import pathlib
import argparse
import warnings

import numpy
import meshio
import xarray


def main(
    input_file: typing.Tuple[pathlib.Path],
    output_file: pathlib.Path,
    mesh_file: typing.Optional[pathlib.Path] = None,
    time_points_file: typing.Optional[pathlib.Path] = None,
) -> None:
    """Open a ``ccx2paraview`` CalculiX-to-VTU output file and convert to Xarray

    Assumes

    1. Nodes are numbered sequentially from one in the CalculiX input file
    2. Nodes will be converted to zero index by ``meshio``

    :param input_file: VTU file(s) created by ``ccx2paraview``
    :param output_file: Xarray H5 output file
    :param mesh_file: CalculiX input file containing node sets
    :param time_points_file: Calculix time points CSV data. If the first time point is 0.0, it will be stripped because
        CalculiX and ccx2paraview do not write the initial, time zero increment.
    """
    if time_points_file is not None and time_points_file.is_file():
        time_points = time_points_from_file(time_points_file)
    else:
        time_points = numpy.array([numpy.nan] * len(input_file))
    if len(time_points) != len(input_file):
        raise RuntimeError("If time points are provided, the length must match the number of VTU files provided")

    data_arrays = []
    for infile, time in zip(input_file, time_points):
        increment_data = []
        results = meshio.read(infile)
        coordinate = ["x", "y", "z"]
        components = ["11", "22", "33", "12", "13", "23"]
        point_numbers = list(range(0, len(results.points)))
        increment_data = [
            xarray.DataArray(
                data=results.points,
                dims=["point", "coordinate"],
                coords={"point": point_numbers, "coordinate": coordinate},
                name="original_location",
            )
        ]
        for key, value in results.point_data.items():
            if len(value.shape) == 1:
                increment_data.append(
                    xarray.DataArray(
                        data=value,
                        dims=["point"],
                        coords={"point": point_numbers},
                        name=key,
                    ).expand_dims({"time": [time]})
                )
            elif len(value.shape) == 2 and value.shape[1] == len(components):
                increment_data.append(
                    xarray.DataArray(
                        data=value,
                        dims=["point", "component"],
                        coords={"point": point_numbers, "component": components},
                        name=key,
                    ).expand_dims({"time": [time]})
                )
            elif len(value.shape) == 2 and value.shape[1] == len(coordinate):
                increment_data.append(
                    xarray.DataArray(
                        data=value,
                        dims=["point", "coordinate"],
                        coords={"point": point_numbers, "coordinate": coordinate},
                        name=key,
                    ).expand_dims({"time": [time]})
                )
            else:
                warnings.warn(
                    f"Do not know how to handle '{key}' data '{value}'. "
                    "Data variable will not be saved in the xarray dataset"
                )
        data_arrays.extend(increment_data)

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
    data.to_netcdf(output_file, engine="h5netcdf")


def time_points_from_file(time_points_file: pathlib.Path) -> numpy.ndarray:
    """Return time points array from CalculiX ``*TIME POINTS`` CSV file

    :param time_points_file: A CalculiX ``*TIME POINTS`` CSV file

    :returns: 1D numpy array of time points
    """
    time_points = numpy.genfromtxt(time_points_file)
    time_points = time_points.flatten()
    # Either calculix or ccx2paraview doesn't write the t0 increment
    if numpy.isclose(time_points[0], 0.0):
        time_points = time_points[1:]
    return time_points


def existing_file(argument: str) -> pathlib.Path:
    """Argparse existing pathlib.Path custom type

    :param argument: string argument from command line argument

    :returns: string converted to pathlib.Path object

    :raises argparse.ArgumentTypeError: If the file does not exist
    """
    path = pathlib.Path(argument)
    if not path.exists():
        raise argparse.ArgumentTypeError(f"file '{path}' does not exist")
    return path


def get_parser() -> argparse.ArgumentParser:
    script_name = pathlib.Path(__file__)
    prog = f"python {script_name.name} "
    cli_description = "Open a CalculiX-to-VTU output file produced by ``ccx2paraview`` and convert to Xarray"
    parser = argparse.ArgumentParser(description=cli_description, prog=prog)
    parser.add_argument(
        "--input-file",
        nargs="+",
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
    parser.add_argument(
        "--time-points-file",
        type=existing_file,
        help="CalculiX ``*TIME POINTS`` CSV data.",
    )
    return parser


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
    main(
        input_file=args.input_file,
        output_file=args.output_file,
        mesh_file=args.mesh_file,
        time_points_file=args.time_points_file,
    )
