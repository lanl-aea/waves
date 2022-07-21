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
        generate_array = TestGenerate.parameter_study.sel(parameter_data='values').to_array().values
        assert numpy.all(generate_array == expected_array)
        # Verify that the parameter set name creation method was called
        assert TestGenerate.parameter_set_names == [f"parameter_set{num}" for num in range(len(expected_array))]
        # Check that the parameter set names are correctly populated in the parameter study Xarray Dataset
        parameter_set_names = [key for key in TestGenerate.parameter_study.keys()]
        assert parameter_set_names == [f"parameter_set{num}" for num in range(len(expected_array))]
