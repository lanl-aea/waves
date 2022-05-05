import sys
import os
import argparse
import inspect
import shutil
import re

import abaqus
import abaqusConstants
import mesh

def export_mesh(model_object, part_name, orphan_mesh_file):
    """Export an orphan mesh for the specified part instance in an Abaqus model

    Using an abaqus model object (``model_object = abaqus.mdb.models[model_name]``) with part(s) that are meshed and
    instanced in an assembly, get the "\*.inp" keyword blocks and save an orphan mesh file, ``orphan_mesh_file``.inp, for
    the specific ``part_name``.

    :param abaqus.mdb.models[model_name] model_object: Abaqus model object
    :param str part_name: Part name to export as an orphan mesh
    :param str orphan_mesh_file: File name to write for the orphan mesh without extension, e.g. ``orphan_mesh_file``.inp

    :returns: writes ``orphan_mesh_file``.inp
    """
    model_object.keywordBlock.synchVersions()
    block = model_object.keywordBlock.sieBlocks
    block_string = '\n'.join(block)
    orphan_mesh = re.findall(".*?\*Part, name=({})$\n(.*?)\*End Part".format(part_name), block_string, re.DOTALL | re.I | re.M)
    part_definition = orphan_mesh[0]
    with open('{}.inp'.format(orphan_mesh_file), 'w') as output:
        output.write(part_definition[1].strip())

def main(input_file, output_file, model_name, part_name, global_seed):
    """Mesh the simple square geometry partitioned by single_element_partition.py

    This script meshes a simple Abaqus model with a single square part.

    **Usage:**

    .. code-block::

       abaqus cae -noGUI single_element_mesh.py
       abaqus cae -noGUI single_element_mesh.py -- [options]
       abaqus cae -noGUI single_element_mesh.py -- --output-file single_element_partition.cae
       abaqus cae -noGUI single_element_mesh.py -- --part-name single_element.cae

    **Node sets:**

    * ALLNODES - all part nodes

    **Element sets:**

    * ELEMENTS - all part elements

    :param str input_file: The Abaqus model file created by single_element_partition.py without extension, e.g.
        ``input_file``.cae
    :param str output_file: The output file for the Abaqus model without extension, e.g. ``output_file``.cae
    :param str model_name: The name of the Abaqus model
    :param str part_name: The name of the Abaqus part
    :param float global_seed: The global mesh seed size

    :returns: ``output_file``.cae, ``output_file``.inp
    """

    input_with_extension = '{}.cae'.format(input_file)
    output_with_extension = '{}.cae'.format(output_file)

    # Avoid modifying the contents or timestamp on the input file.
    # Required to get conditional re-builds with a build system such as GNU Make, CMake, or SCons
    shutil.copyfile(input_with_extension, output_with_extension)

    abaqus.openMdb(pathName=output_with_extension)

    p = abaqus.mdb.models[model_name].parts[part_name]
    a = abaqus.mdb.models[model_name].rootAssembly
    a.Instance(name=part_name, part=p, dependent=abaqusConstants.ON)

    p.seedPart(size=global_seed, deviationFactor=0.1, minSizeFactor=0.1)
    p.generateMesh()

    elemType1 = mesh.ElemType(elemCode=abaqusConstants.CPE4, elemLibrary=abaqusConstants.STANDARD)
    elemType2 = mesh.ElemType(elemCode=abaqusConstants.CPE3, elemLibrary=abaqusConstants.STANDARD)

    f = p.faces
    s = p.edges
    faces = f[:]

    pickedRegions = (faces, )

    p.setElementType(regions=pickedRegions, elemTypes=(elemType1, elemType2))
    p.Set(faces=faces, name='ELEMENTS')
    p.Set(faces=faces, name='ALLNODES')

    model_object = abaqus.mdb.models[model_name]
    export_mesh(model_object, part_name, output_file)

    abaqus.mdb.save()

if __name__ == '__main__':
    # The global '__file__' variable doesn't appear to be set when executing from Abaqus CAE
    filename = inspect.getfile(lambda: None)
    basename = os.path.basename(filename)
    basename_without_extension, extension = os.path.splitext(basename)
    # Construct a part name from the filename less the workflow step
    default_part_name = basename_without_extension
    suffix = '_mesh'
    if default_part_name.endswith(suffix):
        default_part_name = default_part_name[:-len(suffix)]
    # Set default parameter values
    default_input_file = '{}_partition'.format(default_part_name)
    default_output_file = '{}'.format(basename_without_extension)
    default_global_seed = 1.0

    parser = argparse.ArgumentParser(description="Mesh a simple square geometry",
                                     prog=os.path.basename(filename))
    parser.add_argument('-i', '--input-file', type=str, default=default_input_file,
                        help="input file name")
    parser.add_argument('-o', '--output-file', type=str, default=default_output_file,
                        help="output file name")
    parser.add_argument('-m', '--model-name', type=str, default=default_part_name,
                        help="model name")
    parser.add_argument('-p', '--part-name', type=str, default=default_part_name,
                        help="part name")
    parser.add_argument('-g', '--global-seed', type=float, default=default_global_seed,
                        help="global mesh seed size")

    # Abaqus does not strip the CAE options, so we have to skip the unknown options related to the CAE CLI.
    args, unknown = parser.parse_known_args()

    sys.exit(main(input_file=args.input_file,
                  output_file=args.output_file,
                  model_name=args.model_name,
                  part_name=args.part_name,
                  global_seed=args.global_seed))
