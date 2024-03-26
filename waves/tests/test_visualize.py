"""
Test visualize.py
"""
import pytest

from waves import _visualize


@pytest.mark.unittest
def test_check_regex_exclude():
    exclude_regex = 'dummy_name[0-7]+'
    # If node name matches the regular expression
    assert _visualize.check_regex_exclude(exclude_regex, 'dummy_name5', 3, 0, False) == (True, 3)
    # if node name does not match the regular expression
    assert _visualize.check_regex_exclude(exclude_regex, 'dummy_name8', 2, 1, False) == (False, 1)
    # If node name does not match the regular expression but the node was already excluded
    assert _visualize.check_regex_exclude(exclude_regex, 'dummy_name9', 4, 2, True) == (True, 2)
