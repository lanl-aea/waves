#! /usr/bin/env python

import pytest
from unittest.mock import patch
from pathlib import Path

from waves.tutorials.eabm_package.python import post_processing


@pytest.mark.unittest
def test_get_parser():
    with patch('sys.argv', ['post_processing.py', '-i', 'sample.nc', '--x-units', '34', '--y-units', '12']):
        cmd_args = post_processing.get_parser().parse_args()


@pytest.mark.unittest
def test_plot():
    fake_input_path = Path('fake_input_file.nc')
    fake_output_path = Path('fake_output_file.nc')
    group_path = Path("RECTANGLE") / "FieldOutputs" / "ALL"
    with patch('pathlib.Path.exists', return_value=False):
        file_name = msg_parse.file_exists(fake_path)
        assert file_name == str(fake_path)
    with patch('pathlib.Path.exists', return_value=True), \
         patch('builtins.print') as mock_print:
        file_name = msg_parse.file_exists(fake_path)
        assert file_name.startswith('fake_file_')
        assert "already exists" in str(mock_print.call_args)
