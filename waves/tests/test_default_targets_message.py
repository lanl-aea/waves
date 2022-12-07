"""Test WAVES SCons builders and support functions"""

from unittest.mock import patch

from waves import builders

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
