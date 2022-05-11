"""Test WAVES SCons builders and support functions"""

import pathlib
import pytest

from waves import builders

copy_substitute_input = {
    'strings': (['dummy'], ['dummy']),
    'pathlib.Path()s': ([pathlib.Path('dummy')], ['dummy']),
}


@pytest.mark.unittest
@pytest.mark.parametrize('source_list, expected_list',
                         copy_substitute_input.values(),
                         ids=copy_substitute_input.keys())
def test__copy_substitute(source_list, expected_list):
    target_list = builders.copy_substitute(source_list, {})
    target_files = [str(target) for target in target_list]
    assert target_files == expected_list
