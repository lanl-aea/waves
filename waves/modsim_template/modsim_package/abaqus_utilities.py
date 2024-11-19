"""Abaqus utilities to be re-used in multiple places"""

import os
import re
import shutil
import tempfile

import abaqus
import abaqusConstants


def export_mesh(model_object, part_name, orphan_mesh_file):
    """Export an orphan mesh for the specified part instance in an Abaqus model

    Using an abaqus model object (``model_object = abaqus.mdb.models[model_name]``) with part(s) that are meshed and
    instanced in an assembly, get the ``*.inp`` keyword blocks and save an orphan mesh file, ``orphan_mesh_file``.inp,
    for the specific ``part_name``.

    :param abaqus.mdb.models[model_name] model_object: Abaqus model object
    :param str part_name: Part name to export as an orphan mesh
    :param str orphan_mesh_file: File name to write for the orphan mesh. Will be stripped of the extension and ``.cae``
        will be used, e.g. ``orphan_mesh_file``.inp

    :returns: writes ``orphan_mesh_file``.inp
    """
    orphan_mesh_file = os.path.splitext(orphan_mesh_file)[0] + ".inp"
    model_object.keywordBlock.synchVersions()
    block = model_object.keywordBlock.sieBlocks
    block_string = "\n".join(block)
    orphan_mesh = re.findall(
        r".*?\*Part, name=({})$\n(.*?)\*End Part".format(part_name), block_string, re.DOTALL | re.I | re.M
    )
    part_definition = orphan_mesh[0]
    with open(orphan_mesh_file, "w") as output:
        output.write(part_definition[1].strip())


def return_abaqus_constant(search):
    """If search is found in the abaqusConstants module, return the abaqusConstants object.

    :param str search: string to search in the abaqusConstants module attributes

    :return value: abaqusConstants attribute
    :rtype: abaqusConstants.<search>

    :raises ValueError: If the search string is not found.
    """
    search = search.upper()
    if hasattr(abaqusConstants, search):
        attribute = getattr(abaqusConstants, search)
    else:
        raise ValueError("The abaqusConstants module does not have a matching '{}' object".format(search))
    return attribute


class AbaqusNamedTemporaryFile:
    """Open an Abaqus CAE ``input_file`` as a temporary file. Close and delete on exit of context manager.

    Provides Windows compatible temporary file handling. Required until Python 3.12 ``delete_on_close=False`` option is
    available in Abaqus Python.

    :param str input_file: The input file to copy before open
    """

    def __init__(self, input_file, *args, **kwargs):
        self.temporary_file = tempfile.NamedTemporaryFile(*args, delete=False, **kwargs)
        shutil.copyfile(input_file, self.temporary_file.name)
        abaqus.openMdb(pathName=self.temporary_file.name)

    def __enter__(self):
        return self.temporary_file

    def __exit__(self, exc_type, exc_val, exc_tb):
        abaqus.mdb.close()
        self.temporary_file.close()
        os.remove(self.temporary_file.name)
