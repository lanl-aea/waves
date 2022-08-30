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

    generate_input_interface = "parameter_schema, random_state, expected_samples, expected_quantiles, " \
                               "expected_scipy_kwds"
