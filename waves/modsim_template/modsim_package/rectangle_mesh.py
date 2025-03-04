import os
import sys
import shutil
import inspect
import argparse

import abaqus
import abaqusConstants
import mesh

import modsim_package.abaqus_utilities
from modsim_package.argparse_types import positive_float


def main(input_file, output_file, model_name, part_name, global_seed):
    """Mesh the simple rectangle geometry partitioned by ``rectangle_partition.py``

    This script meshes a simple Abaqus model with a single rectangle part.

    **Feature labels:**

    * ``NODES`` - all part nodes
    * ``ELEMENTS`` - all part elements

    :param str input_file: The Abaqus model file created by ``rectangle_partition.py``. Will be stripped of the
        extension and ``.cae`` will be used.
    :param str output_file: The output file for the Abaqus model. Will be stripped of the extension and ``.cae`` and
        ``.inp`` will be used for the model and orphan mesh output files, respectively.
    :param str model_name: The name of the Abaqus model
    :param str part_name: The name of the Abaqus part
    :param float global_seed: The global mesh seed size

    :returns: ``output_file``.cae, ``output_file``.jnl, ``output_file``.inp
    """
    input_file = os.path.splitext(input_file)[0] + ".cae"
    output_file = os.path.splitext(output_file)[0] + ".cae"

    # Avoid modifying the contents or timestamp on the input file.
    # Required to get conditional re-builds with a build system such as GNU Make, CMake, or SCons
    if input_file != output_file:
        shutil.copyfile(input_file, output_file)

    abaqus.openMdb(pathName=output_file)

    part = abaqus.mdb.models[model_name].parts[part_name]
    assembly = abaqus.mdb.models[model_name].rootAssembly
    assembly.Instance(name=part_name, part=part, dependent=abaqusConstants.ON)

    part.seedPart(size=global_seed, deviationFactor=0.1, minSizeFactor=0.1)
    part.generateMesh()

    elemType1 = mesh.ElemType(elemCode=abaqusConstants.CPS4R, elemLibrary=abaqusConstants.STANDARD)

    faces = part.faces
    pickedRegions = (faces,)

    part.setElementType(regions=pickedRegions, elemTypes=(elemType1,))
    part.Set(faces=faces, name="ELEMENTS")
    part.Set(faces=faces, name="NODES")

    model_object = abaqus.mdb.models[model_name]
    modsim_package.abaqus_utilities.export_mesh(model_object, part_name, output_file)

    abaqus.mdb.save()


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
    # Construct a part name from the filename less the workflow step
    default_part_name = basename_without_extension
    suffix = "_mesh"
    if default_part_name.endswith(suffix):
        default_part_name = default_part_name[: -len(suffix)]
    # Set default parameter values
    default_input_file = "{}_partition".format(default_part_name)
    default_output_file = "{}".format(basename_without_extension)
    default_global_seed = 1.0

    prog = "abaqus cae -noGui {} --".format(basename)
    cli_description = (
        "Mesh the simple rectangle geometry partitioned by ``rectangle_partition.py`` "
        "and write an ``output_file``.cae Abaqus model file and ``output_file``.inp orphan mesh file."
    )
    parser = argparse.ArgumentParser(description=cli_description, prog=prog)
    parser.add_argument(
        "--input-file",
        type=str,
        default=default_input_file,
        # fmt: off
        help="The Abaqus model file created by ``rectangle_partition.py``. "
             "Will be stripped of the extension and ``.cae`` will be used, e.g. ``input_file``.cae",
        # fmt: on
    )
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
        "--global-seed",
        type=positive_float,
        default=default_global_seed,
        help="The global mesh seed size. Positive float.",
    )
    return parser


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
            input_file=args.input_file,
            output_file=args.output_file,
            model_name=args.model_name,
            part_name=args.part_name,
            global_seed=args.global_seed,
        )
    )
