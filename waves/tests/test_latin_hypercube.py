"""Test LatinHypercube Class
"""

from unittest.mock import patch
from contextlib import nullcontext as does_not_raise

import pytest
import numpy

from waves.parameter_generators import LatinHypercube, ScipySampler
from waves._settings import _hash_coordinate_key, _set_coordinate_key


class TestLatinHypercube:
    """Class for testing LatinHypercube parameter study generator class"""

    generate_input_interface = "parameter_schema, seed, expected_samples, expected_quantiles, " \
                               "expected_scipy_kwds"
    generate_input = {
        "good schema 5x2": (
            {'num_simulations': 5,
             'parameter_1': {'distribution': 'norm', 'loc': 50, 'scale': 1},
             'parameter_2': {'distribution': 'norm', 'loc': -50, 'scale': 1}},
            42,
            numpy.array([[ 51.01609863, -51.21478363],
                         [ 48.09331069, -49.58609982],
                         [ 50.20487353, -49.140834  ],
                         [ 50.37931242, -50.14390653],
                         [ 49.67971797, -50.49606915]]),
            numpy.array([[  0.84520879,   0.11222431],
                         [  0.02828042,   0.66052639],
                         [  0.58116453,   0.80487553],
                         [  0.64777206,   0.44278714],
                         [  0.37437727,   0.30992281]]),
            [{"loc":  50, "scale": 1},
             {"loc": -50, "scale": 1}]
        ),
        "good schema 2x1": (
            {'num_simulations': 2,
            'parameter_1': {'distribution': 'norm', 'loc': 50, 'scale': 1}},
            42,
            numpy.array([[50.2872041 ], [49.41882358]]),
            numpy.array([[ 0.61302198], [ 0.28056078]]),
            [{"loc":  50, "scale": 1}]
        ),
        "good schema 1x2": (
            {'num_simulations': 1,
             'parameter_1': {'distribution': 'norm', 'loc': 50, 'scale': 1},
             'parameter_2': {'distribution': 'norm', 'loc': -50, 'scale': 1}},
            42,
            numpy.array([[49.24806127, -49.84618661]]),
            numpy.array([[ 0.22604395,   0.56112156]]),
            [{"loc":  50, "scale": 1},
             {"loc": -50, "scale": 1}]
        )
    }

    @pytest.mark.unittest
    @pytest.mark.parametrize(generate_input_interface,
                             generate_input.values(),
                             ids=generate_input.keys())
    def test_generate(self, parameter_schema, seed,
                      expected_samples, expected_quantiles, expected_scipy_kwds):
        parameter_names = [key for key in parameter_schema.keys() if key != 'num_simulations']
        kwargs={'seed': seed}
        generator_classes = (LatinHypercube(parameter_schema, **kwargs),
                             ScipySampler("LatinHypercube", parameter_schema, **kwargs))
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
        'increase simulations': (
            {'num_simulations': 1,
             'parameter_1': {'distribution': 'norm', 'loc': 50, 'scale': 1},
             'parameter_2': {'distribution': 'norm', 'loc': -50, 'scale': 1}},
            {'num_simulations': 2,
             'parameter_1': {'distribution': 'norm', 'loc': 50, 'scale': 1},
             'parameter_2': {'distribution': 'norm', 'loc': -50, 'scale': 1}},
            42,
            numpy.array([[49.24806127, -49.84618661],
                         [50.17815924, -49.61112421],
                         [48.7893875 , -50.58117642]]),
            numpy.array([[ 0.22604395,   0.56112156],
                         [ 0.57070104,   0.65131599],
                         [ 0.11302198,   0.28056078]])
        )
    }

    @pytest.mark.unittest
    @pytest.mark.parametrize('first_schema, second_schema, seed, expected_samples, expected_quantiles',
                                 merge_test.values(),
                             ids=merge_test.keys())
    def test_merge(self, first_schema, second_schema, seed, expected_samples, expected_quantiles):
        # LatinHypercube
        kwargs={'seed': seed}
        TestMerge1 = LatinHypercube(first_schema, **kwargs)
        with patch('xarray.open_dataset', return_value=TestMerge1.parameter_study):
            TestMerge2 = LatinHypercube(second_schema, previous_parameter_study='dummy_string', **kwargs)
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

        # ScipySampler
        TestMerge1 = ScipySampler("LatinHypercube", first_schema, **kwargs)
        with patch('xarray.open_dataset', return_value=TestMerge1.parameter_study):
            TestMerge2 = ScipySampler("LatinHypercube", second_schema, previous_parameter_study='dummy_string', **kwargs)
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
