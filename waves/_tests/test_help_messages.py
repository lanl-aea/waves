"""Test WAVES SCons builders and support functions"""

from unittest.mock import patch, call, ANY

import pytest
import SCons.Environment

from waves import scons_extensions


# TODO: Remove this function once duplicate testing functions have been removed
# https://re-git.lanl.gov/aea/python-projects/waves/-/issues/862
@pytest.fixture(autouse=True)
def reset_alias():
    # Reset aliases before each test
    SCons.Script.DEFAULT_TARGETS = []
    SCons.Node.Alias.default_ans = SCons.Node.Alias.AliasNameSpace()


# TODO: Remove entire test function when old function name `default_targets_message` is fully deprecated
# https://re-git.lanl.gov/aea/python-projects/waves/-/issues/862
def test_default_targets_message():
    # Raise TypeError mocking SCons < 4.6.0
    # Git commit 7a95cef7: Normally you expect something like ``patch("SCons.Script.SConscript.SConsEnvironment...")``
    # but Python <=3.10 chokes on the expected patch, so patch the WAVES module itself instead.
    with (
        patch("waves.scons_extensions.SConsEnvironment.Help", side_effect=[TypeError, None]) as mock_help,
        patch("warnings.warn") as warning,
    ):
        scons_extensions.default_targets_message()
        warning.assert_called_once()
    calls = [
        call(ANY, "\nDefault Targets:\n", append=True, keep_local=True),
        call(ANY, "\nDefault Targets:\n", append=True),
    ]
    mock_help.assert_has_calls(calls)

    # No environment provided
    # Git commit 7a95cef7: Normally you expect something like ``patch("SCons.Script.SConscript.SConsEnvironment...")``
    # but Python <=3.10 chokes on the expected patch, so patch the WAVES module itself instead.
    with (
        patch("waves.scons_extensions.SConsEnvironment.Help", side_effect=[None, None]) as mock_help,
        patch("warnings.warn") as warning,
    ):
        scons_extensions.default_targets_message()
        warning.assert_called_once()
    mock_help.assert_called_once_with(ANY, "\nDefault Targets:\n", append=True, keep_local=True)

    # Provide environment with no defaults
    env = SCons.Environment.Environment()
    env.Default()
    # Git commit 7a95cef7: Normally you expect something like ``patch("SCons.Script.SConscript.SConsEnvironment...")``
    # but Python <=3.10 chokes on the expected patch, so patch the WAVES module itself instead.
    with (
        patch("waves.scons_extensions.SConsEnvironment.Help") as mock_help,
        patch("warnings.warn") as warning,
    ):
        scons_extensions.default_targets_message(env)
        warning.assert_called_once()
    mock_help.assert_called_once_with(ANY, "\nDefault Targets:\n", append=True, keep_local=True)

    # Provide environment with defaults
    env.Default("dummy.target")
    # Git commit 7a95cef7: Normally you expect something like ``patch("SCons.Script.SConscript.SConsEnvironment...")``
    # but Python <=3.10 chokes on the expected patch, so patch the WAVES module itself instead.
    with (
        patch("waves.scons_extensions.SConsEnvironment.Help") as mock_help,
        patch("warnings.warn") as warning,
    ):
        scons_extensions.default_targets_message(env)
        warning.assert_called_once()
    mock_help.assert_called_once_with(ANY, "\nDefault Targets:\n    dummy.target\n", append=True, keep_local=True)

    # Test the Method style interface
    env.AddMethod(scons_extensions.default_targets_message, "ProjectHelp")
    # Git commit 7a95cef7: Normally you expect something like ``patch("SCons.Script.SConscript.SConsEnvironment...")``
    # but Python <=3.10 chokes on the expected patch, so patch the WAVES module itself instead.
    with (
        patch("waves.scons_extensions.SConsEnvironment.Help") as mock_help,
        patch("warnings.warn") as warning,
    ):
        env.ProjectHelp()
        warning.assert_called_once()
    mock_help.assert_called_once_with(ANY, "\nDefault Targets:\n    dummy.target\n", append=True, keep_local=True)


def test_project_help_default_targets():
    # Raise TypeError mocking SCons < 4.6.0
    # Git commit 7a95cef7: Normally you expect something like ``patch("SCons.Script.SConscript.SConsEnvironment...")``
    # but Python <=3.10 chokes on the expected patch, so patch the WAVES module itself instead.
    with patch("waves.scons_extensions.SConsEnvironment.Help", side_effect=[TypeError, None]) as mock_help:
        scons_extensions.project_help_default_targets()
    calls = [
        call(ANY, "\nDefault Targets:\n", append=True, keep_local=True),
        call(ANY, "\nDefault Targets:\n", append=True),
    ]
    mock_help.assert_has_calls(calls)

    # No environment provided
    # Git commit 7a95cef7: Normally you expect something like ``patch("SCons.Script.SConscript.SConsEnvironment...")``
    # but Python <=3.10 chokes on the expected patch, so patch the WAVES module itself instead.
    with patch("waves.scons_extensions.SConsEnvironment.Help", side_effect=[None, None]) as mock_help:
        scons_extensions.project_help_default_targets()
    mock_help.assert_called_once_with(ANY, "\nDefault Targets:\n", append=True, keep_local=True)

    # Provide environment with no defaults
    env = SCons.Environment.Environment()
    env.Default()
    # Git commit 7a95cef7: Normally you expect something like ``patch("SCons.Script.SConscript.SConsEnvironment...")``
    # but Python <=3.10 chokes on the expected patch, so patch the WAVES module itself instead.
    with patch("waves.scons_extensions.SConsEnvironment.Help") as mock_help:
        scons_extensions.project_help_default_targets(env)
    mock_help.assert_called_once_with(ANY, "\nDefault Targets:\n", append=True, keep_local=True)

    # Provide environment with defaults
    env.Default("dummy.target")
    # Git commit 7a95cef7: Normally you expect something like ``patch("SCons.Script.SConscript.SConsEnvironment...")``
    # but Python <=3.10 chokes on the expected patch, so patch the WAVES module itself instead.
    with patch("waves.scons_extensions.SConsEnvironment.Help") as mock_help:
        scons_extensions.project_help_default_targets(env)
    mock_help.assert_called_once_with(ANY, "\nDefault Targets:\n    dummy.target\n", append=True, keep_local=True)

    # Test the Method style interface
    env.AddMethod(scons_extensions.project_help_default_targets, "ProjectHelp")
    # Git commit 7a95cef7: Normally you expect something like ``patch("SCons.Script.SConscript.SConsEnvironment...")``
    # but Python <=3.10 chokes on the expected patch, so patch the WAVES module itself instead.
    with patch("waves.scons_extensions.SConsEnvironment.Help") as mock_help:
        env.ProjectHelp()
    mock_help.assert_called_once_with(ANY, "\nDefault Targets:\n    dummy.target\n", append=True, keep_local=True)


# TODO: Deprecate the old function name
# https://re-git.lanl.gov/aea/python-projects/waves/-/issues/862
def test_alias_list_message():
    # Raise TypeError mocking SCons < 4.6.0
    # Git commit 7a95cef7: Normally you expect something like ``patch("SCons.Script.SConscript.SConsEnvironment...")``
    # but Python <=3.10 chokes on the expected patch, so patch the WAVES module itself instead.
    with (
        patch("waves.scons_extensions.SConsEnvironment.Help", side_effect=[TypeError, None]) as mock_help,
        patch("warnings.warn") as warning,
    ):
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


def test_project_help_aliases():
    # Raise TypeError mocking SCons < 4.6.0
    # Git commit 7a95cef7: Normally you expect something like ``patch("SCons.Script.SConscript.SConsEnvironment...")``
    # but Python <=3.10 chokes on the expected patch, so patch the WAVES module itself instead.
    with patch("waves.scons_extensions.SConsEnvironment.Help", side_effect=[TypeError, None]) as mock_help:
        scons_extensions.project_help_aliases()
    calls = [
        call(ANY, "\nTarget Aliases:\n", append=True, keep_local=True),
        call(ANY, "\nTarget Aliases:\n", append=True),
    ]
    mock_help.assert_has_calls(calls)

    # No environment provided
    # Git commit 7a95cef7: Normally you expect something like ``patch("SCons.Script.SConscript.SConsEnvironment...")``
    # but Python <=3.10 chokes on the expected patch, so patch the WAVES module itself instead.
    with patch("waves.scons_extensions.SConsEnvironment.Help") as mock_help:
        scons_extensions.project_help_aliases()
    mock_help.assert_called_once_with(ANY, "\nTarget Aliases:\n", append=True, keep_local=True)

    # Provide environment with no aliases
    env = SCons.Environment.Environment()
    # Git commit 7a95cef7: Normally you expect something like ``patch("SCons.Script.SConscript.SConsEnvironment...")``
    # but Python <=3.10 chokes on the expected patch, so patch the WAVES module itself instead.
    with patch("waves.scons_extensions.SConsEnvironment.Help") as mock_help:
        scons_extensions.project_help_aliases(env)
    mock_help.assert_called_once_with(ANY, "\nTarget Aliases:\n", append=True, keep_local=True)

    # Provide environment with alias
    env.Alias("dummy_alias", "dummy.target")
    # Git commit 7a95cef7: Normally you expect something like ``patch("SCons.Script.SConscript.SConsEnvironment...")``
    # but Python <=3.10 chokes on the expected patch, so patch the WAVES module itself instead.
    with patch("waves.scons_extensions.SConsEnvironment.Help") as mock_help:
        scons_extensions.project_help_aliases(env)
    mock_help.assert_called_once_with(ANY, "\nTarget Aliases:\n    dummy_alias\n", append=True, keep_local=True)

    # Test the Method style interface
    env.AddMethod(scons_extensions.project_help_aliases, "ProjectHelp")
    # Git commit 7a95cef7: Normally you expect something like ``patch("SCons.Script.SConscript.SConsEnvironment...")``
    # but Python <=3.10 chokes on the expected patch, so patch the WAVES module itself instead.
    with patch("waves.scons_extensions.SConsEnvironment.Help") as mock_help:
        env.ProjectHelp()
    mock_help.assert_called_once_with(ANY, "\nTarget Aliases:\n    dummy_alias\n", append=True, keep_local=True)


# TODO: Deprecate the old function name
# https://re-git.lanl.gov/aea/python-projects/waves/-/issues/862
def test_project_help_message():
    env = SCons.Environment.Environment()
    env.AddMethod(scons_extensions.project_help_message, "ProjectHelp")
    default_kwargs = {"env": ANY, "append": True, "keep_local": True, "target_descriptions": None}
    non_default_kwargs = {
        "env": env,
        "append": False,
        "keep_local": False,
        "target_descriptions": {"somekey": "somevalue"},
    }
    method_interface_non_default_kwargs = {key: value for key, value in non_default_kwargs.items() if key != "env"}
    # Default behavior
    with (
        patch("waves.scons_extensions.project_help_default_targets") as mock_targets,
        patch("waves.scons_extensions.SConsEnvironment.Help") as mock_help,
        patch("waves.scons_extensions.project_help_aliases") as mock_alias,
        patch("warnings.warn") as warning,
    ):
        scons_extensions.project_help_message()
        warning.assert_called_once()
        mock_targets.assert_called_once_with(**default_kwargs)
        mock_alias.assert_called_once_with(**default_kwargs)

    # Pass non-default kwargs
    with (
        patch("waves.scons_extensions.project_help_default_targets") as mock_targets,
        patch("waves.scons_extensions.project_help_aliases") as mock_alias,
    ):
        scons_extensions.project_help_message(**non_default_kwargs)
        mock_targets.assert_called_once_with(**non_default_kwargs)
        mock_alias.assert_called_once_with(**non_default_kwargs)

    # Test the Method style interface
    with (
        patch("waves.scons_extensions.project_help_default_targets") as mock_targets,
        patch("waves.scons_extensions.project_help_aliases") as mock_alias,
    ):
        env.ProjectHelp()
        mock_targets.assert_called_once_with(**default_kwargs)
        mock_alias.assert_called_once_with(**default_kwargs)

    # Test the Method style interface, non-default kwargs
    with (
        patch("waves.scons_extensions.project_help_default_targets") as mock_targets,
        patch("waves.scons_extensions.project_help_aliases") as mock_alias,
    ):
        env.ProjectHelp(**method_interface_non_default_kwargs)
        mock_targets.assert_called_once_with(**non_default_kwargs)
        mock_alias.assert_called_once_with(**non_default_kwargs)


def test_project_help():
    env = SCons.Environment.Environment()
    env.AddMethod(scons_extensions.project_help, "ProjectHelp")
    default_kwargs = {"env": ANY, "append": True, "keep_local": True, "target_descriptions": None}
    non_default_kwargs = {
        "env": env,
        "append": False,
        "keep_local": False,
        "target_descriptions": {"somekey": "somevalue"},
    }
    method_interface_non_default_kwargs = {key: value for key, value in non_default_kwargs.items() if key != "env"}
    # Default behavior
    with (
        patch("waves.scons_extensions.project_help_default_targets") as mock_targets,
        patch("waves.scons_extensions.project_help_aliases") as mock_alias,
    ):
        scons_extensions.project_help()
        mock_targets.assert_called_once_with(**default_kwargs)
        mock_alias.assert_called_once_with(**default_kwargs)

    # Pass non-default kwargs
    with (
        patch("waves.scons_extensions.project_help_default_targets") as mock_targets,
        patch("waves.scons_extensions.project_help_aliases") as mock_alias,
    ):
        scons_extensions.project_help(**non_default_kwargs)
        mock_targets.assert_called_once_with(**non_default_kwargs)
        mock_alias.assert_called_once_with(**non_default_kwargs)

    # Test the Method style interface
    with (
        patch("waves.scons_extensions.project_help_default_targets") as mock_targets,
        patch("waves.scons_extensions.project_help_aliases") as mock_alias,
    ):
        env.ProjectHelp()
        mock_targets.assert_called_once_with(**default_kwargs)
        mock_alias.assert_called_once_with(**default_kwargs)

    # Test the Method style interface, non-default kwargs
    with (
        patch("waves.scons_extensions.project_help_default_targets") as mock_targets,
        patch("waves.scons_extensions.project_help_aliases") as mock_alias,
    ):
        env.ProjectHelp(**method_interface_non_default_kwargs)
        mock_targets.assert_called_once_with(**non_default_kwargs)
        mock_alias.assert_called_once_with(**non_default_kwargs)


project_aliases = {
    "First Alias": (
        [SCons.Environment.Environment(), "dummy_alias"],
        {"description": "dummy_hint", "expected": "kwarg"},
        ["dummy_alias"],
        {"expected": "kwarg"},
        {"dummy_alias": "dummy_hint"},
        True,
    ),
    "Second Alias": (
        [SCons.Environment.Environment(), "dummy_alias2"],
        {"description": "dummy_hint2", "expected2": "kwarg"},
        ["dummy_alias2"],
        {"expected2": "kwarg"},
        {"dummy_alias2": "dummy_hint2"},
        True,
    ),
    "None": ([None, None], {}, None, {}, {}, False),
}


@pytest.mark.parametrize(
    "args, kwargs, expected_alias_args, expected_alias_kwargs, expected_description, expect_called",
    project_aliases.values(),
    ids=project_aliases.keys(),
)
def test_project_alias(args, kwargs, expected_alias_args, expected_alias_kwargs, expected_description, expect_called):
    with patch("SCons.Environment.Base.Alias", return_value=args[1:]) as mock_alias:
        target_descriptions = scons_extensions.project_alias(*args, **kwargs, target_descriptions={})
        assert target_descriptions == expected_description
    if expect_called:
        mock_alias.assert_called_once_with(*expected_alias_args, **expected_alias_kwargs)
    else:
        mock_alias.assert_not_called()


def test_project_alias_accumulated_target_descriptions():
    dependent_aliases = [
        (
            [SCons.Environment.Environment(), "dummy_alias"],
            {"description": "dummy_hint"},
            {"dummy_alias": "dummy_hint"},
        ),
        (
            [SCons.Environment.Environment(), "dummy_alias2"],
            {"description": "dummy_hint2"},
            {"dummy_alias": "dummy_hint", "dummy_alias2": "dummy_hint2"},
        ),
        (
            [SCons.Environment.Environment(), "dummy_alias3"],
            {"description": "dummy_hint3"},
            {"dummy_alias": "dummy_hint", "dummy_alias2": "dummy_hint2", "dummy_alias3": "dummy_hint3"},
        ),
        (
            [SCons.Environment.Environment(), "dummy_alias2"],
            {"description": "changed_hint"},
            {"dummy_alias": "dummy_hint", "dummy_alias2": "changed_hint", "dummy_alias3": "dummy_hint3"},
        ),
    ]
    for args, kwargs, expected_description in dependent_aliases:
        with patch("SCons.Environment.Base.Alias", return_value=args[1:]):
            target_descriptions = scons_extensions.project_alias(*args, **kwargs)
            assert target_descriptions == expected_description


project_help_descriptions = {
    "No Descriptions": (["dummy_alias", "dummy_alias2"], {}, {}, "", "    dummy_alias\n    dummy_alias2\n"),
    "Existing Descriptions": (
        ["dummy_alias", "dummy_alias2"],
        {"dummy_alias": "dummy_description"},
        {},
        "",
        "    dummy_alias: dummy_description\n    dummy_alias2\n",
    ),
    "Target Descriptions": (
        ["dummy_alias", "dummy_alias2"],
        {},
        {"dummy_alias": "dummy_description"},
        "",
        "    dummy_alias: dummy_description\n    dummy_alias2\n",
    ),
    "Existing Message": (
        ["dummy_alias", "dummy_alias2"],
        {},
        {"dummy_alias": "dummy_description"},
        "Existing Message\n",
        "Existing Message\n    dummy_alias: dummy_description\n    dummy_alias2\n",
    ),
    "Override Description": (
        ["dummy_alias"],
        {"dummy_alias": "dummy_description"},
        {"dummy_alias": "dummy_description2"},
        "",
        "    dummy_alias: dummy_description2\n",
    ),
}


@pytest.mark.parametrize(
    "nodes, existing_descriptions, target_descriptions, message, expected",
    project_help_descriptions.values(),
    ids=project_help_descriptions.keys(),
)
def test_project_help_descriptions(nodes, existing_descriptions, target_descriptions, message, expected):
    with patch("waves.scons_extensions.project_alias", return_value=existing_descriptions) as mock_project_alias:
        appended_message = scons_extensions._project_help_descriptions(
            nodes, target_descriptions=target_descriptions, message=message
        )
        assert appended_message == expected
        mock_project_alias.assert_called_once()
