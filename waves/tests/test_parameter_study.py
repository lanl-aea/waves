from unittest.mock import patch, call
import sys

import pytest

from waves import parameter_study

parameter_study_args = {
    'cartesian product': (
        'cartesian_product',
        'CartesianProduct'
    ),
    'custom study': (
        'custom_study',
        'CustomStudy'
    ),
    'latin hypercube': (
        'latin_hypercube',
        'LatinHypercube'
    ),
    'sobol sequence': (
        'sobol_sequence',
        'SobolSequence'
    ),
}


@pytest.mark.integrationtest
@pytest.mark.parametrize('subcommand, class_name',
                         parameter_study_args.values(),
                         ids=list(parameter_study_args.keys()))
def test_parameter_study(subcommand, class_name):
    # Should not raise
    with patch('sys.argv', ['parameter_study.py', subcommand, '-h']):
        try:
            parameter_study.main()
        except SystemExit as err:
            assert err.code == 0

    schema_file = 'dummy.file'
    with patch('sys.argv', ['parameter_study.py', subcommand, schema_file]), \
         patch('argparse.FileType'), patch('yaml.safe_load'), \
         patch(f'waves.parameter_generators.{class_name}') as mock_generator:
        try:
            parameter_study.main()
        except SystemExit:
            pass
        finally:
            mock_generator.assert_called_once()
            assert mock_generator.method_calls == [call.write()]
