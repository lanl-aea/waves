import os
import sys
import shutil
import inspect
import argparse
import tempfile
import functools

import abaqus
import abaqusConstants


image_default_x_angle = 0.
image_default_y_angle = 0.
image_default_z_angle = 0.
image_default_image_size = (1920, 1080)
image_default_model_name = "Model-1"
image_default_part_name = "Part-1"
image_cli_help = "Save an image of an Abaqus model"
image_cli_description = "Save an assembly view image of an Abaqus model from an input or CAE file"

# One time dump from session.viewports['Viewport: 1'].colorMappings.keys()) to stay Python 3 compatible
image_color_map_choices = [
    'Material', 'Section', 'Composite layup', 'Composite ply', 'Part', 'Part instance',
    'Element set', 'Averaging region', 'Element type', 'Default', 'Assembly', 'Part geometry', 'Load', 'Boundary condition',
    'Interaction', 'Constraint', 'Property', 'Meshability', 'Instance type', 'Set', 'Surface', 'Internal set',
    'Internal surface', 'Display group', 'Selection group', 'Skin', 'Stringer', 'Cell', 'Face'
]


def main(input_file, output_file,
         x_angle=image_default_x_angle,
         y_angle=image_default_y_angle,
         z_angle=image_default_z_angle,
         image_size=image_default_image_size,
         model_name=image_default_model_name,
         part_name=image_default_part_name,
         color_map=image_color_map_choices[0]):
    """Wrap image with file input handling

    :param str input_file: Abaqus input file. Suports ``*.inp`` and ``*.cae``.
    :param str output_file: Output image file. Supports ``*.png`` and ``*.svg``.
    :param float x_angle: Rotation about X-axis in degrees for ``session.viewports[].view.rotate`` Abaqus Python method
    :param float y_angle: Rotation about Y-axis in degrees for ``session.viewports[].view.rotate`` Abaqus Python method
    :param float z_angle: Rotation about Z-axis in degrees for ``session.viewports[].view.rotate`` Abaqus Python method
    :param tuple image_size: Tuple containing height and width of the output image in pixels
    :param str model_name: model to query in the Abaqus model database
    :param str part_name: part to query in the specified Abaqus model
    :param str color_map: color map key

    :returns: writes image to ``{output_file}``
    """
    input_file_extension = os.path.splitext(input_file)[1]
    if input_file_extension.lower() == ".cae":
        with tempfile.NamedTemporaryFile(suffix=".cae", dir=".") as copy_file:
            shutil.copyfile(input_file, copy_file.name)
            abaqus.openMdb(pathName=copy_file.name)
            image(output_file, x_angle=x_angle, y_angle=y_angle, z_angle=z_angle, image_size=image_size,
                  model_name=model_name, part_name=part_name, color_map=color_map)
    elif input_file_extension.lower() == ".inp":
        abaqus.mdb.ModelFromInputFile(name=model_name, inputFileName=input_file)
        image(output_file, x_angle=x_angle, y_angle=y_angle, z_angle=z_angle, image_size=image_size,
              model_name=model_name, part_name=part_name, color_map=color_map)
    else:
        sys.stderr.write("Unknown file extension {}".format(input_file_extension))
        sys.exit(1)


def image(output_file,
          x_angle=image_default_x_angle,
          y_angle=image_default_y_angle,
          z_angle=image_default_z_angle,
          image_size=image_default_image_size,
          model_name=image_default_model_name,
          part_name=image_default_part_name,
          color_map=image_color_map_choices[0]):
    """Script for saving an assembly view image (colored by material) for a given Abaqus input file.

    The color map is set to color by material. Finally, viewport is set to fit the view to the viewport screen.

    If the model assembly has no instances, use ``part_name`` to generate one. The ``input_file`` is not modified to
    include this generated instance.

    :param str output_file: Output image file. Supports ``*.png`` and ``*.svg``.
    :param float x_angle: Rotation about X-axis in degrees for ``session.viewports[].view.rotate`` Abaqus Python method
    :param float y_angle: Rotation about Y-axis in degrees for ``session.viewports[].view.rotate`` Abaqus Python method
    :param float z_angle: Rotation about Z-axis in degrees for ``session.viewports[].view.rotate`` Abaqus Python method
    :param tuple image_size: Tuple containing height and width of the output image in pixels
    :param str model_name: model to query in the Abaqus model database
    :param str part_name: part to query in the specified Abaqus model
    :param str color_map: color map key

    :returns: writes image to ``{output_file}``
    """
    output_file_stem, output_file_extension = os.path.splitext(output_file)
    output_file_extension = output_file_extension.lstrip(".")
    assembly = abaqus.mdb.models[model_name].rootAssembly
    if len(assembly.instances.keys()) == 0:
        part = abaqus.mdb.models[model_name].parts[part_name]
        assembly.Instance(name=part_name, part=part, dependent=abaqusConstants.ON)
    session.viewports['Viewport: 1'].assemblyDisplay.setValues(
        optimizationTasks=abaqusConstants.OFF, geometricRestrictions=abaqusConstants.OFF,
        stopConditions=abaqusConstants.OFF)
    session.viewports['Viewport: 1'].setValues(displayedObject=assembly)
    session.viewports['Viewport: 1'].view.rotate(xAngle=x_angle, yAngle=y_angle, zAngle=z_angle,
                                                 mode=abaqusConstants.MODEL)
    session.viewports['Viewport: 1'].view.fitView()
    session.viewports['Viewport: 1'].enableMultipleColors()
    session.viewports['Viewport: 1'].setColor(initialColor='#BDBDBD')
    cmap = session.viewports['Viewport: 1'].colorMappings[color_map]
    session.viewports['Viewport: 1'].setColor(colorMapping=cmap)
    session.viewports['Viewport: 1'].disableMultipleColors()
    session.printOptions.setValues(vpDecorations=abaqusConstants.OFF)
    session.pngOptions.setValues(imageSize=image_size)

    output_format = return_abaqus_constant_or_exit(output_file_extension)
    if output_format is None:
        print >> sys.__stderr__, "{}".format("Abaqus does not recognize the output extension '{}'".format(output_file_extension))

    session.printToFile(fileName=output_file_stem, format=output_format,
                        canvasObjects=(session.viewports['Viewport: 1'],))


def print_exception_message(function):
    """Decorate a function to catch bare exception and instead call sys.exit with the message

    :param function: function to decorate
    """
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        output = None
        try:
            output = function(*args, **kwargs)
        except Exception as err:
            print >> sys.__stderr__, "{}".format(err)
        return output
    return wrapper


def return_abaqus_constant(search):
    """If search is found in the abaqusConstants module, return the abaqusConstants object.

    Raise a ValueError if the search string is not found.

    :param str search: string to search in the abaqusConstants module attributes

    :return value: abaqusConstants attribute
    :rtype: abaqusConstants.<search>
    """
    search = search.upper()
    if hasattr(abaqusConstants, search):
        attribute = getattr(abaqusConstants, search)
    else:
        raise ValueError("The abaqusConstants module does not have a matching '{}' object".format(search))
    return attribute


@print_exception_message
def return_abaqus_constant_or_exit(*args, **kwargs):
    return return_abaqus_constant(*args, **kwargs)


def get_parser():
    file_name = inspect.getfile(lambda: None)
    base_name = os.path.basename(file_name)
    prog = "abaqus cae -noGui {} --".format(base_name)
    cli_description = "Export an image of an Abaqus model"
    parser = argparse.ArgumentParser(description=cli_description, prog=prog)
    parser.add_argument('--input-file', type=str, required=True,
                        help='Abaqus input file. Supports ``*.inp`` and ``*.cae``.')
    parser.add_argument('--output-file', type=str, required=True,
                        help='Output image from the Abaqus viewport. Supports ``*.png`` and ``*.svg``.')
    parser.add_argument('--x-angle', type=float, default=image_default_x_angle,
                        help='Viewer rotation about X-axis in degrees (default: %(default)s)')
    parser.add_argument('--y-angle', type=float, default=image_default_y_angle,
                        help='Viewer rotation about Y-axis in degrees (default: %(default)s)')
    parser.add_argument('--z-angle', type=float, default=image_default_z_angle,
                        help='Viewer rotation about Z-axis in degrees (default: %(default)s)')
    parser.add_argument('--image-size', nargs=2, type=int, default=image_default_image_size,
                        help="Image size in pixels (X, Y) (default: %(default)s)")
    parser.add_argument('--model-name', type=str, default=image_default_model_name,
                        help="Abaqus model name (default: %(default)s)")
    parser.add_argument('--part-name', type=str, default=image_default_part_name,
                        help="Abaqus part name (default: %(default)s)")
    parser.add_argument('--color-map', type=str, choices=image_color_map_choices, default=image_color_map_choices[0],
                        help="Color map (default: %(default)s)")
    return parser


if __name__ == "__main__":

    parser = get_parser()
    try:
        args, unknown = parser.parse_known_args()
    except SystemExit as err:
        sys.exit(err.code)

    sys.exit(main(
        args.input_file,
        args.output_file,
        x_angle=args.x_angle,
        y_angle=args.y_angle,
        z_angle=args.z_angle,
        image_size=args.image_size,
        model_name=args.model_name,
        part_name=args.part_name,
        color_map=args.color_map
    ))
