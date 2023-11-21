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
        scons_extensions.default_targets_message(local_only=False)
    mock_help.assert_called_once_with("\nDefault Targets:\n", append=True, local_only=False)

    # Provide environment with no defaults
    env = SCons.Defaults.DefaultEnvironment()
    env.Default()
    with patch("SCons.Environment.Environment.Help") as mock_help:
        scons_extensions.default_targets_message(env, local_only=False)
    mock_help.assert_called_once_with("\nDefault Targets:\n", append=True, local_only=False)

    # Provide environment with defaults
    env.Default("dummy.target")
    with patch("SCons.Environment.Environment.Help") as mock_help:
        scons_extensions.default_targets_message(env, local_only=False)
    mock_help.assert_called_once_with("\nDefault Targets:\n    dummy.target\n", append=True, local_only=False)


@pytest.mark.unittest
def test_alias_list_message():
    import SCons.Script
    import SCons.Defaults

    # No environment provided
    with patch("SCons.Environment.Environment.Help") as mock_help:
        scons_extensions.alias_list_message(local_only=False)
    mock_help.assert_called_once_with("\nTarget Aliases:\n", append=True, local_only=False)

    # Provide environment with no aliases
    env = SCons.Defaults.DefaultEnvironment()
    with patch("SCons.Environment.Environment.Help") as mock_help:
        scons_extensions.alias_list_message(env, local_only=False)
    mock_help.assert_called_once_with("\nTarget Aliases:\n", append=True, local_only=False)

    # Provide environment with alias
    env.Alias("dummy_alias", "dummy.target")
    with patch("SCons.Environment.Environment.Help") as mock_help:
        scons_extensions.alias_list_message(env, local_only=False)
    mock_help.assert_called_once_with("\nTarget Aliases:\n    dummy_alias\n", append=True, local_only=False)


@pytest.mark.unittest
def test_project_help_message():
    # Default behavior
    with patch("waves.scons_extensions.default_targets_message") as mock_targets, \
         patch("waves.scons_extensions.alias_list_message") as mock_alias:
        scons_extensions.project_help_message()
        mock_targets.assert_called_once_with(env=None, append=True, local_only=True)
        mock_alias.assert_called_once_with(env=None, append=True, local_only=True)

    # Pass non-default kwargs
    with patch("waves.scons_extensions.default_targets_message") as mock_targets, \
         patch("waves.scons_extensions.alias_list_message") as mock_alias:
        scons_extensions.project_help_message(env={}, append=False, local_only=False)
        mock_targets.assert_called_once_with(env={}, append=False, local_only=False)
        mock_alias.assert_called_once_with(env={}, append=False, local_only=False)
