"""Test WAVES SCons builders and support functions"""

import os
import pathlib
import pytest
from contextlib import nullcontext as does_not_raise
import unittest
from unittest.mock import patch, call
import platform

import SCons.Node.FS

from waves import builders
from waves._settings import _cd_action_prefix
from waves._settings import _abaqus_environment_extension
from waves._settings import _abaqus_datacheck_extensions
from waves._settings import _abaqus_explicit_extensions
from waves._settings import _abaqus_standard_extensions
from waves._settings import _abaqus_solver_common_suffixes
from waves._settings import _stdout_extension


fs = SCons.Node.FS.FS()

if platform.system().lower() == "windows":
    root_fs = "C:\\"
    testing_windows = True
else:
    root_fs = "/"
    testing_windows = False


def check_action_string(nodes, post_action, node_count, action_count, expected_string):
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
        expected_string = expected_string + f"\ncd ${{TARGET.dir.abspath}} && {action}"
    assert len(nodes) == node_count
    for node in nodes:
        node.get_executor()
        assert len(node.executor.action_list) == action_count
        assert str(node.executor.action_list[0]) == expected_string


def check_expected_targets(nodes, solver, stem):
    """Verify the expected action string against a builder's target nodes

    :param SCons.Node.NodeList nodes: Target node list returned by a builder
    :param str solver: emit file extensions based on the value of this variable (standard/explicit/datacheck).
    :param str stem: stem name of file

    """
    expected_suffixes = [_stdout_extension, _abaqus_environment_extension]
    if solver == 'standard':
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


@pytest.mark.unittest
@pytest.mark.parametrize("program, mock_exists, outcome",
                         prepend_env_input.values(),
                         ids=prepend_env_input.keys())
def test_append_env_path(program, mock_exists, outcome):
    env = SCons.Environment.Environment()
    with patch("pathlib.Path.exists", return_value=mock_exists), outcome:
        try:
            builders.append_env_path(program, env)
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


@pytest.mark.unittest
@pytest.mark.parametrize("substitution_dictionary, keyword_arguments, expected_dictionary",
                         substitution_syntax_input.values(),
                         ids=substitution_syntax_input.keys())
def test_substitution_syntax(substitution_dictionary, keyword_arguments, expected_dictionary):
    output_dictionary = builders.substitution_syntax(substitution_dictionary, **keyword_arguments)
    assert output_dictionary == expected_dictionary


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
        None)
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
        program = builders.find_program(names, env)
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
        program = builders.add_program(names, env)
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
        program = builders.add_cubit(names, env)
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


prepended_string = f"{_cd_action_prefix} "
post_action_list = {
    "list1": (["thing1"], [prepended_string + "thing1"]),
    "list2": (["thing1", "thing2"], [prepended_string + "thing1", prepended_string + "thing2"]),
    "tuple": (("thing1",), [prepended_string + "thing1"]),
    "str":  ("thing1", [prepended_string + "thing1"]),
}


@pytest.mark.unittest
@pytest.mark.parametrize("post_action, expected",
                         post_action_list.values(),
                         ids=post_action_list.keys())
def test_construct_post_action_list(post_action, expected):
    output = builders._construct_post_action_list(post_action)
    assert output == expected


source_file = fs.File("dummy.py")
journal_emitter_input = {
    "one target": (["target.cae"],
                   [source_file],
                   ["target.cae", "target.stdout", "target.abaqus_v6.env"]),
    "subdirectory": (["set1/dummy.cae"],
                    [source_file],
                    ["set1/dummy.cae", f"set1{os.sep}dummy.stdout", f"set1{os.sep}dummy.abaqus_v6.env"])
}


@pytest.mark.unittest
@pytest.mark.parametrize("target, source, expected",
                         journal_emitter_input.values(),
                         ids=journal_emitter_input.keys())
def test_abaqus_journal_emitter(target, source, expected):
    target, source = builders._abaqus_journal_emitter(target, source, None)
    assert target == expected


# TODO: Figure out how to cleanly reset the construction environment between parameter sets instead of passing a new
# target per set.
abaqus_journal_input = {
    "default behavior": ("abaqus", [], 3, 1, ["journal1.cae"]),
    "different command": ("dummy", [], 3, 1, ["journal2.cae"]),
    "post action": ("abaqus", ["post action"], 3, 1, ["journal3.cae"])
}


@pytest.mark.unittest
@pytest.mark.parametrize("abaqus_program, post_action, node_count, action_count, target_list",
                         abaqus_journal_input.values(),
                         ids=abaqus_journal_input.keys())
def test_abaqus_journal(abaqus_program, post_action, node_count, action_count, target_list):
    env = SCons.Environment.Environment()
    env.Append(BUILDERS={"AbaqusJournal": builders.abaqus_journal(abaqus_program, post_action)})
    nodes = env.AbaqusJournal(target=target_list, source=["journal.py"], journal_options="")
    expected_string = f'cd ${{TARGET.dir.abspath}} && {abaqus_program} -information environment > ' \
                       '${TARGET.filebase}.abaqus_v6.env\n' \
                      f'cd ${{TARGET.dir.abspath}} && {abaqus_program} cae -noGui ${{SOURCE.abspath}} ' \
                       '${abaqus_options} -- ${journal_options} > ${TARGET.filebase}.stdout 2>&1'
    check_action_string(nodes, post_action, node_count, action_count, expected_string)


source_file = fs.File("root.inp")
solver_emitter_input = {
    "empty targets": ("job",
                      [],
                      [source_file],
                      ["job.stdout", "job.abaqus_v6.env", "job.odb", "job.dat", "job.msg", "job.com", "job.prt"],
                      does_not_raise()),
    "one targets": ("job",
                    ["job.sta"],
                    [source_file],
                    ["job.sta", "job.stdout", "job.abaqus_v6.env", "job.odb", "job.dat", "job.msg", "job.com", "job.prt"],
                    does_not_raise()),
    "subdirectory": ("job",
                    ["set1/job.sta"],
                    [source_file],
                    ["set1/job.sta", f"set1{os.sep}job.stdout", f"set1{os.sep}job.abaqus_v6.env", f"set1{os.sep}job.odb", f"set1{os.sep}job.dat",
                     f"set1{os.sep}job.msg", f"set1{os.sep}job.com", f"set1{os.sep}job.prt"],
                    does_not_raise()),
    "missing job_name": (None,
                        [],
                        [source_file],
                        ["root.stdout", "root.abaqus_v6.env", "root.odb", "root.dat", "root.msg", "root.com", "root.prt"],
                        does_not_raise())
}


@pytest.mark.unittest
@pytest.mark.parametrize("job_name, target, source, expected, outcome",
                         solver_emitter_input.values(),
                         ids=solver_emitter_input.keys())
def test_abaqus_solver_emitter(job_name, target, source, expected, outcome):
    env = SCons.Environment.Environment()
    env["job_name"] = job_name
    with outcome:
        try:
            builders._abaqus_solver_emitter(target, source, env)
        finally:
            assert target == expected


# TODO: Figure out how to cleanly reset the construction environment between parameter sets instead of passing a new
# target per set.
abaqus_solver_input = {
    "default behavior": ("abaqus", [], 7, 1, ["input1.inp"], None),
    "different command": ("dummy", [], 7, 1, ["input2.inp"], None),
    "post action": ("abaqus", ["post action"], 7, 1, ["input3.inp"], None),
    "standard solver": ("abaqus", [], 16, 1, ["input4.inp"], "standard"),
    "explicit solver": ("abaqus", [], 15, 1, ["input5.inp"], "explicit"),
    "datacheck solver": ("abaqus", [], 12, 1, ["input6.inp"], "datacheck"),
}


@pytest.mark.unittest
@pytest.mark.parametrize("abaqus_program, post_action, node_count, action_count, source_list, solver",
                         abaqus_solver_input.values(),
                         ids=abaqus_solver_input.keys())
def test_abaqus_solver(abaqus_program, post_action, node_count, action_count, source_list, solver):
    env = SCons.Environment.Environment()
    env.Append(BUILDERS={"AbaqusSolver": builders.abaqus_solver(abaqus_program, post_action, solver)})
    nodes = env.AbaqusSolver(target=[], source=source_list, abaqus_options="")
    expected_string = f'cd ${{TARGET.dir.abspath}} && {abaqus_program} -information environment > ' \
                       '${job_name}.abaqus_v6.env\n' \
                      f'cd ${{TARGET.dir.abspath}} && {abaqus_program} -job ${{job_name}} -input ' \
                       '${SOURCE.filebase} ${abaqus_options} -interactive -ask_delete no ' \
                       '> ${job_name}.stdout 2>&1'
    check_action_string(nodes, post_action, node_count, action_count, expected_string)
    check_expected_targets(nodes, solver, pathlib.Path(source_list[0]).stem)


copy_substitute_input = {
    "strings": (["dummy", "dummy2.in", "root.inp.in", "conf.py.in"],
                ["dummy", "dummy2.in", "dummy2", "root.inp.in", "root.inp", "conf.py.in", "conf.py"]),
    "pathlib.Path()s": ([pathlib.Path("dummy"), pathlib.Path("dummy2.in")],
                        ["dummy", "dummy2.in", "dummy2"]),
}


@pytest.mark.unittest
@pytest.mark.parametrize("source_list, expected_list",
                         copy_substitute_input.values(),
                         ids=copy_substitute_input.keys())
def test_copy_substitute(source_list, expected_list):
    target_list = builders.copy_substitute(source_list, {})
    target_files = [str(target) for target in target_list]
    assert target_files == expected_list


build_subdirectory_input = {
    "no target": ([], pathlib.Path(".")),
    "no parent": (["target.ext"], pathlib.Path(".")),
    "one parent": (["set1/target.ext"], pathlib.Path("set1"))
}


@pytest.mark.unittest
@pytest.mark.parametrize("target, expected",
                         build_subdirectory_input.values(),
                         ids=build_subdirectory_input.keys())
def test_build_subdirectory(target, expected):
    assert builders._build_subdirectory(target) == expected


source_file = fs.File("dummy.py")
first_target_emitter_input = {
    "one target": (["target.cub"],
                   [source_file],
                   ["target.cub", "target.stdout"]),
    "subdirectory": (["set1/dummy.cub"],
                    [source_file],
                    ["set1/dummy.cub", f"set1{os.sep}dummy.stdout"])
}


@pytest.mark.unittest
@pytest.mark.parametrize("target, source, expected",
                         first_target_emitter_input.values(),
                         ids=first_target_emitter_input.keys())
def test_first_target_emitter(target, source, expected):
    target, source = builders._first_target_emitter(target, source, None)
    assert target == expected


# TODO: Figure out how to cleanly reset the construction environment between parameter sets instead of passing a new
# target per set.
python_script_input = {
    "default behavior": ([], 2, 1, ["python_script1.out"]),
    "different command": ([], 2, 1, ["python_script2.out"]),
    "post action": (["post action"], 2, 1, ["python_script3.out"])
}


@pytest.mark.unittest
@pytest.mark.parametrize("post_action, node_count, action_count, target_list",
                         python_script_input.values(),
                         ids=python_script_input.keys())
@pytest.mark.unittest
def test_python_script(post_action, node_count, action_count, target_list):
    env = SCons.Environment.Environment()
    env.Append(BUILDERS={"PythonScript": builders.python_script(post_action)})
    nodes = env.PythonScript(target=target_list, source=["python_script.py"], script_options="")
    expected_string = 'cd ${TARGET.dir.abspath} && python ${python_options} ${SOURCE.abspath} ${script_options} ' \
                      '> ${TARGET.filebase}.stdout 2>&1'
    check_action_string(nodes, post_action, node_count, action_count, expected_string)


source_file = fs.File("dummy.m")
matlab_emitter_input = {
    "one target": (["target.matlab"],
                   [source_file],
                   ["target.matlab", "target.stdout", "target.matlab.env"]),
    "subdirectory": (["set1/dummy.matlab"],
                    [source_file],
                    ["set1/dummy.matlab", f"set1{os.sep}dummy.stdout", f"set1{os.sep}dummy.matlab.env"])
}


@pytest.mark.unittest
@pytest.mark.parametrize("target, source, expected",
                         matlab_emitter_input.values(),
                         ids=matlab_emitter_input.keys())
def test_matlab_script_emitter(target, source, expected):
    target, source = builders._matlab_script_emitter(target, source, None)
    assert target == expected


# TODO: Figure out how to cleanly reset the construction environment between parameter sets instead of passing a new
# target per set.
matlab_script_input = {
    "default behavior": ("matlab", [], 3, 1, ["matlab_script1.out"]),
    "different command": ("/different/matlab", [], 3, 1, ["matlab_script2.out"]),
    "post action": ("matlab", ["post action"], 3, 1, ["matlab_script3.out"])
}


@pytest.mark.unittest
@pytest.mark.parametrize("matlab_program, post_action, node_count, action_count, target_list",
                         matlab_script_input.values(),
                         ids=matlab_script_input.keys())
@pytest.mark.unittest
def test_matlab_script(matlab_program, post_action, node_count, action_count, target_list):
    env = SCons.Environment.Environment()
    env.Append(BUILDERS={"MatlabScript": builders.matlab_script(matlab_program, post_action, symlink=False)})
    nodes = env.MatlabScript(target=target_list, source=["matlab_script.py"], script_options="")
    expected_string = 'Copy("${TARGET.dir.abspath}", "${SOURCE.abspath}")\n' \
                      f'cd ${{TARGET.dir.abspath}} && {matlab_program} ${{matlab_options}} -batch "[fList, pList] = ' \
                          'matlab.codetools.requiredFilesAndProducts(\'${SOURCE.file}\'); display(fList); ' \
                          'display(struct2table(pList, \'AsArray\', true)); exit;" > ${TARGET.filebase}.matlab.env ' \
                          '2>&1\n' \
                      f'cd ${{TARGET.dir.abspath}} && {matlab_program} ${{matlab_options}} -batch ' \
                          '"${SOURCE.filebase}(${script_options})\" > ${TARGET.filebase}.stdout 2>&1'
    check_action_string(nodes, post_action, node_count, action_count, expected_string)


@pytest.mark.unittest
def test_conda_environment():
    env = SCons.Environment.Environment()
    env.Append(BUILDERS={"CondaEnvironment": builders.conda_environment()})
    nodes = env.CondaEnvironment(
        target=["environment.yaml"], source=[], conda_env_export_options="")
    expected_string = 'cd ${TARGET.dir.abspath} && conda env export ${conda_env_export_options} --file ${TARGET.file}'
    check_action_string(nodes, [], 1, 1, expected_string)


source_file = fs.File("dummy.odb")
abaqus_extract_emitter_input = {
    "empty targets": (
        [],
        [source_file],
        ["dummy.h5", "dummy_datasets.h5", "dummy.csv", "dummy.h5.stdout"],
        {}
    ),
    "one target": (
        ["new_name.h5"],
        [source_file],
        ["new_name.h5", "new_name_datasets.h5", "new_name.csv", "new_name.h5.stdout"],
        {}
    ),
    "bad extension": (
        ["new_name.txt"],
        [source_file],
        ["dummy.h5", "new_name.txt", "dummy_datasets.h5", "dummy.csv", "dummy.h5.stdout"],
        {}
    ),
    "subdirectory": (
        ["set1/dummy.h5"],
        [source_file],
        ["set1/dummy.h5", f"set1{os.sep}dummy_datasets.h5", f"set1{os.sep}dummy.csv", f"set1{os.sep}dummy.h5.stdout"],
        {}
    ),
    "subdirectory new name": (
        ["set1/new_name.h5"],
        [source_file],
        ["set1/new_name.h5", f"set1{os.sep}new_name_datasets.h5", f"set1{os.sep}new_name.csv", f"set1{os.sep}new_name.h5.stdout"],
        {}
    ),
    "one target delete report": (
        ["new_name.h5"],
        [source_file],
        ["new_name.h5", "new_name_datasets.h5", "new_name.h5.stdout"],
        {"delete_report_file": True}
    ),
    "subdirectory delete report": (
        ["set1/dummy.h5"],
        [source_file],
        ["set1/dummy.h5", f"set1{os.sep}dummy_datasets.h5", f"set1{os.sep}dummy.h5.stdout"],
        {"delete_report_file": True}
    ),
}


@pytest.mark.unittest
@pytest.mark.parametrize("target, source, expected, env",
                         abaqus_extract_emitter_input.values(),
                         ids=abaqus_extract_emitter_input.keys())
def test_abaqus_extract_emitter(target, source, expected, env):
    target, source = builders._abaqus_extract_emitter(target, source, env)
    assert target == expected


@pytest.mark.unittest
def test_abaqus_extract():
    env = SCons.Environment.Environment()
    env.Append(BUILDERS={"AbaqusExtract": builders.abaqus_extract()})
    nodes = env.AbaqusExtract(
        target=["abaqus_extract.h5"], source=["abaqus_extract.odb"], journal_options="")
    expected_string = 'cd ${TARGET.dir.abspath} && rm ${TARGET.filebase}.csv ${TARGET.filebase}.h5 ' \
                      '${TARGET.filebase}_datasets.h5 > ${TARGET.file}.stdout 2>&1 || true' \
                      '\n_build_odb_extract(target, source, env)'
    check_action_string(nodes, [], 4, 1, expected_string)


source_file = fs.File("/dummy.source")
target_file = fs.File("/dummy.target")
build_odb_extract_input = {
    "no kwargs": ([target_file], [source_file], {"abaqus_program": "NA"},
                  [call([f"{root_fs}dummy.source"], f"{root_fs}dummy.target", output_type="h5", odb_report_args=None,
                       abaqus_command="NA", delete_report_file=False)]),
    "all kwargs": ([target_file], [source_file],
                   {"abaqus_program": "NA", "output_type": "different", "odb_report_args": "notnone",
                    "delete_report_file": True},
                   [call([f"{root_fs}dummy.source"], f"{root_fs}dummy.target", output_type="different", odb_report_args="notnone",
                        abaqus_command="NA", delete_report_file=True)])
}


@pytest.mark.parametrize("target, source, env, calls",
                         build_odb_extract_input.values(),
                         ids=build_odb_extract_input.keys())
@pytest.mark.unittest
def test_build_odb_extract(target, source, env, calls):
    with patch("waves.abaqus.odb_extract.odb_extract") as mock_odb_extract:
        builders._build_odb_extract(target, source, env)
    mock_odb_extract.assert_has_calls(calls)


# TODO: Figure out how to cleanly reset the construction environment between parameter sets instead of passing a new
# target per set.
sbatch_input = {
    "default behavior": ("sbatch", [], 2, 1, ["target1.out"]),
    "different command": ("dummy", [], 2, 1, ["target2.out"]),
    "post action": ("sbatch", ["post action"], 2, 1, ["target3.out"])
}


@pytest.mark.unittest
@pytest.mark.parametrize("sbatch_program, post_action, node_count, action_count, target_list",
                         sbatch_input.values(),
                         ids=sbatch_input.keys())
@pytest.mark.unittest
def test_sbatch(sbatch_program, post_action, node_count, action_count, target_list):
    env = SCons.Environment.Environment()
    env.Append(BUILDERS={"SlurmSbatch": builders.sbatch(sbatch_program, post_action)})
    nodes = env.SlurmSbatch(target=target_list, source=["source.in"], slurm_options="",
                            slurm_job="echo $SOURCE > $TARGET")
    expected_string = f'cd ${{TARGET.dir.abspath}} && {sbatch_program} --wait ${{slurm_options}} ' \
                       '--wrap "${slurm_job}" > ${TARGET.filebase}.stdout 2>&1'
    check_action_string(nodes, post_action, node_count, action_count, expected_string)
