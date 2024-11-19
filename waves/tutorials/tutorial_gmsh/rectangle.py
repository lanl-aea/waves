import typing
import pathlib
import argparse

import numpy
import gmsh


script_name = pathlib.Path(__file__)
# Set default parameter values
default_output_file = pathlib.Path(script_name.with_suffix(".msh").name)
default_width = 1.0
default_height = 1.0
default_global_seed = 1.0


def main(
    output_file: pathlib.Path = default_output_file,
    width: float = default_width,
    height: float = default_height,
    global_seed: float = default_global_seed,
) -> None:
    """Create a simple rectangle geometry.

    This script creates a simple Gmsh model with a single rectangle part.

    :param output_file: The output file for the Gmsh model. Extension must match a supported Gmsh file type.
    :param width: The rectangle width
    :param height: The rectangle height
    :param global_seed: The global mesh seed size

    :returns: writes ``output_file``
    """
    gmsh.initialize()
    gmsh.logger.start()
    gmsh.model.add("rectangle")

    # Geometry
    rectangle_tag = gmsh.model.occ.addRectangle(0, 0, 0, width, height)
    gmsh.model.occ.synchronize()

    # Partition
    # TODO: Move to separate function/script
    rectangle_group_tag = gmsh.model.addPhysicalGroup(2, [rectangle_tag], name="rectangle")

    tolerance = 0.01 * min(width, height)
    bottom_left = get_entities_at_coordinates((0.0, 0.0, 0.0), 0)
    top_right = get_entities_at_coordinates((width, height, 0.0), 0)
    # fmt: off
    top = gmsh.model.getEntitiesInBoundingBox(
        0.0    - tolerance,  # noqa: E221 X-min
        height - tolerance,  # noqa: E221 Y-min
        0.0    - tolerance,  # noqa: E221 Z-min
        width  + tolerance,  # noqa: E221 X-max
        height + tolerance,  # noqa: E221 Y-max
        0.0    + tolerance,  # noqa: E221 Z-max
        0  # Entity dimension: points
    )
    bottom = gmsh.model.getEntitiesInBoundingBox(
        0.0    - tolerance,  # noqa: E221 X-min
        0.0    - tolerance,  # noqa: E221 Y-min
        0.0    - tolerance,  # noqa: E221 Z-min
        width  + tolerance,  # noqa: E221 X-max
        0.0    + tolerance,  # noqa: E221 Y-max
        0.0    + tolerance,  # noqa: E221 Z-max
        0  # Entity dimension: points
    )
    left = gmsh.model.getEntitiesInBoundingBox(
        0.0    - tolerance,  # noqa: E221 X-min
        0.0    - tolerance,  # noqa: E221 Y-min
        0.0    - tolerance,  # noqa: E221 Z-min
        0.0    + tolerance,  # noqa: E221 X-max
        height + tolerance,  # noqa: E221 Y-max
        0.0    + tolerance,  # noqa: E221 Z-max
        0  # Entity dimension: points
    )
    # fmt: on
    gmsh.model.addPhysicalGroup(0, tags_from_dimTags(bottom_left), name="bottom_left")
    gmsh.model.addPhysicalGroup(0, tags_from_dimTags(top_right), name="top_right")
    gmsh.model.addPhysicalGroup(0, tags_from_dimTags(top), name="top")
    gmsh.model.addPhysicalGroup(0, tags_from_dimTags(bottom), name="bottom")
    gmsh.model.addPhysicalGroup(0, tags_from_dimTags(left), name="left")

    # Mesh
    # TODO: Move to separate function/script
    points = gmsh.model.getEntities(0)
    gmsh.model.mesh.setSize(points, global_seed)
    gmsh.model.mesh.generate(2)
    gmsh.model.mesh.recombine()

    gmsh.option.setNumber("Mesh.SaveGroupsOfElements", 1)
    gmsh.option.setNumber("Mesh.SaveGroupsOfNodes", 1)

    gmsh.write(str(output_file))
    gmsh.logger.stop()
    gmsh.finalize()


def tags_from_dimTags(dimTags: typing.List[typing.Tuple[int, int]]) -> typing.List[int]:
    """Return tags from Gmsh entity ``dimTags`` list of tuples

    :returns: list of tags
    """
    return [dimTag[1] for dimTag in dimTags]


def get_entities_at_coordinates(
    coordinates: typing.Tuple[float, float, float],
    dimension: int,
    tolerance: float = 1.0e-6,
) -> typing.List[typing.Tuple[int, int]]:
    """Return Gmsh ``dimTags`` of entities of dimension within bounding box determined by coordinates and tolerance

    :param coordinates: 3D coordinates (X, Y, Z) for center of bounding box
    :param dimension: Return entities matching dimension
    :param tolerance: Distance from center of bounding box to edges of bounding box

    :returns: Gmsh entity ``dimTags``
    """
    if len(coordinates) != 3:
        raise RuntimeError("coordinates must have length 3")
    center = numpy.array(coordinates)
    tolerance_array = numpy.array([tolerance, tolerance, tolerance])
    min_coordinate = center - tolerance_array
    max_coordinate = center + tolerance_array
    return gmsh.model.getEntitiesInBoundingBox(*min_coordinate, *max_coordinate, dimension)


def get_parser():
    prog = f"python {script_name.name} "
    cli_description = "Create a simple rectangle geometry and write an ``output_file``.msh Gmsh model file."
    parser = argparse.ArgumentParser(description=cli_description, prog=prog)
    parser.add_argument(
        "--output-file",
        type=pathlib.Path,
        default=default_output_file,
        # fmt: off
        help="The output file for the Gmsh model. Extension must match a supported Gmsh file type, e.g. "
             "``output_file``.msh (default: %(default)s",
        # fmt: on
    )
    parser.add_argument(
        "--width",
        type=float,
        default=default_width,
        help="The rectangle width",
    )
    parser.add_argument(
        "--height",
        type=float,
        default=default_height,
        help="The rectangle height",
    )
    parser.add_argument(
        "--global-seed",
        type=float,
        default=default_global_seed,
        help="The global mesh seed size (default: %(default)s)",
    )
    return parser


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
    main(
        output_file=args.output_file,
        width=args.width,
        height=args.height,
        global_seed=args.global_seed,
    )
