"""Test system API calls that require real shell execution."""

import shutil

import pytest

from waves import _utilities

sh = shutil.which("sh")
bash = shutil.which("bash")
zsh = shutil.which("zsh")
csh = shutil.which("csh")
tcsh = shutil.which("tcsh")

test_return_environment_cases = (
    pytest.param(
        "export MY_VAR=VALUE",
        {},
        {"MY_VAR": "VALUE"},
        marks=[pytest.mark.skipif(bash is None, reason="bash is required, but not found")],
        id="(default) bash variable export",
    ),
    pytest.param(
        "export MY_VAR=VALUE",
        {"shell": bash},
        {"MY_VAR": "VALUE"},
        marks=[pytest.mark.skipif(bash is None, reason="bash is required, but not found")],
        id="(explicit) bash variable export",
    ),
    pytest.param(
        "export MY_VAR=VALUE",
        {"shell": sh},
        {"MY_VAR": "VALUE"},
        marks=[pytest.mark.skipif(sh is None, reason="sh is required, but not found")],
        id="sh variable export",
    ),
    pytest.param(
        "export MY_VAR=VALUE",
        {"shell": zsh},
        {"MY_VAR": "VALUE"},
        marks=[pytest.mark.skipif(zsh is None, reason="zsh is required, but not found")],
        id="zsh variable export",
    ),
    pytest.param(
        "setenv MY_VAR VALUE",
        {"shell": csh},
        {"MY_VAR": "VALUE"},
        marks=[pytest.mark.skipif(csh is None, reason="csh is required, but not found")],
        id="csh variable setenv",
    ),
    pytest.param(
        "setenv MY_VAR VALUE",
        {"shell": tcsh},
        {"MY_VAR": "VALUE"},
        marks=[pytest.mark.skipif(tcsh is None, reason="tcsh is required, but not found")],
        id="tcsh variable setenv",
    ),
)


@pytest.mark.parametrize(("command", "kwargs", "expected"), test_return_environment_cases)
def test_return_environment(command: str, kwargs: dict[str, str], expected: dict[str, str]) -> None:
    environment = _utilities.return_environment(command, **kwargs)
    for key, value in expected.items():
        assert key in environment
        assert environment[key] == value


@pytest.mark.parametrize(("command", "kwargs", "expected"), test_return_environment_cases)
def test_cache_environment(command: str, kwargs: dict, expected: dict[str, str]) -> None:
    environment = _utilities.cache_environment(command, **kwargs)
    for key, value in expected.items():
        assert key in environment
        assert environment[key] == value
