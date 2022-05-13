"""Test CartesianProduct Class
"""

import pytest

from waves.parameter_generators import CartesianProduct

class TestCartesianProduct:
    """Class for testing CartesianProduct parameter study generator class"""

    generate_io = {
        'one_parameter': ({'parameter_1': [1, 2]}, ['set(parameter_1 "1")\n', 'set(parameter_1 "2")\n']),
        'two_parameter': ({'parameter_1': [1, 2], 'parameter_2': ['a', 'b']},
                          ['set(parameter_1 "1")\nset(parameter_2 "a")\n',
                           'set(parameter_1 "1")\nset(parameter_2 "b")\n',
                           'set(parameter_1 "2")\nset(parameter_2 "a")\n',
                           'set(parameter_1 "2")\nset(parameter_2 "b")\n'])
    }

    @pytest.mark.unittest
    @pytest.mark.parametrize('parameter_schema, expected_text_list',
                                 generate_io.values(),
                             ids=generate_io.keys())
    def test_generate(self, parameter_schema, expected_text_list):
        TestGenerate = CartesianProduct(parameter_schema, None, False, False, False)
        TestGenerate.generate()
        assert list(TestGenerate.parameter_study.values()) == expected_text_list
