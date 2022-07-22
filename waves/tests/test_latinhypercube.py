"""Test LatinHypercube Class
"""

import pytest
from contextlib import nullcontext as does_not_raise

from waves.parameter_generators import LatinHypercube

import numpy

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
        "good schema 5x2":
            {'num_simulations': 5,
             'parameter_1': {'distribution': 'norm', 'loc': 50, 'scale': 1},
             'parameter_2': {'distribution': 'norm', 'loc': -50, 'scale': 1}},
        "good schema 2x1":
            {'num_simulations': 2,
             'parameter_1': {'distribution': 'norm', 'loc': 50, 'scale': 1}}
    }

    @pytest.mark.unittest
    @pytest.mark.parametrize('parameter_schema',
                             generate_input.values(),
                             ids=generate_input.keys())
    def test_generate(self, parameter_schema):
        parameter_names = [key for key in parameter_schema.keys() if key != 'num_simulations']
        TestGenerate = LatinHypercube(parameter_schema)
        TestGenerate.generate()
        values_array = TestGenerate.parameter_study['values'].values
        quantiles_array = TestGenerate.parameter_study['quantiles'].values
        assert values_array.shape == (parameter_schema['num_simulations'], len(parameter_names))
        assert quantiles_array.shape == (parameter_schema['num_simulations'], len(parameter_names))
        # Verify that the parameter set name creation method was called
        assert TestGenerate.parameter_set_names == [f"parameter_set{num}" for num in range(parameter_schema['num_simulations'])]
        # Check that the parameter set names are correctly populated in the parameter study Xarray Dataset
        expected_set_names = [f"parameter_set{num}" for num in range(parameter_schema['num_simulations'])]
        parameter_set_names = list(TestGenerate.parameter_study['parameter_sets'])
        assert numpy.all(parameter_set_names == expected_set_names)
