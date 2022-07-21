from abc import ABC, abstractmethod
import pathlib
import string
import sys
import itertools

import numpy
import pandas
import xarray
import scipy.stats
from smt.sampling_methods import LHS

#========================================================================================================== SETTINGS ===
template_delimiter = '@'


class AtSignTemplate(string.Template):
    """Use the CMake '@' delimiter in a Python 'string.Template' to avoid clashing with bash variable syntax"""
    delimiter = template_delimiter


template_placeholder = f"{template_delimiter}number"
default_output_file_template = AtSignTemplate(f'parameter_set{template_placeholder}')
parameter_study_meta_file = "parameter_study_meta.txt"


# ========================================================================================== PARAMETER STUDY CLASSES ===
class ParameterGenerator(ABC):
    """Abstract base class for internal parameter study generators

    :param dict parameter_schema: The YAML loaded parameter study schema dictionary - {parameter_name: schema value}.
        Validated on class instantiation.
    :param str output_file_template: Output file name template
    :param bool overwrite: Overwrite existing output files
    :param bool dryrun: Print contents of new parameter study output files to STDOUT and exit
    :param bool debug: Print internal variables to STDOUT and exit
    :param bool write_meta: Write a meta file named "parameter_study_meta.txt" containing the parameter set file names.
        Useful for command line execution with build systems that require an explicit file list for target creation.
    """
    def __init__(self, parameter_schema, output_file_template=None,
                 overwrite=False, dryrun=False, debug=False, write_meta=False):
        self.parameter_schema = parameter_schema
        self.output_file_template = output_file_template
        self.overwrite = overwrite
        self.dryrun = dryrun
        self.debug = debug
        self.write_meta = write_meta

        self.default_template = default_output_file_template
        self.provided_template = False
        if self.output_file_template:
            if not f'{template_placeholder}' in self.output_file_template:
                self.output_file_template = f"{self.output_file_template}{template_placeholder}"
            self.output_file_template = AtSignTemplate(self.output_file_template)
            self.provided_template = True
        else:
            self.output_file_template = self.default_template

        self.validate()

    @abstractmethod
    def validate(self):
        """Process parameter study input to verify schema

        :returns: validated_schema
        :rtype: bool
        """
        pass

    @abstractmethod
    def generate(self):
        """Generate the parameter study definition

        Must accept ``self.parameter_schema`` dictionary and set ``self.parameter_study`` as an XArray Dataset in the format

        .. code-block:: bash

           <xarray.Dataset>
           Dimensions:         (parameter_name: 2, parameter_data: 1)
           Coordinates:
             * parameter_name  (parameter_name) object 'parameter_1' 'parameter_2'
             * parameter_data  (parameter_data) object 'values'
           Data variables:
               parameter_set0  (parameter_name, parameter_data) int64 1 3
               parameter_set1  (parameter_name, parameter_data) int64 1 4
               parameter_set2  (parameter_name, parameter_data) int64 2 3
               parameter_set3  (parameter_name, parameter_data) int64 2 4

        :returns: parameter study object: dict(parameter_set_name: parameter_set_text)
        :rtype: dict
        """
        pass

    def write(self):
        """Write the parameter study to STDOUT or an output file.

        If printing to STDOUT, print all parameter sets together. If printing to files, don't overwrite existing files.
        If overwrite is specified, overwrite all parameter set files. If a dry run is requested print file-content
        associations for files that would have been written.

        Writes parameter set files in Python syntax. Alternate syntax options are a WIP.

        .. code-block::

           parameter_1 = 1
           parameter_2 = a
        """
        if self.write_meta and self.provided_template:
            self._write_meta()
        parameter_set_files = [pathlib.Path(parameter_set_name) for parameter_set_name in self.parameter_study.keys()]
        self._write_meta(parameter_set_files)
        for parameter_set_file in parameter_set_files:
            # Construct the output text
            values = self.parameter_study[parameter_set_file.name].sel(parameter_data='values').values
            parameter_names = self.parameter_study[parameter_set_file.name].coords['parameter_name'].values
            text = ''
            for value, parameter_name in zip(values, parameter_names):
                text += f"{parameter_name} = {value}\n"
            # If no output file template is provided, print to stdout
            if not self.provided_template:
                sys.stdout.write(f"{parameter_set_file.name}:\n{text}")
            # If overwrite is specified or if file doesn't exist
            elif self.overwrite or not parameter_set_file.is_file():
                # If dry run is specified, print the files that would have been written to stdout
                if self.dryrun:
                    sys.stdout.write(f"{parameter_set_file.resolve()}:\n{text}")
                else:
                    with open(parameter_set_file, 'w') as outfile:
                        outfile.write(text)

    def _write_meta(self, parameter_set_files):
        """Write the parameter study meta data file.

        The parameter study meta file is always overwritten. It should *NOT* be used to determine if the parameter study
        target or dependee is out-of-date.

        :param list parameter_set_files: List of pathlib.Path parameter set file paths
        """
        # Always overwrite the meta data file to ensure that *all* parameter file names are included.
        with open(f'{parameter_study_meta_file}', 'w') as meta_file:
            for parameter_set_file in parameter_set_files:
                meta_file.write(f"{parameter_set_file.name}\n")

    def _create_parameter_set_names(self, set_count):
        """Construct parameter set names from the output file template and number of parameter sets

        Creates the generator attribute ``self.parameter_set_names`` required to populate the ``generate()`` method's
        parameter study Xarray dataset object.

        :param int set_count: Integer number of parameter sets
        """
        self.parameter_set_names = []
        for number in range(set_count):
            template = self.output_file_template
            self.parameter_set_names.append(template.substitute({'number': number}))


class CartesianProduct(ParameterGenerator):
    """Builds a cartesian product parameter study

    :param dict parameter_schema: The YAML loaded parameter study schema dictionary - {parameter_name: schema value}
        CartesianProduct expects "schema value" to be an iterable. For example, when read from a YAML file "schema
        value" will be a Python list.
    :param str output_file_template: Output file name template
    :param bool overwrite: Overwrite existing output files
    :param bool dryrun: Print contents of new parameter study output files to STDOUT and exit
    :param bool debug: Print internal variables to STDOUT and exit
    :param bool write_meta: Write a meta file named "parameter_study_meta.txt" containing the parameter set file names.
        Useful for command line execution with build systems that require an explicit file list for target creation.

    Expected parameter schema example:

    .. code-block::

       parameter_schema = {
           'parameter_1': [1, 2],
           'parameter_2': ['a', 'b']
       }
    """

    def validate(self):
        # TODO: Settle on an input file schema and validation library
        # https://re-git.lanl.gov/aea/python-projects/waves/-/issues/80
        return True

    def generate(self):
        """Generate the Cartesian Product parameter sets"""
        parameter_names = list(self.parameter_schema.keys())
        parameter_sets = numpy.array(list(itertools.product(*self.parameter_schema.values()))).transpose()
        set_count = len(parameter_sets[0])
        self._create_parameter_set_names(set_count)
        coordinates = [parameter_names, ['values']]
        index = pandas.MultiIndex.from_product(coordinates, names=["parameter_name", "parameter_data"])
        dataframe = pandas.DataFrame(parameter_sets, index=index, columns=self.parameter_set_names)
        self.parameter_study = xarray.Dataset().from_dataframe(dataframe)


class LatinHypercube(ParameterGenerator):
    """Builds a Latin Hypercube parameter study

    :param dict parameter_schema: The YAML loaded parameter study schema dictionary - {parameter_name: schema value}
        LatinHypercube expects "schema value" to be a dictionary with a strict structure and several required keys.
        Validated on class instantiation.
    :param str output_file_template: Output file name template
    :param bool overwrite: Overwrite existing output files
    :param bool dryrun: Print contents of new parameter study output files to STDOUT and exit
    :param bool debug: Print internal variables to STDOUT and exit
    :param bool write_meta: Write a meta file named "parameter_study_meta.txt" containing the parameter set file names.
        Useful for command line execution with build systems that require an explicit file list for target creation.

    Expected parameter schema example:

    .. code-block::

       parameter_schema = {
           'num_simulations': 100  # Required key. Value must be an integer.
           'parameter_name': {  # Parameter names must be valid Python identifiers
               'distribution': 'scipy_distribution_name',  # Required key. Value must be a valid scipy.stats
                                                           # distribution name.
               'kwarg_1': value,
               'kwarg_2': value2
           },
           'parameter_1': {
               'distribution': 'norm',
               'loc': 50,
               'scale': 1
           },
           'parameter_2': {
               'distribution': 'skewnorm',
               'a': 4,
               'loc': 30,
               'scale': 2
           }
       }
    """

    def validate(self):
        # TODO: Settle on an input file schema and validation library
        # https://re-git.lanl.gov/aea/python-projects/waves/-/issues/80
        if not 'num_simulations' in self.parameter_schema.keys():
            raise AttributeError("Parameter schema is missing the required 'num_simulations' key")
        elif not isinstance(self.parameter_schema['num_simulations'], int):
            raise TypeError("Parameter schema 'num_simulations' must be an integer.")
        parameter_names = self._set_names()
        for name in parameter_names:
            parameter_keys = self.parameter_schema[name].keys()
            parameter_definition = self.parameter_schema[name]
            if 'distribution' not in parameter_keys:
                raise AttributeError(f"Parameter '{name}' does not contain the required 'distribution' key")
            elif not isinstance(parameter_definition['distribution'], str) or \
                 not parameter_definition['distribution'].isidentifier():
                raise TypeError(f"Parameter '{name}' distribution '{parameter_definition['distribution']}' is not a " \
                                "valid Python identifier")
            else:
                for key in parameter_keys:
                    if not isinstance(key, str) or not key.isidentifier():
                        raise TypeError(f"Parameter '{name}' keyword argument '{key}' is not a valid " \
                                        "Python identifier")

    def generate(self):
        """Generate the Latin Hypercube parameter sets"""
        set_count = self.parameter_schema['num_simulations']
        parameter_names = self._set_names()
        parameter_count = len(parameter_names)
        self._create_parameter_set_names(set_count)
        quantiles = LHS(xlimits=numpy.repeat([[0, 1]], parameter_count, axis=0))(set_count)
        samples = numpy.zeros((set_count, parameter_count))
        parameter_dict = {key: value for key, value in self.parameter_schema.items() if key != 'num_simulations'}
        for i, attributes in enumerate(parameter_dict.values()):
            distribution_name = attributes.pop('distribution')
            distribution = getattr(scipy.stats, distribution_name)
            samples[:, i] = distribution(**attributes).ppf(quantiles[:, i])
        # Transpose to put parameter names on the columns and parameter sets as rows
        samples = samples.transpose()
        quantiles = quantiles.transpose()
        parameter_data_coordinates = ['values', 'quantiles']
        coordinates = [parameter_names, parameter_data_coordinates]
        rows = parameter_count * len(parameter_data_coordinates)
        parameter_sets = numpy.hstack((samples, quantiles)).reshape(rows, set_count)
        index = pandas.MultiIndex.from_product(coordinates, names=["parameter_name", "parameter_data"])
        dataframe = pandas.DataFrame(parameter_sets, index=index, columns=self.parameter_set_names)
        self.parameter_study = xarray.Dataset().from_dataframe(dataframe)

    def _set_names(self):
        """Construct the Latin Hypercube parameter names"""
        parameter_names = [key for key in self.parameter_schema.keys() if key != 'num_simulations']
        return parameter_names
