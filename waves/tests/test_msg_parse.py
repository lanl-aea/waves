#! /usr/bin/env python

"""Test msg parse
Test msg_parse.py

.. moduleauthor:: Prabhu S. Khalsa <pkhalsa@lanl.gov>
"""

import pytest
from unittest.mock import patch
from pathlib import Path
from contextlib import nullcontext as does_not_raise

from waves.abaqus.command_line_tools import msg_parse

main_input = {
    '': ('', [], does_not_raise()),
    '': pytest.param('', [], pytest.raises(SystemExit))
}

@pytest.mark.unittest
def test_get_parser():
    with patch('sys.argv', ['msg_parse.py', 'sample.msg', '-o', 'sample', '-a']):
        cmd_args = msg_parse.get_parser().parse_args()
        assert cmd_args.msg_file[0] == "sample.msg"
        assert cmd_args.output_file == "sample"
        assert cmd_args.write_all == True
        assert cmd_args.write_summary_table == False
        assert cmd_args.write_yaml == True

@pytest.mark.unittest
#@pytest.mark.parametrize( "", ["", pytest.raises(SystemExit)] )
#@pytest.mark.parametrize("", main_input.values(), ids=main_input.keys())
def test_main():
    with patch('sys.argv', ['msg_parse.py', 'sample.msg']), \
         patch('builtins.print') as mock_print, \
         pytest.raises(SystemExit) as exc_info, \
         patch('waves.abaqus.abaqus_file_parser.MsgFileParser'):
        msg_parse.main()
        assert "sample.msg does not exist" in str(mock_print.call_args)
        exception_raised = exc_info.value
        assert exception_raised == -1

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

@pytest.mark.unittest
def test_file_exists():
    fake_path = Path('fake_file.txt')
    with patch('pathlib.Path.exists', return_value=False):
        file_name = msg_parse.file_exists(fake_path)
        assert file_name == str(fake_path)
    with patch('pathlib.Path.exists', return_value=True), \
         patch('builtins.print') as mock_print:
        file_name = msg_parse.file_exists(fake_path)
        assert file_name.startswith('fake_file_')
        assert "already exists" in str(mock_print.call_args)

