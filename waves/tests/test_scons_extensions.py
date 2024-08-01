"""Test WAVES SCons builders and support functions"""

import os
import pathlib
from contextlib import nullcontext as does_not_raise
import unittest
from unittest.mock import patch, call
import subprocess

import pytest
import SCons.Node.FS

from waves import scons_extensions
from waves import parameter_generators
from waves._settings import _cd_action_prefix
from waves._settings import _redirect_action_postfix
from waves._settings import _redirect_environment_postfix
from waves._settings import _abaqus_environment_extension
from waves._settings import _abaqus_datacheck_extensions
from waves._settings import _abaqus_explicit_extensions
from waves._settings import _abaqus_standard_extensions
from waves._settings import _abaqus_solver_common_suffixes
from waves._settings import _stdout_extension
from common import platform_check


fs = SCons.Node.FS.FS()

testing_windows, root_fs = platform_check()


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
    with patch("atexit.register") as mock_atexit:
        scons_extensions.print_build_failures(True)
        mock_atexit.assert_called_once_with(scons_extensions._print_failed_nodes_stdout)
    with patch("atexit.register") as mock_atexit:
        scons_extensions.print_build_failures(False)
        mock_atexit.assert_not_called()


string_action_list = {
    "one action": (SCons.Builder.Builder(action="one action"), ["one action"]),
    "two actions": (SCons.Builder.Builder(action=["first action", "second action"]), ["first action", "second action"]),
}


@pytest.mark.parametrize("builder, expected",
                         string_action_list.values(),
                         ids=string_action_list.keys())
def test_string_action_list(builder, expected):
    action_list = scons_extensions._string_action_list(builder)
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


def test_ssh_builder_actions():
    remote_server = "myserver.mydomain.com"
    remote_directory = "/scratch/roppenheimer/ssh_wrapper"

    def cat(program="cat"):
        return SCons.Builder.Builder(action=[
                f"{program} ${{SOURCE.abspath}} | tee ${{TARGETS.file}}",
                f"{program} ${{SOURCES.abspath}} | tee ${{TARGETS.file}}",
                f"{program} ${{SOURCES[99].abspath}} | tee ${{TARGETS.file}}",
                f"{program} ${{SOURCES[-1].abspath}} | tee ${{TARGETS.file}}",
                "cat ${SOURCES[-1].abspath} > ${TARGETS[-1].abspath}",
                "echo \"Hello World!\""
        ])

    build_cat = cat()
    build_cat_action_list = [action.cmd_list for action in build_cat.action.list]
    expected = [
        "cat ${SOURCE.abspath} | tee ${TARGETS.file}",
        "cat ${SOURCES.abspath} | tee ${TARGETS.file}",
        "cat ${SOURCES[99].abspath} | tee ${TARGETS.file}",
        "cat ${SOURCES[-1].abspath} | tee ${TARGETS.file}",
        "cat ${SOURCES[-1].abspath} > ${TARGETS[-1].abspath}",
        'echo "Hello World!"'
    ]
    assert build_cat_action_list == expected

    ssh_build_cat = scons_extensions.ssh_builder_actions(
        cat(), remote_server=remote_server
    )
    ssh_build_cat_action_list = [action.cmd_list for action in ssh_build_cat.action.list]
    expected = [
        f'ssh {remote_server} "mkdir -p ${{remote_directory}}"',
        f"rsync -rlptv ${{SOURCES.abspath}} {remote_server}:${{remote_directory}}",
        f"ssh {remote_server} 'cd ${{remote_directory}} && cat ${{SOURCE.file}} | tee ${{TARGETS.file}}'",
        f"ssh {remote_server} 'cd ${{remote_directory}} && cat ${{SOURCES.file}} | tee ${{TARGETS.file}}'",
        f"ssh {remote_server} 'cd ${{remote_directory}} && cat ${{SOURCES[99].file}} | tee ${{TARGETS.file}}'",
        f"ssh {remote_server} 'cd ${{remote_directory}} && cat ${{SOURCES[-1].file}} | tee ${{TARGETS.file}}'",
        f"ssh {remote_server} 'cd ${{remote_directory}} && cat ${{SOURCES[-1].file}} > ${{TARGETS[-1].file}}'",
        f"ssh {remote_server} 'cd ${{remote_directory}} && echo \"Hello World!\"'",
        f"rsync -rltpv {remote_server}:${{remote_directory}}/ ${{TARGET.dir.abspath}}"
    ]
    assert ssh_build_cat_action_list == expected

    ssh_python_builder = scons_extensions.ssh_builder_actions(
        scons_extensions.python_script()
    )
    ssh_python_builder_action_list = [action.cmd_list for action in ssh_python_builder.action.list]
    expected = [
        'ssh ${remote_server} "mkdir -p ${remote_directory}"',
        "rsync -rlptv ${SOURCES.abspath} ${remote_server}:${remote_directory}",
        "ssh ${remote_server} '${action_prefix} ${program} ${python_options} ${SOURCE.file} " \
            "${script_options} ${action_suffix}'",
        "rsync -rltpv ${remote_server}:${remote_directory}/ ${TARGET.dir.abspath}"
    ]
    assert ssh_python_builder_action_list == expected


def check_action_string(nodes, post_action, node_count, action_count, expected_string,
                        post_action_prefix="cd ${TARGET.dir.abspath} &&"):
    """Verify the expected action string against a builder's target nodes

    :param SCons.Node.NodeList nodes: Target node list returned by a builder
    :param list post_action: list of post action strings passed to builder
    :param int node_count: expected length of ``nodes``
    :param int action_count: expected length of action list for each node
    :param str expected_string: the builder's action string.

    .. note::

       The method of interrogating a node's action list results in a newline separated string instead of a list of
       actions. The ``expected_string`` should contain all elements of the expected action list as a single, newline
       separated string. The ``action_count`` should be set to ``1`` until this method is updated to search for the
       finalized action list.
    """
    for action in post_action:
        expected_string = expected_string + f"\n{post_action_prefix} {action}"
    assert len(nodes) == node_count
    for node in nodes:
        node.get_executor()
        assert len(node.executor.action_list) == action_count
        assert str(node.executor.action_list[0]) == expected_string


def check_expected_targets(nodes, solver, stem, suffixes):
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


prepend_env_input = {
    "path exists": (f"{root_fs}program", True, does_not_raise()),
    "path does not exist": (f"{root_fs}notapath", False, pytest.raises(FileNotFoundError))
}


@pytest.mark.parametrize("program, mock_exists, outcome",
                         prepend_env_input.values(),
                         ids=prepend_env_input.keys())
def test_append_env_path(program, mock_exists, outcome):
    env = SCons.Environment.Environment()
    with patch("pathlib.Path.exists", return_value=mock_exists), outcome:
        try:
            scons_extensions.append_env_path(program, env)
            assert root_fs == env["ENV"]["PATH"].split(os.pathsep)[-1]
            assert "PYTHONPATH" not in env["ENV"]
            assert "LD_LIBRARY_PATH" not in env["ENV"]
        finally:
            pass


substitution_dictionary = {"thing1": 1, "thing_two": "two"}
substitution_syntax_input = {
    "default characters": (substitution_dictionary, {}, {"@thing1@": 1, "@thing_two@": "two"}),
    "provided pre/postfix": (substitution_dictionary, {"prefix": "$", "postfix": "%"},
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
    output_dictionary = scons_extensions.substitution_syntax(substitution_dictionary, **keyword_arguments)
    assert output_dictionary == expected_dictionary


return_environment = {
    "no newlines": (b"thing1=a\x00thing2=b", {"thing1": "a", "thing2": "b"}),
    "newlines": (b"thing1=a\nnewline\x00thing2=b", {"thing1": "a\nnewline", "thing2": "b"})
}


@pytest.mark.parametrize("stdout, expected",
                         return_environment.values(),
                         ids=return_environment.keys())
def test_return_environment(stdout, expected):
    """
    :param bytes stdout: byte string with null delimited shell environment variables
    :param dict expected: expected dictionary output containing string key:value pairs and preserving newlines
    """
    mock_run_return = subprocess.CompletedProcess(args="dummy", returncode=0, stdout=stdout)
    with patch("subprocess.run", return_value=mock_run_return):
        environment_dictionary = scons_extensions._return_environment("dummy")
    assert environment_dictionary == expected


cache_environment = {
        # cache,       overwrite_cache, expected,        file_exists
    "no cache":
        (None,         False,           {"thing1": "a"}, False),
    "cache exists":
        ("dummy.yaml", False,           {"thing1": "a"}, True),
    "cache doesn't exist":
        ("dummy.yaml", False,           {"thing1": "a"}, False),
    "overwrite cache":
        ("dummy.yaml", True,            {"thing1": "a"}, True),
    "don't overwrite cache":
        ("dummy.yaml", False,           {"thing1": "a"}, False)
}


@pytest.mark.parametrize("cache, overwrite_cache, expected, file_exists",
                         cache_environment.values(),
                         ids=cache_environment.keys())
def test_cache_environment(cache, overwrite_cache, expected, file_exists):
    with patch("waves.scons_extensions._return_environment", return_value=expected) as return_environment, \
         patch("yaml.safe_load", return_value=expected) as yaml_load, \
         patch("pathlib.Path.exists", return_value=file_exists), \
         patch("yaml.safe_dump") as yaml_dump, \
         patch("builtins.open"):
        environment_dictionary = scons_extensions._cache_environment("dummy command", cache=cache,
                                                                     overwrite_cache=overwrite_cache)
        if cache and file_exists and not overwrite_cache:
            yaml_load.assert_called_once()
            return_environment.assert_not_called()
        else:
            yaml_load.assert_not_called()
            return_environment.assert_called_once()
        if cache:
            yaml_dump.assert_called_once()
    assert environment_dictionary == expected


shell_environment = {
    "no cache": (None, False, {"thing1": "a"}, True),
    "cache": ("dummy.yaml", False, {"thing1": "a"}, True),
    "cache overwrite": ("dummy.yaml", True, {"thing1": "a"}, True),
}


@pytest.mark.skipif(testing_windows, reason="BASH shell specific function incompatible with Windows")
@pytest.mark.parametrize("cache, overwrite_cache, expected, verbose",
                         shell_environment.values(),
                         ids=shell_environment.keys())
def test_shell_environment(cache, overwrite_cache, expected, verbose):
    with patch("waves.scons_extensions._cache_environment", return_value=expected) as cache_environment:
        env = scons_extensions.shell_environment("dummy", cache=cache, overwrite_cache=overwrite_cache)
        cache_environment.assert_called_once_with("dummy", cache=cache, overwrite_cache=overwrite_cache,
                                                  verbose=verbose)
    # Check that the expected dictionary is a subset of the SCons construction environment
    assert all(env["ENV"].get(key, None) == value for key, value in expected.items())


prefix = f"{_cd_action_prefix}"
postfix = "postfix"
construct_action_list = {
    "list1": (["thing1"], prefix, "", [f"{prefix} thing1"]),
    "list2": (["thing1", "thing2"], prefix, "", [f"{prefix} thing1", f"{prefix} thing2"]),
    "tuple": (("thing1",), prefix, "", [f"{prefix} thing1"]),
    "str":  ("thing1", prefix, "", [f"{prefix} thing1"]),
    "list1 postfix": (["thing1"], prefix, postfix, [f"{prefix} thing1 {postfix}"]),
    "list2 postfix": (["thing1", "thing2"], prefix, postfix, [f"{prefix} thing1 {postfix}", f"{prefix} thing2 {postfix}"]),
    "tuple postfix": (("thing1",), prefix, postfix, [f"{prefix} thing1 {postfix}"]),
    "str postfix":  ("thing1", prefix, postfix, [f"{prefix} thing1 {postfix}"]),
}


@pytest.mark.parametrize("actions, prefix, postfix, expected",
                         construct_action_list.values(),
                         ids=construct_action_list.keys())
def test_construct_action_list(actions, prefix, postfix, expected):
    output = scons_extensions.construct_action_list(actions, prefix=prefix, postfix=postfix)
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
        {"program": "abaqus"}, [], 3, 1, ["journal1.cae"]
    ),
    "no defaults": (
        {
         "program": "someothercommand",
         "action_prefix": "nocd",
         "required": "cae python",
         "action_suffix": "",
         "environment_suffix": ""
        },
        [], 3, 1, ["nodefaults.cae"]
    ),
    "different command": (
        {"program": "dummy"}, [], 3, 1, ["journal2.cae"]
    ),
    "post action": (
        {"program": "abaqus"}, ["post action"], 3, 1, ["journal3.cae"]
    )
}


@pytest.mark.parametrize("kwargs, post_action, node_count, action_count, target_list",
                         abaqus_journal_input.values(),
                         ids=abaqus_journal_input.keys())
def test_abaqus_journal(kwargs, post_action, node_count, action_count, target_list):
    # Set default expectations to match default argument values
    expected_kwargs = {
        "program": "abaqus",
        "required": "cae -noGUI ${SOURCE.abspath}",
        "action_prefix": _cd_action_prefix,
        "action_suffix": _redirect_action_postfix,
        "environment_suffix": _redirect_environment_postfix
    }
    # Update expected arguments to match test case
    expected_kwargs.update(kwargs)
    # Expected action matches the pre-SCons-substitution string with newline delimiter
    expected_string = '${action_prefix} ${program} -information environment ${environment_suffix}\n' \
                      '${action_prefix} ${program} ${required} ${abaqus_options} -- ${journal_options} ' \
                          '${action_suffix}'

    # Assemble the builder and a task to interrogate
    env = SCons.Environment.Environment()
    env.Append(BUILDERS={"AbaqusJournal": scons_extensions.abaqus_journal(**kwargs, post_action=post_action)})
    nodes = env.AbaqusJournal(target=target_list, source=["journal.py"], journal_options="")

    # Test task definition node counts, action(s), and task keyword arguments
    check_action_string(nodes, post_action, node_count, action_count, expected_string,
                        post_action_prefix="${action_prefix}")
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
        {"program": "abaqus", "post_action": []}, 7, 1, ["input1.inp"], None
    ),
    "no defaults": (
        {
         "program": "notdefault",
         "required": "-other options",
         "action_prefix": "nocd",
         "action_suffix": "",
         "environment_suffix": "",
         "post_action": []
        },
        7, 1, ["nodefaults.inp"], None
    ),
    "different command": (
        {"program": "dummy", "post_action": []}, 7, 1, ["input2.inp"], None
    ),
    "post action": (
        {"program": "abaqus", "post_action": ["post action"]}, 7, 1, ["input3.inp"], None
    ),
    "standard solver": (
        {"program": "abaqus", "emitter": "standard", "post_action": []}, 8, 1, ["input4.inp"], None
    ),
    "explicit solver": (
        {"program": "abaqus", "emitter": "explicit", "post_action": []}, 8, 1, ["input5.inp"], None
    ),
    "datacheck solver": (
        {"program": "abaqus", "emitter": "datacheck", "post_action": []}, 11, 1, ["input6.inp"], None
    ),
    "standard solver, suffixes override": (
        {"program": "abaqus", "emitter": "standard", "post_action": []}, 3, 1, ["input4.inp"], [".odb"]
    ),
}


@pytest.mark.parametrize("kwargs, node_count, action_count, source_list, suffixes",
                         abaqus_solver_input.values(),
                         ids=abaqus_solver_input.keys())
def test_abaqus_solver(kwargs, node_count, action_count, source_list, suffixes):
    # Set default expectations to match default argument values
    expected_kwargs = {
        "program": "abaqus",
        "required": "-interactive -ask_delete no",
        "action_prefix": _cd_action_prefix,
        "action_suffix": _redirect_action_postfix,
        "environment_suffix": _redirect_environment_postfix,
        "emitter": None,
        "post_action": []
    }
    # Update expected arguments to match test case
    expected_kwargs.update(kwargs)
    # Expected action matches the pre-SCons-substitution string with newline delimiter
    expected_string = \
        "${action_prefix} ${program} -information environment ${environment_suffix}\n" \
        "${action_prefix} ${program} -job ${job_name} -input ${SOURCE.filebase} ${abaqus_options} ${required} " \
            "${action_suffix}"

    # Assemble the builder and a task to interrogate
    env = SCons.Environment.Environment()
    env.Append(BUILDERS={
        "AbaqusSolver": scons_extensions.abaqus_solver(**kwargs)
    })
    nodes = env.AbaqusSolver(target=[], source=source_list, abaqus_options="", suffixes=suffixes)

    # Test task definition node counts, action(s), and task keyword arguments
    check_action_string(
        nodes, kwargs["post_action"], node_count, action_count, expected_string, post_action_prefix="${action_prefix}"
    )
    check_expected_targets(nodes, expected_kwargs["emitter"], pathlib.Path(source_list[0]).stem, suffixes)
    expected_kwargs.pop("emitter")
    expected_kwargs.pop("post_action")
    for node in nodes:
        for key, expected_value in expected_kwargs.items():
            assert node.env[key] == expected_value


def test_sbatch_abaqus_solver():
    expected = 'sbatch --wait --output=${TARGET.base}.slurm.out ${sbatch_options} --wrap "' \
               '${action_prefix} ${program} -information environment ${environment_suffix} && ' \
               '${action_prefix} ${program} -job ${job_name} -input ${SOURCE.filebase} ${abaqus_options} ${required} ' \
                   '${action_suffix}"'
    builder = scons_extensions.sbatch_abaqus_solver()
    assert builder.action.cmd_list == expected
    assert builder.emitter == scons_extensions._abaqus_solver_emitter


source_file = fs.File("dummy.i")
sierra_emitter_input = {
    "one target": (
        ["target.sierra"],
        [source_file],
        ["target.sierra", "target.sierra.env", "target.sierra.stdout"]
    ),
    "subdirectory": (
        ["set1/dummy.sierra"],
        [source_file],
        ["set1/dummy.sierra", f"set1{os.sep}dummy.sierra.env", f"set1{os.sep}dummy.sierra.stdout"]
    )
}


@pytest.mark.parametrize("target, source, expected",
                         sierra_emitter_input.values(),
                         ids=sierra_emitter_input.keys())
def test_sierra_emitter(target, source, expected):
    target, source = scons_extensions._sierra_emitter(target, source, None)
    assert target == expected


# TODO: Figure out how to cleanly reset the construction environment between parameter sets instead of passing a new
# target per set.
sierra_input = {
    "default behavior": (
        {}, [], 3, 1, ["input1.i"], ['inptu1.g']
    ),
    "no defaults": (
        {
         "program": "different program",
         "application": "different application",
         "action_prefix": "different prefix",
         "action_suffix": "different action suffix",
         "environment_suffix": "different environment suffix",
        },
        [], 3, 1, ["nodefaults.i"], ['nodefaults.g']
    ),
    "different command": (
        {"program": "dummy", "application": "application"}, [], 3, 1, ["input2.i"], ['inptu2.g']
    ),
    "post action": (
        {}, ["post action"], 3, 1, ["input3.i"], ['inptu3.g']
    ),
}


@pytest.mark.parametrize("kwargs, post_action, node_count, action_count, source_list, target_list",
                         sierra_input.values(),
                         ids=sierra_input.keys())
def test_sierra(kwargs, post_action, node_count, action_count, source_list, target_list):
    # Set default expectations to match default argument values
    expected_kwargs = {
        "program": "sierra",
        "application": "adagio",
        "action_prefix": _cd_action_prefix,
        "action_suffix": _redirect_action_postfix,
        "environment_suffix": _redirect_environment_postfix
    }
    # Update expected arguments to match test case
    expected_kwargs.update(kwargs)
    # Expected action matches the pre-SCons-substitution string with newline delimiter
    expected_string = \
        "${action_prefix} ${program} ${application} --version ${environment_suffix}\n" \
        "${action_prefix} ${program} ${sierra_options} ${application} ${application_options} -i ${SOURCE.file} ${action_suffix}"

    # Assemble the builder and a task to interrogate
    env = SCons.Environment.Environment()
    env.Append(BUILDERS={
        "Sierra": scons_extensions.sierra(**kwargs, post_action=post_action)
    })

    # Test task definition node counts, action(s), and task keyword arguments
    nodes = env.Sierra(target=target_list, source=source_list, sierra_options="", application_options="")
    check_action_string(nodes, post_action, node_count, action_count, expected_string,
                        post_action_prefix="${action_prefix}")
    for node in nodes:
        for key, expected_value in expected_kwargs.items():
            assert node.env[key] == expected_value


def test_sbatch_sierra():
    expected = 'sbatch --wait --output=${TARGET.base}.slurm.out ${sbatch_options} --wrap "' \
        '${action_prefix} ${program} ${application} --version ${environment_suffix} && ' \
        '${action_prefix} ${program} ${sierra_options} ${application} ${application_options} -i ${SOURCE.file} ' \
           '${action_suffix}"'
    builder = scons_extensions.sbatch_sierra()
    assert builder.action.cmd_list == expected
    assert builder.emitter == scons_extensions._sierra_emitter


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
    target, source = scons_extensions._first_target_emitter(target, source, None)
    assert target == expected


# TODO: Figure out how to cleanly reset the construction environment between parameter sets instead of passing a new
# target per set.
python_script_input = {
    "default behavior": ({}, [], 2, 1, ["python_script1.out"]),
    "no defaults": (
        {
         "program": "different program",
         "action_prefix": "different prefix",
         "action_suffix": "different action suffix",
        },
        [], 2, 1, ["nodefaults.out"]
    ),
    "different command": ({"program": "python2"}, [], 2, 1, ["python_script2.out"]),
    "post action": ({}, ["post action"], 2, 1, ["python_script3.out"])
}


@pytest.mark.parametrize("kwargs, post_action, node_count, action_count, target_list",
                         python_script_input.values(),
                         ids=python_script_input.keys())
def test_python_script(kwargs, post_action, node_count, action_count, target_list):
    # Set default expectations to match default argument values
    expected_kwargs = {
        "program": "python",
        "action_prefix": _cd_action_prefix,
        "action_suffix": _redirect_action_postfix,
    }
    # Update expected arguments to match test case
    expected_kwargs.update(kwargs)
    # Expected action matches the pre-SCons-substitution string with newline delimiter
    expected_string = \
       "${action_prefix} ${program} ${python_options} ${SOURCE.abspath} ${script_options} ${action_suffix}"

    # Assemble the builder and a task to interrogate
    env = SCons.Environment.Environment()
    env.Append(BUILDERS={"PythonScript": scons_extensions.python_script(**kwargs, post_action=post_action)})
    nodes = env.PythonScript(target=target_list, source=["python_script.py"], script_options="")

    # Test task definition node counts, action(s), and task keyword arguments
    check_action_string(nodes, post_action, node_count, action_count, expected_string,
                        post_action_prefix="${action_prefix}")
    for node in nodes:
        for key, expected_value in expected_kwargs.items():
            assert node.env[key] == expected_value


def test_sbatch_python_script():
    expected = 'sbatch --wait --output=${TARGET.base}.slurm.out ${sbatch_options} --wrap "' \
       '${action_prefix} ${program} ${python_options} ${SOURCE.abspath} ${script_options} ${action_suffix}"'
    builder = scons_extensions.sbatch_python_script()
    assert builder.action.cmd_list == expected
    assert builder.emitter == scons_extensions._first_target_emitter


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
        {}, [], 3, 1, ["matlab_script1.out"]
    ),
    "no defaults": (
        {
         "program": "different program",
         "action_prefix": "different action prefix",
         "action_suffix": "different action suffix",
         "environment_suffix": "different environment suffix",
        },
        [], 3, 1, ["nodefaults.out"]
    ),
    "different command": (
        {"program": "/different/matlab"}, [], 3, 1, ["matlab_script2.out"]
    ),
    "post action": (
        {}, ["post action"], 3, 1, ["matlab_script3.out"]
    )
}


@pytest.mark.parametrize("kwargs, post_action, node_count, action_count, target_list",
                         matlab_script_input.values(),
                         ids=matlab_script_input.keys())
def test_matlab_script(kwargs, post_action, node_count, action_count, target_list):
    # Set default expectations to match default argument values
    expected_kwargs = {
        "program": "matlab",
        "action_prefix": _cd_action_prefix,
        "action_suffix": _redirect_action_postfix,
        "environment_suffix": _redirect_environment_postfix,
    }
    # Update expected arguments to match test case
    expected_kwargs.update(kwargs)
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
    env.Append(BUILDERS={"MatlabScript": scons_extensions.matlab_script(**kwargs, post_action=post_action)})
    nodes = env.MatlabScript(target=target_list, source=["matlab_script.py"], script_options="")

    # Test task definition node counts, action(s), and task keyword arguments
    check_action_string(nodes, post_action, node_count, action_count, expected_string,
                        post_action_prefix="${action_prefix}")
    for node in nodes:
        for key, expected_value in expected_kwargs.items():
            assert node.env[key] == expected_value


def test_conda_environment():
    env = SCons.Environment.Environment()
    env.Append(BUILDERS={"CondaEnvironment": scons_extensions.conda_environment()})
    nodes = env.CondaEnvironment(
        target=["environment.yaml"], source=[], conda_env_export_options="")
    expected_string = 'cd ${TARGET.dir.abspath} && conda env export ${conda_env_export_options} --file ${TARGET.file}'
    check_action_string(nodes, [], 1, 1, expected_string)


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
    check_action_string(nodes, [], 3, 1, expected_string)


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
    "default behavior": ("sbatch", [], 2, 1, ["target1.out"]),
    "different command": ("dummy", [], 2, 1, ["target2.out"]),
    "post action": ("sbatch", ["post action"], 2, 1, ["target3.out"])
}


@pytest.mark.parametrize("program, post_action, node_count, action_count, target_list",
                         sbatch_input.values(),
                         ids=sbatch_input.keys())
def test_sbatch(program, post_action, node_count, action_count, target_list):
    env = SCons.Environment.Environment()
    expected_string = f'cd ${{TARGET.dir.abspath}} && {program} --wait --output=${{TARGETS[-1].abspath}} ' \
                       '${sbatch_options} --wrap "${slurm_job}"'

    env.Append(BUILDERS={"SlurmSbatch": scons_extensions.sbatch(program, post_action)})
    nodes = env.SlurmSbatch(target=target_list, source=["source.in"], sbatch_options="",
                            slurm_job="echo $SOURCE > $TARGET")
    check_action_string(nodes, post_action, node_count, action_count, expected_string)


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
    check_action_string(nodes, [], 1, 1, expected_string)


def test_sphinx_latexpdf():
    env = SCons.Environment.Environment()
    env.Append(BUILDERS={"SphinxPDF": scons_extensions.sphinx_latexpdf()})
    nodes = env.SphinxPDF(target=["latex/project.pdf"], source=["conf.py", "index.rst"])
    expected_string = "${program} -M ${builder} ${TARGET.dir.dir.abspath} ${TARGET.dir.dir.abspath} ${tags} ${options}"
    check_action_string(nodes, [], 1, 1, expected_string)


quinoa_solver = {
    "default behavior": ("charmrun", "inciter", "+p1", "", "", [],  2, 1, ["input1.q", "input1.exo"], ["input1.quinoa"]),
    "different commands": ("notcharmrun", "notinciter", "+p2", "inciter options", "prefix", [],  2, 1,
                           ["input2.q", "input2.exo"], ["input2.quinoa"]),
    "post action": ("charmrun", "inciter", "+p1", "", "", ["post action"],  2, 1,
                    ["input3.q", "input3.exo"], ["input3.quinoa"]),
}


@pytest.mark.parametrize("charmrun, inciter, charmrun_options, inciter_options, prefix_command, post_action, node_count, action_count, source_list, target_list",
                         quinoa_solver.values(),
                         ids=quinoa_solver.keys())
def test_quinoa_solver(charmrun, inciter, charmrun_options, inciter_options, prefix_command, post_action,
                       node_count, action_count, source_list, target_list):
    env = SCons.Environment.Environment()
    expected_string = f"${{prefix_command}} {_cd_action_prefix} ${{charmrun}} ${{charmrun_options}} " \
                      "${inciter} ${inciter_options} --control ${SOURCES[0].abspath} --input ${SOURCES[1].abspath} " \
                      f"{_redirect_action_postfix}"
    env.Append(BUILDERS={"QuinoaSolver": scons_extensions.quinoa_solver(
        charmrun=charmrun,
        inciter=inciter,
        charmrun_options=charmrun_options,
        inciter_options=inciter_options,
        prefix_command=prefix_command,
        post_action=post_action
    )})
    nodes = env.QuinoaSolver(target=target_list, source=source_list)
    check_action_string(nodes, post_action, node_count, action_count, expected_string)
    for node in nodes:
        if prefix_command:
            assert node.env['prefix_command'] == prefix_command + " &&"
        else:
            assert node.env['prefix_command'] == ""
        assert node.env['charmrun'] == charmrun
        assert node.env['charmrun_options'] == charmrun_options
        assert node.env['inciter'] == inciter
        assert node.env['inciter_options'] == inciter_options


# TODO: Figure out how to cleanly reset the construction environment between parameter sets instead of passing a new
# target per set.
fierro_input = {
    "default behavior": ("fierro", "parallel-explicit", [], 2, 1, ["input1.yaml"], ['input1.fierro']),
    "different command": ("dummy", "parallel-implicit", [], 2, 1, ["input2.yaml"], ['input2.fierro']),
    "post action": ("fierro", "subcommand", ["post action"], 2, 1, ["input3.yaml"], ['input3.fierro']),
}


@pytest.mark.parametrize("program, subcommand, post_action, node_count, action_count, source_list, target_list",
                         fierro_input.values(),
                         ids=fierro_input.keys())
def test_fierro_builder(program, subcommand, post_action, node_count, action_count, source_list, target_list):
    env = SCons.Environment.Environment()
    expected_string = '${cd_action_prefix} ${mpirun} ${mpirun_options} ${program}-${subcommand} ${required} ' \
                      '${options} ${redirect_action_postfix}'

    env.Append(BUILDERS={"FierroBuilder": scons_extensions.fierro_builder(program=program, subcommand=subcommand, post_action=post_action)})
    nodes = env.FierroBuilder(target=target_list, source=source_list)
    check_action_string(nodes, post_action, node_count, action_count, expected_string,
                        post_action_prefix="${cd_action_prefix}")
    for node in nodes:
        assert node.env['program'] == program
        assert node.env['subcommand'] == subcommand


# TODO: Figure out how to cleanly reset the construction environment between parameter sets instead of passing a new
# target per set.
fierro_explicit = {
    "default behavior": ([], 2, 1, ["input1_explicit.yaml"], ['input1_explicit.fierro']),
}


@pytest.mark.parametrize("post_action, node_count, action_count, source_list, target_list",
                         fierro_explicit.values(),
                         ids=fierro_explicit.keys())
def test_fierro_explicit(post_action, node_count, action_count, source_list, target_list):
    env = SCons.Environment.Environment()
    expected_string = '${cd_action_prefix} ${mpirun} ${mpirun_options} ${program}-${subcommand} ${required} ' \
                      '${options} ${redirect_action_postfix}'

    env.Append(BUILDERS={"FierroExplicit": scons_extensions.fierro_explicit(post_action=post_action)})
    nodes = env.FierroExplicit(target=target_list, source=source_list)
    check_action_string(nodes, post_action, node_count, action_count, expected_string,
                        post_action_prefix="${cd_action_prefix}")
    for node in nodes:
        assert node.env['program'] == "fierro"
        assert node.env['subcommand'] == "parallel-explicit"


# TODO: Figure out how to cleanly reset the construction environment between parameter sets instead of passing a new
# target per set.
fierro_implicit = {
    "default behavior": ([], 2, 1, ["input1_implicit.yaml"], ['input1_implicit.fierro']),
}


@pytest.mark.parametrize("post_action, node_count, action_count, source_list, target_list",
                         fierro_implicit.values(),
                         ids=fierro_implicit.keys())
def test_fierro_implicit(post_action, node_count, action_count, source_list, target_list):
    env = SCons.Environment.Environment()
    expected_string = '${cd_action_prefix} ${mpirun} ${mpirun_options} ${program}-${subcommand} ${required} ' \
                      '${options} ${redirect_action_postfix}'

    env.Append(BUILDERS={"FierroImplicit": scons_extensions.fierro_implicit(post_action=post_action)})
    nodes = env.FierroImplicit(target=target_list, source=source_list)
    check_action_string(nodes, post_action, node_count, action_count, expected_string,
                        post_action_prefix="${cd_action_prefix}")
    for node in nodes:
        assert node.env['program'] == "fierro"
        assert node.env['subcommand'] == "parallel-implicit"


# TODO: Figure out how to cleanly reset the construction environment between parameter sets instead of passing a new
# target per set.
ansys_apdl_input = {
    "default behavior": ("ansys232", [], 2, 1, ["input1.dat"], ['input1.ansys']),
    "different command": ("dummy", [], 2, 1, ["input2.dat"], ['input2.ansys']),
    "post action": ("ansys", ["post action"], 2, 1, ["input3.dat"], ['input3.ansys']),
}


@pytest.mark.parametrize("program, post_action, node_count, action_count, source_list, target_list",
                         ansys_apdl_input.values(),
                         ids=ansys_apdl_input.keys())
def test_ansys_apdl(program, post_action, node_count, action_count, source_list, target_list):
    env = SCons.Environment.Environment()
    expected_string = '${cd_action_prefix} ${program} ${required} ${options}'

    env.Append(BUILDERS={"AnsysAPDL": scons_extensions.ansys_apdl(program=program, post_action=post_action)})
    nodes = env.AnsysAPDL(target=target_list, source=source_list)
    check_action_string(nodes, post_action, node_count, action_count, expected_string,
                        post_action_prefix="${cd_action_prefix}")
    for node in nodes:
        assert node.env['program'] == program


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

    check_action_string(nodes, [], node_count, action_count, expected_string)
