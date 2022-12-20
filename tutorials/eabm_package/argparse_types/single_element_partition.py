import sys
import os
import argparse
import inspect
import shutil

import abaqus

from eabm_package.argparse_types import positive_float


def main(input_file, output_file, model_name, part_name, width, height):
    """Partition the simple rectangle geometry created by ``single_element_geometry.py``

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

    :param str input_file: The Abaqus model file created by ``single_element_geometry.py`` without extension. Will be
        appended with the required extension, e.g. ``input_file``.cae
    :param str output_file: The output file for the Abaqus model without extension. Will be appended with the required
        extension, e.g. ``output_file``.cae
    :param str model_name: The name of the Abaqus model
    :param str part_name: The name of the Abaqus part
    :param float width: The rectangle width
    :param float height: The rectangle height

    :returns: writes ``output_file``.cae
    """

    input_with_extension = '{}.cae'.format(input_file)
    output_with_extension = '{}.cae'.format(output_file)

    # Avoid modifying the contents or timestamp on the input file.
    # Required to get conditional re-builds with a build system such as GNU Make, CMake, or SCons
    if input_file != output_file:
        shutil.copyfile(input_with_extension, output_with_extension)

    abaqus.openMdb(pathName=output_with_extension)

    p = abaqus.mdb.models[model_name].parts[part_name]

    v = p.vertices

    verts = v.findAt(((0, 0, 0),),)
    p.Set(vertices=verts, name='bottom_left')

    verts = v.findAt(((width, 0, 0),),)
    p.Set(vertices=verts, name='bottom_right')

    verts = v.findAt(((width, height, 0),),)
    p.Set(vertices=verts, name='top_right')

    verts = v.findAt(((0, height, 0),),)
    p.Set(vertices=verts, name='top_left')

    s = p.edges

    side1Edges = s.findAt(((0, height / 2., 0),),)
    p.Set(edges=side1Edges, name='left')

    side1Edges = s.findAt(((width / 2., height, 0),),)
    p.Set(edges=side1Edges, name='top')

    side1Edges = s.findAt(((width, height / 2., 0),),)
    p.Set(edges=side1Edges, name='right')

    side1Edges = s.findAt(((width / 2., 0, 0),),)
    p.Set(edges=side1Edges, name='bottom')

    abaqus.mdb.save()

    return 0


def get_parser():
    # The global '__file__' variable doesn't appear to be set when executing from Abaqus CAE
    filename = inspect.getfile(lambda: None)
    basename = os.path.basename(filename)
    basename_without_extension, extension = os.path.splitext(basename)
    # Construct a part name from the filename less the workflow step
    default_part_name = basename_without_extension
    suffix = '_partition'
    if default_part_name.endswith(suffix):
        default_part_name = default_part_name[:-len(suffix)]
    # Set default parameter values
    default_input_file = '{}_geometry'.format(default_part_name)
    default_output_file = '{}'.format(basename_without_extension)
    default_width = 1.0
    default_height = 1.0

    cli_description = "Partition the simple rectangle geometry created by ``single_element_geometry.py`` " \
                      "and write an ``output_file``.cae Abaqus model file."
    parser = argparse.ArgumentParser(description=cli_description,
                                     prog=os.path.basename(filename))
    parser.add_argument('-i', '--input-file', type=str, default=default_input_file,
                        help="The Abaqus model file created by ``single_element_geometry.py`` without extension. " \
                             "Will be appended with the required extension, e.g. ``input_file``.cae")
    parser.add_argument('-o', '--output-file', type=str, default=default_output_file,
                        help="The output file for the Abaqus model without extension. Will be appended with the " \
                             "required extension, e.g. ``output_file``.cae")
    parser.add_argument('-m', '--model-name', type=str, default=default_part_name,
                        help="The name of the Abaqus model")
    parser.add_argument('-p', '--part-name', type=str, default=default_part_name,
                        help="The name of the Abaqus part")
    parser.add_argument('-w', '--width', type=positive_float, default=default_width,
                        help="The rectangle width. Positive float.")
    # Short option '-h' is reserved for the help message
    parser.add_argument('--height', type=positive_float, default=default_height,
                        help="The rectangle height. Positive float.")
    return parser


if __name__ == '__main__':
    parser = get_parser()
    # Abaqus does not strip the CAE options, so we have to skip the unknown options related to the CAE CLI.
    args, unknown = parser.parse_known_args()
    sys.exit(main(input_file=args.input_file,
                  output_file=args.output_file,
                  model_name=args.model_name,
                  part_name=args.part_name,
                  width=args.width,
                  height=args.height))
