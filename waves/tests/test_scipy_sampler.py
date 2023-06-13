"""Test ScipySampler Class
"""

import pytest
import numpy

from waves.parameter_generators import ScipySampler
from waves._settings import _set_coordinate_key, _supported_scipy_samplers
from common import consistent_hash_parameter_check, self_consistency_checks, merge_samplers


class TestScipySampler:
    """Class for testing Scipy Sequence parameter study generator class"""

    generate_input = {
        "good schema 5x2": (
            {'num_simulations': 5,
             'parameter_1': {'distribution': 'uniform', 'loc': 0, 'scale': 10},
             'parameter_2': {'distribution': 'uniform', 'loc': 2, 'scale':  3}},
            {'seed': 42},
        ),
        "good schema 2x1": (
            {'num_simulations': 2,
             'parameter_1': {'distribution': 'uniform', 'loc': 0, 'scale': 10}},
            {'seed': 42},
        ),
        "good schema 1x2": (
            {'num_simulations': 1,
             'parameter_1': {'distribution': 'uniform', 'loc': 0, 'scale': 10},
             'parameter_2': {'distribution': 'uniform', 'loc': 2, 'scale':  3}},
            {'seed': 42},
        )
    }

    @pytest.mark.unittest
    @pytest.mark.parametrize("parameter_schema, kwargs",
                             generate_input.values(),
                             ids=generate_input.keys())
    def test_generate(self, parameter_schema, kwargs):
        parameter_names = [key for key in parameter_schema.keys() if key != 'num_simulations']
        for sampler in _supported_scipy_samplers:
            TestGenerate = ScipySampler(sampler, parameter_schema, **kwargs)
            samples_array = TestGenerate._samples
            quantiles_array = TestGenerate._quantiles
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
            {'seed': 42},
        ),
        'unchanged sets': (
            {'num_simulations': 5,
             'parameter_1': {'distribution': 'uniform', 'loc': 0, 'scale': 10},
             'parameter_2': {'distribution': 'uniform', 'loc': 2, 'scale':  3}},
            {'num_simulations': 5,
             'parameter_1': {'distribution': 'uniform', 'loc': 0, 'scale': 10},
             'parameter_2': {'distribution': 'uniform', 'loc': 2, 'scale':  3}},
            {'seed': 42},
        )
    }

    @pytest.mark.unittest
    @pytest.mark.parametrize('first_schema, second_schema, kwargs',
                                 merge_test.values(),
                             ids=merge_test.keys())
    def test_merge(self, first_schema, second_schema, kwargs):
        for sampler in _supported_scipy_samplers:
            original_study, merged_study = merge_samplers(ScipySampler, first_schema, second_schema, kwargs, sampler)[:2]
            merged_study._quantiles.astype(float)
            consistent_hash_parameter_check(original_study, merged_study)
            self_consistency_checks(merged_study)
