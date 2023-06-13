"""Test Sobol Sequence Class
"""

import pytest
import numpy

from waves.parameter_generators import SobolSequence, ScipySampler
from waves._settings import _set_coordinate_key
from common import consistent_hash_parameter_check, self_consistency_checks, merge_samplers


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
        test_merge1, test_merge2, samples_array = merge_samplers(SobolSequence, first_schema, second_schema, kwargs)
        quantiles_array = test_merge2._quantiles.astype(float)
        assert numpy.allclose(samples_array, expected_samples)
        assert numpy.allclose(quantiles_array, expected_quantiles)
        consistent_hash_parameter_check(test_merge1, test_merge2)
        self_consistency_checks(test_merge2)

        # ScipySampler
        test_merge1, test_merge2, samples_array = merge_samplers(ScipySampler, first_schema, second_schema, kwargs,
                                                                 sampler="Sobol")
        quantiles_array = test_merge2._quantiles.astype(float)
        assert numpy.allclose(samples_array, expected_samples)
        assert numpy.allclose(quantiles_array, expected_quantiles)
        consistent_hash_parameter_check(test_merge1, test_merge2)
        self_consistency_checks(test_merge2)
