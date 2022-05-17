"""Test ParameterGenerator Abstract Base Class
"""

import pytest
from unittest.mock import patch, mock_open
import pathlib

from waves.parameter_generators import ParameterGenerator


class TestParameterGenerator:
    """Class for testing ABC ParmeterGenerator"""

    init_write_stdout = {# schema, template, overwrite, dryrun, debug,         is_file, sets
        'no-template-1': (     {},     None,     False,  False, False,          [False],    1),
        'no-template-2': (     {},     None,      True,  False, False,          [False],    1),
        'no-template-3': (     {},     None,     False,   True, False,   [False, False],    2),
        'no-template-4': (     {},     None,     False,  False, False,   [ True,  True],    2),
        'dryrun-1':      (     {},    'out',     False,   True, False,          [False],    1),
        'dryrun-2':      (     {},    'out',      True,   True, False,          [False],    1),
        'dryrun-3':      (     {},    'out',      True,   True, False,   [ True, False],    2),
        'dryrun-4':      (     {},    'out',     False,   True, False,   [False,  True],    1),
    }

    @pytest.mark.unittest
    @pytest.mark.parametrize('schema, template, overwrite, dryrun, debug, is_file, sets',
                                 init_write_stdout.values(),
                             ids=init_write_stdout.keys())
    def test_write_to_stdout(self, schema, template, overwrite, dryrun, debug, is_file, sets):
        """Check for conditions that should result in calls to stdout

        :param str schema: placeholder string standing in for the schema read from an input file
        :param str template: user supplied string to be used as a template for output file names
        :param bool overwrite: overwrite existing files
        :param bool dryrun: skip file write, but show file name and associated contents that would ahve been written
        :param bool debug: print cli debugging information and exit
        :param bool is_file: test specific argument mocks output for pathlib.Path().is_file()
        :param int sets: test specific argument for the number of sets to build for the test
        """
        WriteParameterGenerator = FakeParameterGenerator(schema, template, overwrite, dryrun, debug)
        WriteParameterGenerator.parameter_study = {pathlib.Path(f"{num}"): '\n' for num in range(sets)}
        with patch('waves.parameter_generators.ParameterGenerator._write_meta'), \
             patch('builtins.open', mock_open(read_data='schema')) as mock_file, \
             patch('sys.stdout.write') as stdout_write, \
             patch('pathlib.Path.is_file', side_effect=is_file):
            WriteParameterGenerator.write()
            mock_file.assert_not_called()
            assert stdout_write.call_count == sets

    init_write_files = {# schema, template, overwrite, dryrun, debug,          is_file, sets, files
        'template-1':  (      {},    'out',     False,  False, False,          [False],    1,     1),
        'template-2':  (      {},    'out',     False,  False, False,   [False, False],    2,     2),
        'template-3':  (      {},    'out',     False,  False, False,   [ True,  True],    2,     0),
        'template-4':  (      {},    'out',     False,  False, False,   [ True, False],    2,     1),
        'overwrite-2': (      {},    'out',      True,  False, False,   [False, False],    2,     2),
        'overwrite-3': (      {},    'out',      True,  False, False,   [ True,  True],    2,     2),
        'overwrite-4': (      {},    'out',      True,  False, False,   [ True, False],    2,     2),
    }

    @pytest.mark.parametrize('schema, template, overwrite, dryrun, debug, is_file, sets, files',
                                 init_write_files.values(),
                             ids=init_write_files.keys())
    @pytest.mark.unittest
    def test_write_to_files(self, schema, template, overwrite, dryrun, debug, is_file, sets, files):
        """Check for conditions that should result in calls to stdout

        :param str schema: placeholder string standing in for the schema read from an input file
        :param str template: user supplied string to be used as a template for output file names
        :param bool overwrite: overwrite existing files
        :param bool dryrun: skip file write, but show file name and associated contents that would ahve been written
        :param bool debug: print cli debugging information and exit
        :param list is_file: test specific argument mocks changing output for pathlib.Path().is_file() repeat calls
        :param int sets: test specific argument for the number of sets to build for the test
        """
        WriteParameterGenerator = FakeParameterGenerator(schema, template, overwrite, dryrun, debug)
        WriteParameterGenerator.parameter_study = {pathlib.Path(f"{num}"): '\n' for num in range(sets)}
        with patch('waves.parameter_generators.ParameterGenerator._write_meta'), \
             patch('builtins.open', mock_open(read_data='schema')) as mock_file, \
             patch('sys.stdout.write') as stdout_write, \
             patch('pathlib.Path.is_file', side_effect=is_file):
            WriteParameterGenerator.write()
            stdout_write.assert_not_called()
            assert mock_file.call_count == files


class FakeParameterGenerator(ParameterGenerator):

    def validate(self):
        pass

    def generate():
        pass
