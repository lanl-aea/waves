from abc import ABC, abstractmethod
import pathlib
import string
import sys
import itertools

import numpy
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

        Must set the class attributes:

        * ``self.parameter_names``: list of strings containing the parameter study's parameter names
        """
        pass

    @abstractmethod
    def generate(self):
        """Generate the parameter study definition

        Must set the class attributes:

        * ``self.samples``: The parameter study values. A 2D numpy array in the shape (number of parameter sets, number of parameters)
        * ``self.parameter_study``: The Xarray Dataset parameter study object, created by calling
          ``_create_parameter_study()`` after defining ``samples`` and the optional ``quantiles`` class attribute.

        May set the class attributes:

        * ``self.quantiles``: The parameter study sample quantiles, if applicable. A 2D numpy array in the shape (number of parameter sets, number of parameters)

        .. code-block::

           import xarray
           import numpy

           set_count = 5
           parameter_names = ['parameter_1', 'parameter_2']
           self.samples = numpy.zeros((set_count, len(parameter_names)))
           self.parameter_study = _create_parameter_study()
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
            text = ''
            for value, parameter_name in zip(values, self.parameter_names):
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

    def _create_parameter_array(self, samples, name):
        """Create the standard structure for a parameter_study array

        requires:

        * ``self.parameter_set_names``: rows of ``samples`` parameter study values
        * ``self.parameter_names``: columns of ``samples`` parameter study values

        :param numpy.array samples: 2D array of parameter study values with shape (number of parameter sets, number of
            parameters).
        :param str name: Name of the array. Used as a data variable name when converting to parameter study dataset.
        """
        array = xarray.DataArray(
            samples,
            coords=[self.parameter_set_names, self.parameter_names],
            dims=['parameter_sets', 'parameters'],
            name=name
        )
        return array

    def _create_parameter_study(self):
        """Create the standard structure for the parameter study dataset

        requires:

        * ``self.parameter_set_names``: rows of ``samples`` parameter study values
        * ``self.parameter_names``: columns of ``samples`` parameter study values
        * ``self.samples``: The parameter study values

        optional:

        * ``self.quantiles``: The quantiles associated with the paramter study sampling distributions

        creates attribute:

        * ``self.parameter_study``
        """
        values = self._create_parameter_array(self.samples, name='values')
        if hasattr(self, "quantiles"):
            quantiles = self._create_parameter_array(self.quantiles, name='quantiles')
            self.parameter_study = xarray.merge([values, quantiles])
        else:
            self.parameter_study = values.to_dataset()


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
        self.parameter_names = list(self.parameter_schema.keys())

    def generate(self):
        """Generate the Cartesian Product parameter sets"""
        self.samples = numpy.array(list(itertools.product(*self.parameter_schema.values())))
        set_count = self.samples.shape[0]
        self._create_parameter_set_names(set_count)
        self._create_parameter_study()


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
        self._create_parameter_names()
        for name in self.parameter_names:
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
        parameter_count = len(self.parameter_names)
        self._create_parameter_set_names(set_count)
        self.quantiles = LHS(xlimits=numpy.repeat([[0, 1]], parameter_count, axis=0))(set_count)
        self.samples = numpy.zeros((set_count, parameter_count))
        parameter_dict = {key: value for key, value in self.parameter_schema.items() if key != 'num_simulations'}
        for i, attributes in enumerate(parameter_dict.values()):
            distribution_name = attributes.pop('distribution')
            distribution = getattr(scipy.stats, distribution_name)
            self.samples[:, i] = distribution(**attributes).ppf(self.quantiles[:, i])
        self._create_parameter_study()


    def _create_parameter_names(self):
        """Construct the Latin Hypercube parameter names"""
        self.parameter_names = [key for key in self.parameter_schema.keys() if key != 'num_simulations']
