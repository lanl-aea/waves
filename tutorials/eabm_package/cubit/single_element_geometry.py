import sys
import argparse
import pathlib

import cubit


def main(output_file, width, height):
    """Create a simple rectangle geometry.

    This script creates a simple Cubit model with a single rectangle part.

    :param str output_file: The output file for the Cubit model without extension. Will be appended with the required
        extension, e.g. ``output_file``.cub
    :param float width: The rectangle width
    :param float height: The rectangle height

    :returns: writes ``output_file``.cub
    """
    cubit.init(['cubit', '-noecho', '-nojournal', '-nographics', '-batch'])
    cubit.cmd('new')
    cubit.cmd('reset')

    cubit.cmd(f"create vertex 0 0 0")
    cubit.cmd(f"create vertex {width} 0 0")
    cubit.cmd(f"create vertex {width} {height} 0")
    cubit.cmd(f"create vertex 0 {height} 0")
    cubit.cmd(f"create surface vertex 1,2,3,4")

    cubit.cmd(f"save as '{output_file}.cub' overwrite")

    return 0


def positive_float(argument):
    """Type function for argparse - positive floats

    :param str argument: string argument from argparse

    :returns: argument
    :rtype: float
    """
    MINIMUM_VALUE = 0.0
    try:
        argument = float(argument)
    except ValueError:
        raise argparse.ArgumentTypeError("invalid float value: '{}'".format(argument))
    if argument < MINIMUM_VALUE:
        raise argparse.ArgumentTypeError("invalid positive float: '{}'".format(argument))
    return argument


def get_parser():
    script_name = pathlib.Path(__file__)
    # Set default parameter values
    default_output_file = script_name.stem
    default_width = 1.0
    default_height = 1.0

    prog = f"python {script_name.name} "
    cli_description = "Create a simple rectangle geometry and write an ``output_file``.cub Cubit model file."
    parser = argparse.ArgumentParser(description=cli_description,
                                     prog=prog)
    parser.add_argument('-o', '--output-file', type=str, default=default_output_file,
                        help="The output file for the Cubit model without extension. Will be appended with the " \
                             "required extension, e.g. ``output_file``.cub")
    parser.add_argument('-w', '--width', type=positive_float, default=default_width,
                        help="The rectangle width. Positive float.")
    # Short option '-h' is reserved for the help message
    parser.add_argument('--height', type=positive_float, default=default_height,
                        help="The rectangle height. Positive float.")
    return parser


if __name__ == '__main__':
    parser = get_parser()
    args, unknown = parser.parse_known_args()
    sys.exit(main(output_file=args.output_file,
                  width=args.width,
                  height=args.height))
