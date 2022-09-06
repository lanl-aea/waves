import tempfile
import subprocess

import pytest

from waves._settings import _project_root_abspath

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
    command = ["python", "-m", "waves.parameter_study", "cartesian_product", '-h']
    output = subprocess.check_output(command, cwd=_project_root_abspath.parent)
