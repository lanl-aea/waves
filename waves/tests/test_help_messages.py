"""Test WAVES SCons builders and support functions"""

from unittest.mock import patch, call, ANY

import pytest
import SCons.Environment

from waves import scons_extensions


def test_default_targets_message():
    # Raise TypeError mocking SCons < 4.6.0
    with patch("SCons.Script.SConscript.SConsEnvironment.Help", side_effect=[TypeError, None]) as mock_help:
        scons_extensions.default_targets_message()
    calls = [
        call("\nDefault Targets:\n", append=True, keep_local=True),
        call("\nDefault Targets:\n", append=True)
    ]
    mock_help.assert_has_calls(calls)

    # No environment provided
    with patch("SCons.Script.SConscript.SConsEnvironment.Help", side_effect=[None, None]) as mock_help:
        scons_extensions.default_targets_message()
    mock_help.assert_called_once_with("\nDefault Targets:\n", append=True, keep_local=True)

    # Provide environment with no defaults
    env = SCons.Environment.Environment()
    env.Default()
    with patch("SCons.Script.SConscript.SConsEnvironment.Help") as mock_help:
        scons_extensions.default_targets_message(env)
    mock_help.assert_called_once_with("\nDefault Targets:\n", append=True, keep_local=True)

    # Provide environment with defaults
    env.Default("dummy.target")
    with patch("SCons.Script.SConscript.SConsEnvironment.Help") as mock_help:
        scons_extensions.default_targets_message(env)
    mock_help.assert_called_once_with("\nDefault Targets:\n    dummy.target\n", append=True, keep_local=True)

    # Test the Method style interface
    env.AddMethod(scons_extensions.default_targets_message, "ProjectHelp")
    with patch("SCons.Script.SConscript.SConsEnvironment.Help") as mock_help:
        env.ProjectHelp()
    mock_help.assert_called_once_with("\nDefault Targets:\n    dummy.target\n", append=True, keep_local=True)


def test_alias_list_message():
    # Raise TypeError mocking SCons < 4.6.0
    with patch("SCons.Script.SConscript.SConsEnvironment.Help", side_effect=[TypeError, None]) as mock_help:
        scons_extensions.alias_list_message()
    calls = [
        call("\nTarget Aliases:\n", append=True, keep_local=True),
        call("\nTarget Aliases:\n", append=True)
    ]
    mock_help.assert_has_calls(calls)

    # No environment provided
    with patch("SCons.Script.SConscript.SConsEnvironment.Help") as mock_help:
        scons_extensions.alias_list_message()
    mock_help.assert_called_once_with("\nTarget Aliases:\n", append=True, keep_local=True)

    # Provide environment with no aliases
    env = SCons.Environment.Environment()
    with patch("SCons.Script.SConscript.SConsEnvironment.Help") as mock_help:
        scons_extensions.alias_list_message(env)
    mock_help.assert_called_once_with("\nTarget Aliases:\n", append=True, keep_local=True)

    # Provide environment with alias
    env.Alias("dummy_alias", "dummy.target")
    with patch("SCons.Script.SConscript.SConsEnvironment.Help") as mock_help:
        scons_extensions.alias_list_message(env)
    mock_help.assert_called_once_with("\nTarget Aliases:\n    dummy_alias\n", append=True, keep_local=True)

    # Test the Method style interface
    env.AddMethod(scons_extensions.alias_list_message, "ProjectHelp")
    with patch("SCons.Script.SConscript.SConsEnvironment.Help") as mock_help:
        env.ProjectHelp()
    mock_help.assert_called_once_with("\nTarget Aliases:\n    dummy_alias\n", append=True, keep_local=True)


def test_project_help_message():
    # Default behavior
    with patch("waves.scons_extensions.default_targets_message") as mock_targets, \
         patch("waves.scons_extensions.alias_list_message") as mock_alias:
        scons_extensions.project_help_message()
        mock_targets.assert_called_once_with(env=ANY, append=True, keep_local=True)
        mock_alias.assert_called_once_with(env=ANY, append=True, keep_local=True)

    # Pass non-default kwargs
    env = SCons.Environment.Environment()
    with patch("waves.scons_extensions.default_targets_message") as mock_targets, \
         patch("waves.scons_extensions.alias_list_message") as mock_alias:
        scons_extensions.project_help_message(env=env, append=False, keep_local=False)
        mock_targets.assert_called_once_with(env=env, append=False, keep_local=False)
        mock_alias.assert_called_once_with(env=env, append=False, keep_local=False)

    # Test the Method style interface
    env.AddMethod(scons_extensions.project_help_message, "ProjectHelp")
    with patch("waves.scons_extensions.default_targets_message") as mock_targets, \
         patch("waves.scons_extensions.alias_list_message") as mock_alias:
        env.ProjectHelp()
        mock_targets.assert_called_once_with(env=env, append=True, keep_local=True)
        mock_alias.assert_called_once_with(env=env, append=True, keep_local=True)
