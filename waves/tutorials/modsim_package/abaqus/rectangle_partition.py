import os
import sys
import shutil
import inspect
import argparse

import abaqus


def main(input_file, output_file, model_name, part_name, width, height):
    """Partition the simple rectangle geometry created by ``rectangle_geometry.py``

    This script partitions a simple Abaqus model with a single rectangle part.

    **Feature labels:**

    * ``bottom_left`` - bottom left vertex
    * ``bottom_right`` - bottom right vertex
    * ``top_right`` - top right vertex
    * ``top_left`` - top left vertex
    * ``left`` - left edge
    * ``top`` - top edge
    * ``right`` - right edge
    * ``bottom`` - bottom edge

    :param str input_file: The Abaqus model file created by ``rectangle_geometry.py``. Will be stripped of the extension
        and ``.cae`` will be used.
    :param str output_file: The output file for the Abaqus model. Will be stripped of the extension and ``.cae`` will be
        used.
    :param str model_name: The name of the Abaqus model
    :param str part_name: The name of the Abaqus part
    :param float width: The rectangle width
    :param float height: The rectangle height

    :returns: writes ``output_file``.cae and ``output_file``.jnl
    """
    input_file = os.path.splitext(input_file)[0] + ".cae"
    output_file = os.path.splitext(output_file)[0] + ".cae"

    # Avoid modifying the contents or timestamp on the input file.
    # Required to get conditional re-builds with a build system such as GNU Make, CMake, or SCons
    if input_file != output_file:
        shutil.copyfile(input_file, output_file)

    abaqus.openMdb(pathName=output_file)

    part = abaqus.mdb.models[model_name].parts[part_name]

    vertices = part.vertices.findAt(
        ((0, 0, 0),),
    )
    part.Set(vertices=vertices, name="bottom_left")

    vertices = part.vertices.findAt(
        ((width, 0, 0),),
    )
    part.Set(vertices=vertices, name="bottom_right")

    vertices = part.vertices.findAt(
        ((width, height, 0),),
    )
    part.Set(vertices=vertices, name="top_right")

    vertices = part.vertices.findAt(
        ((0, height, 0),),
    )
    part.Set(vertices=vertices, name="top_left")

    side1Edges = part.edges.findAt(
        ((0, height / 2.0, 0),),
    )
    part.Set(edges=side1Edges, name="left")

    side1Edges = part.edges.findAt(
        ((width / 2.0, height, 0),),
    )
    part.Set(edges=side1Edges, name="top")

    side1Edges = part.edges.findAt(
        ((width, height / 2.0, 0),),
    )
    part.Set(edges=side1Edges, name="right")

    side1Edges = part.edges.findAt(
        ((width / 2.0, 0, 0),),
    )
    part.Set(edges=side1Edges, name="bottom")

    abaqus.mdb.save()


def get_parser():
    """Return parser for CLI options

    All options should use the double-hyphen ``--option VALUE`` syntax to avoid clashes with the Abaqus option syntax,
    including flag style arguments ``--flag``. Single hyphen ``-f`` flag syntax often clashes with the Abaqus command
    line options and should be avoided.

    :returns: parser
    :rtype: argparse.ArgumentParser
    """
    # The global '__file__' variable doesn't appear to be set when executing from Abaqus CAE
    filename = inspect.getfile(lambda: None)
    basename = os.path.basename(filename)
    basename_without_extension, extension = os.path.splitext(basename)
    # Construct a part name from the filename less the workflow step
    default_part_name = basename_without_extension
    suffix = "_partition"
    if default_part_name.endswith(suffix):
        default_part_name = default_part_name[: -len(suffix)]
    # Set default parameter values
    default_input_file = "{}_geometry".format(default_part_name)
    default_output_file = "{}".format(basename_without_extension)
    default_width = 1.0
    default_height = 1.0

    prog = "abaqus cae -noGui {} --".format(basename)
    cli_description = (
        "Partition the simple rectangle geometry created by ``rectangle_geometry.py`` "
        "and write an ``output_file``.cae Abaqus model file."
    )
    parser = argparse.ArgumentParser(description=cli_description, prog=prog)
    parser.add_argument(
        "--input-file",
        type=str,
        default=default_input_file,
        # fmt: off
        help="The Abaqus model file created by ``rectangle_geometry.py``. "
             "Will be stripped of the extension and ``.cae`` will be used, e.g. ``input_file``.cae",
        # fmt: on
    )
    parser.add_argument(
        "--output-file",
        type=str,
        default=default_output_file,
        # fmt: off
        help="The output file for the Abaqus model. "
             "Will be stripped of the extension and ``.cae`` will be used, e.g. ``output_file``.cae",
        # fmt: on
    )
    parser.add_argument(
        "--model-name",
        type=str,
        default=default_part_name,
        help="The name of the Abaqus model",
    )
    parser.add_argument(
        "--part-name",
        type=str,
        default=default_part_name,
        help="The name of the Abaqus part",
    )
    parser.add_argument(
        "--width",
        type=float,
        default=default_width,
        help="The rectangle width. Positive float.",
    )
    parser.add_argument(
        "--height",
        type=float,
        default=default_height,
        help="The rectangle height. Positive float.",
    )
    return parser


if __name__ == "__main__":
    parser = get_parser()
    # Abaqus does not strip the CAE options, so we have to skip the unknown options related to the CAE CLI.
    try:
        args, unknown = parser.parse_known_args()
    except SystemExit as err:
        sys.exit(err.code)
    # Check for typos in expected arguments. Assumes all arguments use ``--option`` syntax, which is unused by Abaqus.
    possible_typos = [argument for argument in unknown if argument.startswith("--")]
    if len(possible_typos) > 0:
        raise RuntimeError("Found possible typos in CLI option(s) {}".format(possible_typos))

    sys.exit(
        main(
            input_file=args.input_file,
            output_file=args.output_file,
            model_name=args.model_name,
            part_name=args.part_name,
            width=args.width,
            height=args.height,
        )
    )
