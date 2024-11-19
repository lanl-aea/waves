import sys
import argparse
import pathlib

import cubit


def main(output_file, xlength, ylength, zlength):
    """Write brick geometry with specified dimensions

    :param str output_file: The output file for the Cubit model. Will be stripped of the extension and ``.cub`` and
        ``.exo`` will be used for the model and mesh files, respectively.
    :param xlength: box edge length on global x axis
    :param ylength: box edge length on global y axis
    :param zlength: box edge length on global z axis

    :returns: writes ``output_file``.cub and ``output_file``.exo
    """
    cubit.init(["cubit", "-noecho", "-nojournal", "-nographics", "-batch"])
    cubit.cmd("new")
    cubit.cmd("reset")

    cubit_file = pathlib.Path(output_file).with_suffix(".cub")
    exodus_file = cubit_file.with_suffix(".exo")

    # Geometry
    cubit.cmd(f"brick x {xlength} y {ylength} z {zlength}")
    cubit.cmd(f"move volume 1 x {xlength * 0.5} y {ylength * 0.5} z {zlength * 0.5}")
    cubit.cmd(f"webcut volume 1 with plane xplane offset {xlength * 0.5} noimprint nomerge")
    cubit.cmd(f"merge volume 1 2")

    # Sets (partition)
    cubit.cmd("sideset 1 add surface 8 15")
    cubit.cmd("sideset 2 add surface 9 16")
    cubit.cmd("sideset 3 add surface 10 14")
    cubit.cmd("sideset 4 add surface 4")
    cubit.cmd("sideset 5 add surface 11 13")
    cubit.cmd("sideset 6 add surface 6")

    # Mesh
    cubit.cmd("Trimesher surface gradation 1.05")
    cubit.cmd("Trimesher volume gradation 1.05")

    cubit.cmd("surface 6 7 8 9 10 11 13 14 15 16 Scheme TriMesh geometry approximation angle 10")
    cubit.cmd("surface 13 14 15 16  size 0.065")
    cubit.cmd("surface 4 size 0.09")
    cubit.cmd("surface 7 size .09")
    cubit.cmd("surface 8 9 10 11 size 0.45")
    cubit.cmd("surface 6 size 0.09")

    cubit.cmd("mesh surface 6 7 8 9 10 11 13 14 15 16")

    cubit.cmd("volume 1 2 Scheme Tetmesh proximity layers off geometry approximation angle 10")
    cubit.cmd("volume 1 2 Tetmesh growth_factor 1.001")
    cubit.cmd("volume 1 size 0.065")
    cubit.cmd("volume 2 size 0.065")

    cubit.cmd("mesh volume 1 2")
    cubit.cmd("block 1 add volume 1 2")

    cubit.cmd("set exodus netcdf4 off")
    cubit.cmd("set large exodus file on")
    cubit.cmd(f"export Genesis '{exodus_file}' dimension 3 block 1  overwrite")
    cubit.cmd(f"save as '{cubit_file}' overwrite")


def get_parser():
    """Return the command line parser"""
    script_name = pathlib.Path(__file__)
    prog = f"python {script_name.name} "
    cli_description = "Write brick geometry ``output_file``.cub and ``output_file``.exo with specified dimensions"
    parser = argparse.ArgumentParser(description=cli_description, prog=prog)
    parser.add_argument(
        "--output-file",
        type=str,
        required=True,
        # fmt: off
        help="The output file for the Cubit model. Will be stripped of the extension and ``.cub`` and ``.exo`` will "
             "be used for the model and mesh files, respectively.",
        # fmt: on
    )
    parser.add_argument("--xlength", type=float, required=True, help="box edge length on global x axis")
    parser.add_argument("--ylength", type=float, required=True, help="box edge length on global y axis")
    parser.add_argument("--zlength", type=float, required=True, help="box edge length on global z axis")
    return parser


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
    main(
        output_file=args.output_file,
        xlength=args.xlength,
        ylength=args.ylength,
        zlength=args.zlength,
    )
