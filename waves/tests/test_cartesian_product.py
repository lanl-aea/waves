"""Test CartesianProduct Class
"""

import pathlib
import pytest

from waves.parameter_generators import CartesianProduct

class TestCartesianProduct:
    """Class for testing CartesianProduct parameter study generator class"""

    generate_io = {
        'one_parameter': ({'parameter_1': [1, 2]}, ['parameter_1: 1\n', 'parameter_1: 2\n']),
        'two_parameter': ({'parameter_1': [1, 2], 'parameter_2': ['a', 'b']},
                          ['parameter_1: 1\nparameter_2: a\n',
                           'parameter_1: 1\nparameter_2: b\n',
                           'parameter_1: 2\nparameter_2: a\n',
                           'parameter_1: 2\nparameter_2: b\n'])
    }

    @pytest.mark.unittest
    @pytest.mark.parametrize('parameter_schema, expected_text_list',
                                 generate_io.values(),
                             ids=generate_io.keys())
    def test_generate(self, parameter_schema, expected_text_list):
        TestGenerate = CartesianProduct(parameter_schema, None, False, False, False)
        parameter_set_file_paths = TestGenerate.generate()
        assert list(TestGenerate.parameter_study.values()) == expected_text_list
        assert parameter_set_file_paths == [pathlib.Path(f"parameter_set{num}") for num in range(len(expected_text_list))]
