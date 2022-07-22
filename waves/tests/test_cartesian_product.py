"""Test CartesianProduct Class
"""

import numpy
import pytest

from waves.parameter_generators import CartesianProduct

class TestCartesianProduct:
    """Class for testing CartesianProduct parameter study generator class"""

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
        TestGenerate = CartesianProduct(parameter_schema, None, False, False, False)
        TestGenerate.generate()
        generate_array = TestGenerate.parameter_study['values'].values
        assert numpy.all(generate_array == expected_array)
        # Verify that the parameter set name creation method was called
        assert TestGenerate.parameter_set_names == [f"parameter_set{num}" for num in range(len(expected_array))]
        # Check that the parameter set names are correctly populated in the parameter study Xarray Dataset
        expected_set_names = [f"parameter_set{num}" for num in range(len(expected_array))]
        parameter_set_names = list(TestGenerate.parameter_study['parameter_sets'])
        assert numpy.all(parameter_set_names == expected_set_names)
