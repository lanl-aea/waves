"""Test LatinHypercube Class
"""

from unittest.mock import patch
from contextlib import nullcontext as does_not_raise

import pytest
import numpy
import scipy.stats

from waves.parameter_generators import LatinHypercube
from waves._settings import _hash_coordinate_key, _set_coordinate_key


class TestLatinHypercube:
    """Class for testing LatinHypercube parameter study generator class"""

    validate_input = {
        "good schema": (
            {'num_simulations': 1, 'parameter_1': {'distribution': 'norm', 'kwarg1': 1}},
            does_not_raise()
        ),
        "not a dict": (
            'not a dict',
            pytest.raises(TypeError)
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

    generate_input_interface = "parameter_schema, random_state, expected_samples, expected_quantiles, " \
                               "expected_scipy_kwds"
    generate_input = {
        "good schema 5x2": (
            {'num_simulations': 5,
            'parameter_1': {'distribution': 'norm', 'loc': 50, 'scale': 1},
            'parameter_2': {'distribution': 'norm', 'loc': -50, 'scale': 1}},
            42,
            numpy.array([[ 48.55981847, -48.43152778],
                         [ 49.82668961, -50.17332267],
                         [ 50.28353526, -50.87736996],
                         [ 49.6049386 , -49.25045625],
                         [ 51.40657316, -50.4684492 ]]),
            numpy.array([[0.07490802, 0.94161452],
                         [0.43120373, 0.4311989 ],
                         [0.61161672, 0.19014286],
                         [0.34639879, 0.77323523],
                         [0.920223  , 0.3197317 ]]),
            [{"loc":  50, "scale": 1},
             {"loc": -50, "scale": 1}]
        ),
        "good schema 2x1": (
            {'num_simulations': 2,
            'parameter_1': {'distribution': 'norm', 'loc': 50, 'scale': 1}},
            42,
            numpy.array([[51.96611184], [49.11199882]]),
            numpy.array([[0.97535715 ], [0.18727006 ]]),
            [{"loc":  50, "scale": 1}]
        ),
        "good schema 1x2": (
            {'num_simulations': 1,
            'parameter_1': {'distribution': 'norm', 'loc': 50, 'scale': 1},
            'parameter_2': {'distribution': 'norm', 'loc': -50, 'scale': 1}},
            42,
            numpy.array([[49.68014762, -48.34818067]]),
            numpy.array([[0.37454012 ,  0.95071431 ]]),
            [{"loc":  50, "scale": 1},
             {"loc": -50, "scale": 1}]
        )
    }

    @pytest.mark.unittest
    @pytest.mark.parametrize(generate_input_interface,
                             generate_input.values(),
                             ids=generate_input.keys())
    def test_generate(self, parameter_schema, random_state,
                      expected_samples, expected_quantiles, expected_scipy_kwds):
        parameter_names = [key for key in parameter_schema.keys() if key != 'num_simulations']
        TestGenerate = LatinHypercube(parameter_schema)
        TestGenerate.generate(lhs_kwargs={'random_state': random_state})
        samples_array = TestGenerate._samples
        quantiles_array = TestGenerate._quantiles
        assert numpy.allclose(samples_array, expected_samples)
        assert numpy.allclose(quantiles_array, expected_quantiles)
        # Verify that the parameter set name creation method was called
        assert list(TestGenerate._parameter_set_names.values()) == [f"parameter_set{num}" for num in range(parameter_schema['num_simulations'])]
        # Check that the parameter set names are correctly populated in the parameter study Xarray Dataset
        expected_set_names = [f"parameter_set{num}" for num in range(parameter_schema['num_simulations'])]
        parameter_set_names = list(TestGenerate.parameter_study[_set_coordinate_key])
        assert numpy.all(parameter_set_names == expected_set_names)

    @pytest.mark.unittest
    @pytest.mark.parametrize(generate_input_interface,
                             generate_input.values(),
                             ids=generate_input.keys())
    def test_generate_parameter_distributions(self, parameter_schema, random_state,
                                              expected_samples, expected_quantiles, expected_scipy_kwds):
        TestDistributions = LatinHypercube(parameter_schema)
        assert TestDistributions._parameter_names == list(TestDistributions.parameter_distributions.keys())
        for parameter_name, expected_kwds in zip(TestDistributions._parameter_names, expected_scipy_kwds):
            assert TestDistributions.parameter_distributions[parameter_name].kwds == expected_kwds
