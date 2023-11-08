import argparse
import inspect
import os
import sys

import abaqusConstants as ac

def main(input_file, output_file, xAngle=0, yAngle=0, zAngle=0):
    """
    Script for grabbing the default horizontal view image (colored by material) for a given Abaqus input deck.
    This script assumes that the model is imported as an axisymmetric model (y-axis symmetry). The viewport is
    rotated 90 deg. about the the origin around the z-axis. The color map is set to color by material. Finally,
    viewport is set to fit the view to the viewport screen.

    :param str input_file: Abaqus input deck file
    :param str output_file: Output image file
    :param float xAngle: Rotation about X-axis in degrees for ``session.viewports[].view.rotate`` Abaqus Python method
    :param float yAngle: Rotation about Y-axis in degrees for ``session.viewports[].view.rotate`` Abaqus Python method
    :param float zAngle: Rotation about Z-axis in degrees for ``session.viewports[].view.rotate`` Abaqus Python method

    :returns: writes image to ``{output_file}``
    """
    model_name = os.path.splitext(os.path.basename(input_file))[0]  # Get input file name without extension
    mdb.ModelFromInputFile(name=model_name, inputFileName=input_file)
    session.viewports['Viewport: 1'].assemblyDisplay.setValues(
        optimizationTasks=ac.OFF, geometricRestrictions=ac.OFF, stopConditions=ac.OFF)
    a = mdb.models[model_name].rootAssembly
    session.viewports['Viewport: 1'].setValues(displayedObject=a)
    session.viewports['Viewport: 1'].view.rotate(xAngle=xAngle, yAngle=yAngle, zAngle=zAngle, mode=ac.MODEL)
    session.viewports['Viewport: 1'].view.fitView()
    session.viewports['Viewport: 1'].enableMultipleColors()
    session.viewports['Viewport: 1'].setColor(initialColor='#BDBDBD')
    cmap=session.viewports['Viewport: 1'].colorMappings['Material']
    session.viewports['Viewport: 1'].setColor(colorMapping=cmap)
    session.viewports['Viewport: 1'].disableMultipleColors()
    session.printOptions.setValues(vpDecorations=ac.OFF)
    session.pngOptions.setValues(imageSize=(2051, 922))  # This is the aspect ration I found works best for my model
    output_file_name, output_file_ext = os.path.splitext(output_file)  # Need name and extension for printToFile method
    session.printToFile(fileName=output_file_name, format=get_abaqus_image_constant(output_file_ext),
        canvasObjects=(session.viewports['Viewport: 1'], ))
    return


def get_abaqus_image_constant(file_extension):
    """
    Function for converting a string for an image file extension (e.g. ``.png``) to the corresponding
    ``abaqusConstants`` value.
    """
    switcher = {'.PNG': ac.PNG,
                '.SVG': ac.SVG}

    return switcher.get(file_extension.upper(), "")


def get_parser():
    file_name = inspect.getfile(lambda: None)
    base_name = os.path.basename(file_name)
    prog = "abaqus cae -noGui {} --".format(base_name)
    cli_description = "Export an image of an Abaqus model"
    parser = argparse.ArgumentParser(description=cli_description, prog=prog)
    parser.add_argument('-i', '--input-file', type=str, help='Abaqus input deck file')
    parser.add_argument('-o', '--output-file', type=str, help='Output image from the Abaqus viewport')
    parser.add_argument('--x-angle', type=float, default=0., help='Viewer rotation about X-axis')
    parser.add_argument('--y-angle', type=float, default=0., help='Viewer rotation about Y-axis')
    parser.add_argument('--z-angle', type=float, default=0., help='Viewer rotation about Z-axis')
    return parser


if __name__ == "__main__":
    parser = get_parser()
    args, unknown = parser.parse_known_args()
    sys.exit(main(
        input_file=args.input_file,
        output_file=args.output_file,
        xAngle=args.x_angle,
        yAngle=args.y_angle,
        zAngle=args.z_angle,
    ))

