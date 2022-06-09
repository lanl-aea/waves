import re

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
