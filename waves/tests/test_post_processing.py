#! /usr/bin/env python

import pytest
from unittest.mock import patch, mock_open
from pathlib import Path

from waves.tutorials.eabm_package.python import post_processing


@pytest.mark.unittest
def test_get_parser():
    with patch('sys.argv', ['post_processing.py', '-i', 'sample.nc', '--x-units', 'cm', '--y-units', 'cm']):
        cmd_args = post_processing.get_parser().parse_args()


plot_parameters = {  # group_path, x_var, x_units, y_var, y_units, parameter_study_file, csv_regression_file, equals
    'plot-1': (Path("RECTANGLE") / "FieldOutputs" / "ALL", "E", "cm", "S", "cm", None, None, False),
    'plot-study': (Path("RECTANGLE") / "FieldOutputs" / "ALL", "E", "cm", "S", "cm", "dummy_file.nc", None, False),
    'plot-csv': (Path("RECTANGLE") / "FieldOutputs" / "ALL", "E", "cm", "S", "cm", None, "dummy_file.nc", True),
    'plot-study-csv': (Path("RECTANGLE") / "FieldOutputs" / "ALL", "E", "cm", "S", "cm", "dummy_file.nc", "dummy_file", False),
}


@pytest.mark.unittest
@pytest.mark.parametrize('group_path, x_var, x_units, y_var, y_units, parameter_study_file, csv_regression_file, equals',
                         plot_parameters.values(),
                         ids=plot_parameters.keys())
def test_plot(group_path, x_var, x_units, y_var, y_units, parameter_study_file, csv_regression_file, equals):
    input_path = [Path('dummy.nc')]
    output_path = Path('dummy.pdf')
    selection_dict = {'E values': 'E22', 'S values': 'S22', 'elements': 1, 'step': 'Step-1', 'integration point': 0}
    with (patch('xarray.open_dataset', mock_open()),
          patch('xarray.concat'),
          patch('xarray.merge') as merge,
          patch('pandas.read_csv'),
          patch('pandas.DataFrame.equals', return_value=equals) as is_equal,
          patch('builtins.print') as sys_out):
        post_processing.plot(input_files=input_path, output_file=output_path, group_path=group_path, x_var=x_var,
                             x_units=x_units, y_var=y_var, y_units=y_units, selection_dict=selection_dict,
                             parameter_study_file=parameter_study_file, csv_regression_file=csv_regression_file)
        if parameter_study_file:
            assert merge.call_count == 1
        else:
            assert merge.call_count == 0
        if csv_regression_file:
            assert is_equal.call_count == 1
            if equals:
                assert sys_out.call_count == 1
            else:
                assert sys_out.call_count == 2
