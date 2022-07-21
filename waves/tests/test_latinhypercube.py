"""Test LatinHypercube Class
"""

import pytest
from contextlib import nullcontext as does_not_raise

from waves.parameter_generators import LatinHypercube

class TestLatinHypercube:
    """Class for testing LatinHypercube parameter study generator class"""

    validate_input = {
        "good schema": (
            {'num_simulations': 1, 'parameter_1': {'distribution': 'norm', 'kwarg1': 1}},
            does_not_raise()
        ),
        "missing num_simulation": (
            {},
            pytest.raises(AttributeError)
        ),
        "num_simulation non-integer": (
            {'num_simulations': 'not_a_number'},
            pytest.raises(TypeError)
        ),
        "missing distribution": (
            {'num_simulations': 1, 'parameter_1': {}},
            pytest.raises(AttributeError)
        ),
        "distribution non-string": (
            {'num_simulations': 1, 'parameter_1': {'distribution': 1}},
            pytest.raises(TypeError)
        ),
        "distribution bad identifier": (
            {'num_simulations': 1, 'parameter_1': {'distribution': 'my norm'}},
            pytest.raises(TypeError)
        ),
        "kwarg bad identifier": (
            {'num_simulations': 1, 'parameter_1': {'distribution': 'norm', 'kwarg 1': 1}},
            pytest.raises(TypeError)
        )
    }

    @pytest.mark.unittest
    @pytest.mark.parametrize('parameter_schema, outcome',
                             validate_input.values(),
                             ids=validate_input.keys())
    def test__validate(self, parameter_schema, outcome):
        with outcome:
            try:
                # Validate is called in __init__. Do not need to call explicitly.
                TestValidate = LatinHypercube(parameter_schema, None, False, False, False)
            finally:
                pass

    generate_input = {
        "good schema":
            {'num_simulations': 4,
             'parameter_1': {'distribution': 'norm', 'loc': 50, 'scale': 1},
             'parameter_2': {'distribution': 'skewnorm', 'a': 4, 'loc': 30, 'scale': 2}}
    }

    @pytest.mark.unittest
    @pytest.mark.parametrize('parameter_schema',
                             generate_input.values(),
                             ids=generate_input.keys())
    def test_generate(self, parameter_schema):
        TestGenerate = LatinHypercube(parameter_schema)
        TestGenerate.generate()
        # Verify that the parameter set name creation method was called
        assert TestGenerate.parameter_set_names == [f"parameter_set{num}" for num in range(parameter_schema['num_simulations'])]
