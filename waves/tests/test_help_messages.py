"""Test WAVES SCons builders and support functions"""

from unittest.mock import patch, call

import pytest

from waves import scons_extensions


@pytest.mark.unittest
def test_default_targets_message():
    import SCons.Script  # Magic smoke that turns SCons.Defaults.DefaultEnvironment from a SCons.Environment.Base to SCons.Script.SConscript.SConsEnvironment
    import SCons.Defaults

    # Raise TypeError mocking SCons < 4.6.0
    with patch("SCons.Environment.Environment.Help", side_effect=[TypeError, None]) as mock_help:
        scons_extensions.default_targets_message()
    calls = [
        call("\nDefault Targets:\n", append=True, keep_local=True),
        call("\nDefault Targets:\n", append=True)
    ]
    mock_help.assert_has_calls(calls)

    # No environment provided
    with patch("SCons.Environment.Environment.Help") as mock_help:
        scons_extensions.default_targets_message()
    mock_help.assert_called_once_with("\nDefault Targets:\n", append=True, keep_local=True)

    # Provide environment with no defaults
    env = SCons.Defaults.DefaultEnvironment()
    env.Default()
    with patch("SCons.Environment.Environment.Help") as mock_help:
        scons_extensions.default_targets_message(env)
    mock_help.assert_called_once_with("\nDefault Targets:\n", append=True, keep_local=True)

    # Provide environment with defaults
    env.Default("dummy.target")
    with patch("SCons.Environment.Environment.Help") as mock_help:
        scons_extensions.default_targets_message(env)
    mock_help.assert_called_once_with("\nDefault Targets:\n    dummy.target\n", append=True, keep_local=True)


@pytest.mark.unittest
def test_alias_list_message():
    import SCons.Script
    import SCons.Defaults

    # Raise TypeError mocking SCons < 4.6.0
    with patch("SCons.Environment.Environment.Help", side_effect=[TypeError, None]) as mock_help:
        scons_extensions.alias_list_message()
    calls = [
        call("\nTarget Aliases:\n", append=True, keep_local=True),
        call("\nTarget Aliases:\n", append=True)
    ]
    mock_help.assert_has_calls(calls)

    # No environment provided
    with patch("SCons.Environment.Environment.Help") as mock_help:
        scons_extensions.alias_list_message()
    mock_help.assert_called_once_with("\nTarget Aliases:\n", append=True, keep_local=True)

    # Provide environment with no aliases
    env = SCons.Defaults.DefaultEnvironment()
    with patch("SCons.Environment.Environment.Help") as mock_help:
        scons_extensions.alias_list_message(env)
    mock_help.assert_called_once_with("\nTarget Aliases:\n", append=True, keep_local=True)

    # Provide environment with alias
    env.Alias("dummy_alias", "dummy.target")
    with patch("SCons.Environment.Environment.Help") as mock_help:
        scons_extensions.alias_list_message(env)
    mock_help.assert_called_once_with("\nTarget Aliases:\n    dummy_alias\n", append=True, keep_local=True)


@pytest.mark.unittest
def test_project_help_message():
    # Default behavior
    with patch("waves.scons_extensions.default_targets_message") as mock_targets, \
         patch("waves.scons_extensions.alias_list_message") as mock_alias:
        scons_extensions.project_help_message()
        mock_targets.assert_called_once_with(env=None, append=True, keep_local=True)
        mock_alias.assert_called_once_with(env=None, append=True, keep_local=True)

    # Pass non-default kwargs
    with patch("waves.scons_extensions.default_targets_message") as mock_targets, \
         patch("waves.scons_extensions.alias_list_message") as mock_alias:
        scons_extensions.project_help_message(env={}, append=False, keep_local=False)
        mock_targets.assert_called_once_with(env={}, append=False, keep_local=False)
        mock_alias.assert_called_once_with(env={}, append=False, keep_local=False)
