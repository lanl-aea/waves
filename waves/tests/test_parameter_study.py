from unittest.mock import patch, call
import sys

import pytest

from waves import parameter_study

parameter_study_args = {
    'cartesian product': (
        'cartesian_product',
        {'parameter_1': [1, 2], 'parameter_2': ['a', 'b']},
        'CartesianProduct'
    ),
    'custom study': (
        'custom_study',
        {'parameter_samples': [[1, 'a', 5.0], [2.0, 'b', 6]],
         'parameter_names': ['height', 'prefix', 'index']},
        'CustomStudy'
    ),
    'latin hypercube': (
        'latin_hypercube',
        {'num_simulations': 5,
         'parameter_1': {
             'distribution': 'norm',
             'loc': 50,
             'scale': 1},
         'parameter_2': {
           'distribution': 'skewnorm',
           'a': 4,
           'loc': 30,
           'scale': 2}},
        'LatinHypercube'
    ),
}


@pytest.mark.integrationtest
@pytest.mark.parametrize('subcommand, schema, class_name',
                         parameter_study_args.values(),
                         ids=list(parameter_study_args.keys()))
def test_parameter_study(subcommand, schema, class_name):
    with patch('sys.argv', ['parameter_study.py', subcommand, '-h']), \
         pytest.raises(SystemExit) as pytest_exit:
        sys.exit(parameter_study.main())
    assert pytest_exit.value.code == 0

    schema_file = 'dummy.file'
    with patch('sys.argv', ['parameter_study.py', subcommand, schema_file]), \
         patch('argparse.FileType'), patch('yaml.safe_load', return_value=schema), \
         patch(f'waves.parameter_generators.{class_name}') as mock_generator, \
         pytest.raises(SystemExit) as pytest_exit:
        sys.exit(parameter_study.main())
        assert mock_generator.assert_called_once()
        assert mock_generator.method_calls == [call.generate(), call.write()]
    assert pytest_exit.value.code == 0
