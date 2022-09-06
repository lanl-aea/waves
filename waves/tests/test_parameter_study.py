from unittest.mock import patch
import sys
import pathlib

import pytest

from waves import parameter_study

parameter_study_args = {
    'cartesian product': (
        'cartesian_product'
    ),
    'custom study': (
        'custom_study'
    ),
    'latin hypercube': (
        'latin_hypercube'
    ),
}


@pytest.mark.integrationtest
@pytest.mark.parametrize('subcommand',
                         parameter_study_args.values(),
                         ids=list(parameter_study_args.keys()))
def test_parameter_study(subcommand):
    with patch('sys.argv', ['parameter_study.py', subcommand, '-h']), \
         pytest.raises(SystemExit) as pytest_exit:
        sys.exit(parameter_study.main())
    assert pytest_exit.value.code == 0

    schema_file = pathlib.Path(f"tests/{subcommand}.yaml")
    with patch('sys.argv', ['parameter_study.py', subcommand, str(schema_file)]), \
         pytest.raises(SystemExit) as pytest_exit:
        sys.exit(parameter_study.main())
    assert pytest_exit.value.code == 0
