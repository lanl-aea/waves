#! /usr/bin/env python

import pathlib

import SCons.Builder

def abaqus_journal_modify_targets(target, source, env):
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


# TODO: Turn this into a function or class that can take a docstring
abaqus_journal = SCons.Builder.Builder(
    chdir=1,
    action='abaqus cae -noGui ${SOURCE.abspath} -- ${journal_options} > ${SOURCE.filebase}.log 2>&1',
    emitter=abaqus_journal_modify_targets)
