import os
import sys
import inspect
import argparse

import abaqus
import abaqusConstants

from modsim_package.argparse_types import positive_float


def main(output_file, model_name, part_name, width, height):
    """Create a simple rectangle geometry.

    This script creates a simple Abaqus model with a single rectangle part.

    :param str output_file: The output file for the Abaqus model. Will be stripped of the extension and ``.cae`` will be
        used.
    :param str model_name: The name of the Abaqus model
    :param str part_name: The name of the Abaqus part
    :param float width: The rectangle width
    :param float height: The rectangle height

    :returns: writes ``output_file``.cae and ``output_file``.jnl
    """
    output_file = os.path.splitext(output_file)[0] + ".cae"

    abaqus.mdb.Model(name=model_name, modelType=abaqusConstants.STANDARD_EXPLICIT)

    sketch = abaqus.mdb.models[model_name].ConstrainedSketch(name=part_name, sheetSize=1.0)
    sketch.setPrimaryObject(option=abaqusConstants.STANDALONE)
    sketch.rectangle(point1=(0.0, 0.0), point2=(width, height))
    sketch.unsetPrimaryObject()

    part = abaqus.mdb.models[model_name].Part(
        name=part_name,
        dimensionality=abaqusConstants.TWO_D_PLANAR,
        type=abaqusConstants.DEFORMABLE_BODY,
    )
    part.BaseShell(sketch=sketch)

    abaqus.mdb.saveAs(pathName=output_file)


# Comment used in tutorial code snippets: marker-1


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
    # Construct a part name from the filename less the workflow step suffix
    default_part_name = basename_without_extension
    suffix = "_geometry"
    if default_part_name.endswith(suffix):
        default_part_name = default_part_name[: -len(suffix)]
    # Set default parameter values
    default_output_file = "{}".format(basename_without_extension)
    default_width = 1.0
    default_height = 1.0

    prog = "abaqus cae -noGui {} --".format(basename)
    cli_description = "Create a simple rectangle geometry and write an ``output_file``.cae Abaqus model file."
    parser = argparse.ArgumentParser(description=cli_description, prog=prog)
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
        type=positive_float,
        default=default_width,
        help="The rectangle width. Positive float.",
    )
    parser.add_argument(
        "--height",
        type=positive_float,
        default=default_height,
        help="The rectangle height. Positive float.",
    )
    return parser


# Comment used in tutorial code snippets: marker-2


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
            output_file=args.output_file,
            model_name=args.model_name,
            part_name=args.part_name,
            width=args.width,
            height=args.height,
        )
    )
