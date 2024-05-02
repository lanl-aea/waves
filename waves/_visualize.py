"""Internal API module implementing the ``visualize`` subcommand behavior.

Should raise ``RuntimeError`` or a derived class of :class:`waves.exceptions.WAVESError` to allow the CLI implementation
to convert stack-trace/exceptions into STDERR message and non-zero exit codes.
"""
import subprocess
import argparse
import pathlib
import typing
import sys
import re

import networkx
import matplotlib.pyplot

from waves import _settings


_exclude_from_namespace = set(globals().keys())


def get_parser() -> argparse.ArgumentParser:
    """Return a 'no-help' parser for the visualize subcommand

    :return: parser
    """
    parser = argparse.ArgumentParser(add_help=False)

    parser.add_argument("TARGET", help=f"SCons target")
    parser.add_argument("--sconstruct", type=str, default="SConstruct",
        help="Path to SConstruct file (default: %(default)s)")
    parser.add_argument("-o", "--output-file", type=pathlib.Path,
        help="Path to output image file with an extension supported by matplotlib, e.g. 'visualization.svg' " \
             "(default: %(default)s)")
    parser.add_argument("--height", type=int, default=12,
        help="Height of visualization in inches if being saved to a file (default: %(default)s)")
    parser.add_argument("--width", type=int, default=36,
        help="Width of visualization in inches if being saved to a file (default: %(default)s)")
    parser.add_argument("--font-size", type=int, default=_settings._visualize_default_font_size,
        help="Font size of file names in points (default: %(default)s)")
    parser.add_argument("-e", "--exclude-list", nargs="*", default=_settings._visualize_exclude,
        help="If a node starts or ends with one of these string literals, do not visualize it (default: %(default)s)")
    parser.add_argument("-r", "--exclude-regex", type=str,
        help="If a node matches this regular expression, do not visualize it (default: %(default)s)")
    print_group = parser.add_mutually_exclusive_group()
    print_group.add_argument("-g", "--print-graphml", dest="print_graphml", action="store_true",
        help="Print the visualization in graphml format (default: %(default)s)")
    print_group.add_argument("--print-tree", action="store_true",
        help="Print the output of the scons tree command to the screen (default: %(default)s)")
    parser.add_argument("--vertical", action="store_true",
        help="Display the graph in a vertical layout (default: %(default)s)")
    parser.add_argument("-n", "--no-labels", action="store_true",
        help="Create visualization without labels on the nodes (default: %(default)s)")
    parser.add_argument("--input-file", type=str,
        help="Path to text file with output from scons tree command (default: %(default)s). Scons target must "
             "still be specified and must be present in the input file.")

    return parser


def main(
    target: str,
    sconstruct: typing.Union[str, pathlib.Path],
    exclude_list: typing.List[str],
    exclude_regex: str,
    output_file: typing.Optional[pathlib.Path] = None,
    print_graphml: bool = False,
    height: int = _settings._visualize_default_height,
    width: int = _settings._visualize_default_width,
    font_size: int = _settings._visualize_default_font_size,
    vertical: bool = False,
    no_labels: bool = False,
    print_tree: bool = False,
    input_file: typing.Union[str, pathlib.Path, None] = None
) -> None:
    """Visualize the directed acyclic graph created by a SCons build

    Uses matplotlib and networkx to build out an acyclic directed graph showing the relationships of the various
    dependencies using boxes and arrows. The visualization can be saved as an svg and graphml output can be printed
    as well.

    :param target: String specifying an SCons target
    :param sconstruct: Path to an SConstruct file or parent directory
    :param exclude_list: exclude nodes starting with strings in this list (e.g. /usr/bin)
    :param exclude_regex: exclude nodes that match this regular expression
    :param output_file: File for saving the visualization
    :param print_graphml: Whether to print the graph in graphml format
    :param height: Height of visualization if being saved to a file
    :param width: Width of visualization if being saved to a file
    :param font_size: Font size of node labels
    :param vertical: Specifies a vertical layout of graph instead of the default horizontal layout
    :param no_labels: Don't print labels on the nodes of the visualization
    :param print_tree: Print the text output of the scons --tree command to the screen
    :param input_file: Path to text file storing output from scons tree command
    """
    sconstruct = pathlib.Path(sconstruct).resolve()
    if not sconstruct.is_file():
        sconstruct = sconstruct / "SConstruct"
    if not sconstruct.exists() and not input_file:
        raise RuntimeError(f"\t{sconstruct} does not exist.")
    tree_output = ""
    if input_file:
        input_file = pathlib.Path(input_file)
        if not input_file.exists():
            raise RuntimeError(f"\t{input_file} does not exist.")
        else:
            tree_output = input_file.read_text()
    else:
        scons_command = [_settings._scons_command, target, f"--sconstruct={sconstruct.name}"]
        scons_command.extend(_settings._scons_visualize_arguments)
        scons_stdout = subprocess.check_output(scons_command, cwd=sconstruct.parent)
        tree_output = scons_stdout.decode("utf-8")
    if print_tree:
        print(tree_output, file=sys.stdout)
        return
    tree_dict = parse_output(tree_output.split('\n'), exclude_list=exclude_list, exclude_regex=exclude_regex)
    if not tree_dict['nodes']:  # If scons tree or input_file is not in the expected format the nodes will be empty
        raise RuntimeError(f"Unexpected SCons tree format or missing target. Use SCons "
                           f"options '{' '.join(_settings._scons_visualize_arguments)}' or "
                           f"the ``visualize --print-tree`` option to generate the input file.")

    if print_graphml:
        print(tree_dict['graphml'], file=sys.stdout)
        return
    visualize(tree_dict, output_file, height, width, font_size, vertical, no_labels)


def parse_output(tree_lines: typing.List[str], exclude_list: typing.List[str], exclude_regex: str) -> dict:
    """
    Parse the string that has the tree output and store it in a dictionary

    :param tree_lines: output of the scons tree command
    :param exclude_list: exclude nodes starting with strings in this list(e.g. /usr/bin)
    :param exclude_regex: exclude nodes that match this regular expression

    :returns: dictionary of tree output
    """
    edges = list()  # List of tuples for storing all connections
    node_info: typing.Dict[str, typing.Dict] = dict()
    node_number = 0
    nodes = list()
    higher_nodes = dict()
    graphml_nodes = ''
    graphml_edges = ''
    exclude_node = False
    exclude_indent = 0
    for line in tree_lines:
        line_match = re.match(r'^\[(.*)\](.*)\+-(.*)', line)
        if line_match:
            status = [_settings._scons_tree_status[_] for _ in line_match.group(1) if _.strip()]
            placement = line_match.group(2)
            node_name = line_match.group(3)
            current_indent = int(len(placement) / 2) + 1
            if current_indent <= exclude_indent and exclude_node:
                exclude_node = False
            if exclude_node:
                continue
            for exclude in exclude_list:
                if node_name.startswith(exclude) or node_name.endswith(exclude):
                    exclude_node = True
                    exclude_indent = current_indent
            exclude_node, exclude_indent = check_regex_exclude(exclude_regex, node_name, current_indent,
                                                               exclude_indent, exclude_node)
            if exclude_node:
                continue
            node_number += 1  # Increment the node_number
            if node_name not in nodes:
                nodes.append(node_name)
                graphml_nodes += f'    <node id="{node_name}"><data key="label">{node_name}</data></node>\n'
                node_info[node_name] = dict()
            higher_nodes[current_indent] = node_name

            if current_indent != 1:  # If it's not the first node which is the top level node
                higher_node = higher_nodes[current_indent - 1]
                edges.append((higher_node, node_name))
                graphml_edges += f'    <edge source="{higher_node}" target="{node_name}"/>\n'
            node_info[node_name]['status'] = status

    tree_dict: typing.Dict[str, typing.Any] = dict()
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


def check_regex_exclude(exclude_regex: str, node_name: str, current_indent: int, exclude_indent: int,
                        exclude_node: bool = False) -> typing.Tuple[bool, int]:
    """
    Excludes node names that match the regular expression

    :param str exclude_regex: Regular expression
    :param str node_name: Name of the node
    :param int current_indent: Current indent of the parsed output
    :param int exclude_indent: Set to current_indent if node is to be excluded
    :param bool exclude_node: Indicated whether a node should be excluded

    :returns: Tuple containing exclude_node and exclude_indent
    """
    if exclude_regex and re.search(exclude_regex, node_name):
        exclude_node = True
        exclude_indent = current_indent
    return exclude_node, exclude_indent


def click_arrow(event, annotations: dict, arrows: dict) -> None:
    """
    Create effect with arrows when mouse click

    :param matplotlib.backend_bases.Event event: Event that is handled by this function
    :param annotations: Dictionary linking node names to their annotations
    :param arrows: Dictionary linking darker arrow annotations to node names
    """
    fig = matplotlib.pyplot.gcf()
    ax = matplotlib.pyplot.gca()
    for key in annotations.keys():
        if annotations[key].contains(event)[0]:  # If the text annotation contains the event (i.e. is clicked on)
            for to_arrow in arrows[key]['to']:
                if to_arrow:
                    if to_arrow.get_visible():
                        to_arrow.set_visible(False)
                    else:
                        to_arrow.set_visible(True)
                    fig.canvas.draw_idle()
            for from_arrow in arrows[key]['from']:
                if from_arrow:
                    if from_arrow.get_visible():
                        from_arrow.set_visible(False)
                    else:
                        from_arrow.set_visible(True)
                    fig.canvas.draw_idle()


def visualize(
    tree: dict,
    output_file: typing.Optional[pathlib.Path] = None,
    height: int = _settings._visualize_default_height,
    width: int = _settings._visualize_default_width,
    font_size: int = _settings._visualize_default_font_size,
    vertical: bool = False,
    no_labels: bool = False
) -> None:
    """Create a visualization showing the tree

    :param tree: output of the scons tree command stored as dictionary
    :param output_file: Name of file to store visualization
    :param height: Height of visualization if being saved to a file
    :param width: Width of visualization if being saved to a file
    :param font_size: Font size of file names in points
    :param vertical: Specifies a vertical layout of graph instead of the default horizontal layout
    :param no_labels: Don't print labels on the nodes of the visualization
    """
    graph = networkx.DiGraph()
    graph.add_nodes_from(tree['nodes'])
    graph.add_edges_from(tree['edges'])

    for layer, nodes in enumerate(networkx.topological_generations(graph)):
        # `multipartite_layout` expects the layer as a node attribute, so it's added here
        for node in nodes:
            graph.nodes[node]["layer"] = layer
    if vertical:
        pos = networkx.multipartite_layout(graph, subset_key="layer", align="horizontal")
        for k in pos:  # Flip the layout so the root node is on top
            pos[k][-1] *= -1
    else:
        pos = networkx.multipartite_layout(graph, subset_key="layer")
    # The nodes are drawn tiny so that labels can go on top
    collection = networkx.draw_networkx_nodes(graph, pos=pos, node_size=0)
    figure = collection.get_figure()
    figure.axes[0].axis("off")

    box_color = '#5AC7CB'  # Light blue from Waves Logo
    arrow_color = '#B7DEBE'  # Light green from Waves Logo
    # TODO: separate plot construction from output for easier unit testing
    annotations: typing.Dict[str, typing.Any] = dict()
    arrows: typing.Dict[str, typing.Dict] = dict()
    for A, B in graph.edges:  # Arrows and labels are written on top of existing nodes, which are laid out by networkx
        label_A = A
        label_B = B
        if no_labels:
            label_A = " "
            label_B = " "
        patchA = ax.annotate(label_A, xy=pos[A], xycoords='data', ha='center', va='center', size=font_size,
                             bbox=dict(facecolor=box_color, boxstyle='round'))
        patchB = ax.annotate(label_B, xy=pos[B], xycoords='data', ha='center', va='center', size=font_size,
                             bbox=dict(facecolor=box_color, boxstyle='round'))
        arrowprops = dict(
            arrowstyle="<-", color=arrow_color, connectionstyle='arc3,rad=0.1', patchA=patchA, patchB=patchB)
        ax.annotate("", xy=pos[B], xycoords='data', xytext=pos[A], textcoords='data', arrowprops=arrowprops)

        annotations[A] = patchA
        annotations[B] = patchB
        dark_props = dict(arrowstyle="<-", color="0.0", connectionstyle='arc3,rad=0.1', patchA=patchA, patchB=patchB)
        dark_arrow = ax.annotate("", xy=pos[B], xycoords='data', xytext=pos[A], textcoords='data',
                                 arrowprops=dark_props)
        dark_arrow.set_visible(False)  # Draw simultaneous darker arrow, but don't show it
        try:
            arrows[A]['from'].append(dark_arrow)
        except KeyError:
            arrows[A] = dict()
            arrows[A]['from'] = list()
            arrows[A]['to'] = list()
            arrows[A]['from'].append(dark_arrow)
        try:
            arrows[B]['to'].append(dark_arrow)
        except KeyError:
            arrows[B] = dict()
            arrows[B]['from'] = list()
            arrows[B]['to'] = list()
            arrows[B]['to'].append(dark_arrow)

    fig.canvas.mpl_connect("button_press_event", lambda x: click_arrow(x, annotations, arrows))

    if output_file is not None:
        file_name = output_file
        file_name.parent.mkdir(parents=True, exist_ok=True)
        suffix = output_file.suffix
        if not suffix or suffix[1:] not in list(fig.canvas.get_supported_filetypes().keys()):
            # If there is no suffix or it's not supported by matplotlib, use svg
            file_name = file_name.with_suffix('.svg')
            print(f"WARNING: extension '{suffix}' is not supported by matplotlib. Falling back to '{file_name}'",
                  file=sys.stderr)
        fig = matplotlib.pyplot.gcf()
        fig.set_size_inches((width, height), forward=False)
        fig.savefig(str(file_name))
    else:
        matplotlib.pyplot.show()
    matplotlib.pyplot.clf()  # Indicates that we are done with the plot


# Limit help() and 'from module import *' behavior to the module's public API
_module_objects = set(globals().keys()) - _exclude_from_namespace
__all__ = [name for name in _module_objects if not name.startswith("_")]
