"""Test WAVES SCons builders and support functions"""

import pathlib
import pytest
from contextlib import nullcontext as does_not_raise
import unittest
from unittest.mock import patch, call

import SCons.Node.FS

from waves import builders


fs = SCons.Node.FS.FS()

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


prepended_string = f"cd ${{TARGET.dir.abspath}} && "
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
                    ["set1/dummy.cae", "set1/dummy.stdout", "set1/dummy.abaqus_v6.env"])
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
@pytest.mark.unittest
def test_abaqus_journal(abaqus_program, post_action, node_count, action_count, target_list):
    env = SCons.Environment.Environment()
    env.Append(BUILDERS={"AbaqusJournal": builders.abaqus_journal(abaqus_program, post_action)})
    nodes = env.AbaqusJournal(target=target_list, source=["journal.py"], journal_options="")
    expected_string = f'cd ${{TARGET.dir.abspath}} && {abaqus_program} -information environment > ' \
                       '${TARGET.filebase}.abaqus_v6.env\n' \
                      f'cd ${{TARGET.dir.abspath}} && {abaqus_program} cae -noGui ${{SOURCE.abspath}} ' \
                       '${abaqus_options} -- ${journal_options} > ${TARGET.filebase}.stdout 2>&1'
    for action in post_action:
        expected_string = expected_string + f"\ncd ${{TARGET.dir.abspath}} && {action}"
    assert len(nodes) == node_count
    for node in nodes:
        node.get_executor()
        assert len(node.executor.action_list) == action_count
        assert str(node.executor.action_list[0]) == expected_string


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
                    ["set1/job.sta", "set1/job.stdout", "set1/job.abaqus_v6.env", "set1/job.odb", "set1/job.dat",
                     "set1/job.msg", "set1/job.com", "set1/job.prt"],
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


@pytest.mark.unittest
def test_abaqus_solver():
    env = SCons.Environment.Environment()
    env.Append(BUILDERS={"AbaqusSolver": builders.abaqus_solver()})
    # TODO: Figure out how to inspect a builder"s action definition after creating the associated target.
    node = env.AbaqusSolver(target=[], source=["root.inp"], job_name="job", abaqus_options="")


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


source_file = fs.File("dummy.py")
python_emitter_input = {
    "one target": (["target.cub"],
                   [source_file],
                   ["target.cub", "target.stdout"]),
    "subdirectory": (["set1/dummy.cub"],
                    [source_file],
                    ["set1/dummy.cub", "set1/dummy.stdout"])
}


@pytest.mark.unittest
@pytest.mark.parametrize("target, source, expected",
                         python_emitter_input.values(),
                         ids=python_emitter_input.keys())
def test_python_script_emitter(target, source, expected):
    target, source = builders._python_script_emitter(target, source, None)
    assert target == expected


@pytest.mark.unittest
def test_python_script():
    env = SCons.Environment.Environment()
    env.Append(BUILDERS={"PythonScript": builders.python_script()})
    # TODO: Figure out how to inspect a builder"s action definition after creating the associated target.
    node = env.PythonScript(
        target=["python_script_journal.cub"], source=["python_script_journal.py"], journal_options="")


@pytest.mark.unittest
def test_conda_environment():
    env = SCons.Environment.Environment()
    env.Append(BUILDERS={"CondaEnvironment": builders.conda_environment()})
    # TODO: Figure out how to inspect a builder"s action definition after creating the associated target.
    node = env.CondaEnvironment(
        target=["environment.yaml"], source=[], conda_env_export_options="")


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
        ["set1/dummy.h5", "set1/dummy_datasets.h5", "set1/dummy.csv", "set1/dummy.h5.stdout"],
        {}
    ),
    "subdirectory new name": (
        ["set1/new_name.h5"],
        [source_file],
        ["set1/new_name.h5", "set1/new_name_datasets.h5", "set1/new_name.csv", "set1/new_name.h5.stdout"],
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
        ["set1/dummy.h5", "set1/dummy_datasets.h5", "set1/dummy.h5.stdout"],
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
    # TODO: Figure out how to inspect a builder"s action definition after creating the associated target.
    node = env.AbaqusExtract(
        target=["abaqus_extract.h5"], source=["abaqus_extract.odb"], journal_options="")


source_file = fs.File("/dummy.source")
target_file = fs.File("/dummy.target")
build_odb_extract_input = {
    "no kwargs": ([target_file], [source_file], {"abaqus_program": "NA"},
                  [call(["/dummy.source"], "/dummy.target", output_type="h5", odb_report_args=None,
                       abaqus_command="NA", delete_report_file=False)]),
    "all kwargs": ([target_file], [source_file],
                   {"abaqus_program": "NA", "output_type": "different", "odb_report_args": "notnone",
                    "delete_report_file": True},
                   [call(["/dummy.source"], "/dummy.target", output_type="different", odb_report_args="notnone",
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


source_file = fs.File("dummy.ext")
sbatch_emitter_input = {
    "one target": (["target.out"],
                   [source_file],
                   ["target.out", "target.stdout"]),
    "subdirectory": (["set1/target.out"],
                    [source_file],
                    ["set1/target.out", "set1/target.stdout"])
}


@pytest.mark.unittest
@pytest.mark.parametrize("target, source, expected",
                         sbatch_emitter_input.values(),
                         ids=sbatch_emitter_input.keys())
def test_sbatch_emitter(target, source, expected):
    target, source = builders._sbatch_emitter(target, source, None)
    assert target == expected


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
    for action in post_action:
        expected_string = expected_string + f"\ncd ${{TARGET.dir.abspath}} && {action}"
    assert len(nodes) == node_count
    for node in nodes:
        node.get_executor()
        assert len(node.executor.action_list) == action_count
        assert str(node.executor.action_list[0]) == expected_string
