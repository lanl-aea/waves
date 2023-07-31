import os
import pathlib
import unittest
from unittest.mock import patch, call

import pytest
import SCons

from waves import scons
from common import platform_check


testing_windows, root_fs = platform_check()

find_program_input = {
    "string": (
        "dummy",
        ["/installed/executable/dummy"],
        "/installed/executable/dummy"),
    "one path": (
        ["dummy"],
        ["/installed/executable/dummy"],
        "/installed/executable/dummy"),
    "first missing": (
        ["notfound", "dummy"],
        [None, "/installed/executable/dummy"],
        "/installed/executable/dummy"),
    "two found": (
        ["dummy", "dummy1"],
        ["/installed/executable/dummy", "/installed/executable/dummy1"],
        "/installed/executable/dummy"),
    "none found": (
        ["notfound", "dummy"],
        [None, None],
        None),
    "path with spaces": (
        ["dummy"],
        ["/installed/executable with space/dummy"],
        "/installed/\"executable with space\"/dummy"
    )
}


@pytest.mark.skipif(testing_windows, reason="Tests trigger 'SCons user error' on Windows. Believed to be a test construction error, not a test failure.")
@pytest.mark.unittest
@pytest.mark.parametrize("names, checkprog_side_effect, first_found_path",
                         find_program_input.values(),
                         ids=find_program_input.keys())
def test_find_program(names, checkprog_side_effect, first_found_path):
    env = SCons.Environment.Environment()
    mock_conf = unittest.mock.Mock()
    mock_conf.CheckProg = unittest.mock.Mock(side_effect=checkprog_side_effect)
    with patch("SCons.SConf.SConfBase", return_value=mock_conf):
        program = scons.find_program(names, env)
    assert program == first_found_path


@pytest.mark.skipif(testing_windows, reason="Tests trigger 'SCons user error' on Windows. Believed to be a test construction error, not a test failure.")
@pytest.mark.unittest
@pytest.mark.parametrize("names, checkprog_side_effect, first_found_path",
                         find_program_input.values(),
                         ids=find_program_input.keys())
def test_add_program(names, checkprog_side_effect, first_found_path):
    env = SCons.Environment.Environment()
    original_path = env["ENV"]["PATH"]
    mock_conf = unittest.mock.Mock()
    mock_conf.CheckProg = unittest.mock.Mock(side_effect=checkprog_side_effect)
    with patch("SCons.SConf.SConfBase", return_value=mock_conf), \
         patch("pathlib.Path.exists", return_value=True):
        program = scons.add_program(names, env)
    assert program == first_found_path
    if first_found_path is not None:
        parent_path = str(pathlib.Path(first_found_path).parent)
        assert parent_path == env["ENV"]["PATH"].split(os.pathsep)[-1]
    else:
        assert original_path == env["ENV"]["PATH"]


@pytest.mark.skipif(testing_windows, reason="Tests trigger 'SCons user error' on Windows. Believed to be a test construction error, not a test failure.")
@pytest.mark.unittest
@pytest.mark.parametrize("names, checkprog_side_effect, first_found_path",
                         find_program_input.values(),
                         ids=find_program_input.keys())
def test_add_cubit(names, checkprog_side_effect, first_found_path):
    env = SCons.Environment.Environment()
    original_path = env["ENV"]["PATH"]
    mock_conf = unittest.mock.Mock()
    mock_conf.CheckProg = unittest.mock.Mock(side_effect=checkprog_side_effect)
    with patch("SCons.SConf.SConfBase", return_value=mock_conf), \
         patch("pathlib.Path.exists", return_value=True):
        program = scons.add_cubit(names, env)
    assert program == first_found_path
    if first_found_path is not None:
        parent_path = pathlib.Path(first_found_path).parent
        cubit_pythonpath = parent_path / "bin"
        cubit_library_path = cubit_pythonpath / "python3"
        assert str(parent_path) == env["ENV"]["PATH"].split(os.pathsep)[-1]
        assert str(cubit_pythonpath) == env["ENV"]["PYTHONPATH"].split(os.pathsep)[0]
        assert str(cubit_library_path) == env["ENV"]["LD_LIBRARY_PATH"].split(os.pathsep)[0]
    else:
        assert original_path == env["ENV"]["PATH"]
