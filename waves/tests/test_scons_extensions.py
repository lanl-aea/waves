"""Test WAVES SCons builders and support functions"""
import os
import pathlib
from contextlib import nullcontext as does_not_raise
import unittest
from unittest.mock import patch, call
import subprocess

import pytest
import SCons.Node.FS

from waves import parameter_generators
from waves import scons_extensions
from waves import parameter_generators
from waves._settings import _cd_action_prefix
from waves._settings import _redirect_action_suffix
from waves._settings import _redirect_environment_suffix
from waves._settings import _abaqus_environment_extension
from waves._settings import _abaqus_datacheck_extensions
from waves._settings import _abaqus_explicit_extensions
from waves._settings import _abaqus_standard_extensions
from waves._settings import _abaqus_solver_common_suffixes
from waves._settings import _sbatch_wrapper_options
from waves._settings import _stdout_extension
from common import platform_check


# Test setup and helper functions
fs = SCons.Node.FS.FS()

testing_windows, root_fs = platform_check()


check_program = {
    "found": ("program", "/usr/bin/program", "Checking whether 'program' program exists.../usr/bin/program"),
    "not found": ("program", None, "Checking whether 'program' program exists...no"),
}


@pytest.mark.parametrize("prog_name, shutil_return_value, message",
                         check_program.values(),
                         ids=check_program.keys())
def test_check_program(prog_name, shutil_return_value, message):
    env = SCons.Environment.Environment()

    # Test function style interface
    with patch("shutil.which", return_value=shutil_return_value), \
         patch("builtins.print") as mock_print:
        returned_absolute_path = scons_extensions.check_program(env, prog_name)
        assert returned_absolute_path == shutil_return_value
        mock_print.assert_called_once_with(message)

    # Test SCons AddMethod style interface
    env.AddMethod(scons_extensions.check_program, "CheckProgram")
    with patch("shutil.which", return_value=shutil_return_value), \
         patch("builtins.print") as mock_print:
        returned_absolute_path = env.CheckProgram(prog_name)
        assert returned_absolute_path == shutil_return_value
        mock_print.assert_called_once_with(message)


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
@pytest.mark.parametrize("names, checkprog_side_effect, first_found_path",
                         find_program_input.values(),
                         ids=find_program_input.keys())
def test_find_program(names, checkprog_side_effect, first_found_path):
    env = SCons.Environment.Environment()

    # Test function style interface
    with patch("waves.scons_extensions.check_program", side_effect=checkprog_side_effect):
        program = scons_extensions.find_program(env, names)
    assert program == first_found_path

    # Test SCons AddMethod style interface
    env.AddMethod(scons_extensions.find_program, "FindProgram")
    with patch("waves.scons_extensions.check_program", side_effect=checkprog_side_effect):
        program = env.FindProgram(names)
    assert program == first_found_path

    # TODO: Remove reversed arguments test after full deprecation of the older argument order
    # https://re-git.lanl.gov/aea/python-projects/waves/-/issues/755
    with patch("waves.scons_extensions.check_program", side_effect=checkprog_side_effect), \
         patch("warnings.warn") as mock_warn:
        program = scons_extensions.find_program(names, env)
        mock_warn.assert_called_once()
    assert program == first_found_path


@pytest.mark.skipif(testing_windows, reason="Tests trigger 'SCons user error' on Windows. Believed to be a test construction error, not a test failure.")
@pytest.mark.parametrize("names, checkprog_side_effect, first_found_path",
                         find_program_input.values(),
                         ids=find_program_input.keys())
def test_add_program(names, checkprog_side_effect, first_found_path):
    # Test function style interface
    env = SCons.Environment.Environment()
    original_path = env["ENV"]["PATH"]
    with patch("waves.scons_extensions.check_program", side_effect=checkprog_side_effect), \
         patch("pathlib.Path.exists", return_value=True):
        program = scons_extensions.add_program(env, names)
    assert program == first_found_path
    if first_found_path is not None:
        parent_path = str(pathlib.Path(first_found_path).parent)
        assert parent_path == env["ENV"]["PATH"].split(os.pathsep)[-1]
    else:
        assert original_path == env["ENV"]["PATH"]

    # Test SCons AddMethod style interface
    env = SCons.Environment.Environment()
    original_path = env["ENV"]["PATH"]
    env.AddMethod(scons_extensions.add_program, "AddProgram")
    with patch("waves.scons_extensions.check_program", side_effect=checkprog_side_effect), \
         patch("pathlib.Path.exists", return_value=True):
        program = env.AddProgram(names)
    assert program == first_found_path
    if first_found_path is not None:
        parent_path = str(pathlib.Path(first_found_path).parent)
        assert parent_path == env["ENV"]["PATH"].split(os.pathsep)[-1]
    else:
        assert original_path == env["ENV"]["PATH"]

    # TODO: Remove reversed arguments test after full deprecation of the older argument order
    # https://re-git.lanl.gov/aea/python-projects/waves/-/issues/755
    env = SCons.Environment.Environment()
    original_path = env["ENV"]["PATH"]
    with patch("waves.scons_extensions.check_program", side_effect=checkprog_side_effect), \
         patch("pathlib.Path.exists", return_value=True), \
         patch("warnings.warn") as mock_warn:
        program = scons_extensions.add_program(names, env)
        mock_warn.assert_called_once()
    assert program == first_found_path
    if first_found_path is not None:
        parent_path = str(pathlib.Path(first_found_path).parent)
        assert parent_path == env["ENV"]["PATH"].split(os.pathsep)[-1]
    else:
        assert original_path == env["ENV"]["PATH"]


@pytest.mark.skipif(testing_windows, reason="Tests trigger 'SCons user error' on Windows. Believed to be a test construction error, not a test failure.")
@pytest.mark.parametrize("names, checkprog_side_effect, first_found_path",
                         find_program_input.values(),
                         ids=find_program_input.keys())
def test_add_cubit(names, checkprog_side_effect, first_found_path):

    # Test function style interface
    env = SCons.Environment.Environment()
    original_path = env["ENV"]["PATH"]
    if first_found_path is not None:
        find_cubit_bin_return = pathlib.Path(first_found_path).parent / "bin"
    else:
        find_cubit_bin_return = None
    with patch("waves._utilities.find_cubit_bin", return_value=find_cubit_bin_return), \
         patch("waves.scons_extensions.check_program", side_effect=checkprog_side_effect), \
         patch("pathlib.Path.exists", return_value=True):
        program = scons_extensions.add_cubit(env, names)
    assert program == first_found_path
    if first_found_path is not None:
        parent_path = pathlib.Path(first_found_path).parent
        cubit_bin = parent_path / "bin"
        cubit_library_path = cubit_bin / "python3"
        assert str(parent_path) == env["ENV"]["PATH"].split(os.pathsep)[-1]
        assert str(cubit_bin) == env["ENV"]["PYTHONPATH"].split(os.pathsep)[0]
        assert str(cubit_library_path) == env["ENV"]["LD_LIBRARY_PATH"].split(os.pathsep)[0]
    else:
        assert original_path == env["ENV"]["PATH"]

    # Test SCons AddMethod style interface
    env = SCons.Environment.Environment()
    env.AddMethod(scons_extensions.add_cubit, "AddCubit")
    original_path = env["ENV"]["PATH"]
    if first_found_path is not None:
        find_cubit_bin_return = pathlib.Path(first_found_path).parent / "bin"
    else:
        find_cubit_bin_return = None
    with patch("waves._utilities.find_cubit_bin", return_value=find_cubit_bin_return), \
         patch("waves.scons_extensions.check_program", side_effect=checkprog_side_effect), \
         patch("pathlib.Path.exists", return_value=True):
        program = env.AddCubit(names)
    assert program == first_found_path
    if first_found_path is not None:
        parent_path = pathlib.Path(first_found_path).parent
        cubit_bin = parent_path / "bin"
        cubit_library_path = cubit_bin / "python3"
        assert str(parent_path) == env["ENV"]["PATH"].split(os.pathsep)[-1]
        assert str(cubit_bin) == env["ENV"]["PYTHONPATH"].split(os.pathsep)[0]
        assert str(cubit_library_path) == env["ENV"]["LD_LIBRARY_PATH"].split(os.pathsep)[0]
    else:
        assert original_path == env["ENV"]["PATH"]

    # TODO: Remove reversed arguments test after full deprecation of the older argument order
    # https://re-git.lanl.gov/aea/python-projects/waves/-/issues/755
    env = SCons.Environment.Environment()
    original_path = env["ENV"]["PATH"]
    if first_found_path is not None:
        find_cubit_bin_return = pathlib.Path(first_found_path).parent / "bin"
    else:
        find_cubit_bin_return = None
    with patch("waves._utilities.find_cubit_bin", return_value=find_cubit_bin_return), \
         patch("waves.scons_extensions.check_program", side_effect=checkprog_side_effect), \
         patch("pathlib.Path.exists", return_value=True), \
         patch("warnings.warn") as mock_warn:
        program = scons_extensions.add_cubit(names, env)
        mock_warn.assert_called_once()
    assert program == first_found_path
    if first_found_path is not None:
        parent_path = pathlib.Path(first_found_path).parent
        cubit_bin = parent_path / "bin"
        cubit_library_path = cubit_bin / "python3"
        assert str(parent_path) == env["ENV"]["PATH"].split(os.pathsep)[-1]
        assert str(cubit_bin) == env["ENV"]["PYTHONPATH"].split(os.pathsep)[0]
        assert str(cubit_library_path) == env["ENV"]["LD_LIBRARY_PATH"].split(os.pathsep)[0]
    else:
        assert original_path == env["ENV"]["PATH"]


def test_add_cubit_python():

    # Test function style interface
    env = SCons.Environment.Environment()
    cubit_bin = "/path/to/cubit/bin/"
    cubit_python = "/path/to/cubit/bin/python"
    # Cubit Python not found mocked by add_program
    with patch("waves._utilities.find_cubit_python"), \
         patch("waves.scons_extensions.find_program"), \
         patch("waves.scons_extensions.add_program", return_value=None):
        program = scons_extensions.add_cubit_python(env, "dummy_cubit_executable")
    assert program == None
    assert "PYTHONPATH" not in env["ENV"]
    # Cubit Python found mocked by add_program
    with patch("waves._utilities.find_cubit_python"), \
         patch("waves.scons_extensions.find_program"), \
         patch("waves.scons_extensions.add_program", return_value=cubit_python), \
         patch("waves._utilities.find_cubit_bin", return_value=cubit_bin):
        program = scons_extensions.add_cubit_python(env, "dummy_cubit_executable")
    assert program == cubit_python
    assert env["ENV"]["PYTHONPATH"].split(os.pathsep)[0] == str(cubit_bin)

    # Test SCons AddMethod style interface
    env = SCons.Environment.Environment()
    env.AddMethod(scons_extensions.add_cubit_python, "AddCubitPython")
    cubit_bin = "/path/to/cubit/bin/"
    cubit_python = "/path/to/cubit/bin/python"
    # Cubit Python not found mocked by add_program
    with patch("waves._utilities.find_cubit_python"), \
         patch("waves.scons_extensions.find_program"), \
         patch("waves.scons_extensions.add_program", return_value=None):
        program = env.AddCubitPython("dummy_cubit_executable")
    assert program == None
    assert "PYTHONPATH" not in env["ENV"]
    # Cubit Python found mocked by add_program
    with patch("waves._utilities.find_cubit_python"), \
         patch("waves.scons_extensions.find_program"), \
         patch("waves.scons_extensions.add_program", return_value=cubit_python), \
         patch("waves._utilities.find_cubit_bin", return_value=cubit_bin):
        program = scons_extensions.add_cubit_python(env, "dummy_cubit_executable")
    assert program == cubit_python
    assert env["ENV"]["PYTHONPATH"].split(os.pathsep)[0] == str(cubit_bin)

    # TODO: Remove reversed arguments test after full deprecation of the older argument order
    # https://re-git.lanl.gov/aea/python-projects/waves/-/issues/755
    env = SCons.Environment.Environment()
    cubit_bin = "/path/to/cubit/bin/"
    cubit_python = "/path/to/cubit/bin/python"
    # Cubit Python not found mocked by add_program
    with patch("waves._utilities.find_cubit_python"), \
         patch("waves.scons_extensions.find_program"), \
         patch("waves.scons_extensions.add_program", return_value=None), \
         patch("warnings.warn") as mock_warn:
        program = scons_extensions.add_cubit_python("dummy_cubit_executable", env)
        mock_warn.assert_called_once()
    assert program == None
    assert "PYTHONPATH" not in env["ENV"]
    # Cubit Python found mocked by add_program
    with patch("waves._utilities.find_cubit_python"), \
         patch("waves.scons_extensions.find_program"), \
         patch("waves.scons_extensions.add_program", return_value=cubit_python), \
         patch("waves._utilities.find_cubit_bin", return_value=cubit_bin), \
         patch("warnings.warn") as mock_warn:
        program = scons_extensions.add_cubit_python("dummy_cubit_executable", env)
        mock_warn.assert_called_once()
    assert program == cubit_python
    assert env["ENV"]["PYTHONPATH"].split(os.pathsep)[0] == str(cubit_bin)


def dummy_emitter_for_testing(target, source, env):
    return target, source


def check_action_string(nodes, expected_node_count, expected_action_count, expected_string):
    """Verify the expected action string against a builder's target nodes

    :param SCons.Node.NodeList nodes: Target node list returned by a builder
    :param int expected_node_count: expected length of ``nodes``
    :param int expected_action_count: expected length of action list for each node
    :param str expected_string: the builder's action string.

    .. note::

       The method of interrogating a node's action list results in a newline separated string instead of a list of
       actions. The ``expected_string`` should contain all elements of the expected action list as a single, newline
       separated string. The ``action_count`` should be set to ``1`` until this method is updated to search for the
       finalized action list.
    """
    assert len(nodes) == expected_node_count
    for node in nodes:
        node.get_executor()
        assert len(node.executor.action_list) == expected_action_count
        assert str(node.executor.action_list[0]) == expected_string


def check_abaqus_solver_targets(nodes, solver, stem, suffixes):
    """Verify the expected action string against a builder's target nodes

    :param SCons.Node.NodeList nodes: Target node list returned by a builder
    :param str solver: emit file extensions based on the value of this variable (standard/explicit/datacheck).
    :param str stem: stem name of file
    :param list suffixes: list of override suffixes provided to the task
    """
    expected_suffixes = [_stdout_extension, _abaqus_environment_extension]
    if suffixes:
        expected_suffixes.extend(suffixes)
    elif solver == 'standard':
        expected_suffixes.extend(_abaqus_standard_extensions)
    elif solver == 'explicit':
        expected_suffixes.extend(_abaqus_explicit_extensions)
    elif solver == 'datacheck':
        expected_suffixes.extend(_abaqus_datacheck_extensions)
    else:
        expected_suffixes.extend(_abaqus_solver_common_suffixes)
    suffixes = [str(node).split(stem)[-1] for node in nodes]
    assert set(expected_suffixes) == set(suffixes)


def first_target_builder_factory_test_cases(
    name: str,
    default_kwargs: dict,
    default_emitter = scons_extensions.first_target_emitter,
    expected_node_count = 2
) -> dict:
    """Returns template test cases for builder factories based on
    :meth:`waves.scons_extensions.first_target_builder_factory`

    Intended to work in conjunction with :meth:`test_builder_factory` template test function.

    Required because tests involving real SCons tasks require unique target files, one per test. The returned dictionary
    constructs the target files names from ``{name}.out{number}``. Use as

    .. code-block::

        default_kwargs = {
            "environment": "",
            "action_prefix": _cd_action_prefix,
            "program": "",
            "program_required": "",
            "program_options": "",
            "subcommand": "",
            "subcommand_required": "",
            "subcommand_options": "",
            "action_suffix": _redirect_action_suffix
        }
        new_builder_factory_tests = first_target_builder_factory_test_cases("new_builder_factory", default_kwargs)
        @pytest.mark.parametrize("factory_name, default_kwargs, builder_kwargs, task_kwargs, target, emitter, expected_node_count",
                                 new_builder_factory_tests.values(),
                                 ids=new_builder_factory_tests.keys())
        def test_new_builder_factory(factory_name, default_kwargs, builder_kwargs, task_kwargs, target, emitter, expected_node_count):
            check_builder_factory(
                name=factory_name,
                default_kwargs=default_kwargs,
                builder_kwargs=builder_kwargs,
                task_kwargs=task_kwargs,
                target=target,
                default_emitter=scons_extensions.first_target_emitter,
                emitter=emitter,
                expected_node_count=expected_node_count
            )

    :param name: Target file name prefix. Target file names must be unique in the entire test suite, so matching the
        builder factory under test is a good choice.
    :param default_kwargs: Set the default keyword argument values. Expected to be constant as a function of builder
        factory under test.
    :param default_emitter: The emitter to expect when ``False`` is provided for ``emitter`` keyword argument.
    :param expected_node_count: The expected number of target nodes with the default emitter.

    :returns: test cases for builder factories based on :meth:`waves.scons_extensions.first_target_builder_factory`
    """
    target_file_names = [
        f"{name}.out{number}" for number in range(4)
    ]
    test_cases = {
        f"{name} default behavior": (
            name, default_kwargs, {}, {}, [target_file_names[0]], default_emitter, False, expected_node_count
        ),
        f"{name} different emitter": (
            name, default_kwargs, {}, {}, [target_file_names[1]], default_emitter, dummy_emitter_for_testing, 1
        ),
        f"{name} builder kwargs overrides": (
            name, default_kwargs,
            {
             "environment": "different environment",
             "action_prefix": "different action prefix",
             "program": "different program",
             "program_required": "different program required",
             "program_options": "different program options",
             "subcommand": "different subcommand",
             "subcommand_required": "different subcommand required",
             "subcommand_options": "different subcommand options",
             "action_suffix": "different action suffix"
            },
            {}, [target_file_names[2]], default_emitter, False, expected_node_count
        ),
        f"{name} task kwargs overrides": (
            name, default_kwargs,
            {},
            {
             "environment": "different environment",
             "action_prefix": "different action prefix",
             "program": "different program",
             "program_required": "different program required",
             "program_options": "different program options",
             "subcommand": "different subcommand",
             "subcommand_required": "different subcommand required",
             "subcommand_options": "different subcommand options",
             "action_suffix": "different action suffix"
            },
            [target_file_names[3]], default_emitter, False, expected_node_count
        ),
    }
    return test_cases


# Actual tests
def test_print_failed_nodes_stdout():
    mock_failure_file = unittest.mock.Mock()
    mock_failure_file.node = unittest.mock.Mock()
    mock_failure_file.node.abspath = "/failed_node_stdout.ext"
    with patch("SCons.Script.GetBuildFailures", return_value=[mock_failure_file]), \
         patch("pathlib.Path.exists", return_value=True) as mock_exists, \
         patch("builtins.open") as mock_open, \
         patch("builtins.print") as mock_print:
        scons_extensions._print_failed_nodes_stdout()
        mock_exists.assert_called_once()
        mock_open.assert_called_once()
        mock_print.assert_called_once()
    with patch("SCons.Script.GetBuildFailures", return_value=[mock_failure_file]), \
         patch("pathlib.Path.exists", return_value=False) as mock_exists, \
         patch("builtins.open") as mock_open, \
         patch("builtins.print") as mock_print:
        scons_extensions._print_failed_nodes_stdout()
        mock_exists.assert_called()
        mock_open.assert_not_called()
        mock_print.assert_called_once()


def test_print_build_failures():
    # Test the function call interface
    env = SCons.Environment.Environment()
    with patch("atexit.register") as mock_atexit:
        scons_extensions.print_build_failures(env=env, print_stdout=True)
        mock_atexit.assert_called_once_with(scons_extensions._print_failed_nodes_stdout)
    with patch("atexit.register") as mock_atexit:
        scons_extensions.print_build_failures(env=env, print_stdout=False)
        mock_atexit.assert_not_called()

    # Test the SCons AddMethod interface
    env.AddMethod(scons_extensions.print_build_failures, "PrintBuildFailures")
    with patch("atexit.register") as mock_atexit:
        env.PrintBuildFailures(True)
        mock_atexit.assert_called_once_with(scons_extensions._print_failed_nodes_stdout)
    with patch("atexit.register") as mock_atexit:
        env.PrintBuildFailures(False)
        mock_atexit.assert_not_called()

    # TODO: Remove if-structure after full deprecation of the older argument order
    # https://re-git.lanl.gov/aea/python-projects/waves/-/issues/758
    with patch("atexit.register") as mock_atexit, \
         patch("warnings.warn") as mock_warn:
        scons_extensions.print_build_failures(True)
        mock_atexit.assert_called_once_with(scons_extensions._print_failed_nodes_stdout)
        mock_warn.assert_called_once()
    with patch("atexit.register") as mock_atexit, \
         patch("warnings.warn") as mock_warn:
        scons_extensions.print_build_failures(False)
        mock_atexit.assert_not_called()
        mock_warn.assert_called_once()


action_list_scons = {
    "one action": (
        ["one action"], SCons.Action.ListAction([SCons.Action.CommandAction("one action")])
    ),
    "two actions": (
        ["first action", "second action"],
        SCons.Action.ListAction([SCons.Action.CommandAction("first action"), SCons.Action.CommandAction("second action")])
    )
}


@pytest.mark.parametrize("actions, expected",
                         action_list_scons.values(),
                         ids=action_list_scons.keys())
def test_action_list_scons(actions, expected):
    list_action = scons_extensions.action_list_scons(actions)
    assert list_action == expected


action_list_strings = {
    "one action": (SCons.Builder.Builder(action="one action"), ["one action"]),
    "two actions": (SCons.Builder.Builder(action=["first action", "second action"]), ["first action", "second action"]),
}


@pytest.mark.parametrize("builder, expected",
                         action_list_strings.values(),
                         ids=action_list_strings.keys())
def test_action_list_strings(builder, expected):
    action_list = scons_extensions.action_list_strings(builder)
    assert action_list == expected


catenate_builder_actions = {
    "one action - string": ("action one", "action one"),
    "one action - list": (["action one"], "action one"),
    "two action": (["action one", "action two"], "action one && action two")
}


@pytest.mark.parametrize("action_list, catenated_actions",
                         catenate_builder_actions.values(),
                         ids=catenate_builder_actions.keys())
def test_catenate_builder_actions(action_list, catenated_actions):
    builder = scons_extensions.catenate_builder_actions(
        SCons.Builder.Builder(action=action_list), program="bash", options="-c"
    )
    assert builder.action.cmd_list == f"bash -c \"{catenated_actions}\""


def test_catenate_actions():
    def cat(program="cat"):
        return SCons.Builder.Builder(action=f"{program} $SOURCE > $TARGET")
    builder = cat()
    assert builder.action.cmd_list == "cat $SOURCE > $TARGET"

    @scons_extensions.catenate_actions(program="bash", options="-c")
    def bash_cat(**kwargs):
        return cat(**kwargs)
    builder = bash_cat()
    assert builder.action.cmd_list == "bash -c \"cat $SOURCE > $TARGET\""
    builder = bash_cat(program="dog")
    assert builder.action.cmd_list == "bash -c \"dog $SOURCE > $TARGET\""


ssh_builder_actions = {
    "default kwargs": (["ssh_builder_actions.out1"], {}, {}),
    "builder override kwargs": (
        ["ssh_builder_actions.out2"],
        {
         "remote_server": "different remote server",
         "remote_directory": "different remote directory",
         "rsync_push_options": "different rsync push options",
         "rsync_pull_options": "different rsync pull options",
         "ssh_options": "different ssh options"
        },
        {}
    ),
    "task override kwargs": (
        ["ssh_builder_actions.out3"],
        {},
        {
         "remote_server": "different remote server",
         "remote_directory": "different remote directory",
         "rsync_push_options": "different rsync push options",
         "rsync_pull_options": "different rsync pull options",
         "ssh_options": "different ssh options"
        }
    ),
}


@pytest.mark.parametrize("target, builder_kwargs, task_kwargs",
                         ssh_builder_actions.values(),
                         ids=ssh_builder_actions.keys())
def test_ssh_builder_actions(target, builder_kwargs, task_kwargs):
    # Set default expectations to match default argument values
    expected_kwargs = {
        "remote_server": "",
        "remote_directory": "",
        "rsync_push_options": "-rlptv",
        "rsync_pull_options": "-rlptv",
        "ssh_options": ""
    }
    # Update expected arguments to match test case
    expected_kwargs.update(builder_kwargs)
    expected_kwargs.update(task_kwargs)

    def cat():
        return SCons.Builder.Builder(action=[
                "cat ${SOURCE.abspath} | tee ${TARGETS[0].abspath}",
                "cat ${SOURCES.abspath} | tee ${TARGETS[0].abspath}",
                "cat ${SOURCES[99].abspath} | tee ${TARGETS[0].abspath}",
                "cat ${SOURCES[-1].abspath} | tee ${TARGETS[0].abspath}",
                "cat ${SOURCES[-1].abspath} > ${TARGETS[-1].abspath}",
                "echo \"Hello World!\""
        ])

    build_cat = cat()
    build_cat_action_list = [action.cmd_list for action in build_cat.action.list]
    expected = [
        "cat ${SOURCE.abspath} | tee ${TARGETS[0].abspath}",
        "cat ${SOURCES.abspath} | tee ${TARGETS[0].abspath}",
        "cat ${SOURCES[99].abspath} | tee ${TARGETS[0].abspath}",
        "cat ${SOURCES[-1].abspath} | tee ${TARGETS[0].abspath}",
        "cat ${SOURCES[-1].abspath} > ${TARGETS[-1].abspath}",
        'echo "Hello World!"'
    ]
    # Test builder action(s)
    assert build_cat_action_list == expected

    ssh_build_cat = scons_extensions.ssh_builder_actions(cat(), **builder_kwargs)
    ssh_build_cat_action_list = [action.cmd_list for action in ssh_build_cat.action.list]
    expected = [
        'ssh ${ssh_options} ${remote_server} "mkdir -p ${remote_directory}"',
        "rsync ${rsync_push_options} ${SOURCES.abspath} ${remote_server}:${remote_directory}",
        "ssh ${ssh_options} ${remote_server} 'cd ${remote_directory} && cat ${SOURCE.file} | tee ${TARGETS[0].file}'",
        "ssh ${ssh_options} ${remote_server} 'cd ${remote_directory} && cat ${SOURCES.file} | tee ${TARGETS[0].file}'",
        "ssh ${ssh_options} ${remote_server} " \
            "'cd ${remote_directory} && cat ${SOURCES[99].file} | tee ${TARGETS[0].file}'",
        "ssh ${ssh_options} ${remote_server} " \
            "'cd ${remote_directory} && cat ${SOURCES[-1].file} | tee ${TARGETS[0].file}'",
        "ssh ${ssh_options} ${remote_server} 'cd ${remote_directory} && cat ${SOURCES[-1].file} > ${TARGETS[-1].file}'",
        "ssh ${ssh_options} ${remote_server} 'cd ${remote_directory} && echo \"Hello World!\"'",
        "rsync ${rsync_pull_options} ${remote_server}:${remote_directory}/ ${TARGET.dir.abspath}"
    ]
    # Test builder action(s)
    assert ssh_build_cat_action_list == expected

    # Test task keyword arguments
    env = SCons.Environment.Environment()
    env.Append(BUILDERS={
        "SSHBuildCat": ssh_build_cat
    })
    nodes = env.SSHBuildCat(target=target, source=["dummy.py"], **task_kwargs)
    for node in nodes:
        for key, expected_value in expected_kwargs.items():
            assert node.env[key] == expected_value

    ssh_python_builder = scons_extensions.ssh_builder_actions(
        scons_extensions.python_builder_factory()
    )
    ssh_python_builder_action_list = [action.cmd_list for action in ssh_python_builder.action.list]
    expected = [
        'ssh ${ssh_options} ${remote_server} "mkdir -p ${remote_directory}"',
        "rsync ${rsync_push_options} ${SOURCES.abspath} ${remote_server}:${remote_directory}",
        "ssh ${ssh_options} ${remote_server} 'cd ${remote_directory} && ${environment} ${action_prefix} " \
            "${program} ${program_required} ${program_options} " \
            "${subcommand} ${subcommand_required} ${subcommand_options} ${action_suffix}'",
        "rsync ${rsync_pull_options} ${remote_server}:${remote_directory}/ ${TARGET.dir.abspath}"
    ]
    assert ssh_python_builder_action_list == expected


prepend_env_input = {
    "path exists": (f"{root_fs}program", True, does_not_raise()),
    "path does not exist": (f"{root_fs}notapath", False, pytest.raises(FileNotFoundError))
}


@pytest.mark.parametrize("program, mock_exists, outcome",
                         prepend_env_input.values(),
                         ids=prepend_env_input.keys())
def test_append_env_path(program, mock_exists, outcome):
    # Test function interface
    env = SCons.Environment.Environment()
    with patch("pathlib.Path.exists", return_value=mock_exists), outcome:
        try:
            scons_extensions.append_env_path(env, program)
            assert root_fs == env["ENV"]["PATH"].split(os.pathsep)[-1]
            assert "PYTHONPATH" not in env["ENV"]
            assert "LD_LIBRARY_PATH" not in env["ENV"]
        finally:
            pass

    # Test AddMethod interface
    env.AddMethod(scons_extensions.append_env_path, "AppendEnvPath")
    with patch("pathlib.Path.exists", return_value=mock_exists), outcome:
        try:
            env.AppendEnvPath(program)
            assert root_fs == env["ENV"]["PATH"].split(os.pathsep)[-1]
            assert "PYTHONPATH" not in env["ENV"]
            assert "LD_LIBRARY_PATH" not in env["ENV"]
        finally:
            pass

    # TODO: Remove reversed arguments test after full deprecation of the older argument order
    # https://re-git.lanl.gov/aea/python-projects/waves/-/issues/755
    with patch("pathlib.Path.exists", return_value=mock_exists), \
         patch("warnings.warn") as mock_warn, outcome:
        try:
            scons_extensions.append_env_path(program, env)
            assert root_fs == env["ENV"]["PATH"].split(os.pathsep)[-1]
            assert "PYTHONPATH" not in env["ENV"]
            assert "LD_LIBRARY_PATH" not in env["ENV"]
        finally:
            mock_warn.assert_called_once()


substitution_dictionary = {"thing1": 1, "thing_two": "two"}
substitution_syntax_input = {
    "default characters": (substitution_dictionary, {}, {"@thing1@": 1, "@thing_two@": "two"}),
    "provided pre/suffix": (substitution_dictionary, {"prefix": "$", "suffix": "%"},
                             {"$thing1%": 1, "$thing_two%": "two"}),
    "int key": ({1: "one"}, {}, {"@1@": "one"}),
    "float key": ({1.0: "one"}, {}, {"@1.0@": "one"}),
    "nested": ({"nest_parent": {"nest_child": 1}, "thing_two": "two"}, {},
               {"@nest_parent@": {"nest_child": 1}, "@thing_two@": "two"})
}


@pytest.mark.parametrize("substitution_dictionary, keyword_arguments, expected_dictionary",
                         substitution_syntax_input.values(),
                         ids=substitution_syntax_input.keys())
def test_substitution_syntax(substitution_dictionary, keyword_arguments, expected_dictionary):
    env = SCons.Environment.Environment()

    # Test function style interface
    output_dictionary = scons_extensions.substitution_syntax(env, substitution_dictionary, **keyword_arguments)
    assert output_dictionary == expected_dictionary

    # Test AddMethod style interface
    env.AddMethod(scons_extensions.substitution_syntax, "SubstitutionSyntax")
    output_dictionary = env.SubstitutionSyntax(substitution_dictionary, **keyword_arguments)
    assert output_dictionary == expected_dictionary

    # TODO: Remove after full deprecation of the older argument order
    # https://re-git.lanl.gov/aea/python-projects/waves/-/issues/764
    # Test function style interface
    with patch("warnings.warn") as mock_warn:
        output_dictionary = scons_extensions.substitution_syntax(substitution_dictionary, **keyword_arguments)
        assert output_dictionary == expected_dictionary
        mock_warn.assert_called_once()


# TODO: Remove when the 'postfix' kwarg is removed
# https://re-git.lanl.gov/aea/python-projects/waves/-/issues/724
def test_substitution_syntax_warning():
    env = SCons.Environment.Environment()
    substitution_dictionary = {"thing1": 1, "thing_two": "two"}
    expected_dictionary = {"@thing1%": 1, "@thing_two%": "two"}
    with patch("warnings.warn") as mock_warn:
        output_dictionary = scons_extensions.substitution_syntax(env, substitution_dictionary, postfix="%")
        mock_warn.assert_called_once_with(
            "The 'postfix' keyword will be replaced by 'suffix' in version 1.0",
            DeprecationWarning
        )
    assert output_dictionary == expected_dictionary


shell_environment = {
    "default kwargs": (
        {}, {"thing1": "a"}
    ),
    "different shell": (
        {"shell": "different shell"}, {"thing1": "a"}
    ),
    "no cache": (
        {"cache": None, "overwrite_cache": False}, {"thing1": "a"}
    ),
    "cache": (
        {"cache": "dummy.yaml", "overwrite_cache": False}, {"thing1": "a"}
    ),
    "cache overwrite": (
        {"cache": "dummy.yaml", "overwrite_cache": True}, {"thing1": "a"}
    ),
}


@pytest.mark.skipif(testing_windows, reason="BASH shell specific function incompatible with Windows")
@pytest.mark.parametrize("kwargs, expected_environment",
                         shell_environment.values(),
                         ids=shell_environment.keys())
def test_shell_environment(kwargs, expected_environment):
    expected_kwargs = {
        "shell": "bash",
        "cache": None,
        "overwrite_cache": False
    }
    expected_kwargs.update(kwargs)

    with patch("waves._utilities.cache_environment", return_value=expected_environment) as cache_environment:
        env = scons_extensions.shell_environment("dummy", **kwargs)
        cache_environment.assert_called_once_with("dummy", **expected_kwargs, verbose=True)
    # Check that the expected dictionary is a subset of the SCons construction environment
    assert all(env["ENV"].get(key, None) == value for key, value in expected_environment.items())


prefix = f"{_cd_action_prefix}"
suffix = "suffix"
construct_action_list = {
    "list1": (["thing1"], prefix, "", [f"{prefix} thing1"]),
    "list2": (["thing1", "thing2"], prefix, "", [f"{prefix} thing1", f"{prefix} thing2"]),
    "tuple": (("thing1",), prefix, "", [f"{prefix} thing1"]),
    "str":  ("thing1", prefix, "", [f"{prefix} thing1"]),
    "list1 suffix": (["thing1"], prefix, suffix, [f"{prefix} thing1 {suffix}"]),
    "list2 suffix": (["thing1", "thing2"], prefix, suffix, [f"{prefix} thing1 {suffix}", f"{prefix} thing2 {suffix}"]),
    "tuple suffix": (("thing1",), prefix, suffix, [f"{prefix} thing1 {suffix}"]),
    "str suffix":  ("thing1", prefix, suffix, [f"{prefix} thing1 {suffix}"]),
}


@pytest.mark.parametrize("actions, prefix, suffix, expected",
                         construct_action_list.values(),
                         ids=construct_action_list.keys())
def test_construct_action_list(actions, prefix, suffix, expected):
    output = scons_extensions.construct_action_list(actions, prefix=prefix, suffix=suffix)
    assert output == expected


# TODO: Remove when the 'postfix' kwarg is removed
# https://re-git.lanl.gov/aea/python-projects/waves/-/issues/724
def test_construct_action_list_warning():
    original = ["thing1"]
    expected = ["prefix thing1 suffix"]
    with patch("warnings.warn") as mock_warn:
        output = scons_extensions.construct_action_list(original, prefix="prefix", postfix="suffix")
        mock_warn.assert_called_once_with(
            "The 'postfix' keyword will be replaced by 'suffix' in version 1.0",
            DeprecationWarning
        )
    assert output == expected


source_file = fs.File("dummy.py")
journal_emitter_input = {
    "one target": (["target.cae"],
                   [source_file],
                   ["target.cae", "target.cae.abaqus_v6.env", "target.cae.stdout"]),
    "subdirectory": (["set1/dummy.cae"],
                    [source_file],
                    ["set1/dummy.cae", f"set1{os.sep}dummy.cae.abaqus_v6.env", f"set1{os.sep}dummy.cae.stdout"])
}


@pytest.mark.parametrize("target, source, expected",
                         journal_emitter_input.values(),
                         ids=journal_emitter_input.keys())
def test_abaqus_journal_emitter(target, source, expected):
    target, source = scons_extensions._abaqus_journal_emitter(target, source, None)
    assert target == expected


# TODO: Figure out how to cleanly reset the construction environment between parameter sets instead of passing a new
# target per set.
abaqus_journal_input = {
    "default behavior": (
        {}, {}, 3, 1, ["abaqus_journal_1.cae"]
    ),
    "no defaults": (
        {
         "program": "someothercommand",
         "action_prefix": "nocd",
         "required": "cae python",
         "action_suffix": "",
         "environment_suffix": ""
        },
        {}, 3, 1, ["abaqus_journal_2.cae"]
    ),
    "task kwargs overrides": (
        {},
        {
         "program": "someothercommand",
         "action_prefix": "nocd",
         "required": "cae python",
         "action_suffix": "",
         "environment_suffix": ""
        },
        3, 1, ["abaqus_journal_3.cae"]
    ),
    "different command": (
        {"program": "dummy"}, {}, 3, 1, ["abaqus_journal_4.cae"]
    ),
}


@pytest.mark.parametrize("builder_kwargs, task_kwargs, node_count, action_count, target_list",
                         abaqus_journal_input.values(),
                         ids=abaqus_journal_input.keys())
def test_abaqus_journal(builder_kwargs, task_kwargs, node_count, action_count, target_list):
    # Set default expectations to match default argument values
    expected_kwargs = {
        "program": "abaqus",
        "required": "cae -noGUI ${SOURCE.abspath}",
        "action_prefix": _cd_action_prefix,
        "action_suffix": _redirect_action_suffix,
        "environment_suffix": _redirect_environment_suffix
    }
    # Update expected arguments to match test case
    expected_kwargs.update(builder_kwargs)
    expected_kwargs.update(task_kwargs)
    # Expected action matches the pre-SCons-substitution string with newline delimiter
    expected_string = '${action_prefix} ${program} -information environment ${environment_suffix}\n' \
                      '${action_prefix} ${program} ${required} ${abaqus_options} -- ${journal_options} ' \
                          '${action_suffix}'

    # Assemble the builder and a task to interrogate
    env = SCons.Environment.Environment()
    env.Append(BUILDERS={
        "AbaqusJournal": scons_extensions.abaqus_journal(**builder_kwargs)
    })
    nodes = env.AbaqusJournal(target=target_list, source=["journal.py"], journal_options="", **task_kwargs)

    # Test task definition node counts, action(s), and task keyword arguments
    check_action_string(nodes, node_count, action_count, expected_string)
    for node in nodes:
        for key, expected_value in expected_kwargs.items():
            assert node.env[key] == expected_value


def test_sbatch_abaqus_journal():
    expected = 'sbatch --wait --output=${TARGET.base}.slurm.out ${sbatch_options} --wrap "${action_prefix} ' \
               '${program} -information environment ${environment_suffix} && ${action_prefix} ' \
               '${program} ${required} ${abaqus_options} -- ${journal_options} ${action_suffix}"'
    builder = scons_extensions.sbatch_abaqus_journal()
    assert builder.action.cmd_list == expected
    assert builder.emitter == scons_extensions._abaqus_journal_emitter


source_file = fs.File("root.inp")
solver_emitter_input = {
    "empty targets": (
        "job",
        None,
        [],
        [source_file],
        ["job.odb", "job.dat", "job.msg", "job.com", "job.prt", "job.abaqus_v6.env", "job.stdout"],
        does_not_raise()
    ),
    "empty targets, suffixes override": (
        "job",
        [".odb"],
        [],
        [source_file],
        ["job.odb", "job.abaqus_v6.env", "job.stdout"],
        does_not_raise()
    ),
    "empty targets, suffixes override empty list": (
        "job",
        [],
        [],
        [source_file],
        ["job.abaqus_v6.env", "job.stdout"],
        does_not_raise()
    ),
    "one targets": (
        "job",
        None,
        ["job.sta"],
        [source_file],
        ["job.sta", "job.odb", "job.dat", "job.msg", "job.com", "job.prt", "job.abaqus_v6.env", "job.stdout"],
        does_not_raise()
    ),
    "one targets, override suffixes": (
        "job",
        [".odb"],
        ["job.sta"],
        [source_file],
        ["job.sta", "job.odb", "job.abaqus_v6.env", "job.stdout"],
        does_not_raise()
    ),
    "one targets, override suffixes string": (
        "job",
        ".odb",
        ["job.sta"],
        [source_file],
        ["job.sta", "job.odb", "job.abaqus_v6.env", "job.stdout"],
        does_not_raise()
    ),
    "subdirectory": (
        "job",
        None,
        ["set1/job.sta"],
        [source_file],
        ["set1/job.sta", f"set1{os.sep}job.odb", f"set1{os.sep}job.dat",
         f"set1{os.sep}job.msg", f"set1{os.sep}job.com", f"set1{os.sep}job.prt",
         f"set1{os.sep}job.abaqus_v6.env", f"set1{os.sep}job.stdout"],
        does_not_raise()
    ),
    "subdirectory, override suffixes": (
        "job",
        [".odb"],
        ["set1/job.sta"],
        [source_file],
        ["set1/job.sta", f"set1{os.sep}job.odb", f"set1{os.sep}job.abaqus_v6.env", f"set1{os.sep}job.stdout"],
        does_not_raise()
    ),
    "missing job_name": (
        None,
        None,
        [],
        [source_file],
        ["root.odb", "root.dat", "root.msg", "root.com", "root.prt", "root.abaqus_v6.env", "root.stdout"],
        does_not_raise()
    ),
    "missing job_name, override suffixes": (
        None,
        [".odb"],
        [],
        [source_file],
        ["root.odb", "root.abaqus_v6.env", "root.stdout"],
        does_not_raise()
    )
}


@pytest.mark.parametrize("job_name, suffixes, target, source, expected, outcome",
                         solver_emitter_input.values(),
                         ids=solver_emitter_input.keys())
def test_abaqus_solver_emitter(job_name, suffixes, target, source, expected, outcome):
    env = SCons.Environment.Environment()
    env["job_name"] = job_name
    env["suffixes"] = suffixes
    with outcome:
        try:
            target, source = scons_extensions._abaqus_solver_emitter(target, source, env)
        finally:
            assert target == expected


# TODO: Figure out how to cleanly reset the construction environment between parameter sets instead of passing a new
# target per set.
abaqus_solver_input = {
    "default behavior": (
        {"program": "abaqus"}, {}, 7, 1, ["input1.inp"], None
    ),
    "no defaults": (
        {
         "program": "notdefault",
         "required": "-other options",
         "action_prefix": "nocd",
         "action_suffix": "",
         "environment_suffix": ""
        },
        {}, 7, 1, ["abaqus_solver_2.inp"], None
    ),
    "task kwargs overrides": (
        {},
        {
         "program": "notdefault",
         "required": "-other options",
         "action_prefix": "nocd",
         "action_suffix": "",
         "environment_suffix": "",
        },
        7, 1, ["abaqus_solver_3.inp"], None
    ),
    "different command": (
        {"program": "dummy"}, {}, 7, 1, ["input2.inp"], None
    ),
    "standard solver": (
        {"program": "abaqus", "emitter": "standard"}, {}, 8, 1, ["input4.inp"], None
    ),
    "explicit solver": (
        {"program": "abaqus", "emitter": "explicit"}, {}, 8, 1, ["input5.inp"], None
    ),
    "datacheck solver": (
        {"program": "abaqus", "emitter": "datacheck"}, {}, 11, 1, ["input6.inp"], None
    ),
    "standard solver, suffixes override": (
        {"program": "abaqus", "emitter": "standard"}, {}, 3, 1, ["input4.inp"], [".odb"]
    ),
}


@pytest.mark.parametrize("builder_kwargs, task_kwargs, node_count, action_count, source_list, suffixes",
                         abaqus_solver_input.values(),
                         ids=abaqus_solver_input.keys())
def test_abaqus_solver(builder_kwargs, task_kwargs, node_count, action_count, source_list, suffixes):
    # Set default expectations to match default argument values
    expected_kwargs = {
        "program": "abaqus",
        "required": "-interactive -ask_delete no -job ${job_name} -input ${SOURCE.filebase}",
        "action_prefix": _cd_action_prefix,
        "action_suffix": _redirect_action_suffix,
        "environment_suffix": _redirect_environment_suffix,
        "emitter": None
    }
    # Update expected arguments to match test case
    expected_kwargs.update(builder_kwargs)
    expected_kwargs.update(task_kwargs)
    # Expected action matches the pre-SCons-substitution string with newline delimiter
    expected_string = \
        "${action_prefix} ${program} -information environment ${environment_suffix}\n" \
        "${action_prefix} ${program} ${required} ${abaqus_options} ${action_suffix}"

    # Assemble the builder and a task to interrogate
    env = SCons.Environment.Environment()
    env.Append(BUILDERS={
        "AbaqusSolver": scons_extensions.abaqus_solver(**builder_kwargs)
    })
    nodes = env.AbaqusSolver(target=[], source=source_list, abaqus_options="", suffixes=suffixes, **task_kwargs)

    # Test task definition node counts, action(s), and task keyword arguments
    check_action_string(nodes, node_count, action_count, expected_string)
    check_abaqus_solver_targets(nodes, expected_kwargs["emitter"], pathlib.Path(source_list[0]).stem, suffixes)
    expected_kwargs.pop("emitter")
    for node in nodes:
        for key, expected_value in expected_kwargs.items():
            assert node.env[key] == expected_value


def test_sbatch_abaqus_solver():
    expected = 'sbatch --wait --output=${TARGET.base}.slurm.out ${sbatch_options} --wrap "' \
               '${action_prefix} ${program} -information environment ${environment_suffix} && ' \
               '${action_prefix} ${program} ${required} ${abaqus_options} ${action_suffix}"'
    builder = scons_extensions.sbatch_abaqus_solver()
    assert builder.action.cmd_list == expected
    assert builder.emitter == scons_extensions._abaqus_solver_emitter


copy_substfile_input = {
    "strings": (["dummy", "dummy2.in", "root.inp.in", "conf.py.in"],
                ["dummy", "dummy2.in", "dummy2", "root.inp.in", "root.inp", "conf.py.in", "conf.py"]),
    "pathlib.Path()s": ([pathlib.Path("dummy"), pathlib.Path("dummy2.in")],
                        ["dummy", "dummy2.in", "dummy2"]),
}


@pytest.mark.parametrize("source_list, expected_list",
                         copy_substfile_input.values(),
                         ids=copy_substfile_input.keys())
def test_copy_substfile(source_list, expected_list):
    env = SCons.Environment.Environment()
    target_list = scons_extensions.copy_substfile(env, source_list, {})
    target_files = [str(target) for target in target_list]
    assert target_files == expected_list

    # Test the Pseudo-Builder style interface
    env.AddMethod(scons_extensions.copy_substfile, "CopySubstfile")
    target_list = env.CopySubstfile(source_list, {})
    target_files = [str(target) for target in target_list]
    assert target_files == expected_list

    # TODO: Remove when the copy substitute method is deprecated
    # https://re-git.lanl.gov/aea/python-projects/waves/-/issues/665
    target_list = scons_extensions.copy_substitute(source_list, {})
    target_files = [str(target) for target in target_list]
    assert target_files == expected_list


build_subdirectory_input = {
    "no target": ([], pathlib.Path(".")),
    "no parent": (["target.ext"], pathlib.Path(".")),
    "one parent": (["set1/target.ext"], pathlib.Path("set1"))
}


@pytest.mark.parametrize("target, expected",
                         build_subdirectory_input.values(),
                         ids=build_subdirectory_input.keys())
def test_build_subdirectory(target, expected):
    assert scons_extensions._build_subdirectory(target) == expected


source_file = fs.File("dummy.py")
first_target_emitter_input = {
    "one target": (
        ["target.cub"],
        [source_file],
        ["target.cub", "target.cub.stdout"]
    ),
    "only stdout": (
        ["only.stdout"],
        [source_file],
        ["only.stdout"]
    ),
    "first stdout": (
        ["first.stdout", "first.cub"],
        [source_file],
        ["first.cub", "first.stdout"]
    ),
    "second stdout": (
        ["second.cub", "second.stdout"],
        [source_file],
        ["second.cub", "second.stdout"]
    ),
    "subdirectory": (
        ["set1/dummy.cub"],
        [source_file],
        ["set1/dummy.cub", f"set1{os.sep}dummy.cub.stdout"]
    ),
    "subdirectory only stdout": (
        ["set1/subdir1.stdout"],
        [source_file],
        [f"set1/subdir1.stdout"]
    ),
    "subdirectory first stdout": (
        ["set1/subdir2.stdout", "set1/subdir2.cub"],
        [source_file],
        [f"set1/subdir2.cub", f"set1/subdir2.stdout"]
    ),
    "subdirectory second stdout": (
        [ "set1/subdir3.cub", "set1/subdir3.stdout"],
        [source_file],
        [f"set1/subdir3.cub", f"set1/subdir3.stdout"]
    )
}


@pytest.mark.parametrize("target, source, expected",
                         first_target_emitter_input.values(),
                         ids=first_target_emitter_input.keys())
def test_first_target_emitter(target, source, expected):
    target, source = scons_extensions.first_target_emitter(target, source, None)
    assert target == expected


builder_factory_tests = first_target_builder_factory_test_cases(
    "builder_factory",
    {
        "environment": "",
        "action_prefix": "",
        "program": "",
        "program_required": "",
        "program_options": "",
        "subcommand": "",
        "subcommand_required": "",
        "subcommand_options": "",
        "action_suffix": ""
    },
    default_emitter=None,
    expected_node_count=1
)
builder_factory_tests.update(first_target_builder_factory_test_cases(
    "first_target_builder_factory",
    {
        "environment": "",
        "action_prefix": _cd_action_prefix,
        "program": "",
        "program_required": "",
        "program_options": "",
        "subcommand": "",
        "subcommand_required": "",
        "subcommand_options": "",
        "action_suffix": _redirect_action_suffix
    }
))
builder_factory_tests.update(first_target_builder_factory_test_cases(
    "python_builder_factory",
    {
        "environment": "",
        "action_prefix": _cd_action_prefix,
        "program": "python",
        "program_required": "",
        "program_options": "",
        "subcommand": "${SOURCE.abspath}",
        "subcommand_required": "",
        "subcommand_options": "",
        "action_suffix": _redirect_action_suffix
    }
))
builder_factory_tests.update(first_target_builder_factory_test_cases(
    "abaqus_journal_builder_factory",
    {
        "environment": "",
        "action_prefix": _cd_action_prefix,
        "program": "abaqus",
        "program_required": "cae -noGUI ${SOURCES[0].abspath}",
        "program_options": "",
        "subcommand": "--",
        "subcommand_required": "",
        "subcommand_options": "",
        "action_suffix": _redirect_action_suffix
    }
))
builder_factory_tests.update(first_target_builder_factory_test_cases(
    "abaqus_solver_builder_factory",
    {
        "environment": "",
        "action_prefix": _cd_action_prefix,
        "program": "abaqus",
        "program_required": "-interactive -ask_delete no -input ${SOURCE.filebase}",
        "program_options": "",
        "subcommand": "",
        "subcommand_required": "",
        "subcommand_options": "",
        "action_suffix": _redirect_action_suffix
    }
))
builder_factory_tests.update(first_target_builder_factory_test_cases(
    "quinoa_builder_factory",
    {
        "environment": "",
        "action_prefix": _cd_action_prefix,
        "program": "charmrun",
        "program_required": "",
        "program_options": "+p1",
        "subcommand": "inciter",
        "subcommand_required": "--control ${SOURCES[0].abspath} --input ${SOURCES[1].abspath}",
        "subcommand_options": "",
        "action_suffix": _redirect_action_suffix
    }
))
builder_factory_tests.update(first_target_builder_factory_test_cases(
    "fierro_explicit_builder_factory",
    {
        "environment": "",
        "action_prefix": _cd_action_prefix,
        "program": "mpirun",
        "program_required": "",
        "program_options": "-np 1",
        "subcommand": "fierro-parallel-explicit",
        "subcommand_required": "${SOURCE.abspath}",
        "subcommand_options": "",
        "action_suffix": _redirect_action_suffix
    }
))
builder_factory_tests.update(first_target_builder_factory_test_cases(
    "fierro_implicit_builder_factory",
    {
        "environment": "",
        "action_prefix": _cd_action_prefix,
        "program": "mpirun",
        "program_required": "",
        "program_options": "-np 1",
        "subcommand": "fierro-parallel-implicit",
        "subcommand_required": "${SOURCE.abspath}",
        "subcommand_options": "",
        "action_suffix": _redirect_action_suffix
    }
))
builder_factory_tests.update(first_target_builder_factory_test_cases(
    "sierra_builder_factory",
    {
        "environment": "",
        "action_prefix": _cd_action_prefix,
        "program": "sierra",
        "program_required": "",
        "program_options": "",
        "subcommand": "adagio",
        "subcommand_required": "-i ${SOURCE.abspath}",
        "subcommand_options": "",
        "action_suffix": _redirect_action_suffix
    }
))
builder_factory_tests.update(first_target_builder_factory_test_cases(
    "ansys_apdl_builder_factory",
    {
        "environment": "",
        "action_prefix": _cd_action_prefix,
        "program": "ansys",
        "program_required": "-i ${SOURCES[0].abspath} -o ${TARGETS[-1].abspath}",
        "program_options": "",
        "subcommand": "",
        "subcommand_required": "",
        "subcommand_options": "",
        "action_suffix": ""
    }
))

@pytest.mark.parametrize("factory_name, default_kwargs, builder_kwargs, task_kwargs, target, default_emitter, emitter, expected_node_count",
                         builder_factory_tests.values(),
                         ids=builder_factory_tests.keys())
def test_builder_factory(
    factory_name: str,
    default_kwargs: dict,
    builder_kwargs: dict,
    task_kwargs: dict,
    target: list,
    default_emitter,
    emitter,
    expected_node_count: int,
) -> None:
    """Template test for builder factories based on :meth:`waves.scons_extensions.builder_factory`

    :param factory_name: Name of the factory to test
    :param default_kwargs: Set the default keyword argument values. Expected to be constant as a function of builder
        factory under test.
    :param builder_kwargs: Keyword arguments unpacked at the builder instantiation
    :param task_kwargs: Keyword arguments unpacked at the task instantiation
    :param target: Explicit list of targets provided at the task instantiation
    :param default_emitter: The emitter to expect when ``False`` is provided for ``emitter`` keyword argument.
    :param emitter: A custom factory emitter. Mostly intended as a pass-through check. Set to ``False`` to avoid
        providing an emitter argument to the builder factory.
    :param expected_node_count: The expected number of target nodes.
    """
    # Set default expectations to match default argument values
    expected_kwargs = default_kwargs
    # Update expected arguments to match test case
    expected_kwargs.update(builder_kwargs)
    expected_kwargs.update(task_kwargs)
    # Expected action matches the pre-SCons-substitution string with newline delimiter
    expected_action = \
        "${environment} ${action_prefix} ${program} ${program_required} ${program_options} " \
            "${subcommand} ${subcommand_required} ${subcommand_options} ${action_suffix}"

    # Handle additional builder kwargs without changing default behavior
    expected_emitter = default_emitter
    emitter_handling = {}
    if emitter is not False:
        expected_emitter = emitter
        emitter_handling.update({"emitter": emitter})

    # Test builder object attributes
    factory = getattr(scons_extensions, factory_name)
    builder = factory(**builder_kwargs, **emitter_handling)
    assert builder.action.cmd_list == expected_action
    assert builder.emitter == expected_emitter

    # Assemble the builder and a task to interrogate
    env = SCons.Environment.Environment()
    env.Append(BUILDERS={
        "Builder": builder
    })
    nodes = env.Builder(target=target, source=["check_builder_factory.in"], **task_kwargs)

    # Test task definition node counts, action(s), and task keyword arguments
    check_action_string(nodes, expected_node_count, 1, expected_action)
    for node in nodes:
        for key, expected_value in expected_kwargs.items():
            assert node.env[key] == expected_value


sbatch_first_target_builder_factory_names = [
    "python_builder_factory",
    "abaqus_journal_builder_factory",
    "abaqus_solver_builder_factory",
    "quinoa_builder_factory",
    "sierra_builder_factory",
]


@pytest.mark.parametrize("name", sbatch_first_target_builder_factory_names)
def test_sbatch_first_target_builder_factories(name: str):
    """Test the sbatch builder factories created as

    .. code-block::

       @catenate_actions(program="sbatch", options=_settings._sbatch_wrapper_options)
       def sbatch_thing_builder_factory(*args, **kwargs):
           return thing_builder_factory(*args, **kwargs)

    Assumes the naming convention ``thing_builder_factory`` and ``sbatch_thing_builder_factory``

    :param name: wrapped builder factory name
    """
    expected = f'sbatch {_sbatch_wrapper_options} "' \
        '${environment} ${action_prefix} ${program} ${program_required} ${program_options} ' \
        '${subcommand} ${subcommand_required} ${subcommand_options} ${action_suffix}"'
    wrapped_factory = getattr(scons_extensions, name)
    factory = getattr(scons_extensions, f"sbatch_{name}")
    with patch(f"waves.scons_extensions.{name}", side_effect=wrapped_factory) as mock_wrapped_factory:
        builder = factory()
        mock_wrapped_factory.assert_called_once()
    assert builder.action.cmd_list == expected
    assert builder.emitter == scons_extensions.first_target_emitter


# TODO: Figure out how to cleanly reset the construction environment between parameter sets instead of passing a new
# target per set.
python_script_input = {
    "default behavior": ({}, {}, 2, 1, ["python_script1.out"]),
    "no defaults": (
        {
         "program": "different program",
         "action_prefix": "different prefix",
         "action_suffix": "different action suffix",
        },
        {}, 2, 1, ["python_script2.out"]
    ),
    "task kwargs overrides": (
        {},
        {
         "program": "different program",
         "action_prefix": "different prefix",
         "action_suffix": "different action suffix",
        },
        2, 1, ["python_script3.out"]
    ),
    "different command": ({"program": "python2"}, {}, 2, 1, ["python_script4.out"]),
}


@pytest.mark.parametrize("builder_kwargs, task_kwargs, node_count, action_count, target_list",
                         python_script_input.values(),
                         ids=python_script_input.keys())
def test_python_script(builder_kwargs, task_kwargs, node_count, action_count, target_list):
    # Set default expectations to match default argument values
    expected_kwargs = {
        "program": "python",
        "action_prefix": _cd_action_prefix,
        "action_suffix": _redirect_action_suffix,
    }
    # Update expected arguments to match test case
    expected_kwargs.update(builder_kwargs)
    expected_kwargs.update(task_kwargs)
    # Expected action matches the pre-SCons-substitution string with newline delimiter
    expected_string = \
       "${action_prefix} ${program} ${python_options} ${SOURCE.abspath} ${script_options} ${action_suffix}"

    # Assemble the builder and a task to interrogate
    env = SCons.Environment.Environment()
    message = "This builder will be replaced by ``waves.scons_extensions.python_builder_factory`` in version 1.0"
    with patch("warnings.warn") as mock_warn:
        env.Append(BUILDERS={"PythonScript": scons_extensions.python_script(**builder_kwargs)})
        mock_warn.assert_any_call(message, DeprecationWarning)
    nodes = env.PythonScript(target=target_list, source=["python_script.py"], script_options="", **task_kwargs)

    # Test task definition node counts, action(s), and task keyword arguments
    check_action_string(nodes, node_count, action_count, expected_string)
    for node in nodes:
        for key, expected_value in expected_kwargs.items():
            assert node.env[key] == expected_value


def test_sbatch_python_script():
    expected = 'sbatch --wait --output=${TARGET.base}.slurm.out ${sbatch_options} --wrap "' \
       '${action_prefix} ${program} ${python_options} ${SOURCE.abspath} ${script_options} ${action_suffix}"'
    message = "This builder will be replaced by ``waves.scons_extensions.sbatch_python_builder_factory`` in version 1.0"
    with patch("warnings.warn") as mock_warn:
        builder = scons_extensions.sbatch_python_script()
        mock_warn.assert_any_call(message, DeprecationWarning)
    assert builder.action.cmd_list == expected
    assert builder.emitter == scons_extensions.first_target_emitter


source_file = fs.File("dummy.m")
matlab_emitter_input = {
    "one target": (["target.matlab"],
                   [source_file],
                   ["target.matlab", "target.matlab.matlab.env", "target.matlab.stdout"]),
    "subdirectory": (["set1/dummy.matlab"],
                    [source_file],
                    ["set1/dummy.matlab", f"set1{os.sep}dummy.matlab.matlab.env", f"set1{os.sep}dummy.matlab.stdout"])
}


@pytest.mark.parametrize("target, source, expected",
                         matlab_emitter_input.values(),
                         ids=matlab_emitter_input.keys())
def test_matlab_script_emitter(target, source, expected):
    target, source = scons_extensions._matlab_script_emitter(target, source, None)
    assert target == expected


# TODO: Figure out how to cleanly reset the construction environment between parameter sets instead of passing a new
# target per set.
matlab_script_input = {
    "default behavior": (
        {}, {}, 3, 1, ["matlab_script1.out"]
    ),
    "no defaults": (
        {
         "program": "different program",
         "action_prefix": "different action prefix",
         "action_suffix": "different action suffix",
         "environment_suffix": "different environment suffix",
        },
        {}, 3, 1, ["matlab_script2.out"]
    ),
    "task kwargs overrides": (
        {},
        {
         "program": "different program",
         "action_prefix": "different action prefix",
         "action_suffix": "different action suffix",
         "environment_suffix": "different environment suffix",
        },
        3, 1, ["matlab_script3.out"]
    ),
    "different command": (
        {"program": "/different/matlab"}, {}, 3, 1, ["matlab_script4.out"]
    )
}


@pytest.mark.parametrize("builder_kwargs, task_kwargs, node_count, action_count, target_list",
                         matlab_script_input.values(),
                         ids=matlab_script_input.keys())
def test_matlab_script(builder_kwargs, task_kwargs, node_count, action_count, target_list):
    # Set default expectations to match default argument values
    expected_kwargs = {
        "program": "matlab",
        "action_prefix": _cd_action_prefix,
        "action_suffix": _redirect_action_suffix,
        "environment_suffix": _redirect_environment_suffix,
    }
    # Update expected arguments to match test case
    expected_kwargs.update(builder_kwargs)
    expected_kwargs.update(task_kwargs)
    # Expected action matches the pre-SCons-substitution string with newline delimiter
    expected_string = '${action_prefix} ${program} ${matlab_options} -batch ' \
                          '"path(path, \'${SOURCE.dir.abspath}\'); ' \
                          '[fileList, productList] = matlab.codetools.requiredFilesAndProducts(\'${SOURCE.file}\'); ' \
                          'disp(cell2table(fileList)); disp(struct2table(productList, \'AsArray\', true)); exit;" ' \
                          '${environment_suffix}\n' \
                      '${action_prefix} ${program} ${matlab_options} -batch ' \
                          '"path(path, \'${SOURCE.dir.abspath}\'); ' \
                          '${SOURCE.filebase}(${script_options})\" ' \
                          '${action_suffix}'

    # Assemble the builder and a task to interrogate
    env = SCons.Environment.Environment()
    env.Append(BUILDERS={
        "MatlabScript": scons_extensions.matlab_script(**builder_kwargs)
    })
    nodes = env.MatlabScript(target=target_list, source=["matlab_script.py"], script_options="", **task_kwargs)

    # Test task definition node counts, action(s), and task keyword arguments
    check_action_string(nodes, node_count, action_count, expected_string)
    for node in nodes:
        for key, expected_value in expected_kwargs.items():
            assert node.env[key] == expected_value


conda_environment_input = {
    "defaults": ({}, {}, ["conda_environment_1.yml"]),
    "no defaults": (
        {
         "program": "different program",
         "subcommand": "different subcommand",
         "required": "different required",
         "options": "different options",
         "action_prefix": "different action prefix",
        },
        {},
        ["conda_environment_2.yml"]
    ),
    "task keyword overrides": (
        {},
        {
         "program": "different program",
         "subcommand": "different subcommand",
         "required": "different required",
         "options": "different options",
         "action_prefix": "different action prefix",
        },
        ["conda_environment_3.yml"]
    )
}


@pytest.mark.parametrize("builder_kwargs, task_kwargs, target",
                         conda_environment_input.values(),
                         ids=conda_environment_input.keys())
def test_conda_environment(builder_kwargs, task_kwargs, target):
    # Set default expectations to match default argument values
    expected_kwargs = {
        "program": "conda",
        "subcommand": "env export",
        "required": "--file ${TARGET.abspath}",
        "options": "",
        "action_prefix": _cd_action_prefix
    }
    # Update expected arguments to match test case
    expected_kwargs.update(builder_kwargs)
    expected_kwargs.update(task_kwargs)
    # Expected action matches the pre-SCons-substitution string with newline delimiter
    expected_string = '${action_prefix} ${program} ${subcommand} ${required} ${options}'

    # Assemble the builder and a task to interrogate
    env = SCons.Environment.Environment()
    env.Append(BUILDERS={
        "CondaEnvironment": scons_extensions.conda_environment(**builder_kwargs)
    })
    nodes = env.CondaEnvironment(target=target, source=[], **task_kwargs)

    # Test task definition node counts, action(s), and task keyword arguments
    check_action_string(nodes, 1, 1, expected_string)
    for node in nodes:
        for key, expected_value in expected_kwargs.items():
            assert node.env[key] == expected_value


source_file = fs.File("dummy.odb")
abaqus_extract_emitter_input = {
    "empty targets": (
        [],
        [source_file],
        ["dummy.h5", "dummy_datasets.h5", "dummy.csv"],
        {}
    ),
    "one target": (
        ["new_name.h5"],
        [source_file],
        ["new_name.h5", "new_name_datasets.h5", "new_name.csv"],
        {}
    ),
    "bad extension": (
        ["new_name.txt"],
        [source_file],
        ["dummy.h5", "new_name.txt", "dummy_datasets.h5", "dummy.csv"],
        {}
    ),
    "subdirectory": (
        ["set1/dummy.h5"],
        [source_file],
        ["set1/dummy.h5", f"set1{os.sep}dummy_datasets.h5", f"set1{os.sep}dummy.csv"],
        {}
    ),
    "subdirectory new name": (
        ["set1/new_name.h5"],
        [source_file],
        ["set1/new_name.h5", f"set1{os.sep}new_name_datasets.h5", f"set1{os.sep}new_name.csv"],
        {}
    ),
    "one target delete report": (
        ["new_name.h5"],
        [source_file],
        ["new_name.h5", "new_name_datasets.h5"],
        {"delete_report_file": True}
    ),
    "subdirectory delete report": (
        ["set1/dummy.h5"],
        [source_file],
        ["set1/dummy.h5", f"set1{os.sep}dummy_datasets.h5"],
        {"delete_report_file": True}
    ),
}


@pytest.mark.parametrize("target, source, expected, env",
                         abaqus_extract_emitter_input.values(),
                         ids=abaqus_extract_emitter_input.keys())
def test_abaqus_extract_emitter(target, source, expected, env):
    target, source = scons_extensions._abaqus_extract_emitter(target, source, env)
    assert target == expected


def test_abaqus_extract():
    env = SCons.Environment.Environment()
    env.Append(BUILDERS={"AbaqusExtract": scons_extensions.abaqus_extract()})
    nodes = env.AbaqusExtract(
        target=["abaqus_extract.h5"], source=["abaqus_extract.odb"], journal_options="")
    expected_string = '_build_odb_extract(target, source, env)'
    check_action_string(nodes, 3, 1, expected_string)


source_file = fs.File("/dummy.source")
target_file = fs.File("/dummy.target")
build_odb_extract_input = {
    "no kwargs": ([target_file], [source_file], {"program": "NA"},
                  [call([f"{root_fs}dummy.source"], f"{root_fs}dummy.target", output_type="h5", odb_report_args=None,
                       abaqus_command="NA", delete_report_file=False)]),
    "all kwargs": ([target_file], [source_file],
                   {"program": "NA", "output_type": "different", "odb_report_args": "notnone",
                    "delete_report_file": True},
                   [call([f"{root_fs}dummy.source"], f"{root_fs}dummy.target", output_type="different", odb_report_args="notnone",
                        abaqus_command="NA", delete_report_file=True)])
}


@pytest.mark.parametrize("target, source, env, calls",
                         build_odb_extract_input.values(),
                         ids=build_odb_extract_input.keys())
def test_build_odb_extract(target, source, env, calls):
    with patch("waves._abaqus.odb_extract.odb_extract") as mock_odb_extract, \
         patch("pathlib.Path.unlink") as mock_unlink:
        scons_extensions._build_odb_extract(target, source, env)
    mock_odb_extract.assert_has_calls(calls)
    mock_unlink.assert_has_calls([call(missing_ok=True)])
    assert mock_unlink.call_count == len(target)


# TODO: Figure out how to cleanly reset the construction environment between parameter sets instead of passing a new
# target per set.
sbatch_input = {
    "default behavior": (
        {}, {}, 2, 1, ["sbatch1.out"]
    ),
    "no defaults": (
        {
         "program": "different program",
         "required": "different required",
         "action_prefix": "different action prefix",
        },
        {}, 2, 1, ["sbatch2.out"]
    ),
    "task kwargs overrides": (
        {},
        {
         "program": "different program",
         "required": "different required",
         "action_prefix": "different action prefix",
        },
        2, 1, ["sbatch3.out"]
    )
}


@pytest.mark.parametrize("builder_kwargs, task_kwargs, node_count, action_count, target_list",
                         sbatch_input.values(),
                         ids=sbatch_input.keys())
def test_sbatch(builder_kwargs, task_kwargs, node_count, action_count, target_list):
    # Set default expectations to match default argument values
    expected_kwargs = {
        "program": "sbatch",
        "required": "--wait --output=${TARGETS[-1].abspath}",
        "action_prefix": _cd_action_prefix
    }
    # Update expected arguments to match test case
    expected_kwargs.update(builder_kwargs)
    expected_kwargs.update(task_kwargs)
    # Expected action matches the pre-SCons-substitution string with newline delimiter
    expected_string = \
        '${action_prefix} ${program} ${required} ${sbatch_options} --wrap "${slurm_job}"'

    # Assemble the builder and a task to interrogate
    env = SCons.Environment.Environment()
    env.Append(BUILDERS={
        "SlurmSbatch": scons_extensions.sbatch(**builder_kwargs)
    })
    nodes = env.SlurmSbatch(target=target_list, source=["source.in"], sbatch_options="",
                            slurm_job="echo $SOURCE > $TARGET", **task_kwargs)

    # Test task definition node counts, action(s), and task keyword arguments
    check_action_string(nodes, node_count, action_count, expected_string)
    for node in nodes:
        for key, expected_value in expected_kwargs.items():
            assert node.env[key] == expected_value


scanner_input = {                                   # content,       expected_dependencies
    'has_suffix':             ('**\n*INCLUDE, INPUT=dummy.inp',               ['dummy.inp']),
    'no_suffix':              ('**\n*INCLUDE, INPUT=dummy.out',               ['dummy.out']),
    'pattern_not_found':      ( '**\n*DUMMY, STRING=dummy.out',                          []),
    'multiple_files':     ('**\n*INCLUDE, INPUT=dummy.out\n**'
                              '**\n*INCLUDE, INPUT=dummy2.inp', ['dummy.out', 'dummy2.inp']),
    'lower_case':             ('**\n*include, input=dummy.out',               ['dummy.out']),
    'mixed_case':             ('**\n*inClUdE, iNpuT=dummy.out',               ['dummy.out']),
    'no_leading':                 ('*INCLUDE, INPUT=dummy.out',               ['dummy.out']),
    'comment':                   ('**INCLUDE, INPUT=dummy.out'
                              '\n***INCLUDE, INPUT=dummy2.inp',                          []),
    'mixed_keywords':     ('**\n*INCLUDE, INPUT=dummy.out\n**'
                            '\n*TEMPERATURE, INPUT=dummy2.inp', ['dummy.out', 'dummy2.inp']),
    'trailing_whitespace': ('**\n*INCLUDE, INPUT=dummy.out   ',               ['dummy.out']),
    'partial match':     ('**\n*DUMMY, MATRIX INPUT=dummy.out',                          []),
    'extra_space':         ('**\n*INCLUDE,    INPUT=dummy.out',               ['dummy.out']),
}


@pytest.mark.parametrize("content, expected_dependencies",
                         scanner_input.values(),
                         ids=scanner_input.keys())
def test_abaqus_input_scanner(content, expected_dependencies):
    """Tests the expected dependencies based on the mocked content of the file.

    This function does NOT test for recursion.

    :param str content: Mocked content of the file
    :param list expected_dependencies: List of the expected dependencies
    """
    mock_file = unittest.mock.Mock()
    mock_file.get_text_contents.return_value = content
    env = SCons.Environment.Environment()
    scanner = scons_extensions.abaqus_input_scanner()
    dependencies = scanner(mock_file, env)
    found_files = [file.name for file in dependencies]
    assert set(found_files) == set(expected_dependencies)


sphinx_scanner_input = {
     # Test name, content, expected_dependencies
    'include directive': ('.. include:: dummy.txt', ['dummy.txt']),
    'literalinclude directive': ('.. literalinclude:: dummy.txt', ['dummy.txt']),
    'image directive': ( '.. image:: dummy.png',  ['dummy.png']),
    'figure directive': ( '.. figure:: dummy.png',  ['dummy.png']),
    'bibliography directive': ( '.. figure:: dummy.bib', ['dummy.bib']),
    'no match': ('.. notsuppored:: notsupported.txt', []),
    'indented': ('.. only:: html\n\n   .. include:: dummy.txt', ['dummy.txt']),
    'one match multiline': ('.. include:: dummy.txt\n.. notsuppored:: notsupported.txt', ['dummy.txt']),
    'three match multiline': ('.. include:: dummy.txt\n.. figure:: dummy.png\n.. bibliography:: dummy.bib',
                              ['dummy.txt', 'dummy.png', 'dummy.bib'])
}


@pytest.mark.parametrize("content, expected_dependencies",
                         sphinx_scanner_input.values(),
                         ids=sphinx_scanner_input.keys())
def test_sphinx_scanner(content, expected_dependencies):
    mock_file = unittest.mock.Mock()
    mock_file.get_text_contents.return_value = content
    env = SCons.Environment.Environment()
    scanner = scons_extensions.sphinx_scanner()
    dependencies = scanner(mock_file, env)
    found_files = [file.name for file in dependencies]
    assert set(found_files) == set(expected_dependencies)


def test_sphinx_build():
    env = SCons.Environment.Environment()
    env.Append(BUILDERS={"SphinxBuild": scons_extensions.sphinx_build()})
    nodes = env.SphinxBuild(target=["html/index.html"], source=["conf.py", "index.rst"])
    expected_string = "${program} ${options} -b ${builder} ${TARGET.dir.dir.abspath} ${TARGET.dir.abspath} ${tags}"
    check_action_string(nodes, 1, 1, expected_string)


def test_sphinx_latexpdf():
    env = SCons.Environment.Environment()
    env.Append(BUILDERS={"SphinxPDF": scons_extensions.sphinx_latexpdf()})
    nodes = env.SphinxPDF(target=["latex/project.pdf"], source=["conf.py", "index.rst"])
    expected_string = "${program} -M ${builder} ${TARGET.dir.dir.abspath} ${TARGET.dir.dir.abspath} ${tags} ${options}"
    check_action_string(nodes, 1, 1, expected_string)


# Remove the older quinoa builders in favor of the builder factory template for WAVESv1.0
# https://re-git.lanl.gov/aea/python-projects/waves/-/issues/745
quinoa_solver = {
    "default behavior": (
        {}, {}, 2, 1, ["input1.q", "input1.exo"], ["input1.quinoa"]
    ),
    "no defaults": (
        {
         "charmrun": "different charmrun",
         "inciter": "different inciter",
         "charmrun_options": "different charmrun options",
         "inciter_options": "different inciter options",
         "prefix_command": "different prefix command",
         "action_prefix": "different action prefix",
         "action_suffix": "different action suffix"
        },
        {}, 2, 1, ["input2.q", "input2.exo"], ["input2.quinoa"]
    ),
    "task kwargs overrides": (
        {},
        {
         "charmrun": "different charmrun",
         "inciter": "different inciter",
         "charmrun_options": "different charmrun options",
         "inciter_options": "different inciter options",
         "prefix_command": "different prefix command",
         "action_prefix": "different action prefix",
         "action_suffix": "different action suffix"
        },
        2, 1, ["input3.q", "input3.exo"], ["input3.quinoa"]
    )
}


# Remove the older quinoa builders in favor of the builder factory template for WAVESv1.0
# https://re-git.lanl.gov/aea/python-projects/waves/-/issues/745
@pytest.mark.parametrize("builder_kwargs, task_kwargs, node_count, action_count, source_list, target_list",
                         quinoa_solver.values(),
                         ids=quinoa_solver.keys())
def test_quinoa_solver(builder_kwargs, task_kwargs, node_count, action_count, source_list, target_list):
    # Set default expectations to match default argument values
    expected_kwargs = {
        "charmrun": "charmrun",
        "inciter": "inciter",
        "charmrun_options": "+p1",
        "inciter_options": "",
        "prefix_command": "",
        "action_prefix": _cd_action_prefix,
        "action_suffix": _redirect_action_suffix,
    }
    # Update expected arguments to match test case
    expected_kwargs.update(builder_kwargs)
    if expected_kwargs["prefix_command"] and not expected_kwargs["prefix_command"].endswith(" &&"):
        expected_kwargs["prefix_command"] += " &&"
    expected_kwargs.update(task_kwargs)
    # Expected action matches the pre-SCons-substitution string with newline delimiter
    expected_string = \
        "${prefix_command} ${action_prefix} ${charmrun} ${charmrun_options} " \
            "${inciter} ${inciter_options} --control ${SOURCES[0].abspath} --input ${SOURCES[1].abspath} " \
            "${action_suffix}"

    # Assemble the builder and a task to interrogate
    message = "This builder will be replaced by ``waves.scons_extensions.quinoa_builder_factory`` in version 1.0"
    env = SCons.Environment.Environment()
    with patch("warnings.warn") as mock_warn:
        env.Append(BUILDERS={
            "QuinoaSolver": scons_extensions.quinoa_solver(**builder_kwargs)
        })
        mock_warn.assert_called_once_with(message, DeprecationWarning)
    nodes = env.QuinoaSolver(target=target_list, source=source_list, **task_kwargs)

    # Test task definition node counts, action(s), and task keyword arguments
    check_action_string(nodes, node_count, action_count, expected_string)
    for node in nodes:
        for key, expected_value in expected_kwargs.items():
            assert node.env[key] == expected_value


# Remove the older quinoa builders in favor of the builder factory template for WAVESv1.0
# https://re-git.lanl.gov/aea/python-projects/waves/-/issues/745
def test_sbatch_quinoa_solver():
    expected = f'sbatch {_sbatch_wrapper_options} "' \
        '${prefix_command} ${action_prefix} ${charmrun} ${charmrun_options} ' \
        '${inciter} ${inciter_options} --control ${SOURCES[0].abspath} --input ${SOURCES[1].abspath} ' \
        '${action_suffix}"'
    message = "This builder will be replaced by ``waves.scons_extensions.sbatch_quinoa_builder_factory`` in version 1.0"
    with patch("warnings.warn") as mock_warn:
        builder = scons_extensions.sbatch_quinoa_solver()
        mock_warn.assert_any_call(message, DeprecationWarning)
    assert builder.action.cmd_list == expected
    assert builder.emitter == scons_extensions.first_target_emitter


# TODO: Figure out how to cleanly reset the construction environment between parameter sets instead of passing a new
# target per set.
python_script_input = {
    "pass through: no study": (
        2, 1, ["file1.out"], None
    ),
    "pass through: target string": (
        2, 1, "file1.out", None
    ),
    "pass through: target pathlib": (
        2, 1, pathlib.Path("file1.out"), None
    ),
    "pass through: dictionary": (
        2, 1, ["file2.out"], {"parameter_one": 1}
    ),
    "study: two sets": (
        4, 1, ["file3.out"], parameter_generators.CartesianProduct({"one": [1, 2]})
    )
}


@pytest.mark.parametrize("node_count, action_count, target_list, study",
                         python_script_input.values(),
                         ids=python_script_input.keys())
def test_parameter_study(node_count, action_count, target_list, study):
    expected_string = '${action_prefix} ${program} ${python_options} ${SOURCE.abspath} ${script_options} ' \
                          '${action_suffix}'

    env = SCons.Environment.Environment()
    env.Append(BUILDERS={"PythonScript": scons_extensions.python_script()})
    env.AddMethod(scons_extensions.parameter_study, "ParameterStudy")
    nodes = env.ParameterStudy(
        env.PythonScript,
        target=target_list,
        source=["python_script.py"],
        script_options="",
        study=study
    )

    check_action_string(nodes, node_count, action_count, expected_string)


cartesian_product = parameter_generators.CartesianProduct(
    {"parameter_one": [1]},
    set_name_template="set@number"
)
parameter_study_sconscript = {
    "exports not a dictionary": ([], {"exports": list()}, {}, pytest.raises(TypeError)),
    "default kwargs": (
        ["SConscript"],
        {},
        {"variant_dir": None, "exports": {"set_name": "", "parameters": dict()}},
        does_not_raise()
    ),
    "added kwarg": (
        ["SConscript"],
        {"extra kwarg": "value"},
        {"extra kwarg": "value", "variant_dir": None, "exports": {"set_name": "", "parameters": dict()}},
        does_not_raise()
    ),
    "variant_dir": (
        ["SConscript"],
        {"variant_dir": "build"},
        {"variant_dir": pathlib.Path("build"), "exports": {"set_name": "", "parameters": dict()}},
        does_not_raise()
    ),
    "variant_dir subdirectories": (
        ["SConscript"],
        {"variant_dir": "build", "subdirectories": True},
        {"variant_dir": pathlib.Path("build"), "exports": {"set_name": "", "parameters": dict()}},
        does_not_raise()
    ),
    "dictionary study": (
        ["SConscript"],
        {"study": {"parameter_one": 1}},
        {"variant_dir": None, "exports": {"set_name": "", "parameters": {"parameter_one": 1}}},
        does_not_raise()
    ),
    "parameter generator study": (
        ["SConscript"],
        {"study": cartesian_product},
        {"variant_dir": None, "exports": {"set_name": "set0", "parameters": {"parameter_one": 1}}},
        does_not_raise()
    ),
    "parameter generator variant_dir subdirectories": (
        ["SConscript"],
        {"variant_dir": "build", "subdirectories": True, "study": cartesian_product},
        {"variant_dir": pathlib.Path("build/set0"), "exports": {"set_name": "set0", "parameters": {"parameter_one": 1}}},
        does_not_raise()
    ),
    "parameter generator no variant_dir subdirectories": (
        ["SConscript"],
        {"variant_dir": None, "subdirectories": True, "study": cartesian_product},
        {"variant_dir": pathlib.Path("set0"), "exports": {"set_name": "set0", "parameters": {"parameter_one": 1}}},
        does_not_raise()
    ),
}


@pytest.mark.parametrize("args, kwargs, expected, outcome",
                         parameter_study_sconscript.values(),
                         ids=parameter_study_sconscript.keys())
def test_parameter_study_sconscript(args, kwargs, expected, outcome):
    env = SCons.Environment.Environment()

    # Test function style call
    # Git commit 7a95cef7: Normally you expect something like ``patch("SCons.Script.SConscript.SConsEnvironment...")``
    # but Python <=3.10 chokes on the expected patch, so patch the WAVES module itself instead.
    with patch("waves.scons_extensions.SConsEnvironment.SConscript") as mock_SConscript, \
         outcome:
        try:
            scons_extensions.parameter_study_sconscript(env, *args, **kwargs)
            mock_SConscript.assert_called_once_with(*args, **expected)
        finally:
            pass

    # Test AddMethod style call
    env.AddMethod(scons_extensions.parameter_study_sconscript, "ParameterStudySConscript")
    # Git commit 7a95cef7: Normally you expect something like ``patch("SCons.Script.SConscript.SConsEnvironment...")``
    # but Python <=3.10 chokes on the expected patch, so patch the WAVES module itself instead.
    with patch("waves.scons_extensions.SConsEnvironment.SConscript") as mock_SConscript, \
         outcome:
        try:
            env.ParameterStudySConscript(*args, **kwargs)
            mock_SConscript.assert_called_once_with(*args, **expected)
        finally:
            pass


waves_environment_attributes = {
    "default": ({}),
    "no defaults": ({
        "ABAQUS_PROGRAM": "different abaqus",
        "PYTHON_PROGRAM": "different python",
        "CHARMRUN_PROGRAM": "different charmrun",
        "INCITER_PROGRAM": "different inciter",
        "MPIRUN_PROGRAM": "different mpirun",
        "FIERRO_EXPLICIT_PROGRAM": "different fierro-parallel-explicit",
        "FIERRO_IMPLICIT_PROGRAM": "different fierro-parallel-implicit",
        "SIERRA_PROGRAM": "different sierra",
        "ANSYS_PROGRAM": "different ansys",
        "SPHINX_BUILD_PROGRAM": "different sphinx-build",
    }),
}


@pytest.mark.parametrize("kwargs",
                         waves_environment_attributes.values(),
                         ids=waves_environment_attributes.keys())
def test_waves_environment_attributes(kwargs):
    expected_attributes = {
        "ABAQUS_PROGRAM": "abaqus",
        "PYTHON_PROGRAM": "python",
        "CHARMRUN_PROGRAM": "charmrun",
        "INCITER_PROGRAM": "inciter",
        "MPIRUN_PROGRAM": "mpirun",
        "FIERRO_EXPLICIT_PROGRAM": "fierro-parallel-explicit",
        "FIERRO_IMPLICIT_PROGRAM": "fierro-parallel-implicit",
        "SIERRA_PROGRAM": "sierra",
        "ANSYS_PROGRAM": "ansys",
        "SPHINX_BUILD_PROGRAM": "sphinx-build",
    }
    expected_attributes.update(**kwargs)
    env = scons_extensions.WAVESEnvironment(**kwargs)
    for key, value in expected_attributes.items():
        assert env[key] == value


waves_environment_methods = {
    "PrintBuildFailures": ("PrintBuildFailures", "print_build_failures"),
    "CheckProgram": ("CheckProgram", "check_program"),
    "FindProgram": ("FindProgram", "find_program"),
    "AddProgram": ("AddProgram", "add_program"),
    "AddCubit": ("AddCubit", "add_cubit"),
    "AddCubitPython": ("AddCubitPython", "add_cubit_python"),
    "CopySubstfile": ("CopySubstfile", "copy_substfile"),
    "ProjectHelp": ("ProjectHelp", "project_help_message"),
    "SubstitutionSyntax": ("SubstitutionSyntax", "substitution_syntax"),
    "ParameterStudy": ("ParameterStudy", "parameter_study"),
    "ParameterStudySConscript": ("ParameterStudySConscript", "parameter_study_sconscript"),
}


@pytest.mark.parametrize("method, function",
                         waves_environment_methods.values(),
                         ids=waves_environment_methods.keys())
def test_waves_environment_methods(method, function):
    args = ["arg1"]
    kwargs = {"kwarg1": "value1"}
    env = scons_extensions.WAVESEnvironment()
    attribute = getattr(env, method)
    with patch(f"waves.scons_extensions.{function}") as mock_function:
        attribute(*args, **kwargs)
        mock_function.assert_called_once_with(env, *args, **kwargs)


waves_environment_builders = {
    "FirstTargetBuilder": ("FirstTargetBuilder", "first_target_builder_factory", {}),
    "AbaqusJournal": ("AbaqusJournal", "abaqus_journal_builder_factory", {"program": "${ABAQUS_PROGRAM}"}),
    "AbaqusSolver": ("AbaqusSolver", "abaqus_solver_builder_factory", {"program": "${ABAQUS_PROGRAM}"}),
    "PythonScript": ("PythonScript", "python_builder_factory", {"program": "${PYTHON_PROGRAM}"}),
    "QuinoaSolver": (
        "QuinoaSolver",
        "quinoa_builder_factory",
        {"program": "${CHARMRUN_PROGRAM}", "subcommand": "${INCITER_PROGRAM}"}
    ),
    "FierroExplicit": (
        "FierroExplicit",
        "fierro_explicit_builder_factory",
        {"program": "${MPIRUN_PROGRAM}", "subcommand": "${FIERRO_EXPLICIT_PROGRAM}"}
    ),
    "FierroImplicit": (
        "FierroImplicit",
        "fierro_implicit_builder_factory",
        {"program": "${MPIRUN_PROGRAM}", "subcommand": "${FIERRO_IMPLICIT_PROGRAM}"}
    ),
    "Sierra": (
        "Sierra",
        "sierra_builder_factory",
        {"program": "${SIERRA_PROGRAM}"}
    ),
    "AnsysAPDL": ("AnsysAPDL", "ansys_apdl_builder_factory", {"program": "${ANSYS_PROGRAM}"}),
    "SphinxBuild": ("SphinxBuild", "sphinx_build", {"program": "${SPHINX_BUILD_PROGRAM}"}),
    "SphinxPDF": ("SphinxPDF", "sphinx_latexpdf", {"program": "${SPHINX_BUILD_PROGRAM}"}),
}


@pytest.mark.parametrize("builder, factory, factory_kwargs",
                         waves_environment_builders.values(),
                         ids=waves_environment_builders.keys())
def test_waves_environment_builders(builder, factory, factory_kwargs):
    env = scons_extensions.WAVESEnvironment()

    args = ["arg1"]
    kwargs = {"kwarg1": "value1"}
    target = [f"{builder}.target"]
    source = [ f"{builder}.source"]
    mock_builder = unittest.mock.Mock()

    attribute = getattr(env, builder)
    with patch(f"waves.scons_extensions.{factory}", return_value=mock_builder) as mock_factory:
        attribute(target, source, *args, **kwargs)
        mock_factory.assert_called_once_with(**factory_kwargs)
        mock_builder.assert_called_once_with(env, *args, target=target, source=source, **kwargs)
