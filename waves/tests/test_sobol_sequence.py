"""Test Sobol Sequence Class
"""

from unittest.mock import patch
from contextlib import nullcontext as does_not_raise

import pytest
import numpy
import pkg_resources

from waves.parameter_generators import SobolSequence, ScipySampler
from waves._settings import _hash_coordinate_key, _set_coordinate_key


class TestSobolSequence:
    """Class for testing Sobol Sequence parameter study generator class"""

    generate_input = {
        "good schema 5x2": (
            {'num_simulations': 5,
             'parameter_1': {'distribution': 'uniform', 'loc': 0, 'scale': 10},
             'parameter_2': {'distribution': 'uniform', 'loc': 2, 'scale':  3}},
            {'scramble': False},
            numpy.array([[0.   , 2.   ],
                         [5.   , 3.5  ],
                         [7.5  , 2.75 ],
                         [2.5  , 4.25 ],
                         [3.75 , 3.125]]),
            numpy.array([[0.   , 0.   ],
                         [0.5  , 0.5  ],
                         [0.75 , 0.25 ],
                         [0.25 , 0.75 ],
                         [0.375, 0.375]]),
        ),
        "good schema 2x1": (
            {'num_simulations': 2,
             'parameter_1': {'distribution': 'uniform', 'loc': 0, 'scale': 10}},
            {'scramble': False},
            numpy.array([[0.], [5.0]]),
            numpy.array([[0.], [0.5]]),
        ),
        "good schema 1x2": (
            {'num_simulations': 1,
             'parameter_1': {'distribution': 'uniform', 'loc': 0, 'scale': 10},
             'parameter_2': {'distribution': 'uniform', 'loc': 2, 'scale':  3}},
            {'scramble': False},
            numpy.array([[0., 2.]]),
            numpy.array([[0., 0.]])
        )
    }

    @pytest.mark.unittest
    @pytest.mark.parametrize("parameter_schema, kwargs, expected_samples, expected_quantiles",
                             generate_input.values(),
                             ids=generate_input.keys())
    def test_generate(self, parameter_schema, kwargs, expected_samples, expected_quantiles):
        parameter_names = [key for key in parameter_schema.keys() if key != 'num_simulations']
        generator_classes = (SobolSequence(parameter_schema, **kwargs),
                             ScipySampler("Sobol", parameter_schema, **kwargs))
        for TestGenerate in generator_classes:
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
        'new sets': (
            {'num_simulations': 5,
             'parameter_1': {'distribution': 'uniform', 'loc': 0, 'scale': 10},
             'parameter_2': {'distribution': 'uniform', 'loc': 2, 'scale':  3}},
            {'num_simulations': 8,
             'parameter_1': {'distribution': 'uniform', 'loc': 0, 'scale': 10},
             'parameter_2': {'distribution': 'uniform', 'loc': 2, 'scale':  3}},
            {'scramble': False},
            # Ordered by md5 hash during Xarray merge operation. New tests must verify hash ordering.
            numpy.array([[5.   , 3.5  ],
                         [7.5  , 2.75 ],
                         [1.25 , 3.875],
                         [3.75 , 3.125],
                         [0.   , 2.   ],
                         [6.25 , 2.375],
                         [2.5  , 4.25 ],
                         [8.75 , 4.625]]),
            numpy.array([[0.5  , 0.5  ],
                         [0.75 , 0.25 ],
                         [0.125, 0.625],
                         [0.375, 0.375],
                         [0.   , 0.   ],
                         [0.625, 0.125],
                         [0.25 , 0.75 ],
                         [0.875, 0.875]])
        ),
        'unchanged sets': (
            {'num_simulations': 5,
             'parameter_1': {'distribution': 'uniform', 'loc': 0, 'scale': 10},
             'parameter_2': {'distribution': 'uniform', 'loc': 2, 'scale':  3}},
            {'num_simulations': 5,
             'parameter_1': {'distribution': 'uniform', 'loc': 0, 'scale': 10},
             'parameter_2': {'distribution': 'uniform', 'loc': 2, 'scale':  3}},
            {'scramble': False},
            # Ordered by md5 hash during Xarray merge operation. New tests must verify hash ordering.
            numpy.array([[5.   , 3.5  ],
                         [7.5  , 2.75 ],
                         [3.75 , 3.125],
                         [0.   , 2.   ],
                         [2.5  , 4.25 ]]),
            numpy.array([[0.5  , 0.5  ],
                         [0.75 , 0.25 ],
                         [0.375, 0.375],
                         [0.   , 0.   ],
                         [0.25 , 0.75 ]])
        )
    }

    @pytest.mark.unittest
    @pytest.mark.parametrize('first_schema, second_schema, kwargs, expected_samples, expected_quantiles',
                                 merge_test.values(),
                             ids=merge_test.keys())
    def test_merge(self, first_schema, second_schema, kwargs, expected_samples, expected_quantiles):
        # Sobol
        TestMerge1 = SobolSequence(first_schema, **kwargs)
        with patch('xarray.open_dataset', return_value=TestMerge1.parameter_study):
            TestMerge2 = SobolSequence(second_schema, previous_parameter_study='dummy_string', **kwargs)
        samples_array = TestMerge2._samples.astype(float)
        quantiles_array = TestMerge2._quantiles.astype(float)
        assert numpy.allclose(samples_array, expected_samples)
        assert numpy.allclose(quantiles_array, expected_quantiles)
        # Check for consistent hash-parameter set relationships
        for set_name, parameter_set in TestMerge1.parameter_study.groupby(_set_coordinate_key):
            assert parameter_set == TestMerge2.parameter_study.sel(parameter_sets=set_name)
        # Self-consistency checks
        assert list(TestMerge2._parameter_set_names.values()) == TestMerge2.parameter_study[_set_coordinate_key].values.tolist()
        assert TestMerge2._parameter_set_hashes == TestMerge2.parameter_study[_hash_coordinate_key].values.tolist()

        # ScipySampler
        TestMerge1 = ScipySampler("Sobol", first_schema, **kwargs)
        with patch('xarray.open_dataset', return_value=TestMerge1.parameter_study):
            TestMerge2 = ScipySampler("Sobol", second_schema, previous_parameter_study='dummy_string', **kwargs)
        samples_array = TestMerge2._samples.astype(float)
        quantiles_array = TestMerge2._quantiles.astype(float)
        assert numpy.allclose(samples_array, expected_samples)
        assert numpy.allclose(quantiles_array, expected_quantiles)
        # Check for consistent hash-parameter set relationships
        for set_name, parameter_set in TestMerge1.parameter_study.groupby(_set_coordinate_key):
            assert parameter_set == TestMerge2.parameter_study.sel(parameter_sets=set_name)
        # Self-consistency checks
        assert list(TestMerge2._parameter_set_names.values()) == TestMerge2.parameter_study[_set_coordinate_key].values.tolist()
        assert TestMerge2._parameter_set_hashes == TestMerge2.parameter_study[_hash_coordinate_key].values.tolist()
