import sys
import os
import argparse
import inspect

import abaqus

def main(input_file, output_file, model_name, part_name, width, height):
    """Partition the simple square geometry created by single_element_geometry.py

    This script partitions a simple Abaqus model with a single square part.

    **Usage:**

    .. code-block::

       abaqus cae -noGUI single_element_partition.py
       abaqus cae -noGUI single_element_partition.py -- [options]
       abaqus cae -noGUI single_element_partition.py -- --output-file single_element_geometry.cae
       abaqus cae -noGUI single_element_partition.py -- --part-name single_element.cae

    **Feature labels:**

    * ``bottom_left`` - bottom left vertex
    * ``bottom_right`` - bottom right vertex
    * ``top_right`` - top right vertex
    * ``top_left`` - top left vertex
    * ``left`` - left edge
    * ``top`` - top edge
    * ``right`` - right edge
    * ``bottom`` - bottom edge

    :param str input_file: The Abaqus model file created by single_element_geometry.py without extension, e.g.
        ``input_file``.cae
    :param str output_file: The output file for the Abaqus model without extension, e.g. ``output_file``.cae
    :param str model_name: The name of the Abaqus model
    :param str part_name: The name of the Abaqus part
    :param float width: The square width
    :param float height: The square height

    :returns: writes ``output_file``.cae
    """

    abaqus.openMdb(pathName='{}.cae'.format(input_file))

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
    p.Surface(side1Edges=side1Edges, name='left')

    side1Edges = s.findAt(((width / 2., height, 0),),)
    p.Surface(side1Edges=side1Edges, name='top')

    side1Edges = s.findAt(((width, height / 2., 0),),)
    p.Surface(side1Edges=side1Edges, name='right')

    side1Edges = s.findAt(((width / 2., 0, 0),),)
    p.Surface(side1Edges=side1Edges, name='bottom')

    abaqus.mdb.saveAs(pathName='{}.cae'.format(output_file))

if __name__ == '__main__':
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

    parser = argparse.ArgumentParser(description="Partition a simple square geometry",
                                     prog=os.path.basename(filename))
    parser.add_argument('-i', '--input-file', type=str, default=default_input_file,
                        help="input file name")
    parser.add_argument('-o', '--output-file', type=str, default=default_output_file,
                        help="output file name")
    parser.add_argument('-m', '--model-name', type=str, default=default_part_name,
                        help="model name")
    parser.add_argument('-p', '--part-name', type=str, default=default_part_name,
                        help="part name")
    parser.add_argument('-w', '--width', type=float, default=default_width,
                        help="square width")
    # Short option '-h' is reserved for the help message
    parser.add_argument('--height', type=float, default=default_height,
                        help="square height")

    # Abaqus does not strip the CAE options, so we have to skip the unknown options related to the CAE CLI.
    args, unknown = parser.parse_known_args()

    sys.exit(main(input_file=args.input_file,
                  output_file=args.output_file,
                  model_name=args.model_name,
                  part_name=args.part_name,
                  width=args.width,
                  height=args.height))
