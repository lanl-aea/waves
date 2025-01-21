"""Test WAVES SCons builders and support functions"""

from unittest.mock import patch, call, ANY

import pytest
import SCons.Environment

from waves import scons_extensions


def test_default_targets_message():
    # Raise TypeError mocking SCons < 4.6.0
    # Git commit 7a95cef7: Normally you expect something like ``patch("SCons.Script.SConscript.SConsEnvironment...")``
    # but Python <=3.10 chokes on the expected patch, so patch the WAVES module itself instead.
    with patch("waves.scons_extensions.SConsEnvironment.Help", side_effect=[TypeError, None]) as mock_help:
        scons_extensions.default_targets_message()
    calls = [
        call(ANY, "\nDefault Targets:\n", append=True, keep_local=True),
        call(ANY, "\nDefault Targets:\n", append=True),
    ]
    mock_help.assert_has_calls(calls)

    # No environment provided
    # Git commit 7a95cef7: Normally you expect something like ``patch("SCons.Script.SConscript.SConsEnvironment...")``
    # but Python <=3.10 chokes on the expected patch, so patch the WAVES module itself instead.
    with patch("waves.scons_extensions.SConsEnvironment.Help", side_effect=[None, None]) as mock_help:
        scons_extensions.default_targets_message()
    mock_help.assert_called_once_with(ANY, "\nDefault Targets:\n", append=True, keep_local=True)

    # Provide environment with no defaults
    env = SCons.Environment.Environment()
    env.Default()
    # Git commit 7a95cef7: Normally you expect something like ``patch("SCons.Script.SConscript.SConsEnvironment...")``
    # but Python <=3.10 chokes on the expected patch, so patch the WAVES module itself instead.
    with patch("waves.scons_extensions.SConsEnvironment.Help") as mock_help:
        scons_extensions.default_targets_message(env)
    mock_help.assert_called_once_with(ANY, "\nDefault Targets:\n", append=True, keep_local=True)

    # Provide environment with defaults
    env.Default("dummy.target")
    # Git commit 7a95cef7: Normally you expect something like ``patch("SCons.Script.SConscript.SConsEnvironment...")``
    # but Python <=3.10 chokes on the expected patch, so patch the WAVES module itself instead.
    with patch("waves.scons_extensions.SConsEnvironment.Help") as mock_help:
        scons_extensions.default_targets_message(env)
    mock_help.assert_called_once_with(ANY, "\nDefault Targets:\n    dummy.target\n", append=True, keep_local=True)

    # Test the Method style interface
    env.AddMethod(scons_extensions.default_targets_message, "ProjectHelp")
    # Git commit 7a95cef7: Normally you expect something like ``patch("SCons.Script.SConscript.SConsEnvironment...")``
    # but Python <=3.10 chokes on the expected patch, so patch the WAVES module itself instead.
    with patch("waves.scons_extensions.SConsEnvironment.Help") as mock_help:
        env.ProjectHelp()
    mock_help.assert_called_once_with(ANY, "\nDefault Targets:\n    dummy.target\n", append=True, keep_local=True)


def test_alias_list_message():
    # Raise TypeError mocking SCons < 4.6.0
    # Git commit 7a95cef7: Normally you expect something like ``patch("SCons.Script.SConscript.SConsEnvironment...")``
    # but Python <=3.10 chokes on the expected patch, so patch the WAVES module itself instead.
    with patch("waves.scons_extensions.SConsEnvironment.Help", side_effect=[TypeError, None]) as mock_help:
        scons_extensions.alias_list_message()
    calls = [
        call(ANY, "\nTarget Aliases:\n", append=True, keep_local=True),
        call(ANY, "\nTarget Aliases:\n", append=True),
    ]
    mock_help.assert_has_calls(calls)

    # No environment provided
    # Git commit 7a95cef7: Normally you expect something like ``patch("SCons.Script.SConscript.SConsEnvironment...")``
    # but Python <=3.10 chokes on the expected patch, so patch the WAVES module itself instead.
    with patch("waves.scons_extensions.SConsEnvironment.Help") as mock_help:
        scons_extensions.alias_list_message()
    mock_help.assert_called_once_with(ANY, "\nTarget Aliases:\n", append=True, keep_local=True)

    # Provide environment with no aliases
    env = SCons.Environment.Environment()
    # Git commit 7a95cef7: Normally you expect something like ``patch("SCons.Script.SConscript.SConsEnvironment...")``
    # but Python <=3.10 chokes on the expected patch, so patch the WAVES module itself instead.
    with patch("waves.scons_extensions.SConsEnvironment.Help") as mock_help:
        scons_extensions.alias_list_message(env)
    mock_help.assert_called_once_with(ANY, "\nTarget Aliases:\n", append=True, keep_local=True)

    # Provide environment with alias
    env.Alias("dummy_alias", "dummy.target")
    # Git commit 7a95cef7: Normally you expect something like ``patch("SCons.Script.SConscript.SConsEnvironment...")``
    # but Python <=3.10 chokes on the expected patch, so patch the WAVES module itself instead.
    with patch("waves.scons_extensions.SConsEnvironment.Help") as mock_help:
        scons_extensions.alias_list_message(env)
    mock_help.assert_called_once_with(ANY, "\nTarget Aliases:\n    dummy_alias\n", append=True, keep_local=True)

    # Test the Method style interface
    env.AddMethod(scons_extensions.alias_list_message, "ProjectHelp")
    # Git commit 7a95cef7: Normally you expect something like ``patch("SCons.Script.SConscript.SConsEnvironment...")``
    # but Python <=3.10 chokes on the expected patch, so patch the WAVES module itself instead.
    with patch("waves.scons_extensions.SConsEnvironment.Help") as mock_help:
        env.ProjectHelp()
    mock_help.assert_called_once_with(ANY, "\nTarget Aliases:\n    dummy_alias\n", append=True, keep_local=True)


def test_project_help_message():
    # Default behavior
    with (
        patch("waves.scons_extensions.default_targets_message") as mock_targets,
        patch("waves.scons_extensions.alias_list_message") as mock_alias,
    ):
        scons_extensions.project_help_message()
        mock_targets.assert_called_once_with(env=ANY, append=True, keep_local=True, target_descriptions=None)
        mock_alias.assert_called_once_with(env=ANY, append=True, keep_local=True, target_descriptions=None)

    # Pass non-default kwargs
    env = SCons.Environment.Environment()
    with (
        patch("waves.scons_extensions.default_targets_message") as mock_targets,
        patch("waves.scons_extensions.alias_list_message") as mock_alias,
    ):
        scons_extensions.project_help_message(env=env, append=False, keep_local=False)
        mock_targets.assert_called_once_with(env=env, append=False, keep_local=False, target_descriptions=None)
        mock_alias.assert_called_once_with(env=env, append=False, keep_local=False, target_descriptions=None)

    # Test non-default target_descriptions
    with (
        patch("waves.scons_extensions.default_targets_message") as mock_targets,
        patch("waves.scons_extensions.alias_list_message") as mock_alias,
    ):
        descriptions = {"somekey": "somevalue"}
        scons_extensions.project_help_message(env=env, append=False, keep_local=False,
                                              target_descriptions=descriptions)
        mock_targets.assert_called_once_with(env=env, append=False, keep_local=False, target_descriptions=descriptions)
        mock_alias.assert_called_once_with(env=env, append=False, keep_local=False, target_descriptions=descriptions)

    # Test the Method style interface
    env.AddMethod(scons_extensions.project_help_message, "ProjectHelp")
    with (
        patch("waves.scons_extensions.default_targets_message") as mock_targets,
        patch("waves.scons_extensions.alias_list_message") as mock_alias,
    ):
        env.ProjectHelp()
        mock_targets.assert_called_once_with(env=env, append=True, keep_local=True, target_descriptions=None)
        mock_alias.assert_called_once_with(env=env, append=True, keep_local=True, target_descriptions=None)
    
    # Test the Method style interface, non-default target_descriptions
    with (
        patch("waves.scons_extensions.default_targets_message") as mock_targets,
        patch("waves.scons_extensions.alias_list_message") as mock_alias,
    ):
        descriptions = {"someotherkey": "someothervalue"}
        env.ProjectHelp(target_descriptions=descriptions)
        mock_targets.assert_called_once_with(env=env, append=True, keep_local=True, target_descriptions=descriptions)
        mock_alias.assert_called_once_with(env=env, append=True, keep_local=True, target_descriptions=descriptions)


project_aliases = {
    "First Alias": (SCons.Environment.Environment(), ["dummy_alias"], {"SomeKey": "SomeValue"}, "dummy_hint",
                    {"dummy_alias": "dummy_hint"}),
    "Second Alias": (SCons.Environment.Environment(), ["dummy_alias2"], {}, "dummy_hint2",
                     {"dummy_alias": "dummy_hint", "dummy_alias2": "dummy_hint2"}),
    "None": (None, [], {}, None, {"dummy_alias": "dummy_hint", "dummy_alias2": "dummy_hint2"}),
}


@pytest.mark.parametrize(
    "env, args, kwargs, description, expected",
    project_aliases.values(),
    ids=project_aliases.keys(),
)
def test_project_alias(env, args, kwargs, description, expected):
    with patch("SCons.Environment.Base.Alias", return_value=args) as mock_alias:
        target_descriptions = scons_extensions.project_alias(env, *args, description=description, **kwargs)
        assert target_descriptions == expected
    if env:
        mock_alias.assert_called_once_with(*args, **kwargs)
    else:
        mock_alias.assert_not_called()


project_help_descriptions = {
    "No Descriptions": (["dummy_alias", "dummy_alias2"], {}, {}, "    dummy_alias\n    dummy_alias2\n"),
    "Existing Descriptions": (
        ["dummy_alias", "dummy_alias2"],
        {"dummy_alias": "dummy_description"},
        {},
        "    dummy_alias: dummy_description\n    dummy_alias2\n",
    ),
    "Target Descriptions": (
        ["dummy_alias", "dummy_alias2"],
        {},
        {"dummy_alias": "dummy_description"},
        "    dummy_alias: dummy_description\n    dummy_alias2\n",
    ),
    "Both Descriptions": (
        ["dummy_alias", "dummy_alias2"],
        {"dummy_alias": "dummy_description"},
        {"dummy_alias": "dummy_description2"},
        "    dummy_alias: dummy_description2\n    dummy_alias2\n",
    ),
}


@pytest.mark.parametrize(
    "nodes, existing_descriptions, target_descriptions, expected",
    project_help_descriptions.values(),
    ids=project_help_descriptions.keys(),
)
def test_project_help_descriptions(nodes, existing_descriptions, target_descriptions, expected):
    with patch("waves.scons_extensions.project_alias", return_value=existing_descriptions) as mock_project_alias:
        message = scons_extensions.project_help_descriptions(nodes, target_descriptions=target_descriptions)
        assert message == expected
        mock_project_alias.assert_called_once()
