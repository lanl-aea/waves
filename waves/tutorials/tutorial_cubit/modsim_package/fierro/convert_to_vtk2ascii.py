import pathlib
import argparse

import meshio


def get_parser():
    cli_description = (
        "Convert mesh files to older VTK ASCII version 2 mesh files required by Fierro with MeshIO API. "
        "This output is not supported by the MeshIO CLI and must be constructed manually."
    )
    parser = argparse.ArgumentParser(description=cli_description)
    parser.add_argument(
        "infile",
        type=pathlib.Path,
        help="Input file to convert",
    )
    parser.add_argument(
        "outfile",
        type=pathlib.Path,
        help="Output file to write",
    )
    parser.add_argument(
        "-i",
        "--input-format",
        type=str,
        default=None,
        help="Explicit input file format (default: %(default)s)",
    )
    return parser


def main():
    parser = get_parser()
    args = parser.parse_args()

    infile = pathlib.Path(args.infile).resolve()
    mesh = meshio.read(infile, file_format=args.input_format)

    # Ensure input mesh structure meets Fierro criteria
    if len(mesh.cells) != 1:
        raise ValueError("More than one kind of cell type present")
    if mesh.cells[0].dim == 1:
        raise ValueError("Input file is 1D, only 2D/3D work")
    if mesh.cells[0].type != "hexahedron" and mesh.cells[0].type != "quad":
        raise ValueError("Cell type is not quad/hexahedron")

    points = mesh.points
    npoints = points.shape[0]

    ndim = mesh.cells[0].dim
    cells = mesh.cells[0].data
    ncells = cells.shape[0]
    pts_per_cell = cells.shape[1]

    outfile = pathlib.Path(args.outfile).resolve()
    with open(outfile, "w") as mesh_out:

        mesh_out.write("# vtk DataFile Version 2.0\n")
        mesh_out.write("meshio converted to Fierro VTK\n")
        mesh_out.write("ASCII\n")
        mesh_out.write("DATASET UNSTRUCTURED_GRID\n")
        # Write points
        mesh_out.write(f"POINTS {npoints} double\n")
        for n in range(npoints):
            for i in range(ndim):
                mesh_out.write(f"{points[n, i]} ")
            mesh_out.write("\n")
        mesh_out.write("\n")

        # Write cells
        mesh_out.write(f"CELLS {ncells} {ncells * pts_per_cell + ncells}\n")
        for n in range(ncells):
            mesh_out.write(f"{pts_per_cell} ")
            for i in range(pts_per_cell):
                mesh_out.write(f"{cells[n, i]} ")
            mesh_out.write("\n")
        mesh_out.write("\n")
        mesh_out.write(f"CELL_TYPES {ncells}\n")
        if ndim == 2:
            for n in range(ncells):
                mesh_out.write("9\n")
        else:
            for n in range(ncells):
                mesh_out.write("12\n")


if __name__ == "__main__":
    main()
