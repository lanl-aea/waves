"""Test CartesianProduct Class
"""

from unittest.mock import patch, call, mock_open
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

    generate_io = {
        'one parameter yaml':
            ({"parameter_1": [1, 2]},
             'yaml',
             2,
             [call("parameter_1: 1\n"),
              call("parameter_1: 2\n")]),
        'two parameter yaml':
            ({"parameter_1": [1, 2], "parameter_2": ["a", "b"]},
             'yaml',
             4,
             [call("parameter_1: '1'\nparameter_2: 'a'\n"),
              call("parameter_1: '1'\nparameter_2: 'b'\n"),
              call("parameter_1: '2'\nparameter_2: 'a'\n"),
              call("parameter_1: '2'\nparameter_2: 'b'\n")])
    }

    @pytest.mark.unittest
    @pytest.mark.parametrize('parameter_schema, output_type, file_count, expected_calls',
                                 generate_io.values(),
                             ids=generate_io.keys())
    def test_write_yaml(self, parameter_schema, output_type, file_count, expected_calls):
        with patch('waves.parameter_generators._ParameterGenerator._write_meta'), \
             patch('builtins.open', mock_open()) as mock_file, \
             patch('xarray.Dataset.to_netcdf') as xarray_to_netcdf, \
             patch('sys.stdout.write') as stdout_write, \
             patch('pathlib.Path.is_file', return_value=False):
            TestWriteYAML = CartesianProduct(parameter_schema, output_file_template='out',
                                             output_file_type=output_type)
            TestWriteYAML.generate()
            TestWriteYAML.write()
            stdout_write.assert_not_called()
            xarray_to_netcdf.assert_not_called()
            assert mock_file.call_count == file_count
            mock_file().write.assert_has_calls(expected_calls, any_order=False)

    output_file_io = {
        'one parameter yaml':
            ({"parameter_1": [1, 2]},
             'yaml',
             1,
             [call("parameter_set0:\n  parameter_1: 1\n" \
                   "parameter_set1:\n  parameter_1: 2\n")]),
        'two parameter yaml':
            ({"parameter_1": [1, 2], "parameter_2": ["a", "b"]},
             'yaml',
             1,
             [call("parameter_set0:\n  parameter_1: '1'\n  parameter_2: 'a'\n" \
                   "parameter_set1:\n  parameter_1: '1'\n  parameter_2: 'b'\n" \
                   "parameter_set2:\n  parameter_1: '2'\n  parameter_2: 'a'\n" \
                   "parameter_set3:\n  parameter_1: '2'\n  parameter_2: 'b'\n")])
    }

    @pytest.mark.unittest
    @pytest.mark.parametrize('parameter_schema, output_type, file_count, expected_calls',
                                 output_file_io.values(),
                             ids=output_file_io.keys())
    def test_write_yaml_single_file(self, parameter_schema, output_type, file_count, expected_calls):
        with patch('waves.parameter_generators._ParameterGenerator._write_meta'), \
             patch('builtins.open', mock_open()) as mock_file, \
             patch('xarray.Dataset.to_netcdf') as xarray_to_netcdf, \
             patch('sys.stdout.write') as stdout_write, \
             patch('pathlib.Path.is_file', return_value=False):
            TestWriteYAML = CartesianProduct(parameter_schema, output_file='parameter_study.yaml',
                                             output_file_type=output_type)
            TestWriteYAML.generate()
            TestWriteYAML.write()
            stdout_write.assert_not_called()
            xarray_to_netcdf.assert_not_called()
            assert mock_file.call_count == file_count
            mock_file().write.assert_has_calls(expected_calls, any_order=False)
