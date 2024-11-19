import sys
import pathlib
import argparse

import cubit


def main(output_file, width, height):
    """Create a simple rectangle geometry.

    This script creates a simple Cubit model with a single rectangle part.

    :param str output_file: The output file for the Cubit model. Will be stripped of the extension and ``.cub`` will be
        used.
    :param float width: The rectangle width
    :param float height: The rectangle height

    :returns: writes ``output_file``.cub
    """
    output_file = pathlib.Path(output_file).with_suffix(".cub")

    cubit.init(["cubit", "-noecho", "-nojournal", "-nographics", "-batch"])
    cubit.cmd("new")
    cubit.cmd("reset")

    cubit.cmd(f"create vertex 0 0 0")
    cubit.cmd(f"create vertex {width} 0 0")
    cubit.cmd(f"create vertex {width} {height} 0")
    cubit.cmd(f"create vertex 0 {height} 0")
    cubit.cmd(f"create surface vertex 1,2,3,4")

    cubit.cmd(f"save as '{output_file}' overwrite")


def get_parser():
    script_name = pathlib.Path(__file__)
    # Set default parameter values
    default_output_file = script_name.with_suffix(".cub").name
    default_width = 1.0
    default_height = 1.0

    prog = f"python {script_name.name} "
    cli_description = "Create a simple rectangle geometry and write an ``output_file``.cub Cubit model file."
    parser = argparse.ArgumentParser(description=cli_description, prog=prog)
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
            output_file=args.output_file,
            width=args.width,
            height=args.height,
        )
    )
