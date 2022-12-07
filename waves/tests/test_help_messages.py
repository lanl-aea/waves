"""Test WAVES SCons builders and support functions"""

from unittest.mock import patch

import pytest

from waves import builders


@pytest.mark.unittest
def test_default_targets_message():
    import SCons.Script  # Magic smoke that turns SCons.Defaults.DefaultEnvironment from a SCons.Environment.Base to SCons.Script.SConscript.SConsEnvironment
    import SCons.Defaults
    env = SCons.Defaults.DefaultEnvironment()
    env.Default()
    with patch("SCons.Environment.Environment.Help") as mock_help:
        builders.default_targets_message(env)
    mock_help.assert_called_once_with("\nDefault Targets:\n", append=True)
    env.Default("dummy.target")
    with patch("SCons.Environment.Environment.Help") as mock_help:
        builders.default_targets_message(env)
    mock_help.assert_called_once_with("\nDefault Targets:\n    dummy.target\n", append=True)


@pytest.mark.unittest
def test_alias_list_message():
    import SCons.Script
    import SCons.Defaults
    env = SCons.Defaults.DefaultEnvironment()
    with patch("SCons.Environment.Environment.Help") as mock_help:
        builders.alias_list_message(env)
    mock_help.assert_called_once_with("\nTarget Aliases:\n", append=True)
    env.Alias("dummy_alias", "dummy.target")
    with patch("SCons.Environment.Environment.Help") as mock_help:
        builders.alias_list_message(env)
    mock_help.assert_called_once_with("\nTarget Aliases:\n    dummy_alias\n", append=True)
