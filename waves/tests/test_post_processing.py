#! /usr/bin/env python

import pytest
from unittest.mock import patch, mock_open
from pathlib import Path

from waves.tutorials.eabm_package.python import post_processing


@pytest.mark.unittest
def test_get_parser():
    with patch('sys.argv', ['post_processing.py', '-i', 'sample.nc', '--x-units', 'cm', '--y-units', 'cm']):
        cmd_args = post_processing.get_parser().parse_args()


plot_parameters = {  # group_path, x_var, x_units, y_var, y_units, parameter_study_file, csv_regression_file,
    'plot-1':         ("RECTANGLE/FieldOutputs/ALL", "E", "cm", "S", "cm",            None,            None),
    'plot-study':     ("RECTANGLE/FieldOutputs/ALL", "E", "cm", "S", "cm", "dummy_file.nc",            None),
    'plot-csv':       ("RECTANGLE/FieldOutputs/ALL", "E", "cm", "S", "cm",            None, "dummy_file.nc"),
    'plot-study-csv': ("RECTANGLE/FieldOutputs/ALL", "E", "cm", "S", "cm", "dummy_file.nc",    "dummy_file"),
}


@pytest.mark.unittest
@pytest.mark.parametrize('group_path, x_var, x_units, y_var, y_units, parameter_study_file, csv_regression_file',
                         plot_parameters.values(),
                         ids=plot_parameters.keys())
def test_plot(group_path, x_var, x_units, y_var, y_units, parameter_study_file, csv_regression_file):
    input_path = [Path('dummy.nc')]
    output_path = Path('dummy.pdf')
    selection_dict = {'E values': 'E22', 'S values': 'S22', 'elements': 1, 'step': 'Step-1', 'integration point': 0}
    with (patch('xarray.open_dataset', mock_open()),
          patch('waves.tutorials.eabm_package.python.post_processing.combine_data') as combine_data,
          patch('waves.tutorials.eabm_package.python.post_processing.merge_parameter_study') as merge_parameter_study,
          patch('waves.tutorials.eabm_package.python.post_processing.regression_test') as regression_test,
          patch('waves.tutorials.eabm_package.python.post_processing.save_plots') as save_plots,
          patch('matplotlib.pyplot.savefig'),
          patch('pandas.read_csv'),
          patch('builtins.print')):
        post_processing.plot(input_files=input_path, output_file=output_path, group_path=group_path, x_var=x_var,
                             x_units=x_units, y_var=y_var, y_units=y_units, selection_dict=selection_dict,
                             parameter_study_file=parameter_study_file, csv_regression_file=csv_regression_file)
        assert combine_data.call_count == 1
        assert save_plots.call_count == 1
        if parameter_study_file:
            assert merge_parameter_study.call_count == 1
        else:
            assert merge_parameter_study.call_count == 0
        if csv_regression_file:
            assert regression_test.call_count == 1
        else:
            assert regression_test.call_count == 0
