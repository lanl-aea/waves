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
    # Help/usage. Should not raise
    with patch('sys.argv', ['parameter_study.py', subcommand, '-h']):
        exit_code = None
        try:
            parameter_study.main()
        except SystemExit as err:
            exit_code = err.code
        finally:
            assert exit_code == 0

    # Run main code. No SystemExit expected.
    schema_file = 'dummy.file'
    with patch('sys.argv', ['parameter_study.py', subcommand, schema_file]), \
         patch('argparse.FileType'), patch('yaml.safe_load'), \
         patch(f'waves.parameter_generators.{class_name}') as mock_generator:
        exit_code = parameter_study.main()
        assert exit_code == 0
        mock_generator.assert_called_once()
