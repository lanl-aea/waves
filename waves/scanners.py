import re

import SCons.Scanner


def abaqus_implicit_scanner():
    """Abaqus implicit dependency scanner

    Custom Scons scanner that searches for ``INCLUDE`` keyword inside of ``.inp`` files.

    :return: Abaqus implicit dependency Scanner
    :rtype: Scons.Scanner.Scanner
    """
    return custom_scanner('^\*INCLUDE,\s*input=(.+)$', ['.inp'])


def custom_scanner(pattern, suffixes):
    """Custom Scons scanner

    constructs a scanner object based on a regular expression pattern. Will only search for files matching the list of
    suffixes provided.

    :param str pattern: Regular expression pattern.
    :param list suffixes: List of suffixes of files to search

    :return: Custom Scons scanner
    :rtype: Scons.Scanner.Scanner
    """
    inp_pattern = re.compile(rf'{pattern}', re.M | re.I)

    def inp_scan(node, env, path):
        contents = node.get_text_contents()
        includes = inp_pattern.findall(contents)
        return includes

    def inp_only(node_list):

        return [node for node in node_list if node.path.endswith(tuple(suffixes))]

    inp_scanner = SCons.Scanner.Scanner(function=inp_scan, skeys=suffixes, recursive=inp_only)
    return inp_scanner
