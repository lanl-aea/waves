from unittest.mock import patch
import sys
import pathlib

import pytest

from waves import parameter_study

parameter_study_args = {
    'cartesian product': (
        'cartesian_product',
        {'parameter_1': [1, 2], 'parameter_2': ['a', 'b']}
    ),
    'custom study': (
        'custom_study',
        {'parameter_samples': [[1, 'a', 5.0], [2.0, 'b', 6]],
         'parameter_names': ['height', 'prefix', 'index']}
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
           'scale': 2}}
    ),
}


@pytest.mark.integrationtest
@pytest.mark.parametrize('subcommand, schema',
                         parameter_study_args.values(),
                         ids=list(parameter_study_args.keys()))
def test_parameter_study(subcommand, schema):
    with patch('sys.argv', ['parameter_study.py', subcommand, '-h']), \
         pytest.raises(SystemExit) as pytest_exit:
        sys.exit(parameter_study.main())
    assert pytest_exit.value.code == 0

    schema_file = 'dummy.file'
    with patch('sys.argv', ['parameter_study.py', subcommand, schema_file]), \
         patch('argparse.FileType'), patch('yaml.safe_load', return_value=schema), \
         pytest.raises(SystemExit) as pytest_exit:
        sys.exit(parameter_study.main())
    assert pytest_exit.value.code == 0
