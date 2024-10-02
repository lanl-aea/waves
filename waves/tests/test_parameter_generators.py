"""Test ParameterGenerator Abstract Base Class
"""
from unittest.mock import patch, mock_open
from contextlib import nullcontext as does_not_raise

import pytest
import numpy
import xarray

from waves.parameter_generators import ParameterGenerator, _ScipyGenerator, LatinHypercube, SobolSequence
from waves.exceptions import ChoicesError, MutuallyExclusiveError, SchemaValidationError


class TestParameterGenerator:
    """Class for testing ABC ParameterGenerator"""

    def test_output_file_conflict(self):
        with pytest.raises(MutuallyExclusiveError):
            try:
                OutputFileConflict = NoQuantilesGenerator({}, output_file_template='out@number',
                                                          output_file='single_output_file')
            finally:
                pass

    def test_output_file_type(self):
        with pytest.raises(ChoicesError):
            try:
                OutputTypeError = NoQuantilesGenerator({}, output_file_type='notsupported')
            finally:
                pass

    def test_missing_previous_parameter_study_file(self):
        with patch("pathlib.Path.is_file", return_value=False), pytest.raises(RuntimeError):
            try:
                MissingPreviousStudy = NoQuantilesGenerator({}, previous_parameter_study="doesnotexist.h5")
            finally:
                pass

    def test_scons_write(self):
        sconsWrite = NoQuantilesGenerator({})
        with patch("waves.parameter_generators.ParameterGenerator.write") as mock_write:
            sconsWrite.scons_write([], [], {})
        mock_write.assert_called_once()

    templates = {      #schema, file_template, set_template,          expected
        'no template':   (    {},        None,         None, ['parameter_set0']),
        'file template': (    {},       'out',         None,           ['out0']),
        'file template': (    {},        None,        'out',           ['out0']),
        'file template': (    {},       'out', 'overridden',           ['out0'])
    }

    @pytest.mark.parametrize("length", range(1, 20, 5))
    def test_parameter_study_to_dict(self, length):
        kwargs = {"sets": length}
        sconsIterator = NoQuantilesGenerator({}, **kwargs)
        set_samples = sconsIterator.parameter_study_to_dict()
        assert set_samples == {f"parameter_set{index}": {"parameter_1": float(index)} for index in range(length)}

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
        kwargs = {"sets": 1}
        if not set_template:
            TemplateGenerator = NoQuantilesGenerator(schema, output_file_template=file_template, **kwargs)
        else:
            TemplateGenerator = NoQuantilesGenerator(schema, output_file_template=file_template,
                                                     set_name_template=set_template, **kwargs)
        assert list(TemplateGenerator._parameter_set_names.values()) == expected

    @pytest.mark.parametrize('schema, file_template, set_template, expected',
                                 templates.values(),
                             ids=templates.keys())
    def test_update_parameter_set_names(self, schema, file_template, set_template, expected):
        """Check the generated and updated parameter set names against template arguments

        :param str schema: placeholder string standing in for the schema read from an input file
        :param str file_template: user supplied string to be used as a template for output file names
        :param str set_template: user supplied string to be used as a template for parameter names
        :param list expected: list of expected parameter name strings
        """
        kwargs = {"sets": 1}
        if not set_template:
            TemplateGenerator = NoQuantilesGenerator(schema, output_file_template=file_template, **kwargs)
        else:
            TemplateGenerator = NoQuantilesGenerator(schema, output_file_template=file_template,
                                                     set_name_template=set_template, **kwargs)
        assert list(TemplateGenerator._parameter_set_names.values()) == expected

        # Test that the update function runs with only a single set. Check that the names don't change.
        TemplateGenerator._update_parameter_set_names()
        assert list(TemplateGenerator._parameter_set_names.values()) == expected

    init_write_stdout = {# schema, template, overwrite, dry_run,         is_file,  sets, stdout_calls
        'no-template-1': (     {},     None,     False,  False,          [False],    1,            1),
        'no-template-2': (     {},     None,      True,  False,          [False],    1,            1),
        'no-template-3': (     {},     None,     False,   True,   [False, False],    2,            1),
        'no-template-4': (     {},     None,     False,  False,   [ True,  True],    2,            1),
        'dry_run-1':     (     {},    'out',     False,   True,          [False],    1,            1),
        'dry_run-2':     (     {},    'out',      True,   True,          [False],    1,            1),
        'dry_run-3':     (     {},    'out',      True,   True,   [ True, False],    2,            2),
        'dry_run-4':     (     {},    'out',     False,   True,   [False,  True],    1,            1),
    }

    @pytest.mark.parametrize('schema, template, overwrite, dry_run, is_file, sets, stdout_calls',
                                 init_write_stdout.values(),
                             ids=init_write_stdout.keys())
    def test_write_to_stdout(self, schema, template, overwrite, dry_run, is_file, sets, stdout_calls):
        """Check for conditions that should result in calls to stdout

        :param str schema: placeholder string standing in for the schema read from an input file
        :param str template: user supplied string to be used as a template for output file names
        :param bool overwrite: overwrite existing files
        :param bool dry_run: skip file write, but show file name and associated contents that would ahve been written
        :param bool is_file: test specific argument mocks output for pathlib.Path().is_file()
        :param int sets: test specific argument for the number of sets to build for the test
        :param int stdout_calls: number of calls to stdout. Should only differ from set count when no template is
            provides. Should always be 1 when no template is provided.
        """
        kwargs = {"sets": sets}
        WriteParameterGenerator = NoQuantilesGenerator(schema, output_file_template=template, output_file_type='yaml',
                                                       overwrite=overwrite, dry_run=dry_run, **kwargs)
        with patch('waves.parameter_generators.ParameterGenerator._write_meta'), \
             patch('builtins.open', mock_open()) as mock_file, \
             patch('sys.stdout.write') as stdout_write, \
             patch('xarray.Dataset.to_netcdf') as xarray_to_netcdf, \
             patch('pathlib.Path.is_file', side_effect=is_file), \
             patch('pathlib.Path.mkdir'):
            WriteParameterGenerator.write()
            mock_file.assert_not_called()
            xarray_to_netcdf.assert_not_called()
            assert stdout_write.call_count == stdout_calls

    init_write_files = {# schema, template, overwrite, dry_run,          is_file, sets, files
        'template-1':  (      {},    'out',     False,   False,          [False],    1,     1),
        'template-2':  (      {},    'out',     False,   False,   [False, False],    2,     2),
        'template-3':  (      {},    'out',     False,   False,   [ True,  True],    2,     0),
        'template-4':  (      {},    'out',     False,   False,   [ True, False],    2,     1),
        'overwrite-2': (      {},    'out',      True,   False,   [False, False],    2,     2),
        'overwrite-3': (      {},    'out',      True,   False,   [ True,  True],    2,     2),
        'overwrite-4': (      {},    'out',      True,   False,   [ True, False],    2,     2),
    }

    @pytest.mark.parametrize('schema, template, overwrite, dry_run, is_file, sets, files',
                                 init_write_files.values(),
                             ids=init_write_files.keys())
    def test_write_yaml(self, schema, template, overwrite, dry_run, is_file, sets, files):
        """Check for conditions that should result in calls to builtins.open

        :param str schema: placeholder string standing in for the schema read from an input file
        :param str template: user supplied string to be used as a template for output file names
        :param bool overwrite: overwrite existing files
        :param bool dry_run: skip file write, but show file name and associated contents that would ahve been written
        :param list is_file: test specific argument mocks changing output for pathlib.Path().is_file() repeat calls
        :param int sets: test specific argument for the number of sets to build for the test
        :param int files: integer number of files that should be written
        """
        kwargs = {"sets": sets}
        WriteParameterGenerator = NoQuantilesGenerator(schema, output_file_template=template, output_file_type='yaml',
                                                       overwrite=overwrite, dry_run=dry_run, **kwargs)
        with patch('waves.parameter_generators.ParameterGenerator._write_meta'), \
             patch('waves.parameter_generators.ParameterGenerator._conditionally_write_yaml') as mock_file, \
             patch('sys.stdout.write') as stdout_write, \
             patch('xarray.Dataset.to_netcdf') as xarray_to_netcdf, \
             patch('pathlib.Path.is_file', side_effect=is_file):
            WriteParameterGenerator.write()
            stdout_write.assert_not_called()
            xarray_to_netcdf.assert_not_called()
            assert mock_file.call_count == files

    @pytest.mark.parametrize('schema, template, overwrite, dry_run, is_file, sets, files',
                                 init_write_files.values(),
                             ids=init_write_files.keys())
    def test_write_dataset(self, schema, template, overwrite, dry_run, is_file, sets, files):
        """Check for conditions that should result in calls to ParameterGenerator._write_netcdf

        :param str schema: placeholder string standing in for the schema read from an input file
        :param str template: user supplied string to be used as a template for output file names
        :param bool overwrite: overwrite existing files
        :param bool dry_run: skip file write, but show file name and associated contents that would ahve been written
        :param list is_file: test specific argument mocks changing output for pathlib.Path().is_file() repeat calls
        :param int sets: test specific argument for the number of sets to build for the test
        :param int files: integer number of files that should be written
        """
        kwargs = {"sets": sets}
        WriteParameterGenerator = NoQuantilesGenerator(schema, output_file_template=template, output_file_type='h5',
                                                       overwrite=overwrite, dry_run=dry_run, **kwargs)

        with patch('waves.parameter_generators.ParameterGenerator._write_meta'), \
             patch('builtins.open', mock_open()) as mock_file, \
             patch('sys.stdout.write') as stdout_write, \
             patch('waves.parameter_generators.ParameterGenerator._conditionally_write_dataset') as write_netcdf, \
             patch('pathlib.Path.is_file', side_effect=is_file), \
             patch('pathlib.Path.mkdir'):
            WriteParameterGenerator.write()
            mock_file.assert_not_called()
            stdout_write.assert_not_called()
            assert write_netcdf.call_count == files

    init_write_dataset_files = {# equals, is_file, overwrite, expected_call_count
        'equal-datasets':      (    True,  [True],     False,                   0),
        'equal-overwrite':     (    True,  [True],      True,                   1),
        'different-datasets':  (   False,  [True],     False,                   1),
        'not-file-1':          (    True, [False],     False,                   1),
        'not-file-2':          (   False, [False],     False,                   1),
    }

    @pytest.mark.parametrize('equals, is_file, overwrite, expected_call_count',
                             init_write_dataset_files.values(),
                             ids=init_write_dataset_files.keys())
    def test_conditionally_write_dataset(self, equals, is_file, overwrite, expected_call_count):
        """Check for conditions that should result in calls to xarray.Dataset.to_netcdf

        :param bool equals: parameter that identifies when the xarray.Dataset objects should be equal
        :param list is_file: test specific argument mocks changing output for pathlib.Path().is_file() repeat calls
        :param bool overwrite: parameter that identifies when the file should always be overwritten
        :param int expected_call_count: amount of times that the xarray.Dataset.to_netcdf function should be called
        """
        WriteParameterGenerator = NoQuantilesGenerator({}, overwrite=overwrite)

        with patch('xarray.Dataset.to_netcdf') as xarray_to_netcdf, \
             patch('xarray.open_dataset', mock_open()), \
             patch('xarray.Dataset.equals', return_value=equals), \
             patch('pathlib.Path.is_file', side_effect=is_file):
            WriteParameterGenerator._conditionally_write_dataset('dummy_string', xarray.Dataset())
            assert xarray_to_netcdf.call_count == expected_call_count

    @pytest.mark.parametrize('equals, is_file, overwrite, expected_call_count',
                             init_write_dataset_files.values(),
                             ids=init_write_dataset_files.keys())
    def test_conditionally_write_yaml(self, equals, is_file, overwrite, expected_call_count):
        """Check for conditions that should result in writing out to file

        :param bool equals: parameter that identifies when the dictionaries should be equal
        :param list is_file: test specific argument mocks changing output for pathlib.Path().is_file() repeat calls
        :param bool overwrite: parameter that identifies when the file should always be overwritten
        :param int expected_call_count: amount of times that the open.write function should be called
        """
        WriteParameterGenerator = NoQuantilesGenerator({}, overwrite=overwrite)
        existing_dict = {'dummy': 'dict'} if equals else {'smart': 'dict'}

        with patch('builtins.open', mock_open()) as write_yaml_file, \
             patch('yaml.safe_load', return_value=existing_dict), \
             patch('pathlib.Path.is_file', side_effect=is_file):
            WriteParameterGenerator._conditionally_write_yaml('dummy_string', {'dummy': 'dict'})
            assert write_yaml_file.return_value.write.call_count == expected_call_count

    set_hashes = {
        'set1': (
            ["name1", "name2", "name3"],
            numpy.array([[1, 10.1, 'a']], dtype=object),
            None,
            ['732411987fea3ae4a1e0bd7ea6a8841a']
        ),
        'set1 different parameter order': (
            ["name3", "name2", "name1"],
            numpy.array([['a', 10.1, 1]], dtype=object),
            None,
            ['732411987fea3ae4a1e0bd7ea6a8841a']
        ),
        'set1 different parameter names': (
            ["newname1", "newname2", "newname3"],
            numpy.array([[1, 10.1, 'a']], dtype=object),
            None,
            ['45458adbaeb9a55dcec2211383c9bd96']
        ),
        'set1 quantiles': (
            ["name1", "name2", "name3"],
            numpy.array([[1, 10.1, 'a']], dtype=object),
            numpy.array([[.1, 1.01, None]], dtype=object),
            ['d42ee7b8139d8dab2fcc6444c62da0a1']
        ),
        'set2': (
            ["name1", "name2", "name3"],
            numpy.array([[1, 10.1, 'a'], [2, 20.2, 'b'], [3, 30.3, 'c']], dtype=object),
            None,
            ['732411987fea3ae4a1e0bd7ea6a8841a',
             '6dfcf74620c998f3ef7ab4cc9fb2d510',
             '57af5a35970eb8a1a93c1ed62ff3ff37']
        )
    }

    @pytest.mark.parametrize('parameter_names, samples, quantiles, expected_hashes',
                                 set_hashes.values(),
                             ids=set_hashes.keys())
    def test_create_parameter_set_hashes(self, parameter_names, samples, quantiles, expected_hashes):
        HashesParameterGenerator = NoQuantilesGenerator({})
        HashesParameterGenerator._parameter_names = parameter_names
        HashesParameterGenerator._samples = samples
        if quantiles is not None:
            HashesParameterGenerator._quantiles = quantiles
        HashesParameterGenerator._create_parameter_set_hashes()
        assert HashesParameterGenerator._parameter_set_hashes == expected_hashes

    def test_create_parameter_set_names(self):
        """Test the parmater set name generation"""
        SetNamesParameterGenerator = NoQuantilesGenerator({}, output_file_template='out')
        SetNamesParameterGenerator._samples = numpy.array([[1], [2]])
        SetNamesParameterGenerator._create_parameter_set_hashes()
        SetNamesParameterGenerator._create_parameter_set_names()
        assert list(SetNamesParameterGenerator._parameter_set_names.values()) == ['out0', 'out1']

    def test_parameter_study_to_numpy(self):
        """Test the self-consistency of the parameter study dataset construction and deconstruction"""
        # Setup
        DataParameterGenerator = NoQuantilesGenerator({})
        DataParameterGenerator._parameter_names = ['ints', 'floats', 'strings']
        DataParameterGenerator._samples = numpy.array([[1, 10.1, 'a'], [2, 20.2, 'b']], dtype=object)
        DataParameterGenerator._create_parameter_set_hashes()
        DataParameterGenerator._create_parameter_set_names()
        DataParameterGenerator._create_parameter_study()
        # Test
        returned_samples = DataParameterGenerator._parameter_study_to_numpy('samples')
        assert numpy.all(returned_samples == DataParameterGenerator._samples)


class TestParameterDistributions:
    """Class for testing _ScipyGenerator ABC class common methods"""

    validate_input = {
        "good schema": (
            {'num_simulations': 1, 'parameter_1': {'distribution': 'norm', 'kwarg1': 1}},
            does_not_raise()
        ),
        "not a dict": (
            'not a dict',
            pytest.raises(SchemaValidationError)
        ),
        "missing num_simulation": (
            {},
            pytest.raises(SchemaValidationError)
        ),
        "num_simulation non-integer": (
            {'num_simulations': 'not_a_number'},
            pytest.raises(SchemaValidationError)
        ),
        "missing distribution": (
            {'num_simulations': 1, 'parameter_1': {}},
            pytest.raises(SchemaValidationError)
        ),
        "distribution non-string": (
            {'num_simulations': 1, 'parameter_1': {'distribution': 1}},
            pytest.raises(SchemaValidationError)
        ),
        "distribution bad identifier": (
            {'num_simulations': 1, 'parameter_1': {'distribution': 'my norm'}},
            pytest.raises(SchemaValidationError)
        ),
        "kwarg bad identifier": (
            {'num_simulations': 1, 'parameter_1': {'distribution': 'norm', 'kwarg 1': 1}},
            pytest.raises(SchemaValidationError)
        )
    }

    @pytest.mark.parametrize('parameter_schema, outcome',
                             validate_input.values(),
                             ids=validate_input.keys())
    def test_validate(self, parameter_schema, outcome):
        with patch("waves.parameter_generators._ScipyGenerator._generate_parameter_distributions") as mock_distros, \
             outcome:
            try:
                # Validate is called in __init__. Do not need to call explicitly.
                TestValidate = ParameterDistributions(parameter_schema)
                mock_distros.assert_called_once()
            finally:
                pass

    generate_input = {
        "good schema 5x2": (
            {'num_simulations': 5,
             'parameter_1': {'distribution': 'norm', 'loc': 50, 'scale': 1},
             'parameter_2': {'distribution': 'norm', 'loc': -50, 'scale': 1}},
            [{"loc":  50, "scale": 1},
             {"loc": -50, "scale": 1}],
        ),
        "good schema 2x1": (
            {'num_simulations': 2,
            'parameter_1': {'distribution': 'norm', 'loc': 50, 'scale': 1}},
            [{"loc":  50, "scale": 1}]
        ),
        "good schema 1x2": (
            {'num_simulations': 1,
             'parameter_1': {'distribution': 'norm', 'loc': 50, 'scale': 1},
             'parameter_2': {'distribution': 'norm', 'loc': -50, 'scale': 1}},
            [{"loc":  50, "scale": 1},
             {"loc": -50, "scale": 1}]
        )
    }

    @pytest.mark.parametrize("parameter_schema, expected_scipy_kwds",
                             generate_input.values(),
                             ids=generate_input.keys())
    def test_generate_parameter_distributions(self, parameter_schema, expected_scipy_kwds):
        TestDistributions = ParameterDistributions(parameter_schema)
        assert TestDistributions._parameter_names == list(TestDistributions.parameter_distributions.keys())
        for parameter_name, expected_kwds in zip(TestDistributions._parameter_names, expected_scipy_kwds):
            assert TestDistributions.parameter_distributions[parameter_name].kwds == expected_kwds


class NoQuantilesGenerator(ParameterGenerator):

    def _validate(self):
        self._parameter_names = ['parameter_1']

    def _generate(self, sets=1):
        """Generate float samples for all parameters. Value matches parameter set index"""
        parameter_count = len(self._parameter_names)
        self._samples = numpy.ones((sets, parameter_count))
        for row in range(sets):
            self._samples[row, :] = self._samples[row, :]*row
        super()._generate()


class ParameterDistributions(_ScipyGenerator):

    def _generate(self):
        pass
