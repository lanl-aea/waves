"""Test LatinHypercube Class
"""

import pytest
from contextlib import nullcontext as does_not_raise

from waves.parameter_generators import LatinHypercube

class TestLatinHypercube:
    """Class for testing LatinHypercube parameter study generator class"""

    validate_input = {
        "good schema": (
            {'num_simulations': 2, 'parameter_1': {'distribution': 'norm', 'kwarg1': 1}},
            does_not_raise()
        ),
        "missing num_simulation": (
            {},
            pytest.raises(AttributeError)
        ),
        "num_simulation non-integer": (
            {'num_simulations': 'not_a_number'},
            pytest.raises(TypeError)
        )
    }

    @pytest.mark.unittest
    @pytest.mark.parametrize('parameter_schema, outcome',
                             validate_input.values(),
                             ids=validate_input.keys())
    def test__validate(self, parameter_schema, outcome):
        with outcome:
            try:
                # Validate is called in __init__. Do not need to call explicitly.
                TestValidate = LatinHypercube(parameter_schema, None, False, False, False)
            finally:
                pass
