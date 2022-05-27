import sys
import os
import argparse
import inspect

import abaqus
import abaqusConstants

def main(output_file, model_name, part_name, width, height):
    """Create a simple rectangle geometry.

    This script creates a simple Abaqus model with a single rectangle part.

    :param str output_file: The output file for the Abaqus model without extension, e.g. ``output_file``.cae
    :param str model_name: The name of the Abaqus model
    :param str part_name: The name of the Abaqus part
    :param float width: The rectangle width
    :param float height: The rectangle height

    :returns: writes ``output_file``.cae
    """

    abaqus.mdb.Model(name=model_name, modelType=abaqusConstants.STANDARD_EXPLICIT)

    s = abaqus.mdb.models[model_name].ConstrainedSketch(name=part_name, sheetSize=1.0)
    s.setPrimaryObject(option=abaqusConstants.STANDALONE)

    s.Line(point1=(  0.0,    0.0), point2=(width,    0.0))
    s.Line(point1=(width,    0.0), point2=(width, height))
    s.Line(point1=(width, height), point2=(  0.0, height))
    s.Line(point1=(  0.0, height), point2=(  0.0,    0.0))

    s.unsetPrimaryObject()
    p = abaqus.mdb.models[model_name].Part(name=part_name, dimensionality=abaqusConstants.TWO_D_PLANAR,
                                           type=abaqusConstants.DEFORMABLE_BODY)
    p.BaseShell(sketch=s)

    abaqus.mdb.saveAs(pathName='{}.cae'.format(output_file))

    return 0


def get_parser():
    # The global '__file__' variable doesn't appear to be set when executing from Abaqus CAE
    filename = inspect.getfile(lambda: None)
    basename = os.path.basename(filename)
    basename_without_extension, extension = os.path.splitext(basename)
    # Construct a part name from the filename less the workflow step suffix
    default_part_name = basename_without_extension
    suffix = '_geometry'
    if default_part_name.endswith(suffix):
        default_part_name = default_part_name[:-len(suffix)]
    # Set default parameter values
    default_output_file = '{}'.format(basename_without_extension)
    default_width = 1.0
    default_height = 1.0
    
    prog = "abaqus cae -noGui {} --".format(basename)
    cli_description = "Create a simple rectangle geometry and write an ``output_file``.cae Abaqus model file."
    parser = argparse.ArgumentParser(description=cli_description,
                                     prog=prog)
    parser.add_argument('-o', '--output-file', type=str, default=default_output_file,
                        help="The output file for the Abaqus model without extension, e.g. ``output_file``.cae")
    parser.add_argument('-m', '--model-name', type=str, default=default_part_name,
                        help="The name of the Abaqus model")
    parser.add_argument('-p', '--part-name', type=str, default=default_part_name,
                        help="The name of the Abaqus part")
    parser.add_argument('-w', '--width', type=float, default=default_width,
                        help="The rectangle width")
    # Short option '-h' is reserved for the help message
    parser.add_argument('--height', type=float, default=default_height,
                        help="The rectangle height")
    return parser


if __name__ == '__main__':
    parser = get_parser()
    # Abaqus does not strip the CAE options, so we have to skip the unknown options related to the CAE CLI.
    args, unknown = parser.parse_known_args()
    sys.exit(main(output_file=args.output_file,
                  model_name=args.model_name,
                  part_name=args.part_name,
                  width=args.width,
                  height=args.height))

