#! /usr/bin/env python

"""Test sta parse
Test sta_parse.py

.. moduleauthor:: Prabhu S. Khalsa <pkhalsa@lanl.gov>
"""

from unittest.mock import patch

from waves.abaqus.command_line_tools import sta_parse


def test_get_parser():
    with patch('sys.argv', ['sta_parse.py', 'sample.sta', '-o', 'sample.yaml']):
        cmd_args = sta_parse.get_parser().parse_args()
        assert cmd_args.sta_file[0] == "sample.sta"
        assert cmd_args.output_file == "sample.yaml"


def test_main():
    with patch('sys.argv', ['sta_parse.py', 'sample.sta']), \
         patch('builtins.print') as mock_print, \
         patch('waves.abaqus.abaqus_file_parser.StaFileParser'):
        sta_parse.main()
        mock_print.assert_called_with("sample.sta does not exist")

    path_exists = [True, True]
    with patch('sys.argv', ['sta_parse.py', 'sample.sta']), \
         patch('pathlib.Path.exists', side_effect=path_exists), \
         patch('builtins.print') as mock_print, \
         patch('waves.abaqus.abaqus_file_parser.StaFileParser.write_yaml') as write_yaml, \
         patch('waves.abaqus.abaqus_file_parser.StaFileParser.parse') as parse:
        sta_parse.main()
        assert parse.called
        assert write_yaml.called
        mock_print.assert_called_with("already exists")
