import contextlib
import pathlib
from unittest.mock import patch

import matplotlib.pyplot
import networkx
import pytest

from waves import _visualize

does_not_raise = contextlib.nullcontext()

test_ancestor_subgraph_cases = {
    "node not found": (
        networkx.DiGraph([("parent", "child")]),
        ["notanode"],
        pytest.raises(RuntimeError, match="Nodes 'notanode' not found in the graph"),
        None,
    ),
    "parent-child: request child": (
        networkx.DiGraph([("parent", "child")]),
        ["child"],
        does_not_raise,
        networkx.DiGraph([("parent", "child")]),
    ),
    "parent-child: request parent": (
        networkx.DiGraph([("parent", "child")]),
        ["parent"],
        does_not_raise,
        networkx.DiGraph([("parent", "child")]).subgraph("parent"),
    ),
    "parent1/2-child1/2: request child": (
        networkx.DiGraph([("parent", "child"), ("parent2", "child2")]),
        ["child"],
        does_not_raise,
        networkx.DiGraph([("parent", "child")]),
    ),
    "parent1/2-child1/2: request child2": (
        networkx.DiGraph([("parent", "child"), ("parent2", "child2")]),
        ["child2"],
        does_not_raise,
        networkx.DiGraph([("parent2", "child2")]),
    ),
    "parent1/2-child1/2: request child1/2": (
        networkx.DiGraph([("parent", "child"), ("parent2", "child2")]),
        ["child", "child2"],
        does_not_raise,
        networkx.DiGraph([("parent", "child"), ("parent2", "child2")]),
    ),
    "grandparent-parent-child: request child": (
        networkx.DiGraph([("grandparent", "parent"), ("parent", "child")]),
        ["child"],
        does_not_raise,
        networkx.DiGraph([("grandparent", "parent"), ("parent", "child")]),
    ),
    "grandparent-parent-child: request parent": (
        networkx.DiGraph([("grandparent", "parent"), ("parent", "child")]),
        ["parent"],
        does_not_raise,
        networkx.DiGraph([("grandparent", "parent")]),
    ),
    "grandparent-parent-child/child2: request child": (
        networkx.DiGraph([("grandparent", "parent"), ("parent", "child"), ("parent", "child2")]),
        ["child"],
        does_not_raise,
        networkx.DiGraph([("grandparent", "parent"), ("parent", "child")]),
    ),
    "grandparent-parent-child/child2: request child2": (
        networkx.DiGraph([("grandparent", "parent"), ("parent", "child"), ("parent", "child2")]),
        ["child2"],
        does_not_raise,
        networkx.DiGraph([("grandparent", "parent"), ("parent", "child2")]),
    ),
    "grandparent-parent-child/child2: request child/child2": (
        networkx.DiGraph([("grandparent", "parent"), ("parent", "child"), ("parent", "child2")]),
        ["child", "child2"],
        does_not_raise,
        networkx.DiGraph([("grandparent", "parent"), ("parent", "child"), ("parent", "child2")]),
    ),
    "grandparent-parent-child/child2: request parent": (
        networkx.DiGraph([("grandparent", "parent"), ("parent", "child"), ("parent", "child2")]),
        ["parent"],
        does_not_raise,
        networkx.DiGraph([("grandparent", "parent")]),
    ),
    "grandparent-parent-child/child2: request grandparent": (
        networkx.DiGraph([("grandparent", "parent"), ("parent", "child"), ("parent", "child2")]),
        ["grandparent"],
        does_not_raise,
        networkx.DiGraph([("grandparent", "parent")]).subgraph("grandparent"),
    ),
}


@pytest.mark.parametrize(
    ("graph", "nodes", "outcome", "expected"),
    test_ancestor_subgraph_cases.values(),
    ids=test_ancestor_subgraph_cases.keys(),
)
def test_ancestor_subgraph(
    graph: networkx.DiGraph,
    nodes: list[str],
    outcome: contextlib.nullcontext | pytest.RaisesExc,
    expected: networkx.DiGraph | None,
) -> None:
    # Check for a runtime error on empty subgraph/missing node
    with outcome:
        subgraph = _visualize.ancestor_subgraph(graph, nodes)
        assert subgraph.nodes == expected.nodes


def test_add_node_count() -> None:
    graph = networkx.DiGraph()
    graph.add_node(1, label="one", layer=1)
    graph.add_node(2, label="two", layer=2)
    graph.add_edge(1, 2)
    new_graph = _visualize.add_node_count(graph)
    assert "Node count: 2" in new_graph.nodes


def test_graph_to_graphml() -> None:
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
    ("tree_output", "break_path_separator", "expected_nodes", "expected_edge_count", "no_labels"),
    parse_output_input.values(),
    ids=parse_output_input.keys(),
)
def test_parse_output(
    tree_output: str,
    break_path_separator: str | None,
    expected_nodes: dict,
    expected_edge_count: int,
    no_labels: bool,
) -> None:
    """Test raises behavior and regression test a sample SCons tree output parsing."""
    # Check for a runtime error on empty parsing
    with pytest.raises(RuntimeError):
        graph = _visualize.parse_output([])

    tree_lines = tree_output.split("\n")
    break_paths = True if break_path_separator is not None else False  # noqa: SIM210
    with patch("os.path.sep", new=break_path_separator):
        graph = _visualize.parse_output(tree_lines, break_paths=break_paths, no_labels=no_labels)

    assert len(graph.nodes) == len(expected_nodes)
    assert len(graph.edges) == expected_edge_count
    for expected_node, expected_label in expected_nodes.items():
        assert expected_node in graph.nodes
        assert expected_label in graph.nodes[expected_node]["label"]


test_check_regex_exclude_cases = {
    "regular expression not provided (None)": (None, "dummy_name5", 3, 0, False, (False, 0)),
    "regular expression is empty": ("", "dummy_name5", 3, 0, False, (False, 0)),
    "node name matches the regular expression": ("dummy_name[0-7]+", "dummy_name5", 3, 0, False, (True, 3)),
    "node name does not match the regular expression": ("dummy_name[0-7]+", "dummy_name8", 2, 1, False, (False, 1)),
    "node name does not match the regular expression but the node was already excluded": (
        "dummy_name[0-7]+",
        "dummy_name9",
        4,
        2,
        True,
        (True, 2),
    ),
}


@pytest.mark.parametrize(
    ("exclude_regex", "node_name", "current_indent", "exclude_indent", "exclude_node", "expected"),
    test_check_regex_exclude_cases.values(),
    ids=test_check_regex_exclude_cases.keys(),
)
def test_check_regex_exclude(
    exclude_regex: str | None,
    node_name: str,
    current_indent: int,
    exclude_indent: int,
    exclude_node: bool,
    expected: tuple[bool, int],
) -> None:
    """Test the regular expression exclusion of the visualize subcommand."""
    assert (
        _visualize.check_regex_exclude(
            exclude_regex, node_name, current_indent, exclude_indent, exclude_node=exclude_node
        )
        == expected
    )


def test_visualize() -> None:
    """Sign-of-life test for the visualize figure."""
    graph = networkx.DiGraph()
    graph.add_node(1, label="one", layer=1)
    graph.add_node(2, label="two", layer=2)
    graph.add_edge(1, 2)
    _visualize.visualize(graph)


def test_plot() -> None:
    """Check that the expected plot output function is called."""
    figure, _axes = matplotlib.pyplot.subplots()
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
