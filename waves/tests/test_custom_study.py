"""Test CustomStudy Class
"""

from unittest.mock import patch, call, mock_open
from contextlib import nullcontext as does_not_raise

from waves.parameter_generators import CustomStudy

import pytest
import numpy


class TestCustomStudy:
    """Class for testing CustomStudy parameter study generator class"""

    validate_input = {
        "good schema": (
            {'parameter_names': ['a', 'b'], 'parameter_samples': numpy.array([[1, 2.0], [3, 4.5]], dtype=object)},
            does_not_raise()
        ),
        "not a dict": (
            'not a dict',
            pytest.raises(TypeError)
        ),
        "bad schema no names": (
            {'parameter_samples': numpy.array([[1, 2.0], [3, 4.5]], dtype=object)},
            pytest.raises(KeyError)
        ),
        "bad schema no values": (
            {'parameter_names': ['a', 'b']},
            pytest.raises(KeyError)
        ),
        "bad schema shape": (
            {'parameter_names': ['a', 'b', 'c'], 'parameter_samples': numpy.array([[1, 2.0], [3, 4.5]], dtype=object)},
            pytest.raises(ValueError)
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
                TestValidate = CustomStudy(parameter_schema)
            finally:
                pass

    generate_io = {
        'one_parameter': ({'parameter_names': ['a'], 'parameter_samples': numpy.array([[1], [2.0]], dtype=object)},
                          numpy.array([[1], [2.0]], dtype=object)),
        'two_parameter': ({'parameter_names': ['a', 'b'], 'parameter_samples': numpy.array([[1, 2.0], [3, 4.5]], dtype=object)},
                          numpy.array(
                              [[1, 2.0],
                               [3, 4.5]], dtype=object))
    }

    @pytest.mark.unittest
    @pytest.mark.parametrize('parameter_schema, expected_array',
                                 generate_io.values(),
                             ids=generate_io.keys())
    def test_generate(self, parameter_schema, expected_array):
        TestGenerate = CustomStudy(parameter_schema)
        TestGenerate.generate()
        generate_array = TestGenerate.samples
        assert numpy.all(generate_array == expected_array)
        # Verify that the parameter set name creation method was called
        assert TestGenerate.parameter_set_names == [f"parameter_set{num}" for num in range(len(expected_array))]
        # Check that the parameter set names are correctly populated in the parameter study Xarray Dataset
        expected_set_names = [f"parameter_set{num}" for num in range(len(expected_array))]
        parameter_set_names = list(TestGenerate.parameter_study['parameter_sets'])
        assert numpy.all(parameter_set_names == expected_set_names)

    generate_io = {
        'one parameter yaml':
            ({'parameter_names': ['a'], 'parameter_samples': numpy.array([[1], [2]], dtype=object)},
             'out',
             None,
             'yaml',
             2,
             [call("a: 1\n"),
              call("a: 2\n")]),
        'two parameter yaml':
            ({'parameter_names': ['a', 'b'], 'parameter_samples': numpy.array([[1, 2.0], [3, 4.5]], dtype=object)},
             'out',
             None,
             'yaml',
             2,
             [call("a: 1\nb: 2.0\n"),
              call("a: 3\nb: 4.5\n")]),
        'one parameter one file yaml':
            ({'parameter_names': ['a'], 'parameter_samples': numpy.array([[1], [2]], dtype=object)},
             None,
             'parameter_study.yaml',
             'yaml',
             1,
             [call("parameter_set0:\n  a: 1\n" \
                   "parameter_set1:\n  a: 2\n")]),
        'two parameter one file yaml':
            ({'parameter_names': ['a', 'b'], 'parameter_samples': numpy.array([[1, 2.0], [3, 4.5]], dtype=object)},
             None,
             'parameter_study.yaml',
             'yaml',
             1,
             [call("parameter_set0:\n  a: 1\n  b: 2.0\n" \
                   "parameter_set1:\n  a: 3\n  b: 4.5\n")])
    }

    @pytest.mark.unittest
    @pytest.mark.parametrize('parameter_schema, output_file_template, output_file, output_type, file_count, expected_calls',
                                 generate_io.values(),
                             ids=generate_io.keys())
    def test_write_yaml(self, parameter_schema, output_file_template, output_file, output_type, file_count, expected_calls):
        with patch('waves.parameter_generators._ParameterGenerator._write_meta'), \
             patch('builtins.open', mock_open()) as mock_file, \
             patch('xarray.Dataset.to_netcdf') as xarray_to_netcdf, \
             patch('sys.stdout.write') as stdout_write, \
             patch('pathlib.Path.is_file', return_value=False):
            TestWriteYAML = CustomStudy(parameter_schema,
                                        output_file_template=output_file_template,
                                        output_file=output_file,
                                        output_file_type=output_type)
            TestWriteYAML.generate()
            TestWriteYAML.write()
            stdout_write.assert_not_called()
            xarray_to_netcdf.assert_not_called()
            assert mock_file.call_count == file_count
            mock_file().write.assert_has_calls(expected_calls, any_order=False)
