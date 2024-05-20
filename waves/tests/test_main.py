"""Test command line utility and associated functions"""
import pathlib
from unittest.mock import patch, mock_open
from contextlib import nullcontext as does_not_raise

import pytest

from waves import _main
from waves import _settings


def test_main():
    with patch('sys.argv', ['waves.py', 'docs']), \
         patch("waves._docs.main") as mock_docs:
        _main.main()
        mock_docs.assert_called()

    target_string = 'dummy.target'
    with patch('sys.argv', ['waves.py', 'build', target_string]), \
         patch("waves._build.main") as mock_build:
        _main.main()
        mock_build.assert_called_once()
        assert mock_build.call_args[0][0] == [target_string]

    requested_paths = ['dummy.file1', 'dummy.file2']
    requested_paths_args = [pathlib.Path(path) for path in requested_paths]
    with patch('sys.argv', ['waves.py', 'fetch'] + requested_paths), \
         patch("waves._fetch.recursive_copy") as mock_recursive_copy:
        _main.main()
        mock_recursive_copy.assert_called_once()
        assert mock_recursive_copy.call_args[1]['requested_paths'] == requested_paths_args

    tutorial_number = 7
    with patch('sys.argv', ['waves.py', 'fetch', '--tutorial', str(tutorial_number)]), \
            patch("waves._fetch.recursive_copy") as mock_recursive_copy:
        _main.main()
        mock_recursive_copy.assert_called_once()
        assert mock_recursive_copy.call_args[1]['tutorial'] == tutorial_number


parameter_study_args = {  #               subcommand,         class_name,                   argument,         option,   argument_value
    'cartesian product':        ('cartesian_product', 'CartesianProduct',                       None,           None,             None),
    'custom study':             (     'custom_study',      'CustomStudy',                       None,           None,             None),
    'latin hypercube':          (  'latin_hypercube',   'LatinHypercube',                       None,           None,             None),
    'sobol sequence':           (   'sobol_sequence',    'SobolSequence',                       None,           None,             None),
    'output file template':     ('cartesian_product', 'CartesianProduct',     'output_file_template',           '-o', 'dummy_template'),
    'output file':              (     'custom_study',      'CustomStudy',              'output_file',           '-f', 'dummy_file.txt'),
    'output file type':         (  'latin_hypercube',   'LatinHypercube',         'output_file_type',           '-t',             'h5'),
    'set name template':        (   'sobol_sequence',    'SobolSequence',        'set_name_template',           '-s',        '@number'),
    'previous parameter study': ('cartesian_product', 'CartesianProduct', 'previous_parameter_study',           '-p', 'dummy_file.txt'),
    'overwrite':                (     'custom_study',      'CustomStudy',                'overwrite',  '--overwrite',             True),
    'dry run':                  (  'latin_hypercube',   'LatinHypercube',                  'dry_run',    '--dry-run',             True),
    'write meta':               (   'sobol_sequence',    'SobolSequence',               'write_meta', '--write-meta',             True)
}


@pytest.mark.parametrize('subcommand, class_name, argument, option, argument_value',
                         parameter_study_args.values(),
                         ids=list(parameter_study_args.keys()))
def test_parameter_study(subcommand, class_name, argument, option, argument_value):
    # Help/usage. Should not raise
    with patch('sys.argv', ['_main.py', subcommand, '-h']), \
         pytest.raises(SystemExit) as err:
        _main.main()
    assert err.value.code == 0

    # Run main code. No SystemExit expected.
    arg_list = ['_main.py', subcommand, 'dummy.file']
    if option:
        arg_list.append(option)
    if argument_value:
        # Don't pass boolean values
        if not isinstance(argument_value, bool):
            arg_list.append(argument_value)
    with patch('sys.argv', arg_list), \
         patch('builtins.open', mock_open()), patch('yaml.safe_load'), \
         patch(f'waves.parameter_generators.{class_name}') as mock_generator, \
         patch("pathlib.Path.is_file", return_value=True), \
         does_not_raise():
        _main.main()
        mock_generator.assert_called_once()
        if argument:
            assert mock_generator.call_args.kwargs[argument] == argument_value
