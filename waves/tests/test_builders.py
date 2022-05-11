"""Test WAVES SCons builders and support functions 
"""

import pytest

from waves import builders

copy_substitute_input = {
    'strings': (['dummy'])
}


@pytest.mark.unittest
@pytest.mark.parametrize('source_list',
                         copy_substitute_input.values(),
                         ids=copy_substitute_input.keys())
def test__copy_substitute(source_list):
    builders.copy_substitute(source_list, {})
