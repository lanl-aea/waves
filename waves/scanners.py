import re

import SCons.Scanner


def implicit_dependency_scanner():
    return custom_scanner('^\*INCLUDE,\s*input=(.+)$', ['.inp'])


def custom_scanner(pattern, suffixes):
    inp_pattern = re.compile(rf'{pattern}', re.M | re.I)

    def inp_scan(node, env, path):
        contents = node.get_text_contents()
        includes = inp_pattern.findall(contents)
        return includes

    def inp_only(node_list):

        return [node for node in node_list if node.path.endswith(tuple(suffixes))]

    inp_scanner = SCons.Scanner(function=inp_scan, skeys=suffixes, recursive=inp_only)
    return inp_scanner
