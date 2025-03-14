import os
import pathlib
from unittest.mock import patch

import pytest
import networkx
import matplotlib.pyplot

from waves import _visualize


def test_ancestor_subgraph():
    graph = networkx.DiGraph()
    graph.add_edge("parent", "child")

    # Check for a runtime error on empty subgraph/missing node
    with pytest.raises(RuntimeError):
        subgraph = _visualize.ancestor_subgraph(graph, ["notanode"])

    # Check subgraph(s)
    subgraph = _visualize.ancestor_subgraph(graph, ["child"])
    assert subgraph.nodes == graph.nodes

    # Check subgraph(s)
    subgraph = _visualize.ancestor_subgraph(graph, ["parent"])
    assert list(subgraph.nodes) == ["parent"]


def test_add_node_count():
    graph = networkx.DiGraph()
    graph.add_node(1, label="one", layer=1)
    graph.add_node(2, label="two", layer=2)
    graph.add_edge(1, 2)
    new_graph = _visualize.add_node_count(graph)
    assert "Node count: 2" in new_graph.nodes


def test_graph_to_graphml():
    """Sign-of-life test for a non-empty Python string return value.

    Testing the content of an XML file subject to change with data unrelated to the input is fragile. If something more
    than a sign-of-life test is performed, it should probably include converting the XML back into a graph object and
    testing equality of the graph objects.
    """
    graph = networkx.DiGraph()
    graph.add_edge(1, 2)
    graphml = _visualize.graph_to_graphml(graph)
    assert isinstance(graphml, str)
    assert graphml != ""


parse_output_input = {
    "no break path": (
        "[E b   C  ]+-nominal\n[  B      ]  +-build/nominal/stress_strain_comparison.pdf",
        None,
        {
            "nominal": "nominal",
            "build/nominal/stress_strain_comparison.pdf": "build/nominal/stress_strain_comparison.pdf",
        },
        1,
        False,
    ),
    "no label": (
        "[E b   C  ]+-nominal\n[  B      ]  +-build/nominal/stress_strain_comparison.pdf",
        None,
        {
            "nominal": " ",
            "build/nominal/stress_strain_comparison.pdf": " ",
        },
        1,
        True,
    ),
    "windows break path": (
        "[E b   C  ]+-nominal\n[  B      ]  +-build\\nominal\\stress_strain_comparison.pdf",
        "\\",
        {
            "nominal": "nominal",
            "build\\nominal\\stress_strain_comparison.pdf": "build\\\nnominal\\\nstress_strain_comparison.pdf",
        },
        1,
        False,
    ),
    "linux break path": (
        "[E b   C  ]+-nominal\n[  B      ]  +-build/nominal/stress_strain_comparison.pdf",
        "/",
        {
            "nominal": "nominal",
            "build/nominal/stress_strain_comparison.pdf": "build/\nnominal/\nstress_strain_comparison.pdf",
        },
        1,
        False,
    ),
}


@pytest.mark.parametrize(
    "tree_output, break_path_separator, expected_nodes, expected_edge_count, no_labels",
    parse_output_input.values(),
    ids=parse_output_input.keys(),
)
def test_parse_output(
    tree_output,
    break_path_separator,
    expected_nodes,
    expected_edge_count,
    no_labels,
):
    """Test raises behavior and regression test a sample SCons tree output parsing"""
    # Check for a runtime error on empty parsing
    with pytest.raises(RuntimeError):
        graph = _visualize.parse_output([])

    tree_lines = tree_output.split("\n")
    break_paths = True if break_path_separator is not None else False
    with patch(f"os.path.sep", new=break_path_separator):
        graph = _visualize.parse_output(tree_lines, break_paths=break_paths, no_labels=no_labels)

    assert len(graph.nodes) == len(expected_nodes)
    assert len(graph.edges) == expected_edge_count
    for expected_node, expected_label in expected_nodes.items():
        assert expected_node in graph.nodes
        assert expected_label in graph.nodes[expected_node]["label"]


def test_check_regex_exclude():
    """Test the regular expression exclusion of the visualize subcommand"""
    exclude_regex = "dummy_name[0-7]+"
    # If node name matches the regular expression
    assert _visualize.check_regex_exclude(exclude_regex, "dummy_name5", 3, 0, False) == (True, 3)
    # if node name does not match the regular expression
    assert _visualize.check_regex_exclude(exclude_regex, "dummy_name8", 2, 1, False) == (False, 1)
    # If node name does not match the regular expression but the node was already excluded
    assert _visualize.check_regex_exclude(exclude_regex, "dummy_name9", 4, 2, True) == (True, 2)


def test_visualize():
    """Sign-of-life test for the visualize figure"""
    graph = networkx.DiGraph()
    graph.add_node(1, label="one", layer=1)
    graph.add_node(2, label="two", layer=2)
    graph.add_edge(1, 2)
    _visualize.visualize(graph)


def test_plot():
    """Check that the expected plot output function is called"""
    figure, axes = matplotlib.pyplot.subplots()
    with (
        patch("matplotlib.pyplot.show") as mock_show,
        patch("matplotlib.figure.Figure.savefig") as mock_savefig,
    ):
        _visualize.plot(figure, output_file=None)
    mock_show.assert_called_once()
    mock_savefig.assert_not_called()

    with (
        patch("matplotlib.pyplot.show") as mock_show,
        patch("matplotlib.figure.Figure.savefig") as mock_savefig,
    ):
        _visualize.plot(figure, output_file=pathlib.Path("dummy.png"))
    mock_savefig.assert_called_once()
    mock_show.assert_not_called()
