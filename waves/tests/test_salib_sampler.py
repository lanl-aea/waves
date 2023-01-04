"""Test SALibSampler Class
"""

from unittest.mock import patch
from contextlib import nullcontext as does_not_raise
import inspect

import pytest
import numpy

from waves.parameter_generators import SALibSampler
from waves._settings import _hash_coordinate_key, _set_coordinate_key, _supported_salib_samplers


class TestSALibSampler:
    """Class for testing SALib Sampler parameter study generator class"""

    generate_input = {
        "good schema 5x2": (
            {"N": 5,
             "problem": {"num_vars": 2,
                         "names": ["parameter_1", "parameter_2"],
                         "bounds": [[-1, 1], [-2, 2]]},
            },
            {"seed": 42},
        ),
        "good schema 2x1": (
            {"N": 2,
             "problem": {"num_vars": 1,
                         "names": ["parameter_1"],
                         "bounds": [[-1, 1]]},
            },
            {"seed": 42},
        ),
        "good schema 1x2": (
            {"N": 1,
             "problem": {"num_vars": 2,
                         "names": ["parameter_1", "parameter_2"],
                         "bounds": [[-1, 1], [-2, 2]]}
            },
            {"seed": 42},
        )
    }

    def _expected_set_names(self, sampler, N, num_vars):
        number_of_simulations = N
        if sampler == "sobol":
            number_of_simulations = N * (2*num_vars + 2)
        return [f"parameter_set{num}" for num in range(number_of_simulations)]

    @pytest.mark.unittest
    @pytest.mark.parametrize("parameter_schema, kwargs",
                             generate_input.values(),
                             ids=generate_input.keys())
    def test_generate(self, parameter_schema, kwargs):
        for sampler in _supported_salib_samplers:
            TestGenerate = SALibSampler(sampler, parameter_schema)
            TestGenerate.generate(kwargs=kwargs)
            samples_array = TestGenerate._samples
            # Verify that the parameter set name creation method was called
            expected_set_names = self._expected_set_names(sampler, parameter_schema["N"], parameter_schema["problem"]["num_vars"])
            assert list(TestGenerate._parameter_set_names.values()) == expected_set_names
            # Check that the parameter set names are correctly populated in the parameter study Xarray Dataset
            parameter_set_names = list(TestGenerate.parameter_study[_set_coordinate_key])
            assert numpy.all(parameter_set_names == expected_set_names)

    merge_test = {
        "new sets": (
            {"N": 5,
             "problem": {"num_vars": 2,
                         "names": ["parameter_1", "parameter_2"],
                         "bounds": [[-1, 1], [-2, 2]]},
            },
            {"N": 8,
             "problem": {"num_vars": 2,
                         "names": ["parameter_1", "parameter_2"],
                         "bounds": [[-1, 1], [-2, 2]]},
            },
            {"seed": 42},
        ),
        "unchanged sets": (
            {"N": 5,
             "problem": {"num_vars": 2,
                         "names": ["parameter_1", "parameter_2"],
                         "bounds": [[-1, 1], [-2, 2]]},
            },
            {"N": 5,
             "problem": {"num_vars": 2,
                         "names": ["parameter_1", "parameter_2"],
                         "bounds": [[-1, 1], [-2, 2]]},
            },
            {"seed": 42},
        )
    }

    @pytest.mark.unittest
    @pytest.mark.parametrize('first_schema, second_schema, kwargs',
                                 merge_test.values(),
                             ids=merge_test.keys())
    def test_merge(self, first_schema, second_schema, kwargs):
        for sampler in _supported_salib_samplers:
            TestMerge1 = SALibSampler(sampler, first_schema)
            TestMerge1.generate(kwargs=kwargs)
            with patch('xarray.open_dataset', return_value=TestMerge1.parameter_study):
                TestMerge2 = SALibSampler(sampler, second_schema, previous_parameter_study='dummy_string')
                TestMerge2.generate(kwargs=kwargs)
            samples_array = TestMerge2._samples.astype(float)
            # Check for consistent hash-parameter set relationships
            for set_name, parameter_set in TestMerge1.parameter_study.groupby(_set_coordinate_key):
                assert parameter_set == TestMerge2.parameter_study.sel(parameter_sets=set_name)
            # Self-consistency checks
            assert list(TestMerge2._parameter_set_names.values()) == TestMerge2.parameter_study[_set_coordinate_key].values.tolist()
            assert TestMerge2._parameter_set_hashes == TestMerge2.parameter_study[_hash_coordinate_key].values.tolist()
