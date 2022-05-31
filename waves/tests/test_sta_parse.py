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


def test_main(caplog):
    with patch('sys.argv', ['sta_parse.py', 'sample.sta']), \
         patch('waves.abaqus.abaqus_file_parser.StaFileParser'):
        sta_parse.main()
    critical_records = [r.message for r in caplog.records if r.levelname == 'CRITICAL']
    assert "sample.sta does not exist" in critical_records[0]
    caplog.clear()

    path_exists = [True, True]
    with patch('sys.argv', ['sta_parse.py', 'sample.sta']), \
         patch('pathlib.Path.exists', side_effect=path_exists), \
         patch('waves.abaqus.abaqus_file_parser.StaFileParser.write_yaml') as write_yaml, \
         patch('waves.abaqus.abaqus_file_parser.StaFileParser.parse') as parse:
        sta_parse.main()
        assert parse.called
        assert write_yaml.called

    warning_logs = [r.message for r in caplog.records if r.levelname == 'WARNING']
    assert "already exists" in warning_logs[0]
    caplog.clear()


