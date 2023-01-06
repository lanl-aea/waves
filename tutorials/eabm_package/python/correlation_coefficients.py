#!/usr/bin/env python
"""Example of catenating WAVES parameter study results and definition"""

import sys
import argparse
import pathlib
import yaml

import numpy
import seaborn
import xarray
import pandas
import matplotlib.pyplot
import SALib.analyze.sobol

from eabm_package.python.correlation_coefficients_schema import parameter_schema


default_selection_dict = {'E values': 'E22', 'S values': 'S22', 'elements': 1, 'step': 'Step-1', 'time': 1.0,
                          'integration point': 0, 'data_type': 'samples'}


def plot(input_files, output_file, group_path, selection_dict,
         parameter_study_file=None):
    """Catenate ``input_files`` datasets along the ``parameter_sets`` dimension and plot selected data.

    Optionally merges the parameter study results datasets with the parameter study definition dataset, where the
    parameter study dataset file is assumed to be written by a WAVES parameter generator.

    :param list input_files: list of path-like or file-like objects pointing to h5netcdf files containing Xarray Datasets
    :param str output_file: The plot file name. Relative or absolute path.
    :param str group_path: The h5netcdf group path locating the Xarray Dataset in the input files.
    :param dict selection_dict: Dictionary to define the down selection of data to be plotted. Dictionary ``key: value``
        pairs must match the data variables and coordinates of the expected Xarray Dataset object.
    :param str parameter_study_file: path-like or file-like object containing the parameter study dataset. Assumes the
        h5netcdf file contains only a single dataset at the root group path, .e.g. ``/``.
    """
    output_file = pathlib.Path(output_file)
    output_csv = output_file.with_suffix(".csv")
    concat_coord = "parameter_sets"

    # Build single dataset along the "parameter_sets" dimension
    paths = [pathlib.Path(input_file).resolve() for input_file in input_files]
    data_generator = (xarray.open_dataset(path, group=group_path).assign_coords({concat_coord:
                          path.parent.name}) for path in paths)
    combined_data = xarray.concat(data_generator, concat_coord)

    # Open and merge WAVES parameter study if provided
    if parameter_study_file:
        parameter_study = xarray.open_dataset(parameter_study_file)
        combined_data = combined_data.merge(parameter_study)

    # Correlation coefficients
    correlation_data = combined_data.sel(selection_dict).to_array().to_pandas().transpose()
    seaborn.pairplot(correlation_data, corner=True)
    matplotlib.pyplot.savefig("correlation_pairplot.pdf")

    correlation_matrix = numpy.corrcoef(correlation_data.to_numpy(), rowvar=False)
    correlation_coefficients = pandas.DataFrame(correlation_matrix, index=correlation_data.columns,
                                                columns=correlation_data.columns)
    correlation_coefficients.to_csv(output_csv)

    # Sobol sensitivity
    stress = combined_data.sel(selection_dict)['S'].to_numpy()
    print(stress)
    sobol_sensitivity = SALib.analyze.sobol.analyze(parameter_schema["problem"], stress)
    with open("sobol_sensitivity.yaml") as sobol_output:
        yaml.safe_dump(sobol_sensitivity, sobol_output)

    # Clean up open files
    combined_data.close()
    if parameter_study_file:
        parameter_study.close()

    return 0


def get_parser():
    script_name = pathlib.Path(__file__)
    default_output_file = f"{script_name.stem}.pdf"
    default_group_path = "SINGLE_ELEMENT/FieldOutputs/ALL"
    default_parameter_study_file = None

    prog = f"python {script_name.name} "
    cli_description = "Read Xarray Datasets and plot stress-strain comparisons as a function of parameter set name. " \
                      " Save to ``output_file``."
    parser = argparse.ArgumentParser(description=cli_description,
                                     prog=prog)
    required_named = parser.add_argument_group('required named arguments')
    required_named.add_argument("-i", "--input-file", nargs="+", required=True,
                                help="The Xarray Dataset file(s)")

    parser.add_argument("-o", "--output-file", type=str, default=default_output_file,
                        help="The output file for the stress-strain comparison plot with extension, " \
                             "e.g. ``output_file.pdf``. Extension must be supported by matplotlib. File stem is also " \
                             "used for the CSV table output, e.g. ``output_file.csv``. (default: %(default)s)")
    parser.add_argument("-g", "--group-path", type=str, default=default_group_path,
                        help="The h5py group path to the dataset object (default: %(default)s)")
    parser.add_argument("-s", "--selection-dict", type=str, default=None,
                        help="The YAML formatted dictionary file to define the down selection of data to be plotted. " \
                             "Dictionary key: value pairs must match the data variables and coordinates of the expected Xarray Dataset object. " \
                             "If no file is provided, the a default selection dict will be used " \
                             f"(default: {default_selection_dict})")
    parser.add_argument("-p", "--parameter-study-file", type=str, default=default_parameter_study_file,
                        help="An optional h5 file with a WAVES parameter study Xarray Dataset (default: %(default)s)")

    return parser


if __name__ == "__main__":
    parser = get_parser()
    args, unknown = parser.parse_known_args()
    if not args.selection_dict:
        selection_dict = default_selection_dict
    else:
        with open(args.selection_dict, 'r') as input_yaml:
            selection_dict = yaml.safe_load(input_yaml)
    sys.exit(plot(input_files=args.input_file,
                  output_file=args.output_file,
                  group_path=args.group_path,
                  selection_dict=selection_dict,
                  parameter_study_file=args.parameter_study_file))
