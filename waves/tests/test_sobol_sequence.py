"""Test Sobol Sequence Class
"""

from unittest.mock import patch
from contextlib import nullcontext as does_not_raise

import pytest
import numpy
import scipy.stats

from waves.parameter_generators import SobolSequence 
from waves._settings import _hash_coordinate_key, _set_coordinate_key


class TestSobolSequence:
    """Class for testing Sobol Sequence parameter study generator class"""

    validate_input = {
        "good schema": (
            {'num_simulations': 1, 'parameter_1': [0., 1.]},
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
        "not an iterable": (
            {'num_simulations': 1, 'parameter_1': 0.},
            pytest.raises(TypeError)
        ),
        "too short": (
            {'num_simulations': 1, 'parameter_1': [0.]},
            pytest.raises(ValueError)
        ),
        "too long": (
            {'num_simulations': 1, 'parameter_1': [0., 1., 3.]},
            pytest.raises(ValueError)
        ),
        "strings": (
            {'num_simulations': 1, 'parameter_1': ['a', 'b']},
            pytest.raises(TypeError)
        ),
    }

    @pytest.mark.unittest
    @pytest.mark.parametrize('parameter_schema, outcome',
                             validate_input.values(),
                             ids=validate_input.keys())
    def test__validate(self, parameter_schema, outcome):
        with outcome:
            try:
                # Validate is called in __init__. Do not need to call explicitly.
                TestValidate = SobolSequence(parameter_schema)
            finally:
                pass

    generate_input_interface = "parameter_schema, expected_samples, expected_quantiles"

    generate_input = {
        "good schema 5x2": (
            {'num_simulations': 5,
             'parameter_1': [0., 10.],
             'parameter_2': [2.,  5.]},
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
             'parameter_1': [0., 10.]},
            numpy.array([[0.], [5.0]]),
            numpy.array([[0.], [0.5]]),
        ),
        "good schema 1x2": (
            {'num_simulations': 1,
             'parameter_1': [0., 10.],
             'parameter_2': [2.,  5.]},
            numpy.array([[0., 2.]]),
            numpy.array([[0., 0.]])
        )
    }

    @pytest.mark.unittest
    @pytest.mark.parametrize(generate_input_interface,
                             generate_input.values(),
                             ids=generate_input.keys())
    def test_generate(self, parameter_schema, expected_samples, expected_quantiles):
        parameter_names = [key for key in parameter_schema.keys() if key != 'num_simulations']
        TestGenerate = SobolSequence(parameter_schema)
        TestGenerate.generate()
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
