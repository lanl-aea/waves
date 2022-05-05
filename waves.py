#! /usr/bin/env python

import pathlib

import SCons.Builder


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
       env.Append(BUILDERS={'AbaqusJournal': waves.abaqus_journal()})
       AbaqusJournal(target=my_journal.cae, source=my_journal.py, journal_options='')
    """
    abaqus_journal_builder = SCons.Builder.Builder(
        chdir=1,
        action='abaqus cae -noGui ${SOURCE.abspath} ${abaqus_options} -- ${journal_options} > ${SOURCE.filebase}.log 2>&1',
        emitter=_abaqus_journal_emitter)
    return abaqus_journal_builder
