#! /usr/bin/env python

"""Test odb extract
Test odb_extract.py

.. moduleauthor:: Prabhu S. Khalsa <pkhalsa@lanl.gov>
"""

import pytest
from unittest.mock import patch, mock_open

from waves.abaqus.command_line_tools import odb_extract


fake_odb = {
    "rootAssembly": {
        "name": "ASSEMBLY",
        "instances": {
            "RIGID-1": {
                "name": "RIGID-1",
                "embeddedSpace": "THREE_D",
                "type": "ANALYTIC_RIGID_SURFACE",
                "nodes": [
                    {
                        "label": 1,
                        "coordinates": [
                            100.0,
                            20,
                            6.12323e-15
                        ]
                    }
                ],
                "tuple": (1, 2.0),
                "float": 1.0,
                "string_list": ['list', 'of', 'strings']
            }
        }
    }
}


@pytest.mark.unittest
def test_get_parser():
    with patch('sys.argv', ['odb_extract.py', 'sample.odb']):
        cmd_args = odb_extract.get_parser().parse_args()
        assert cmd_args.abaqus_command == "abaqus"


@pytest.mark.unittest
def test_main():
    with patch('sys.argv', ['odb_extract.py', 'sample.odb']), \
         patch('yaml.safe_dump'), \
         patch('waves.abaqus.command_line_tools.odb_extract.which', return_value='abaqus'), \
         patch('select.select', return_value=[None, None, None]), \
         patch('waves.abaqus.abaqus_file_parser.OdbReportFileParser'), \
         pytest.raises(SystemExit) as mock_exception, \
         patch('builtins.print') as mock_print, \
         patch('builtins.open', mock_open(read_data="data")):  # Test first critical error
        odb_extract.main()
        assert "sample.odb does not exist" in str(mock_print.call_args)
        assert mock_exception.value == -1

    with patch('sys.argv', ['odb_extract.py', 'sample']),  \
         patch('yaml.safe_dump'), patch('builtins.open', mock_open(read_data="data")), \
         patch('waves.abaqus.command_line_tools.odb_extract.which', return_value='abaqus'), \
         patch('select.select', return_value=[None, None, None]), \
         patch('waves.abaqus.abaqus_file_parser.OdbReportFileParser'), \
         patch('waves.abaqus.command_line_tools.odb_extract.print_warning') as mock_print, \
         patch('pathlib.Path.exists', return_value=True):  # Test warning after second critical error
        odb_extract.main()
        assert "sample is not an odb file" in str(mock_print.call_args_list[0])

    with patch('sys.argv', ['odb_extract.py', 'sample.odb', '-r', 'odbreport all', '-f', 'yaml']), \
         patch('yaml.safe_dump'), patch('builtins.open', mock_open(read_data="data")), \
         patch('waves.abaqus.command_line_tools.odb_extract.which', return_value='abaqus'), \
         patch('select.select', return_value=[None, None, None]), \
         patch('waves.abaqus.abaqus_file_parser.OdbReportFileParser', side_effect=IndexError('Test')), \
         pytest.raises(SystemExit) as mock_exception, \
         patch('builtins.print') as mock_print, \
         patch('pathlib.Path.exists', return_value=True):  # Test second critical error
        odb_extract.main()
        assert "could not be parsed." in str(mock_print.call_args)
        assert mock_exception.value == -1

    with patch('sys.argv', ['odb_extract.py', 'sample.odb', '-r', '"job=job_name odb=odb_file all"']), \
         patch('pathlib.Path.exists', return_value=True), \
         patch('builtins.open', mock_open(read_data="data")), \
         patch('yaml.safe_dump'), \
         patch('waves.abaqus.command_line_tools.odb_extract.which', return_value='abaqus'), \
         patch('select.select', return_value=['y', None, None]), \
         patch('sys.stdin', return_value='y'), \
         pytest.raises(SystemExit) as mock_exception, \
         patch('builtins.print') as mock_print, \
         patch('waves.abaqus.abaqus_file_parser.OdbReportFileParser') as mock_abaqus_file_parser, \
         patch(
             'waves.abaqus.command_line_tools.odb_extract.run_external', return_value=[b'', -1, b'invalid command.']) \
                 as mock_run_external:
        # Test case where report args need to be adjusted, abaqus file parser is called, and third critical error
        odb_extract.main()
        mock_abaqus_file_parser.assert_called()
        mock_run_external.assert_called_with('abaqus odbreport job=sample odb=sample.odb all mode=CSV blocked')
        assert "Abaqus odbreport command failed to execute" in str(mock_print.call_args)
        assert mock_exception.value == -1

    with patch('sys.argv', ['odb_extract.py', 'sample.odb', '-r', 'odbreport all', '-f', 'yaml']), \
         patch('pathlib.Path.exists', return_value=[True, False]), \
         patch('builtins.open', mock_open(read_data="data")), \
         patch('yaml.safe_dump') as mock_safe_dump, \
         patch('waves.abaqus.command_line_tools.odb_extract.which', return_value='abaqus'), \
         patch('select.select', return_value=['y', None, None]), \
         patch('sys.stdin', return_value='y'), \
         patch('waves.abaqus.abaqus_file_parser.OdbReportFileParser'), \
         patch(
             'waves.abaqus.command_line_tools.odb_extract.run_external', return_value=[b'', 0, b'valid command.']) \
                 as mock_run_external:
        # Test case where yaml dump is called
        odb_extract.main()
        mock_run_external.assert_called_with('abaqus odbreport job=sample odb=sample.odb all blocked mode=CSV')
        mock_safe_dump.assert_called()

    with patch('sys.argv', ['odb_extract.py', 'sample.odb', '-f', 'json', '-o', 'sample.j' , '-d']), \
         patch('pathlib.Path.exists', return_value=[True, False]), \
         patch('builtins.open', mock_open(read_data="data")), \
         patch('select.select', return_value=[None, None, None]), \
         patch('waves.abaqus.command_line_tools.odb_extract.which', return_value='abaqus'), \
         patch('json.dump') as mock_safe_dump, \
         patch('waves.abaqus.abaqus_file_parser.OdbReportFileParser'), \
         patch('pathlib.Path.unlink') as mock_unlink, \
         patch('waves.abaqus.command_line_tools.odb_extract.run_external', return_value=[b'', 0, b'valid command.']):
        # Test case where yaml dump is called
        odb_extract.main()
        mock_safe_dump.assert_called()
        mock_unlink.assert_called()

    with patch('sys.argv', ['odb_extract.py', 'sample.odb', '-f', 'h5']), \
         patch('pathlib.Path.exists', return_value=[True, False]), \
         patch('builtins.open', mock_open(read_data="data")), \
         patch('waves.abaqus.command_line_tools.odb_extract.which', return_value='abaqus'), \
         patch('select.select', return_value=[None, None, None]), \
         patch('waves.abaqus.abaqus_file_parser.OdbReportFileParser') as h5_parser, \
         patch('waves.abaqus.command_line_tools.odb_extract.run_external', return_value=[b'', 0, b'valid command.']):
        # Test case where h5 file is created
        odb_extract.main()
        h5_parser.assert_called()

    with patch('sys.argv', ['odb_extract.py', 'sample.odb', '-f', 'h5']), \
         patch('yaml.safe_dump'), patch('builtins.open', mock_open(read_data="data")), \
         patch('waves.abaqus.command_line_tools.odb_extract.which', return_value='abaqus'), \
         patch('select.select', return_value=[None, None, None]), \
         patch('waves.abaqus.abaqus_file_parser.OdbReportFileParser', side_effect=IndexError('Test')), \
         pytest.raises(SystemExit) as mock_exception, \
         patch('builtins.print') as mock_print, \
         patch('pathlib.Path.exists', return_value=True):  # Test second critical error
        # Test case where h5 file is requested, but error is raised
        odb_extract.main()
        assert "could not be parsed." in str(mock_print.call_args)
        assert mock_exception.value == -1
