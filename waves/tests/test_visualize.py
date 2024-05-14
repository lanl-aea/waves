import pytest
import networkx

from waves import _visualize


def test_check_regex_exclude():
    """Test the regular expression exclusion of the visualize subcommand"""
    exclude_regex = 'dummy_name[0-7]+'
    # If node name matches the regular expression
    assert _visualize.check_regex_exclude(exclude_regex, 'dummy_name5', 3, 0, False) == (True, 3)
    # if node name does not match the regular expression
    assert _visualize.check_regex_exclude(exclude_regex, 'dummy_name8', 2, 1, False) == (False, 1)
    # If node name does not match the regular expression but the node was already excluded
    assert _visualize.check_regex_exclude(exclude_regex, 'dummy_name9', 4, 2, True) == (True, 2)


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
