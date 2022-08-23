"""Test ParameterGenerator Abstract Base Class
"""

from unittest.mock import patch, mock_open
import pathlib

from waves.parameter_generators import _ParameterGenerator

import pytest
import numpy
import xarray


class TestParameterGenerator:
    """Class for testing ABC ParmeterGenerator"""

    def test_output_file_conflict(self):
        with pytest.raises(RuntimeError):
            try:
                OutputFileConflict = NoQuantilesGenerator({}, output_file_template='out@number',
                                                          output_file='single_output_file')
            finally:
                pass

    def test_output_file_type(self):
        with pytest.raises(RuntimeError):
            try:
                OutputTypeError = NoQuantilesGenerator({}, output_file_type='notsupported')
            finally:
                pass

    templates = {      #schema, file_template, set_template,          expected
        'no template':   (    {},        None,         None, ['parameter_set0']),
        'file template': (    {},       'out',         None,           ['out0']),
        'file template': (    {},        None,        'out',           ['out0']),
        'file template': (    {},       'out', 'overridden',           ['out0'])
    }

    @pytest.mark.unittest
    @pytest.mark.parametrize('schema, file_template, set_template, expected',
                                 templates.values(),
                             ids=templates.keys())
    def test_set_names(self, schema, file_template, set_template, expected):
        """Check the generated parameter set names against template arguments

        :param str schema: placeholder string standing in for the schema read from an input file
        :param str file_template: user supplied string to be used as a template for output file names
        :param str set_template: user supplied string to be used as a template for parameter names
        :param list expected: list of expected parameter name strings
        """
        if not set_template:
            TemplateGenerator = NoQuantilesGenerator(schema, output_file_template=file_template)
        else:
            TemplateGenerator = NoQuantilesGenerator(schema, output_file_template=file_template,
                                                     set_name_template=set_template)
        TemplateGenerator.generate(1)
        assert list(TemplateGenerator.parameter_set_names.values()) == expected

    init_write_stdout = {# schema, template, overwrite, dryrun, debug,         is_file,  sets, stdout_calls
        'no-template-1': (     {},     None,     False,  False, False,          [False],    1,            1),
        'no-template-2': (     {},     None,      True,  False, False,          [False],    1,            1),
        'no-template-3': (     {},     None,     False,   True, False,   [False, False],    2,            1),
        'no-template-4': (     {},     None,     False,  False, False,   [ True,  True],    2,            1),
        'dryrun-1':      (     {},    'out',     False,   True, False,          [False],    1,            1),
        'dryrun-2':      (     {},    'out',      True,   True, False,          [False],    1,            1),
        'dryrun-3':      (     {},    'out',      True,   True, False,   [ True, False],    2,            2),
        'dryrun-4':      (     {},    'out',     False,   True, False,   [False,  True],    1,            1),
    }

    @pytest.mark.unittest
    @pytest.mark.parametrize('schema, template, overwrite, dryrun, debug, is_file, sets, stdout_calls',
                                 init_write_stdout.values(),
                             ids=init_write_stdout.keys())
    def test_write_to_stdout(self, schema, template, overwrite, dryrun, debug, is_file, sets, stdout_calls):
        """Check for conditions that should result in calls to stdout

        :param str schema: placeholder string standing in for the schema read from an input file
        :param str template: user supplied string to be used as a template for output file names
        :param bool overwrite: overwrite existing files
        :param bool dryrun: skip file write, but show file name and associated contents that would ahve been written
        :param bool debug: print cli debugging information and exit
        :param bool is_file: test specific argument mocks output for pathlib.Path().is_file()
        :param int sets: test specific argument for the number of sets to build for the test
        :param int stdout_calls: number of calls to stdout. Should only differ from set count when no template is
            provides. Should always be 1 when no template is provided.
        """
        WriteParameterGenerator = NoQuantilesGenerator(schema, output_file_template=template, output_file_type='yaml',
                                                       overwrite=overwrite, dryrun=dryrun, debug=debug)
        WriteParameterGenerator.generate(sets)
        with patch('waves.parameter_generators._ParameterGenerator._write_meta'), \
             patch('builtins.open', mock_open()) as mock_file, \
             patch('sys.stdout.write') as stdout_write, \
             patch('xarray.Dataset.to_netcdf') as xarray_to_netcdf, \
             patch('pathlib.Path.is_file', side_effect=is_file), \
             patch('pathlib.Path.mkdir'):
            WriteParameterGenerator.write()
            mock_file.assert_not_called()
            xarray_to_netcdf.assert_not_called()
            assert stdout_write.call_count == stdout_calls

    init_write_files = {# schema, template, overwrite, dryrun, debug,          is_file, sets, files
        'template-1':  (      {},    'out',     False,  False, False,          [False],    1,     1),
        'template-2':  (      {},    'out',     False,  False, False,   [False, False],    2,     2),
        'template-3':  (      {},    'out',     False,  False, False,   [ True,  True],    2,     0),
        'template-4':  (      {},    'out',     False,  False, False,   [ True, False],    2,     1),
        'overwrite-2': (      {},    'out',      True,  False, False,   [False, False],    2,     2),
        'overwrite-3': (      {},    'out',      True,  False, False,   [ True,  True],    2,     2),
        'overwrite-4': (      {},    'out',      True,  False, False,   [ True, False],    2,     2),
    }

    @pytest.mark.unittest
    @pytest.mark.parametrize('schema, template, overwrite, dryrun, debug, is_file, sets, files',
                                 init_write_files.values(),
                             ids=init_write_files.keys())
    def test_write_to_files(self, schema, template, overwrite, dryrun, debug, is_file, sets, files):
        """Check for conditions that should result in calls to builtins.open

        :param str schema: placeholder string standing in for the schema read from an input file
        :param str template: user supplied string to be used as a template for output file names
        :param bool overwrite: overwrite existing files
        :param bool dryrun: skip file write, but show file name and associated contents that would ahve been written
        :param bool debug: print cli debugging information and exit
        :param list is_file: test specific argument mocks changing output for pathlib.Path().is_file() repeat calls
        :param int sets: test specific argument for the number of sets to build for the test
        :param int files: integer number of files that should be written
        """
        WriteParameterGenerator = NoQuantilesGenerator(schema, output_file_template=template, output_file_type='yaml',
                                                       overwrite=overwrite, dryrun=dryrun, debug=debug)
        WriteParameterGenerator.generate(sets)
        with patch('waves.parameter_generators._ParameterGenerator._write_meta'), \
             patch('builtins.open', mock_open()) as mock_file, \
             patch('sys.stdout.write') as stdout_write, \
             patch('xarray.Dataset.to_netcdf') as xarray_to_netcdf, \
             patch('pathlib.Path.is_file', side_effect=is_file):
            WriteParameterGenerator.write()
            stdout_write.assert_not_called()
            xarray_to_netcdf.assert_not_called()
            assert mock_file.call_count == files

    @pytest.mark.unittest
    @pytest.mark.parametrize('schema, template, overwrite, dryrun, debug, is_file, sets, files',
                                 init_write_files.values(),
                             ids=init_write_files.keys())
    def test_write_to_netcdf(self, schema, template, overwrite, dryrun, debug, is_file, sets, files):
        """Check for conditions that should result in calls to xarray.Dataset.to_netcdf

        :param str schema: placeholder string standing in for the schema read from an input file
        :param str template: user supplied string to be used as a template for output file names
        :param bool overwrite: overwrite existing files
        :param bool dryrun: skip file write, but show file name and associated contents that would ahve been written
        :param bool debug: print cli debugging information and exit
        :param list is_file: test specific argument mocks changing output for pathlib.Path().is_file() repeat calls
        :param int sets: test specific argument for the number of sets to build for the test
        :param int files: integer number of files that should be written
        """
        WriteParameterGenerator = NoQuantilesGenerator(schema, output_file_template=template, output_file_type='h5',
                                                       overwrite=overwrite, dryrun=dryrun, debug=debug)
        WriteParameterGenerator.generate(sets)
        with patch('waves.parameter_generators._ParameterGenerator._write_meta'), \
             patch('builtins.open', mock_open()) as mock_file, \
             patch('sys.stdout.write') as stdout_write, \
             patch('xarray.Dataset.to_netcdf') as xarray_to_netcdf, \
             patch('pathlib.Path.is_file', side_effect=is_file), \
             patch('pathlib.Path.mkdir'):
            WriteParameterGenerator.write()
            mock_file.assert_not_called()
            stdout_write.assert_not_called()
            assert xarray_to_netcdf.call_count == files

    set_hashes = {
        'set1':
            (numpy.array([[1, 10.1, 'a']], dtype=object), ['524c99353118939a452503456d3100e8']),
        'set2':
            (numpy.array([[1, 10.1, 'a'], [2, 20.2, 'b'], [3, 30.3, 'c']], dtype=object),
             ['524c99353118939a452503456d3100e8',
              'b8797cbda6f68f71de15d10f6f901d5d',
              'cff4a038d9980830bc4ea32145b26cf7'])
    }

    @pytest.mark.unittest
    @pytest.mark.parametrize('samples, expected_hashes',
                                 set_hashes.values(),
                             ids=set_hashes.keys())
    def test_create_parameter_set_hashes(self, samples, expected_hashes):
        HashesParameterGenerator = NoQuantilesGenerator({})
        HashesParameterGenerator.samples = samples
        HashesParameterGenerator._create_parameter_set_hashes()
        assert HashesParameterGenerator.parameter_set_hashes == expected_hashes

    @pytest.mark.unittest
    def test_create_parameter_set_names(self):
        """Test the parmater set name generation"""
        SetNamesParameterGenerator = NoQuantilesGenerator({}, output_file_template='out')
        SetNamesParameterGenerator.samples = numpy.array([[1], [2]])
        SetNamesParameterGenerator._create_parameter_set_hashes()
        SetNamesParameterGenerator._create_parameter_set_names()
        assert list(SetNamesParameterGenerator.parameter_set_names.values()) == ['out0', 'out1']

    @pytest.mark.unittest
    def test_parameter_study_to_numpy(self):
        """Test the self-consistency of the parameter study dataset construction and deconstruction"""
        # Setup
        DataParameterGenerator = NoQuantilesGenerator({})
        DataParameterGenerator.parameter_names = ['ints', 'floats', 'strings']
        DataParameterGenerator.samples = numpy.array([[1, 10.1, 'a'], [2, 20.2, 'b']], dtype=object)
        DataParameterGenerator._create_parameter_set_hashes()
        DataParameterGenerator._create_parameter_set_names()
        DataParameterGenerator._create_parameter_study()
        # Test
        returned_samples = DataParameterGenerator._parameter_study_to_numpy('samples')
        assert numpy.all(returned_samples == DataParameterGenerator.samples)


class NoQuantilesGenerator(_ParameterGenerator):

    def _validate(self):
        self.parameter_names = ['parameter_1']

    def generate(self, sets):
        parameter_count = len(self.parameter_names)
        self.samples = numpy.ones((sets, parameter_count))
        for row in range(sets):
            self.samples[row, :] = self.samples[row, :]*row
        self._create_parameter_set_hashes()
        self._create_parameter_set_names()
        self._create_parameter_study()
