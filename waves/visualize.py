import os
import pathlib
import sys
import re
import networkx
import matplotlib
import matplotlib.pyplot as plt

from waves import _settings

def parse_output(tree_lines):
    """
    Parse the string that has the tree output and store it in a dictionary

    :param list tree_lines: output of the scons tree command
    :returns: dictionary of tree output
    :rtype: dict
    """
    edges = list()  # List of tuples for storing all connections
    node_info = dict()
    depth = dict()
    last_indent = 0
    parent_indent = 0
    node_number = 0
    nodes = list()
    higher_nodes = dict()
    graphml_nodes = ''
    graphml_edges = ''
    for line in tree_lines:
        line_match = re.match(r'^\[(.*)\](.*)\+-(.*)', line)
        if line_match:
            status = [_settings._scons_tree_status[_] for _ in line_match.group(1) if _.strip()]
            placement = line_match.group(2)
            node_name = line_match.group(3)
            current_indent = int(len(placement) / 2) + 1
            if node_name.startswith('/usr/bin'):  # Skip any system dependencies like /usr/bin/cd
                last_indent = current_indent
                continue
            node_number += 1  # Increment the node_number
            if node_name not in nodes:
                nodes.append(node_name)
                graphml_nodes += f'    <node id="{node_name}"><data key="label">{node_name}</data></node>\n'
                node_info[node_name] = dict()
            higher_nodes[current_indent] = node_name

            if current_indent == 1:  # Case for top level indentation
                depth[current_indent] = f"['{node_name}']"
            elif current_indent == last_indent:  # At same level
                depth[current_indent] = f"{depth[parent_indent]}['{node_name}']"
            elif current_indent > last_indent:  # Gone down a level
                parent_indent = last_indent
                depth[current_indent] = f"{depth[parent_indent]}['{node_name}']"
            elif current_indent < last_indent:  # Gone up a level
                parent_indent = current_indent - 1
                depth[current_indent] = f"{depth[parent_indent]}['{node_name}']"

            if current_indent != 1:  # If it's not the first node which is the top level node
                higher_node = higher_nodes[current_indent - 1]
                edges.append((higher_node, node_name))
                graphml_edges += f'    <edge source="{higher_node}" target="{node_name}"/>\n'
            node_info[node_name]['status'] = status
            last_indent = current_indent

    tree_dict = dict()
    tree_dict['nodes'] = nodes
    tree_dict['edges'] = edges
    tree_dict['node_info'] = node_info

    tree_dict['graphml'] = '''<?xml version = "1.0" encoding = "UTF-8"?>
      <graphml xmlns="http://graphml.graphdrawing.org/xmlns"
      xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
      xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns
      http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd ">
      <graph id = "tree" edgedefault = "directed">
    '''
    tree_dict['graphml'] += graphml_nodes
    tree_dict['graphml'] += graphml_edges
    tree_dict['graphml'] += '  </graph>\n</graphml>\n'

    return tree_dict
