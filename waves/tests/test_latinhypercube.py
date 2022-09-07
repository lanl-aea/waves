"""Test LatinHypercube Class
"""

from unittest.mock import patch
from contextlib import nullcontext as does_not_raise

import pytest
import numpy

from waves.parameter_generators import LatinHypercube
from waves._settings import _hash_coordinate_key, _set_coordinate_key


class TestLatinHypercube:
    """Class for testing LatinHypercube parameter study generator class"""

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
        TestGenerate.generate(kwargs={'random_state': random_state})
        samples_array = TestGenerate._samples
        quantiles_array = TestGenerate._quantiles
        assert numpy.allclose(samples_array, expected_samples)
        assert numpy.allclose(quantiles_array, expected_quantiles)
        # Verify that the parameter set name creation method was called
        expected_set_names = [f"parameter_set{num}" for num in range(parameter_schema['num_simulations'])]
        assert list(TestGenerate._parameter_set_names.values()) == expected_set_names
        # Check that the parameter set names are correctly populated in the parameter study Xarray Dataset
        expected_set_names = [f"parameter_set{num}" for num in range(parameter_schema['num_simulations'])]
        parameter_set_names = list(TestGenerate.parameter_study[_set_coordinate_key])
        assert numpy.all(parameter_set_names == expected_set_names)

    merge_test = {
        'increase simulations': (
            {'num_simulations': 1,
             'parameter_1': {'distribution': 'norm', 'loc': 50, 'scale': 1},
             'parameter_2': {'distribution': 'norm', 'loc': -50, 'scale': 1}},
            {'num_simulations': 2,
             'parameter_1': {'distribution': 'norm', 'loc': 50, 'scale': 1},
             'parameter_2': {'distribution': 'norm', 'loc': -50, 'scale': 1}},
            42,
            numpy.array([[ 49.68014762, -48.34818067],
                         [ 49.11199882, -49.16077225],
                         [ 51.10766607, -50.06180979]]),
            numpy.array([[0.37454012, 0.95071431],
                         [0.18727006, 0.79932924],
                         [0.86599697, 0.47535715]])
        )
    }

    @pytest.mark.unittest
    @pytest.mark.parametrize('first_schema, second_schema, random_state, expected_samples, expected_quantiles',
                                 merge_test.values(),
                             ids=merge_test.keys())
    def test_merge(self, first_schema, second_schema, random_state, expected_samples, expected_quantiles):
        TestMerge1 = LatinHypercube(first_schema)
        TestMerge1.generate(kwargs={'random_state': random_state})
        with patch('xarray.open_dataset', return_value=TestMerge1.parameter_study):
            TestMerge2 = LatinHypercube(second_schema, previous_parameter_study='dummy_string')
            TestMerge2.generate(kwargs={'random_state': random_state})
        samples = TestMerge2._samples.astype(float)
        quantiles = TestMerge2._quantiles.astype(float)
        assert numpy.allclose(samples, expected_samples)
        assert numpy.allclose(quantiles, expected_quantiles)
        # Check for consistent hash-parameter set relationships
        for set_name, parameter_set in TestMerge1.parameter_study.groupby(_set_coordinate_key):
            assert parameter_set == TestMerge2.parameter_study.sel(parameter_sets=set_name)
        # Self-consistency checks
        assert list(TestMerge2._parameter_set_names.values()) == TestMerge2.parameter_study[_set_coordinate_key].values.tolist()
        assert TestMerge2._parameter_set_hashes == TestMerge2.parameter_study[_hash_coordinate_key].values.tolist()
