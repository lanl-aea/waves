"""Test CartesianProduct Class
"""

from contextlib import nullcontext as does_not_raise

from waves.parameter_generators import CartesianProduct

import pytest
import numpy

class TestCartesianProduct:
    """Class for testing CartesianProduct parameter study generator class"""

    validate_input = {
        "good schema": (
            {'parameter_1': [1], 'parameter_2': (2,) , 'parameter_3': set([3, 4])},
            does_not_raise()
        ),
        "bad schema int": (
            {'parameter_1': 1},
            pytest.raises(TypeError)
        ),
        "bad schema dict": (
            {'parameter_1': {'thing1': 1}},
            pytest.raises(TypeError)
        ),
        "bad schema str": (
            {'parameter_1': '1'},
            pytest.raises(TypeError)
        ),
    }

    @pytest.mark.unittest
    @pytest.mark.parametrize('parameter_schema, outcome',
                             validate_input.values(),
                             ids=validate_input.keys())
    def test_validate(self, parameter_schema, outcome):
        with outcome:
            try:
                # Validate is called in __init__. Do not need to call explicitly.
                TestValidate = CartesianProduct(parameter_schema)
            finally:
                pass

    generate_io = {
        'one_parameter': ({'parameter_1': [1, 2]},
                          numpy.array([[1], [2]])),
        'two_parameter': ({'parameter_1': [1, 2], 'parameter_2': ['a', 'b']},
                          numpy.array(
                              [["1", "a"],
                               ["1", "b"],
                               ["2", "a"],
                               ["2", "b"]]))
    }

    @pytest.mark.unittest
    @pytest.mark.parametrize('parameter_schema, expected_array',
                                 generate_io.values(),
                             ids=generate_io.keys())
    def test_generate(self, parameter_schema, expected_array):
        TestGenerate = CartesianProduct(parameter_schema)
        TestGenerate.generate()
        generate_array = TestGenerate.parameter_study['values'].values
        assert numpy.all(generate_array == expected_array)
        # Verify that the parameter set name creation method was called
        assert TestGenerate.parameter_set_names == [f"parameter_set{num}" for num in range(len(expected_array))]
        # Check that the parameter set names are correctly populated in the parameter study Xarray Dataset
        expected_set_names = [f"parameter_set{num}" for num in range(len(expected_array))]
        parameter_set_names = list(TestGenerate.parameter_study['parameter_sets'])
        assert numpy.all(parameter_set_names == expected_set_names)
