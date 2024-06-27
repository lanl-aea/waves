import sys
import pathlib
import argparse

import cubit


def main(output_file, width, height, depth):
    """Create a simple cube geometry.

    This script creates a simple Cubit model with a single cube part.

    :param str output_file: The output file for the Cubit model. Will be stripped of the extension and ``.cub`` will be
        used.
    :param float width: The cube width (X-axis)
    :param float height: The cube height (Y-axis)
    :param float depth: The cube depth (Z-axis)

    :returns: writes ``output_file``.cub
    """
    output_file = pathlib.Path(output_file).with_suffix(".cub")

    cubit.init(['cubit', '-noecho', '-nojournal', '-nographics', '-batch'])
    cubit.cmd('new')
    cubit.cmd('reset')

    cubit.cmd(f"brick {width} {height} {depth}")
    cubit.cmd(f"move volume 1 x {width / 2} y {height / 2} z {depth / 2} include_merged")

    # TODO: separate sets into a partition script
    cubit.cmd("nodeset 1 add surface 5")
    cubit.cmd("nodeset 1 name 'top'")
    cubit.cmd("sideset 1 add surface 5")
    cubit.cmd("sideset 1 name 'top'")

    cubit.cmd("nodeset 2 add surface 3")
    cubit.cmd("nodeset 2 name 'bottom'")
    cubit.cmd("sideset 2 add surface 3")
    cubit.cmd("sideset 2 name 'bottom'")

    cubit.cmd("nodeset 3 add surface 4")
    cubit.cmd("nodeset 3 name 'left'")
    cubit.cmd("sideset 3 add surface 4")
    cubit.cmd("sideset 3 name 'left'")

    cubit.cmd("nodeset 4 add surface 6")
    cubit.cmd("nodeset 4 name 'right'")
    cubit.cmd("sideset 4 add surface 6")
    cubit.cmd("sideset 4 name 'right'")

    cubit.cmd("nodeset 5 add surface 1")
    cubit.cmd("nodeset 5 name 'front'")
    cubit.cmd("sideset 5 add surface 1")
    cubit.cmd("sideset 5 name 'front'")

    cubit.cmd("nodeset 6 add surface 2")
    cubit.cmd("nodeset 6 name 'back'")
    cubit.cmd("sideset 6 add surface 2")
    cubit.cmd("sideset 6 name 'back'")

    cubit.cmd(f"save as '{output_file}' overwrite")


def get_parser():
    script_name = pathlib.Path(__file__)
    # Set default parameter values
    default_output_file = script_name.with_suffix(".cub").name
    default_width = 1.0
    default_height = 1.0
    default_depth = 1.0

    prog = f"python {script_name.name} "
    cli_description = "Create a simple cube geometry and write an ``output_file``.cub Cubit model file."
    parser = argparse.ArgumentParser(description=cli_description, prog=prog)
    parser.add_argument('--output-file', type=str, default=default_output_file,
                        help="The output file for the Cubit model. " \
                             "Will be stripped of the extension and ``.cub`` will be used, e.g. ``output_file``.cub " \
                             "(default: %(default)s")
    parser.add_argument('--width', type=float, default=default_width,
                        help="The cube width (X-axis)")
    parser.add_argument('--height', type=float, default=default_height,
                        help="The cube height (Y-axis)")
    parser.add_argument('--depth', type=float, default=default_height,
                        help="The cube depth (Z-axis)")
    return parser


if __name__ == '__main__':
    parser = get_parser()
    args = parser.parse_args()
    sys.exit(main(
        output_file=args.output_file,
        width=args.width,
        height=args.height
    ))
