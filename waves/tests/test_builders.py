"""Test WAVES SCons builders and support functions"""

import pathlib
import pytest
from contextlib import nullcontext as does_not_raise
import unittest
from unittest.mock import patch, call

import SCons.Node.FS

from waves import builders



find_program_input = {
    'string': (
        'dummy',
        ['/installed/executable/dummy'],
        '/installed/executable/dummy'),
    'one path': (
        ['dummy'],
        ['/installed/executable/dummy'],
        '/installed/executable/dummy'),
    'first missing': (
        ['notfound', 'dummy'],
        [None, '/installed/executable/dummy'],
        '/installed/executable/dummy'),
    'two found': (
        ['dummy', 'dummy1'],
        ['/installed/executable/dummy', '/installed/executable/dummy1'],
        '/installed/executable/dummy'),
    'none found': (
        ['notfound', 'dummy'],
        [None, None],
        None)
}


@pytest.mark.unittest
@pytest.mark.parametrize('names, checkprog_side_effect, first_found_path',
                         find_program_input.values(),
                         ids=find_program_input.keys())
def test__find_program(names, checkprog_side_effect, first_found_path):
    env = SCons.Environment.Environment()
    mock_conf = unittest.mock.Mock()
    mock_conf.CheckProg = unittest.mock.Mock(side_effect=checkprog_side_effect)
    with patch('SCons.SConf.SConfBase', return_value=mock_conf):
        program = builders.find_program(names, env)
    assert program == first_found_path


fs = SCons.Node.FS.FS()
source_file = fs.File('dummy.py')
journal_emitter_input = {
    'one target': (['target.cae'],
                   [source_file],
                   ['target.cae', 'target.stdout', 'target.abaqus_v6.env']),
    'subdirectory': (['set1/dummy.cae'],
                    [source_file],
                    ['set1/dummy.cae', 'set1/dummy.stdout', 'set1/dummy.abaqus_v6.env'])
}


@pytest.mark.unittest
@pytest.mark.parametrize('target, source, expected',
                         journal_emitter_input.values(),
                         ids=journal_emitter_input.keys())
def test__abaqus_journal_emitter(target, source, expected):
    target, source = builders._abaqus_journal_emitter(target, source, None)
    assert target == expected


@pytest.mark.unittest
def test__abaqus_journal():
    env = SCons.Environment.Environment()
    env.Append(BUILDERS={'AbaqusJournal': builders.abaqus_journal()})
    # TODO: Figure out how to inspect a builder's action definition after creating the associated target.
    node = env.AbaqusJournal(target=['journal.cae'], source=['journal.py'], journal_options="")


fs = SCons.Node.FS.FS()
source_file = fs.File('root.inp')
solver_emitter_input = {
    'empty targets': ('job',
                      [],
                      [source_file],
                      ['job.stdout', 'job.abaqus_v6.env', 'job.odb', 'job.dat', 'job.msg', 'job.com', 'job.prt'],
                      does_not_raise()),
    'one targets': ('job',
                    ['job.sta'],
                    [source_file],
                    ['job.sta', 'job.stdout', 'job.abaqus_v6.env', 'job.odb', 'job.dat', 'job.msg', 'job.com', 'job.prt'],
                    does_not_raise()),
    'subdirectory': ('job',
                    ['set1/job.sta'],
                    [source_file],
                    ['set1/job.sta', 'set1/job.stdout', 'set1/job.abaqus_v6.env', 'set1/job.odb', 'set1/job.dat',
                     'set1/job.msg', 'set1/job.com', 'set1/job.prt'],
                    does_not_raise()),
    'missing job_name': (None,
                        [],
                        [source_file],
                        ['root.stdout', 'root.abaqus_v6.env', 'root.odb', 'root.dat', 'root.msg', 'root.com', 'root.prt'],
                        does_not_raise())
}


@pytest.mark.unittest
@pytest.mark.parametrize('job_name, target, source, expected, outcome',
                         solver_emitter_input.values(),
                         ids=solver_emitter_input.keys())
def test__abaqus_solver_emitter(job_name, target, source, expected, outcome):
    env = SCons.Environment.Environment()
    env['job_name'] = job_name
    with outcome:
        try:
            builders._abaqus_solver_emitter(target, source, env)
        finally:
            assert target == expected


@pytest.mark.unittest
def test__abaqus_solver():
    env = SCons.Environment.Environment()
    env.Append(BUILDERS={'AbaqusSolver': builders.abaqus_solver()})
    # TODO: Figure out how to inspect a builder's action definition after creating the associated target.
    node = env.AbaqusSolver(target=[], source=['root.inp'], job_name="job", abaqus_options="")


copy_substitute_input = {
    'strings': (['dummy', 'dummy2.in', 'root.inp.in', 'conf.py.in'],
                ['dummy', 'dummy2.in', 'dummy2', 'root.inp.in', 'root.inp', 'conf.py.in', 'conf.py']),
    'pathlib.Path()s': ([pathlib.Path('dummy'), pathlib.Path('dummy2.in')],
                        ['dummy', 'dummy2.in', 'dummy2']),
}


@pytest.mark.unittest
@pytest.mark.parametrize('source_list, expected_list',
                         copy_substitute_input.values(),
                         ids=copy_substitute_input.keys())
def test__copy_substitute(source_list, expected_list):
    target_list = builders.copy_substitute(source_list, {})
    target_files = [str(target) for target in target_list]
    assert target_files == expected_list


fs = SCons.Node.FS.FS()
source_file = fs.File('dummy.py')
python_emitter_input = {
    'one target': (['target.cub'],
                   [source_file],
                   ['target.cub', 'target.stdout']),
    'subdirectory': (['set1/dummy.cub'],
                    [source_file],
                    ['set1/dummy.cub', 'set1/dummy.stdout'])
}


@pytest.mark.unittest
@pytest.mark.parametrize('target, source, expected',
                         python_emitter_input.values(),
                         ids=python_emitter_input.keys())
def test__python_script_emitter(target, source, expected):
    target, source = builders._python_script_emitter(target, source, None)
    assert target == expected


@pytest.mark.unittest
def test__python_script():
    env = SCons.Environment.Environment()
    env.Append(BUILDERS={'PythonScript': builders.python_script()})
    # TODO: Figure out how to inspect a builder's action definition after creating the associated target.
    node = env.PythonScript(
        target=['python_script_journal.cub'], source=['python_script_journal.py'], journal_options="")


fs = SCons.Node.FS.FS()
source_file = fs.File('dummy.odb')
abaqus_extract_emitter_input = {
    'empty targets': ([],
                      [source_file],
                      ['dummy.h5', 'dummy_datasets.h5', 'dummy.csv']),
    'one target': (['new_name.h5'],
                   [source_file],
                   ['new_name.h5', 'new_name_datasets.h5', 'dummy.csv']),
    'bad extension': (['new_name.txt'],
                      [source_file],
                      ['dummy.h5', 'new_name.txt', 'dummy_datasets.h5', 'dummy.csv']),
    'subdirectory': (['set1/dummy.h5'],
                    [source_file],
                    ['set1/dummy.h5', 'set1/dummy_datasets.h5', 'set1/dummy.csv'])
}


@pytest.mark.unittest
@pytest.mark.parametrize('target, source, expected',
                         abaqus_extract_emitter_input.values(),
                         ids=abaqus_extract_emitter_input.keys())
def test__abaqus_extract_emitter(target, source, expected):
    target, source = builders._abaqus_extract_emitter(target, source, None)
    assert target == expected


@pytest.mark.unittest
def test__abaqus_extract():
    env = SCons.Environment.Environment()
    env.Append(BUILDERS={'AbaqusExtract': builders.abaqus_extract()})
    # TODO: Figure out how to inspect a builder's action definition after creating the associated target.
    node = env.AbaqusExtract(
        target=['abaqus_extract.h5'], source=['abaqus_extract.odb'], journal_options="")


fs = SCons.Node.FS.FS()
source_file = fs.File('/dummy.source')
target_file = fs.File('/dummy.target')
build_odb_extract_input = {
    'no kwargs': ([target_file], [source_file], {'abaqus_program': 'NA'},
                  [call(['/dummy.source'], '/dummy.target', output_type='h5', odb_report_args=None,
                       abaqus_command='NA', delete_report_file=False)])
}


@pytest.mark.parametrize('target, source, env, calls',
                         build_odb_extract_input.values(),
                         ids=build_odb_extract_input.keys())
@pytest.mark.unittest
def test_build_odb_extract(target, source, env, calls):
    with patch("waves.abaqus.odb_extract.odb_extract") as mock_odb_extract:
        builders._build_odb_extract(target, source, env)
    mock_odb_extract.assert_has_calls(calls)
