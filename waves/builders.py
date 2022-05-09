#! /usr/bin/env python

import pathlib

import SCons.Builder

# TODO: (2) Find the abaqus wrapper in the installation directory (or re-write in Python here)
# https://re-git.lanl.gov/kbrindley/scons-simulation/-/issues/40
waves_source_dir = pathlib.Path(__file__).parent.resolve()
abaqus_wrapper = waves_source_dir / 'bin/abaqus_wrapper'


def _abaqus_journal_emitter(target, source, env):
    """Appends the abaqus_journal builder target list with the builder managed targets

    Appends ``source[0]``.jnl and ``source[0]``.log to the ``target`` list. The abaqus_journal Builder requires that the
    journal file to execute is the first source in the list.

    :return: target, source
    :rtype: tuple with two lists
    """
    journal_file = pathlib.Path(source[0].path).name
    journal_file = pathlib.Path(journal_file)
    target.append(f"{str(journal_file.with_suffix('.jnl'))}")
    target.append(f"{str(journal_file.with_suffix('.log'))}")
    return target, source


def abaqus_journal():
    """Abaqus journal file SCons builder

    This builder requires that the journal file to execute is the first source in the list. The builder returned by this
    function accepts all SCons Builder arguments and adds the ``journal_options`` and ``abaqus_options`` string
    arguments. The Builder emitter will append the builder managed targets automatically.

    .. code-block::
       :caption: Abaqus journal builder action
       :name: abaqus_journal_action

       abaqus cae -noGui ${SOURCE.abspath} ${abaqus_options} -- ${journal_options} > ${SOURCE.filebase}.log 2>&1

    .. code-block::
       :caption: SConstruct
       :name: abaqus_journal_example

       import waves
       env.Environment()
       env.Append(BUILDERS={'AbaqusJournal': waves.builders.abaqus_journal()})
       AbaqusJournal(target=my_journal.cae, source=my_journal.py, journal_options='')
    """
    abaqus_journal_builder = SCons.Builder.Builder(
        chdir=1,
        action='abaqus cae -noGui ${SOURCE.abspath} ${abaqus_options} -- ${journal_options} > ${SOURCE.filebase}.log 2>&1',
        emitter=_abaqus_journal_emitter)
    return abaqus_journal_builder


def _abaqus_solver_emitter(target, source, env):
    """Appends the abaqus_solver builder target list with the builder managed targets
    """
    if not 'job_name' in env:
        raise RuntimeError('Builder is missing required keyword argument "job_name".')
    builder_suffixes = ['log']
    abaqus_simulation_suffixes = ['odb', 'dat', 'msg', 'com', 'prt']
    suffixes = builder_suffixes + abaqus_simulation_suffixes
    for suffix in suffixes:
        target.append(f"{env['job_name']}.{suffix}")
    return target, source


def abaqus_solver():
    """Abaqus solver SCons builder

    This builder requires that the root input file is the first source in the list. The builder returned by this
    functions accepts all SCons Builder arguments and adds the required string argument ``job_name`` and optional string
    argument ``abaqus_options``.  The Builder emitter will append common Abaqus output files as targets automatically
    from the ``job_name``, e.g. ``job_name.odb``, ``job_name.dat``, ``job_name.sta``, etc.

    .. code-block::
       :caption: Abaqus journal builder action
       :name: abaqus_solver_action

       abaqus_wrapper ${job_name} abaqus -job ${job_name} -input ${SOURCE} ${abaqus_options}'

    .. code-block::
       :caption: SConstruct
       :name: abaqus_solver_example

       import waves
       env.Environment()
       env.Append(BUILDERS={'AbaqusSolver': waves.builders.abaqus_solver()})
       AbaqusSolver(target=[], source=input.inp, job_name='my_job', abaqus_options='-cpus 4')
    """
    abaqus_solver_builder = SCons.Builder.Builder(
        chdir=1,
        action=f'{abaqus_wrapper} ${{job_name}} abaqus -job ${{job_name}} -input ${{SOURCE.filebase}} ${{abaqus_options}}',
        emitter=_abaqus_solver_emitter)
    return abaqus_solver_builder
