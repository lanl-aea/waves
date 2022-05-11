"""Test WAVES SCons builders and support functions"""

import pathlib
import pytest

from waves import builders


# TODO: Find a better way to instantiate or mock SCons objects for testing
class fakeSConsFile(str): 
    """Add a ''.path method to the string built-in

    Used here because instantiating an SCons.Node.FS.File object is hard and requires mucking about in the SCons
    internals. All we really need for the emitter unit tests is the target and source lists and the ''.path attribute of
    an SCons.Node.FS.File object.
    """
    def __init__(self, string): 
        super().__init__() 
        self.path = string


journal_emitter_input = {
    'empty targets': ([],
                      [fakeSConsFile('dummy.py')],
                      ['dummy.jnl', 'dummy.log']),
    'one target': (['dummy.cae'],
                   [fakeSConsFile('dummy.py')],
                   ['dummy.cae', 'dummy.jnl', 'dummy.log'])
}


@pytest.mark.unittest
@pytest.mark.parametrize('target, source, expected',
                         journal_emitter_input.values(),
                         ids=journal_emitter_input.keys())
def test__abaqus_journal_emitter(target, source, expected):
    target, source = builders._abaqus_journal_emitter(target, source, None)
    assert target == expected


copy_substitute_input = {
    'strings': (['dummy', 'dummy2.in'],
                ['dummy', 'dummy2.in', 'dummy2']),
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
