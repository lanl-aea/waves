from unittest.mock import patch

import pytest

from waves._settings import _project_root_abspath
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
    with patch('sys.argv', return_value=[subcommand, '-h']):
        parameter_study.main()

    schema_file = _project_root_abspath / f"tests/{subcommand}.yaml"
    with patch('sys.argv', return_value=[subcommand, str(schema_file)]):
        parameter_study.main()
