"""Test WAVES SCons builders and support functions"""

from unittest.mock import patch

import pytest

from waves import scons_extensions


@pytest.mark.unittest
def test_default_targets_message():
    import SCons.Script  # Magic smoke that turns SCons.Defaults.DefaultEnvironment from a SCons.Environment.Base to SCons.Script.SConscript.SConsEnvironment
    import SCons.Defaults

    # No environment provided
    with patch("SCons.Environment.Environment.Help") as mock_help:
        scons_extensions.default_targets_message()
    mock_help.assert_called_once_with("\nDefault Targets:\n", append=True)

    # Provide environment with no defaults
    env = SCons.Defaults.DefaultEnvironment()
    env.Default()
    with patch("SCons.Environment.Environment.Help") as mock_help:
        scons_extensions.default_targets_message(env)
    mock_help.assert_called_once_with("\nDefault Targets:\n", append=True)

    # Provide environment with defaults
    env.Default("dummy.target")
    with patch("SCons.Environment.Environment.Help") as mock_help:
        scons_extensions.default_targets_message(env)
    mock_help.assert_called_once_with("\nDefault Targets:\n    dummy.target\n", append=True)


@pytest.mark.unittest
def test_alias_list_message():
    import SCons.Script
    import SCons.Defaults

    # No environment provided
    with patch("SCons.Environment.Environment.Help") as mock_help:
        scons_extensions.alias_list_message()
    mock_help.assert_called_once_with("\nTarget Aliases:\n", append=True)

    # Provide environment with no aliases
    env = SCons.Defaults.DefaultEnvironment()
    with patch("SCons.Environment.Environment.Help") as mock_help:
        scons_extensions.alias_list_message(env)
    mock_help.assert_called_once_with("\nTarget Aliases:\n", append=True)

    # Provide environment with alias
    env.Alias("dummy_alias", "dummy.target")
    with patch("SCons.Environment.Environment.Help") as mock_help:
        scons_extensions.alias_list_message(env)
    mock_help.assert_called_once_with("\nTarget Aliases:\n    dummy_alias\n", append=True)


@pytest.mark.unittest
def test_project_help_message():
    with patch("waves.scons_extensions.default_targets_message") as mock_default, \
         patch("waves.scons_extensions.alias_list_message") as mock_alias:
        scons_extensions.project_help_message()
    mock_default.assert_called_once()
    mock_alias.assert_called_once()
