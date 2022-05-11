"""Test WAVES SCons builders and support functions 
"""

import pytest

from waves import builders


def test__copy_substitute():
    builders.copy_substitute(['dummy'], {})
