#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""Test msg parse
Test msg_parse.py

.. moduleauthor:: Prabhu S. Khalsa <pkhalsa@lanl.gov>
"""

from unittest.mock import patch
from pathlib import Path

from waves.abaqus.command_line_tools import msg_parse


def test_get_parser():
    with patch('sys.argv', ['msg_parse.py', 'sample.msg', '-o', 'sample', '-a']):
        cmd_args = msg_parse.get_parser().parse_args()
        assert cmd_args.msg_file[0] == "sample.msg"
        assert cmd_args.output_file == "sample"
        assert cmd_args.write_all == True
        assert cmd_args.write_summary_table == False
        assert cmd_args.write_yaml == True

def test_main(caplog):
    with patch('sys.argv', ['msg_parse.py', 'sample.msg']), \
         patch('waves.abaqus.abaqus_file_parser.MsgFileParser'):
        msg_parse.main()
    critical_records = [r.message for r in caplog.records if r.levelname == 'CRITICAL']
    assert "sample.msg does not exist" in critical_records[0]
    caplog.clear()

    path_exists = [True, False, False, False]
    with patch('sys.argv', ['msg_parse.py', 'sample.msg', '-s', '-a']), \
         patch('pathlib.Path.exists', side_effect=path_exists), \
         patch('waves.abaqus.abaqus_file_parser.MsgFileParser.write_yaml') as write_yaml, \
         patch('waves.abaqus.abaqus_file_parser.MsgFileParser.write_all') as write_all, \
         patch('waves.abaqus.abaqus_file_parser.MsgFileParser.write_summary_table') as write_summary, \
         patch('waves.abaqus.abaqus_file_parser.MsgFileParser.parse') as parse:
        msg_parse.main()
        assert parse.called
        assert write_yaml.called
        assert write_all.called
        assert write_summary.called

def test_file_exists(caplog):
    fake_path = Path('fake_file.txt')
    with patch('pathlib.Path.exists', return_value=False):
        file_name = msg_parse.file_exists(fake_path)
        assert file_name == str(fake_path)
    with patch('pathlib.Path.exists', return_value=True):
        file_name = msg_parse.file_exists(fake_path)
        assert file_name.startswith('fake_file_')

    warning_logs = [r.message for r in caplog.records if r.levelname == 'WARNING']
    assert "already exists" in warning_logs[0]
    caplog.clear()
