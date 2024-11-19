import sys
import shutil
import pathlib
import argparse

import cubit


def main(input_file, output_file, width, height):
    """Partition the simple rectangle geometry created by ``rectangle_geometry.py``

    This script partitions a simple Cubit model with a single rectangle part.

    **Feature labels:**

    * ``bottom_left`` - bottom left vertex
    * ``bottom_right`` - bottom right vertex
    * ``top_right`` - top right vertex
    * ``top_left`` - top left vertex
    * ``left`` - left edge nodes
    * ``top`` - top edge nodes
    * ``right`` - right edge nodes
    * ``bottom`` - bottom edge nodes
    * ``elset_left`` - left edge elements
    * ``elset_top`` - top edge elements
    * ``elset_right`` - right edge elements
    * ``elset_bottom`` - bottom edge elements

    :param str input_file: The Cubit model file created by ``rectangle_geometry.py``. Will be stripped of the extension
        and ``.cub`` will be used.
    :param str output_file: The output file for the Cubit model. Will be stripped of the extension and ``.cub`` will be
        used.
    :param float width: The rectangle width
    :param float height: The rectangle height

    :returns: writes ``output_file``.cub
    """
    input_file = pathlib.Path(input_file).with_suffix(".cub")
    output_file = pathlib.Path(output_file).with_suffix(".cub")

    # Avoid modifying the contents or timestamp on the input file.
    # Required to get conditional re-builds with a build system such as GNU Make, CMake, or SCons
    if input_file != output_file:
        shutil.copyfile(input_file, output_file)

    cubit.init(["cubit", "-noecho", "-nojournal", "-nographics", "-batch"])
    cubit.cmd("new")
    cubit.cmd("reset")

    cubit.cmd(f"open '{output_file}'")

    cubit.cmd("nodeset 1 add vertex 1")
    cubit.cmd("nodeset 1 name 'bottom_left'")
    cubit.cmd("nodeset 2 add vertex 2")
    cubit.cmd("nodeset 2 name 'bottom_right'")
    cubit.cmd("nodeset 3 add vertex 3")
    cubit.cmd("nodeset 3 name 'top_right'")
    cubit.cmd("nodeset 4 add vertex 4")
    cubit.cmd("nodeset 4 name 'top_left'")

    cubit.cmd("nodeset 5 add curve 4")
    cubit.cmd("nodeset 5 name 'left'")
    cubit.cmd("nodeset 6 add curve 3")
    cubit.cmd("nodeset 6 name 'top'")
    cubit.cmd("nodeset 7 add curve 2")
    cubit.cmd("nodeset 7 name 'right'")
    cubit.cmd("nodeset 8 add curve 1")
    cubit.cmd("nodeset 8 name 'bottom'")

    cubit.cmd("sideset 1 add curve 4")
    cubit.cmd("sideset 1 name 'elset_left'")
    cubit.cmd("sideset 2 add curve 3")
    cubit.cmd("sideset 2 name 'elset_top'")
    cubit.cmd("sideset 3 add curve 2")
    cubit.cmd("sideset 3 name 'elset_right'")
    cubit.cmd("sideset 4 add curve 1")
    cubit.cmd("sideset 4 name 'elset_bottom'")

    cubit.cmd(f"save as '{output_file}' overwrite")


def get_parser():
    script_name = pathlib.Path(__file__)
    # Set default parameter values
    default_input_file = script_name.with_suffix(".cub").name.replace("_partition", "_geometry")
    default_output_file = script_name.with_suffix(".cub").name
    default_width = 1.0
    default_height = 1.0

    prog = f"python {script_name.name} "
    cli_description = (
        "Partition the simple rectangle geometry created by ``rectangle_geometry.py`` "
        "and write an ``output_file``.cub Cubit model file."
    )
    parser = argparse.ArgumentParser(description=cli_description, prog=prog)
    parser.add_argument(
        "--input-file",
        type=str,
        default=default_input_file,
        # fmt: off
        help="The Cubit model file created by ``rectangle_geometry.py``. "
             "Will be stripped of the extension and ``.cub`` will be used, e.g. ``input_file``.cub "
             "(default: %(default)s",
        # fmt: on
    )
    parser.add_argument(
        "--output-file",
        type=str,
        default=default_output_file,
        # fmt: off
        help="The output file for the Cubit model. "
             "Will be stripped of the extension and ``.cub`` will be used, e.g. ``output_file``.cub "
             "(default: %(default)s",
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
    return parser


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
    sys.exit(
        main(
            input_file=args.input_file,
            output_file=args.output_file,
            width=args.width,
            height=args.height,
        )
    )
