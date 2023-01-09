"""Test SALibSampler Class
"""

from unittest.mock import patch
from contextlib import nullcontext as does_not_raise

import pytest
import numpy

from waves.parameter_generators import SALibSampler
from waves._settings import _hash_coordinate_key, _set_coordinate_key, _supported_salib_samplers


class TestSALibSampler:
    """Class for testing SALib Sampler parameter study generator class"""

    sampler_overrides = {
        "sobol: two parameter": (
            "sobol",
            {"N": 4,
             "problem": {
                 "num_vars": 2,
                 "names": ["parameter_1", "parameter_2"],
                 "bounds": [[-1, 1], [-2, 2]]
             }
            },
            {},
            {"calc_second_order": False}
        )
    }
    @pytest.mark.unittest
    @pytest.mark.parametrize('sampler_class, parameter_schema, original, expected',
                             sampler_overrides.values(),
                             ids=sampler_overrides.keys())
    def test_sampler_overrides(self, sampler_class, parameter_schema, original, expected):
        TestValidate = SALibSampler(sampler_class, parameter_schema)
        override_kwargs = TestValidate._sampler_overrides(original)
        assert override_kwargs == expected

    validate_input = {
        "sobol: good schema": (
            "sobol",
            {"N": 4,
             "problem": {
                 "num_vars": 3,
                 "names": ["parameter_1", "parameter_2", "parameter_3"],
                 "bounds": [[-1, 1], [-2, 2], [-3, 3]]
             }
            },
            does_not_raise()
        ),
        "latin: good schema": (
            "latin",
            {"N": 4,
             "problem": {
                 "num_vars": 3,
                 "names": ["parameter_1", "parameter_2", "parameter_3"],
                 "bounds": [[-1, 1], [-2, 2], [-3, 3]]
             }
            },
            does_not_raise()
        ),
        "sobol: one parameter": (
            "sobol",
            {"N": 4,
             "problem": {
                 "num_vars": 1,
                 "names": ["parameter_1",],
                 "bounds": [[-1, 1]]
             }
            },
            pytest.raises(ValueError)
        ),
        "morris: one parameter": (
            "morris",
            {"N": 4,
             "problem": {
                 "num_vars": 1,
                 "names": ["parameter_1",],
                 "bounds": [[-1, 1]]
             }
            },
            pytest.raises(ValueError)
        ),
        "missing N": (
            "latin",
            {"problem": {"num_vars": 4, "names": ["p1"], "bounds": [[-1, 1]]}},
            pytest.raises(AttributeError)
        ),
        "missing problem": (
            "latin",
            {"N": 4},
            pytest.raises(AttributeError)
        ),
        "missing names": (
            "latin",
            {"N": 4, "problem": {"num_vars": 4, "bounds": [[-1, 1]]}},
            pytest.raises(AttributeError)
        ),
        "schema not a dict": (
            "latin",
            "not a dict",
            pytest.raises(TypeError)
        ),
        "N not an int": (
            "latin",
            {"N": "not an int", "problem": {"num_vars": 4, "names": ["p1"], "bounds": [[-1, 1]]}},
            pytest.raises(TypeError)
        ),
        "problem not a dict": (
            "latin",
            {"N": 4, "problem": "not a dict"},
            pytest.raises(TypeError)
        ),
        "names not a list": (
            "latin",
            {"N": 4, "problem": {"num_vars": 4, "names": "not a list", "bounds": [[-1, 1]]}},
            pytest.raises(TypeError)
        ),
    }

    @pytest.mark.unittest
    @pytest.mark.parametrize('sampler_class, parameter_schema, outcome',
                             validate_input.values(),
                             ids=validate_input.keys())
    def test_validate(self, sampler_class, parameter_schema, outcome):
        with outcome:
            try:
                # Validate is called in __init__. Do not need to call explicitly.
                TestValidate = SALibSampler(sampler_class, parameter_schema)
            finally:
                pass

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
        ),
        "good schema 1x3": (
            {"N": 1,
             "problem": {"num_vars": 3,
                         "names": ["parameter_1", "parameter_2", "parameter_3"],
                         "bounds": [[-1, 1], [-2, 2], [-3, 3]]},
            },
            {"seed": 42},
        ),
        "good schema 65x3": (
            {"N": 65,
             "problem": {"num_vars": 3,
                         "names": ["parameter_1", "parameter_2", "parameter_3"],
                         "bounds": [[-1, 1], [-2, 2], [-3, 3]]},
            },
            {"seed": 42},
        )
    }

    def _expected_set_names(self, sampler, N, num_vars):
        number_of_simulations = N
        if sampler == "sobol" and num_vars <= 2:
            number_of_simulations = N * (num_vars + 2)
        elif sampler == "sobol":
            number_of_simulations = N * (2 * num_vars + 2)
        elif sampler == "fast_sampler":
            number_of_simulations = N * num_vars
        elif sampler == "finite_diff":
            number_of_simulations = N * (num_vars + 1)
        elif sampler == "morris":
            # Default interface settings
            number_of_simulations = int((num_vars + 1) * N)
        return [f"parameter_set{num}" for num in range(number_of_simulations)]

    def _big_enough(self, sampler, N, num_vars):
        if sampler == "sobol" and num_vars < 2:
            return False
        elif sampler == "fast_sampler" and N < 64:
            return False
        elif sampler == "morris" and num_vars < 2:
            return False
        return True

    @pytest.mark.unittest
    @pytest.mark.parametrize("parameter_schema, kwargs",
                             generate_input.values(),
                             ids=generate_input.keys())
    def test_generate(self, parameter_schema, kwargs):
        for sampler in _supported_salib_samplers:
            # TODO: find a better way to separate the sampler types and their test parameterization
            if not self._big_enough(sampler, parameter_schema["N"], parameter_schema["problem"]["num_vars"]):
                return
            # Unit tests
            TestGenerate = SALibSampler(sampler, parameter_schema, **kwargs)
            samples_array = TestGenerate._samples
            assert samples_array.shape[1] == parameter_schema["problem"]["num_vars"]
            # Verify that the parameter set name creation method was called
            # Morris produces inconsistent set counts depending on seed. Rely on the variable count shape check above.
            if not sampler == "morris":
                expected_set_names = self._expected_set_names(sampler, parameter_schema["N"], parameter_schema["problem"]["num_vars"])
                assert samples_array.shape[0] == len(expected_set_names)
                assert list(TestGenerate._parameter_set_names.values()) == expected_set_names
                # Check that the parameter set names are correctly populated in the parameter study Xarray Dataset
                parameter_set_names = list(TestGenerate.parameter_study[_set_coordinate_key])
                assert numpy.all(parameter_set_names == expected_set_names)

    merge_test = {
        "new sets, 5(8)x2": (
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
        "new sets, 5(8)x3": (
            {"N": 5,
             "problem": {"num_vars": 3,
                         "names": ["parameter_1", "parameter_2", "parameter_3"],
                         "bounds": [[-1, 1], [-2, 2], [-3, 3]]},
            },
            {"N": 8,
             "problem": {"num_vars": 3,
                         "names": ["parameter_1", "parameter_2", "parameter_3"],
                         "bounds": [[-1, 1], [-2, 2], [-3, 3]]},
            },
            {"seed": 42},
        ),
        "unchanged sets, 5x2": (
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
        ),
        "unchanged sets, 5x3": (
            {"N": 5,
             "problem": {"num_vars": 3,
                         "names": ["parameter_1", "parameter_2", "parameter_3"],
                         "bounds": [[-1, 1], [-2, 2], [-3, 3]]},
            },
            {"N": 5,
             "problem": {"num_vars": 3,
                         "names": ["parameter_1", "parameter_2", "parameter_3"],
                         "bounds": [[-1, 1], [-2, 2], [-3, 3]]},
            },
            {"seed": 42},
        ),
        "changed sets, 65(70)x3": (
            {"N": 65,
             "problem": {"num_vars": 3,
                         "names": ["parameter_1", "parameter_2", "parameter_3"],
                         "bounds": [[-1, 1], [-2, 2], [-3, 3]]},
            },
            {"N": 70,
             "problem": {"num_vars": 3,
                         "names": ["parameter_1", "parameter_2", "parameter_3"],
                         "bounds": [[-1, 1], [-2, 2], [-3, 3]]},
            },
            {"seed": 42},
        ),
        "unchanged sets, 65x3": (
            {"N": 65,
             "problem": {"num_vars": 3,
                         "names": ["parameter_1", "parameter_2", "parameter_3"],
                         "bounds": [[-1, 1], [-2, 2], [-3, 3]]},
            },
            {"N": 65,
             "problem": {"num_vars": 3,
                         "names": ["parameter_1", "parameter_2", "parameter_3"],
                         "bounds": [[-1, 1], [-2, 2], [-3, 3]]},
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
            # TODO: find a better way to separate the sampler types and their test parameterization
            if not self._big_enough(sampler, first_schema["N"], first_schema["problem"]["num_vars"]):
                return
            # Unit tests
            TestMerge1 = SALibSampler(sampler, first_schema, **kwargs)
            with patch('xarray.open_dataset', return_value=TestMerge1.parameter_study):
                TestMerge2 = SALibSampler(sampler, second_schema, previous_parameter_study='dummy_string', **kwargs)
            samples_array = TestMerge2._samples.astype(float)
            # Check for consistent hash-parameter set relationships
            for set_name, parameter_set in TestMerge1.parameter_study.groupby(_set_coordinate_key):
                assert parameter_set == TestMerge2.parameter_study.sel(parameter_sets=set_name)
            # Self-consistency checks
            assert list(TestMerge2._parameter_set_names.values()) == TestMerge2.parameter_study[_set_coordinate_key].values.tolist()
            assert TestMerge2._parameter_set_hashes == TestMerge2.parameter_study[_hash_coordinate_key].values.tolist()
