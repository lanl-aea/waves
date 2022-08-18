"""Test LatinHypercube Class
"""

from unittest.mock import patch
from contextlib import nullcontext as does_not_raise

from waves.parameter_generators import LatinHypercube

import pytest
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
        with patch("waves.parameter_generators.LatinHypercube._generate_parameter_distributions") as mock_distros, \
             outcome:
            try:
                # Validate is called in __init__. Do not need to call explicitly.
                TestValidate = LatinHypercube(parameter_schema)
                mock_distros.assert_called_once()
            finally:
                pass

    generate_input = {
        "good schema 5x2":
            {'num_simulations': 5,
             'parameter_1': {'distribution': 'norm', 'loc': 50, 'scale': 1},
             'parameter_2': {'distribution': 'norm', 'loc': -50, 'scale': 1}},
        "good schema 2x1":
            {'num_simulations': 2,
             'parameter_1': {'distribution': 'norm', 'loc': 50, 'scale': 1}},
        "good schema 1x2":
            {'num_simulations': 1,
             'parameter_1': {'distribution': 'norm', 'loc': 50, 'scale': 1},
             'parameter_2': {'distribution': 'norm', 'loc': -50, 'scale': 1}},
    }

    @pytest.mark.unittest
    @pytest.mark.parametrize('parameter_schema',
                             generate_input.values(),
                             ids=generate_input.keys())
    def test_generate(self, parameter_schema):
        parameter_names = [key for key in parameter_schema.keys() if key != 'num_simulations']
        TestGenerate = LatinHypercube(parameter_schema)
        TestGenerate.generate()
        samples_array = TestGenerate.samples
        quantiles_array = TestGenerate.quantiles
        assert samples_array.shape == (parameter_schema['num_simulations'], len(parameter_names))
        assert quantiles_array.shape == (parameter_schema['num_simulations'], len(parameter_names))
        # Verify that the parameter set name creation method was called
        assert TestGenerate.parameter_set_names == [f"parameter_set{num}" for num in range(parameter_schema['num_simulations'])]
        # Check that the parameter set names are correctly populated in the parameter study Xarray Dataset
        expected_set_names = [f"parameter_set{num}" for num in range(parameter_schema['num_simulations'])]
        parameter_set_names = list(TestGenerate.parameter_study['parameter_sets'])
        assert numpy.all(parameter_set_names == expected_set_names)

    @pytest.mark.unittest
    @pytest.mark.parametrize('parameter_schema',
                             generate_input.values(),
                             ids=generate_input.keys())
    def test_generate_parameter_distributions(self, parameter_schema):
        TestDistributions = LatinHypercube(parameter_schema)
        assert TestDistributions.parameter_names == list(TestDistributions.parameter_distributions.keys())
        # TODO: More rigorous scipy.stats object inspection to test object construction
        # https://re-git.lanl.gov/aea/python-projects/waves/-/issues/261
