"""Internal API module implementing the ``visualize`` subcommand behavior.

Should raise ``RuntimeError`` or a derived class of :class:`waves.exceptions.WAVESError` to allow the CLI implementation
to convert stack-trace/exceptions into STDERR message and non-zero exit codes.
"""

import io
import os
import re
import sys
import typing
import pathlib
import argparse
import subprocess

import networkx
import matplotlib.pyplot

from waves import _settings


_exclude_from_namespace = set(globals().keys())


def get_parser() -> argparse.ArgumentParser:
    """Return a 'no-help' parser for the visualize subcommand

    :return: parser
    """
    parser = argparse.ArgumentParser(add_help=False)

    parser.add_argument(
        "TARGET",
        nargs="+",
        help=f"SCons target(s)",
    )

    parser.add_argument(
        "-o",
        "--output-file",
        type=pathlib.Path,
        # fmt: off
        help="Path to output image file with an extension supported by matplotlib, e.g. 'visualization.svg' "
             "(default: %(default)s)",
        # fmt: on
    )
    parser.add_argument(
        "--sconstruct",
        type=pathlib.Path,
        default=_settings._default_sconstruct,
        help="Path to SConstruct file (default: %(default)s)",
    )
    parser.add_argument(
        "--input-file",
        type=str,
        help="Path to text file with output from SCons tree command (default: %(default)s)",
    )

    graph_options = parser.add_argument_group("graph options", "graph options affect plotting and graphml output")
    graph_options.add_argument(
        "-e",
        "--exclude-list",
        nargs="*",
        default=_settings._visualize_exclude,
        help="If a node starts or ends with one of these string literals, do not visualize it (default: %(default)s)",
    )
    graph_options.add_argument(
        "-r",
        "--exclude-regex",
        type=str,
        help="If a node matches this regular expression, do not visualize it (default: %(default)s)",
    )
    graph_options.add_argument(
        "-n",
        "--no-labels",
        action="store_true",
        help="Create visualization without labels on the nodes (default: %(default)s)",
    )
    graph_options.add_argument(
        "-c",
        "--node-count",
        action="store_true",
        help="Add the node count as an node with no edges (default: %(default)s)",
    )

    plot_options = parser.add_argument_group("plot options", "plot options affect the output figure")
    plot_options.add_argument(
        "--height",
        type=int,
        default=_settings._visualize_default_height,
        help="Height of visualization in inches if being saved to a file (default: %(default)s)",
    )
    plot_options.add_argument(
        "--width",
        type=int,
        default=_settings._visualize_default_width,
        help="Width of visualization in inches if being saved to a file (default: %(default)s)",
    )
    plot_options.add_argument(
        "--font-size",
        type=int,
        default=_settings._visualize_default_font_size,
        help="Font size of file names in points (default: %(default)s)",
    )
    plot_options.add_argument(
        "--node-color",
        type=str,
        default=_settings._default_node_color,
        help="Node face color (default: %(default)s)",
    )
    plot_options.add_argument(
        "--edge-color",
        type=str,
        default=_settings._default_edge_color,
        help="Edge (arrow) color (default: %(default)s)",
    )
    plot_options.add_argument(
        "--vertical",
        action="store_true",
        help="Display the graph in a vertical layout (default: %(default)s)",
    )
    plot_options.add_argument(
        "--transparent",
        action="store_true",
        help="Use a transparent background. Requires a format that supports transparency (default: %(default)s)",
    )
    plot_options.add_argument(
        "--break-paths",
        action="store_true",
        help="Format paths by breaking at path separator with a newline (default: %(default)s)",
    )

    print_group = parser.add_mutually_exclusive_group()
    print_group.add_argument(
        "-g",
        "--print-graphml",
        dest="print_graphml",
        action="store_true",
        help="Print the visualization in graphml format and exit (default: %(default)s)",
    )
    print_group.add_argument(
        "--print-tree",
        action="store_true",
        help="Print the output of the SCons tree command to the screen and exit (default: %(default)s)",
    )

    return parser


def main(
    targets: typing.List[str],
    scons_args: typing.Optional[list] = None,
    sconstruct: pathlib.Path = _settings._default_sconstruct,
    output_file: typing.Optional[pathlib.Path] = None,
    height: int = _settings._visualize_default_height,
    width: int = _settings._visualize_default_width,
    font_size: int = _settings._visualize_default_font_size,
    node_color: str = _settings._default_node_color,
    edge_color: str = _settings._default_edge_color,
    exclude_list: typing.List[str] = _settings._visualize_exclude,
    exclude_regex: typing.Optional[str] = None,
    print_graphml: bool = False,
    print_tree: bool = False,
    vertical: bool = False,
    no_labels: bool = False,
    node_count: bool = False,
    transparent: bool = False,
    break_paths: bool = False,
    input_file: typing.Union[str, pathlib.Path, None] = None,
) -> None:
    """Visualize the directed acyclic graph created by a SCons build

    Uses matplotlib and networkx to build out an acyclic directed graph showing the relationships of the various
    dependencies using boxes and arrows. The visualization can be saved as an svg and graphml output can be printed
    as well.

    :param targets: Strings specifying SCons targets
    :param scons_args: list of SCons arguments
    :param sconstruct: Path to an SConstruct file or parent directory
    :param output_file: File for saving the visualization
    :param height: Height of visualization if being saved to a file
    :param width: Width of visualization if being saved to a file
    :param font_size: Font size of node labels
    :param exclude_list: exclude nodes starting with strings in this list (e.g. /usr/bin)
    :param exclude_regex: exclude nodes that match this regular expression
    :param print_graphml: Whether to print the graph in graphml format
    :param print_tree: Print the text output of the ``scons --tree`` command to the screen
    :param vertical: Specifies a vertical layout of graph instead of the default horizontal layout
    :param no_labels: Don't print labels on the nodes of the visualization
    :param node_count: Add a node count orphan node
    :param transparent: Use a transparent background
    :param break_paths: Format paths by breaking at path separator with a newline
    :param input_file: Path to text file storing output from SCons tree command
    """
    if not scons_args:
        scons_args = []

    # Source file handling
    sconstruct = pathlib.Path(sconstruct).resolve()
    if not sconstruct.is_file():
        sconstruct = sconstruct / "SConstruct"
    if not sconstruct.exists() and not input_file:
        raise RuntimeError(f"\t{sconstruct} does not exist.")

    # Generate or read the SCons tree text
    tree_output = ""
    if input_file:
        input_file = pathlib.Path(input_file)
        if not input_file.exists():
            raise RuntimeError(f"\t{input_file} does not exist.")
        else:
            tree_output = input_file.read_text()
    else:
        scons_command = [_settings._scons_command] + targets + [f"--sconstruct={sconstruct.name}"]
        scons_command.extend(scons_args)
        scons_command.extend(_settings._scons_visualize_arguments)
        scons_stdout = subprocess.check_output(scons_command, cwd=sconstruct.parent)
        tree_output = scons_stdout.decode("utf-8")

    # Command output
    if print_tree:
        print(tree_output, file=sys.stdout)
        return

    # Create the target selected subgraph
    # TODO: Wrap all graph handling into a parent function for unit testing
    # https://re-git.lanl.gov/aea/python-projects/waves/-/issues/677
    graph = parse_output(
        tree_output.splitlines(),
        exclude_list=exclude_list,
        exclude_regex=exclude_regex,
        no_labels=no_labels,
        break_paths=break_paths,
    )
    subgraph = ancestor_subgraph(graph, targets)
    if node_count:
        subgraph = add_node_count(subgraph)

    # Command output
    if print_graphml:
        print(graph_to_graphml(subgraph))
        return
    figure = visualize(
        subgraph,
        height=height,
        width=width,
        font_size=font_size,
        node_color=node_color,
        edge_color=edge_color,
        vertical=vertical,
    )
    plot(figure, output_file=output_file, transparent=transparent)


def ancestor_subgraph(
    graph: networkx.DiGraph,
    nodes: typing.Iterable[str],
) -> networkx.DiGraph:
    """Return a new directed graph containing nodes and their ancestors

    :param graph: original directed graph
    :param nodes: iterable of nodes name strings

    :returns: subgraph

    :raises RuntimeError: If one or more nodes are missing from the graph
    """
    sources = set(nodes)
    missing = list()
    for node in nodes:
        try:
            sources = sources.union(networkx.ancestors(graph, node))
        except networkx.NetworkXError as err:
            missing.append(node)

    if missing:
        raise RuntimeError(f"Nodes '{' '.join(missing)}' not found in the graph")

    return networkx.DiGraph(graph.subgraph(sources))


def add_node_count(graph: networkx.DiGraph, text: str = "Node count: ") -> networkx.DiGraph:
    """Add an orphan node with the total node count to a directed graph

    The graph nodes must contain a ``layer`` attribute with integer values. Orphan node is assigned to the minimum
    layer.

    :param graph: original graph
    :param text: Leading text for node name and label
    """
    number_of_nodes = graph.number_of_nodes()
    label = f"{text}{number_of_nodes}"
    layer = min(graph.nodes[node]["layer"] for node in graph.nodes)
    graph.add_node(label, label=label, layer=layer)
    return graph


def graph_to_graphml(graph: networkx.DiGraph) -> str:
    """Return the networkx graphml text

    :param graph: networkx directed graph
    """
    with io.BytesIO() as graphml_buffer:
        networkx.write_graphml_lxml(graph, graphml_buffer)
        graphml = graphml_buffer.getvalue().decode("utf-8")
    return graphml


def parse_output(
    tree_lines: typing.List[str],
    exclude_list: typing.List[str] = _settings._visualize_exclude,
    exclude_regex: typing.Optional[str] = None,
    no_labels: bool = False,
    break_paths: bool = False,
) -> networkx.DiGraph:
    """Parse the string that has the tree output and return as a networkx directed graph

    :param tree_lines: output of the scons tree command pre-split on newlines to a list of strings
    :param exclude_list: exclude nodes starting with strings in this list(e.g. /usr/bin)
    :param exclude_regex: exclude nodes that match this regular expression
    :param no_labels: Don't print labels on the nodes of the visualization
    :param break_paths: Format paths by breaking at path separator with a newline

    :returns: networkx directed graph

    :raises RuntimeError: If the parsed input doesn't contain recognizable SCons nodes
    """
    graph = networkx.DiGraph()
    higher_nodes = dict()
    exclude_node = False
    exclude_indent = 0
    for line in tree_lines:
        line_match = re.match(r"^\[(.*)\](.*)\+-(.*)", line)
        if line_match:
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
            exclude_node, exclude_indent = check_regex_exclude(
                exclude_regex, node_name, current_indent, exclude_indent, exclude_node
            )
            if exclude_node:
                continue

            if no_labels:
                label = " "
            elif break_paths:
                label = f"{os.path.sep}\n".join(node_name.split(os.path.sep))
            else:
                label = node_name

            if node_name not in graph.nodes:
                graph.add_node(node_name, label=label)
            higher_nodes[current_indent] = node_name

            if current_indent != 1:  # If it's not the first node which is the top level node
                higher_node = higher_nodes[current_indent - 1]
                graph.add_edge(node_name, higher_node)

    for layer, nodes in enumerate(networkx.topological_generations(graph)):
        for node in nodes:
            graph.nodes[node]["layer"] = layer * -1

    # If SCons tree or input_file is not in the expected format the nodes will be empty
    number_of_nodes = graph.number_of_nodes()
    if number_of_nodes <= 0:
        raise RuntimeError(
            f"Unexpected SCons tree format. Use SCons options '{' '.join(_settings._scons_visualize_arguments)}' or "
            "the ``visualize --print-tree`` option to generate the input file."
        )

    return graph


def check_regex_exclude(
    exclude_regex: str,
    node_name: str,
    current_indent: int,
    exclude_indent: int,
    exclude_node: bool = False,
) -> typing.Tuple[bool, int]:
    """Excludes node names that match the regular expression

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


def visualize(
    graph: networkx.DiGraph,
    height: int = _settings._visualize_default_height,
    width: int = _settings._visualize_default_width,
    font_size: int = _settings._visualize_default_font_size,
    node_color: str = _settings._default_node_color,
    edge_color: str = _settings._default_edge_color,
    vertical: bool = False,
) -> matplotlib.figure.Figure:
    """Create a visualization showing the tree

    Nodes in graph require the ``layer`` and ``label`` attributes.

    :param tree: output of the scons tree command stored as dictionary
    :param height: Height of visualization if being saved to a file
    :param width: Width of visualization if being saved to a file
    :param font_size: Font size of file names in points
    :param vertical: Specifies a vertical layout of graph instead of the default horizontal layout
    """
    multipartite_kwargs = dict(align="vertical")
    if vertical:
        multipartite_kwargs.update({"align": "horizontal"})
    node_positions = networkx.multipartite_layout(graph, subset_key="layer", **multipartite_kwargs)

    # The nodes are drawn tiny so that labels can go on top
    collection = networkx.draw_networkx_nodes(graph, pos=node_positions, node_size=0)
    figure = collection.get_figure()
    axes = figure.axes[0]
    axes.axis("off")

    # Sort edges by the lowest layer of their connected nodes
    sorted_edges = sorted(
        graph.edges(), key=lambda edge: min(graph.nodes[edge[0]]["layer"], graph.nodes[edge[1]]["layer"])
    )

    patch_kwargs = dict(
        xycoords="data",
        ha="center",
        va="center",
        size=font_size,
        bbox=dict(facecolor=node_color, boxstyle="round"),
    )

    # Labels are written on top of existing nodes, which are laid out by networkx
    for source, target in sorted_edges:
        patch_a = axes.annotate(graph.nodes[target]["label"], xy=node_positions[target], **patch_kwargs)
        patch_b = axes.annotate(graph.nodes[source]["label"], xy=node_positions[source], **patch_kwargs)

        arrowprops = dict(
            arrowstyle="<-", color=edge_color, connectionstyle="arc3,rad=0.1", patchA=patch_a, patchB=patch_b
        )

        axes.annotate(
            "",
            xy=node_positions[source],
            xycoords="data",
            xytext=node_positions[target],
            textcoords="data",
            arrowprops=arrowprops,
        )

    figure.set_size_inches((width, height))

    return figure


def plot(
    figure: matplotlib.figure.Figure,
    output_file: typing.Optional[pathlib.Path] = None,
    transparent: bool = False,
) -> None:
    """Open a matplotlib plot or save to file

    :param figure: The matplotlib figure
    :param output_file: File for saving the visualization
    :param transparent: Use a transparent background
    """
    if output_file is not None:
        file_name = output_file
        file_name.parent.mkdir(parents=True, exist_ok=True)
        suffix = output_file.suffix
        if not suffix or suffix[1:] not in list(figure.canvas.get_supported_filetypes().keys()):
            # If there is no suffix or it's not supported by matplotlib, use svg
            file_name = file_name.with_suffix(".svg")
            print(
                f"WARNING: extension '{suffix}' is not supported by matplotlib. Falling back to '{file_name}'",
                file=sys.stderr,
            )
        figure.savefig(str(file_name), transparent=transparent)
    else:
        matplotlib.pyplot.show()


# Limit help() and 'from module import *' behavior to the module's public API
_module_objects = set(globals().keys()) - _exclude_from_namespace
__all__ = [name for name in _module_objects if not name.startswith("_")]
