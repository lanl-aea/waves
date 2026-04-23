"""Test system API calls that require real shell execution."""

import contextlib
import shutil
import subprocess

import pytest

from waves import _utilities

does_not_raise = contextlib.nullcontext()

sh = shutil.which("sh")
bash = shutil.which("bash")
zsh = shutil.which("zsh")
csh = shutil.which("csh")
tcsh = shutil.which("tcsh")
dash = shutil.which("dash")
ksh = shutil.which("ksh")

test_return_environment_cases = (
    pytest.param(
        "export THING_ONE=Bim && export THING_TWO=Ben",
        {},
        {"THING_ONE": "Bim", "THING_TWO": "Ben"},
        does_not_raise,
        marks=[pytest.mark.skipif(bash is None, reason="bash is required, but not found")],
        id="(default) bash variable export",
    ),
    pytest.param(
        "exit 1",
        {},
        None,
        pytest.raises(subprocess.CalledProcessError),
        marks=[pytest.mark.skipif(bash is None, reason="bash is required, but not found")],
        id="(default) bash exit 1",
    ),
    pytest.param(
        "export THING_ONE=Bim && export THING_TWO=Ben",
        {"shell": bash},
        {"THING_ONE": "Bim", "THING_TWO": "Ben"},
        does_not_raise,
        marks=[pytest.mark.skipif(bash is None, reason="bash is required, but not found")],
        id="(explicit) bash variable export",
    ),
    pytest.param(
        "exit 1",
        {"shell": bash},
        None,
        pytest.raises(subprocess.CalledProcessError),
        marks=[pytest.mark.skipif(bash is None, reason="bash is required, but not found")],
        id="(explicit) bash exit 1",
    ),
    pytest.param(
        "export THING_ONE=Bim && export THING_TWO=Ben",
        {"shell": sh},
        {"THING_ONE": "Bim", "THING_TWO": "Ben"},
        does_not_raise,
        marks=[pytest.mark.skipif(sh is None, reason="sh is required, but not found")],
        id="sh variable export",
    ),
    pytest.param(
        "exit 1",
        {"shell": sh},
        None,
        pytest.raises(subprocess.CalledProcessError),
        marks=[pytest.mark.skipif(sh is None, reason="sh is required, but not found")],
        id="sh exit 1",
    ),
    pytest.param(
        "export THING_ONE=Bim && export THING_TWO=Ben",
        {"shell": zsh},
        {"THING_ONE": "Bim", "THING_TWO": "Ben"},
        does_not_raise,
        marks=[pytest.mark.skipif(zsh is None, reason="zsh is required, but not found")],
        id="zsh variable export",
    ),
    pytest.param(
        "exit 1",
        {"shell": zsh},
        None,
        pytest.raises(subprocess.CalledProcessError),
        marks=[pytest.mark.skipif(zsh is None, reason="zsh is required, but not found")],
        id="zsh exit 1",
    ),
    pytest.param(
        "setenv THING_ONE Bim && setenv THING_TWO Ben",
        {"shell": csh},
        {"THING_ONE": "Bim", "THING_TWO": "Ben"},
        does_not_raise,
        marks=[pytest.mark.skipif(csh is None, reason="csh is required, but not found")],
        id="csh variable setenv",
    ),
    pytest.param(
        "exit 1",
        {"shell": csh},
        None,
        pytest.raises(subprocess.CalledProcessError),
        marks=[pytest.mark.skipif(csh is None, reason="csh is required, but not found")],
        id="csh variable setenv",
    ),
    pytest.param(
        "setenv THING_ONE Bim && setenv THING_TWO Ben",
        {"shell": tcsh},
        {"THING_ONE": "Bim", "THING_TWO": "Ben"},
        does_not_raise,
        marks=[pytest.mark.skipif(tcsh is None, reason="tcsh is required, but not found")],
        id="tcsh variable setenv",
    ),
    pytest.param(
        "exit 1",
        {"shell": tcsh},
        None,
        pytest.raises(subprocess.CalledProcessError),
        marks=[pytest.mark.skipif(tcsh is None, reason="tcsh is required, but not found")],
        id="tcsh variable setenv",
    ),
    pytest.param(
        "export THING_ONE=Bim && export THING_TWO=Ben",
        {"shell": dash},
        {"THING_ONE": "Bim", "THING_TWO": "Ben"},
        does_not_raise,
        marks=[pytest.mark.skipif(dash is None, reason="dash is required, but not found")],
        id="dash variable export",
    ),
    pytest.param(
        "exit 1",
        {"shell": dash},
        None,
        pytest.raises(subprocess.CalledProcessError),
        marks=[pytest.mark.skipif(dash is None, reason="dash is required, but not found")],
        id="dash exit 1",
    ),
    pytest.param(
        "export THING_ONE=Bim && export THING_TWO=Ben",
        {"shell": ksh},
        {"THING_ONE": "Bim", "THING_TWO": "Ben"},
        does_not_raise,
        marks=[pytest.mark.skipif(ksh is None, reason="ksh is required, but not found")],
        id="ksh variable export",
    ),
    pytest.param(
        "exit 1",
        {"shell": ksh},
        None,
        pytest.raises(subprocess.CalledProcessError),
        marks=[pytest.mark.skipif(ksh is None, reason="ksh is required, but not found")],
        id="ksh exit 1",
    ),
    pytest.param(
        "export THING_ONE=Bim && export THING_TWO=Ben",
        {"shell": "notashell"},
        None,
        pytest.raises(FileNotFoundError),
        id="shell not found",
    ),
)


@pytest.mark.systemtest
@pytest.mark.parametrize(("command", "kwargs", "expected", "outcome"), test_return_environment_cases)
def test_return_environment(
    command: str,
    kwargs: dict[str, str],
    expected: dict[str, str],
    outcome: contextlib.nullcontext | pytest.RaisesExc,
) -> None:
    with outcome:
        environment = _utilities.return_environment(command, **kwargs)
        for key, value in expected.items():
            assert key in environment
            assert environment[key] == value


@pytest.mark.systemtest
@pytest.mark.parametrize(("command", "kwargs", "expected", "outcome"), test_return_environment_cases)
def test_cache_environment(
    command: str,
    kwargs: dict[str, str],
    expected: dict[str, str],
    outcome: contextlib.nullcontext | pytest.RaisesExc,
) -> None:
    with outcome:
        environment = _utilities.cache_environment(command, **kwargs)
        for key, value in expected.items():
            assert key in environment
            assert environment[key] == value
