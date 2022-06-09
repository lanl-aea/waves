"""Test WAVES SCons builders and support functions"""

import pathlib
import pytest
from contextlib import nullcontext as does_not_raise

import SCons.Node.FS

from waves import builders


fs = SCons.Node.FS.FS()
source_file = fs.File('dummy.py')
journal_emitter_input = {
    'empty targets': ([],
                      [source_file],
                      ['dummy.jnl', 'dummy.stdout', 'dummy.abaqus_v6.env']),
    'one target': (['dummy.cae'],
                   [source_file],
                   ['dummy.cae', 'dummy.jnl', 'dummy.stdout', 'dummy.abaqus_v6.env']),
    'subdirectory': (['set1/dummy.cae'],
                    [source_file],
                    ['set1/dummy.cae', 'set1/dummy.jnl', 'set1/dummy.stdout', 'set1/dummy.abaqus_v6.env'])
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
    'empty targets': ([],
                      [source_file],
                      ['dummy.stdout']),
    'one target': (['dummy.cub'],
                   [source_file],
                   ['dummy.cub', 'dummy.stdout']),
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
