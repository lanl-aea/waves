from abc import ABC, abstractmethod
import pathlib
import string
import sys
import itertools
import copy

import yaml
import numpy
import xarray
import scipy.stats
from smt.sampling_methods import LHS

#========================================================================================================== SETTINGS ===
template_delimiter = '@'


class _AtSignTemplate(string.Template):
    """Use the CMake '@' delimiter in a Python 'string.Template' to avoid clashing with bash variable syntax"""
    delimiter = template_delimiter


template_placeholder = f"{template_delimiter}number"
default_output_file_template = _AtSignTemplate(f'parameter_set{template_placeholder}')
parameter_study_meta_file = "parameter_study_meta.txt"


# ========================================================================================== PARAMETER STUDY CLASSES ===
class _ParameterGenerator(ABC):
    """Abstract base class for internal parameter study generators

    :param dict parameter_schema: The YAML loaded parameter study schema dictionary, e.g.
        ``{parameter_name: schema_value}``.  Validated on class instantiation.
    :param str output_file_template: Output file name template. Required if parameter sets will be written to files
        instead of printed to STDOUT. May contain pathseps for an absolute or relative path template. May contain the
        ``@number`` set number placeholder in the file basename but not in the path. If the placeholder is not found it
        will be appended to the template string.
    :param str output_file: Output file name for a single file output of the parameter study. May contain pathseps for
        an absolute or relative path. ``output_file`` and ``output_file_template`` are mutually exclusive. Output file
        is always overwritten.
    :param str output_file_type: Output file syntax or type. Options are: 'yaml', 'h5'.
    :param bool overwrite: Overwrite existing output files
    :param bool dryrun: Print contents of new parameter study output files to STDOUT and exit
    :param bool debug: Print internal variables to STDOUT and exit
    :param bool write_meta: Write a meta file named "parameter_study_meta.txt" containing the parameter set file names.
        Useful for command line execution with build systems that require an explicit file list for target creation.
    """
    def __init__(self, parameter_schema, output_file_template=None, output_file=None, output_file_type='yaml',
                 set_name_template=None, overwrite=False, dryrun=False, debug=False, write_meta=False):
        self.parameter_schema = parameter_schema
        self.output_file_template = output_file_template
        self.output_file = output_file
        self.output_file_type = output_file_type
        self.set_name_template = set_name_template
        self.overwrite = overwrite
        self.dryrun = dryrun
        self.debug = debug
        self.write_meta = write_meta

        # TODO: redesign the interface to make it possible to specify a parameter set name template and either the
        # output file template or a single output file name.
        if self.output_file_template is not None and self.output_file is not None:
            raise RuntimeError("The options 'output_file_template' and 'output_file' are mutually exclusive. " \
                               "Please specify one or the other.")

        if self.output_file:
            self.output_file = pathlib.Path(output_file)

        # Configurat set name template, which doubles as the output name template.
        self.provided_output_file_template = False
        if self.output_file_template:
            if not f'{template_placeholder}' in self.output_file_template:
                self.output_file_template = f"{self.output_file_template}{template_placeholder}"
            self.output_file_template = _AtSignTemplate(self.output_file_template)
            self.provided_output_file_template = True
        else:
            self.output_file_template = default_output_file_template

        # Infer output directory from output file template
        self.output_directory = pathlib.Path(self.output_file_template.safe_substitute()).parent
        self.parameter_study_meta_file = self.output_directory / parameter_study_meta_file

        self.validate()

    @abstractmethod
    def validate(self):
        """Process parameter study input to verify schema

        Must set the class attributes:

        * ``self.parameter_names``: list of strings containing the parameter study's parameter names

        Minimum necessary work example:

        .. code-block::

           self.parameter_names = list(self.parameter_schema.keys())
        """
        pass

    @abstractmethod
    def generate(self):
        """Generate the parameter study definition

        Must set the class attributes:

        * ``self.parameter_set_names``: list of parameter set name strings created by calling
          ``self._create_parameter_set_names`` with the number of integer parameter sets.
        * ``self.samples``: The parameter study samples. A 2D numpy array in the shape (number of parameter sets, number
          of parameters). If it's possible that the samples may be of mixed type, ``numpy.array(..., dtype=object)``
          should be used to preserve the original Python types.
        * ``self.parameter_study``: The Xarray Dataset parameter study object, created by calling
          ``self.parameter_study = self._create_parameter_study()`` after defining ``self.samples`` and the optional
          ``self.quantiles`` class attribute.

        May set the class attributes:

        * ``self.quantiles``: The parameter study sample quantiles, if applicable. A 2D numpy array in the shape (number of parameter sets, number of parameters)

        Minimum necessary work example:

        .. code-block::

           set_count = 5
           self._create_parameter_set_names(set_count)
           parameter_count = len(self.parameter_names)
           self.samples = numpy.zeros((set_count, parameter_count))
           self.parameter_study = self._create_parameter_study()
        """
        pass

    def write(self):
        """Write the parameter study to STDOUT or an output file.

        Writes to STDOUT by default. Requires non-default ``output_file_template`` or ``output_file`` specification to
        write to files.

        If printing to STDOUT, print all parameter sets together. If printing to files, don't overwrite existing files.
        If overwrite is specified, overwrite all parameter set files. If a dry run is requested print file-content
        associations for files that would have been written.

        Writes parameter set files in YAML syntax by default. Output formatting is controlled by
        ``output_file_type``.

        .. code-block::

           parameter_1: 1
           parameter_2: a
        """
        self.output_directory.mkdir(parents=True, exist_ok=True)
        parameter_set_files = [pathlib.Path(parameter_set_name) for parameter_set_name in self.parameter_set_names]
        if self.write_meta and self.provided_output_file_template:
            self._write_meta(parameter_set_files)
        if self.output_file_type == 'h5':
            self._write_dataset(parameter_set_files)
        elif self.output_file_type == 'yaml':
            self._write_yaml(parameter_set_files)
        else:
            raise ValueError(f"Unsupported output file type '{self.output_file_type}'")

    def _write_dataset(self, parameter_set_files):
        if self.output_file:
            if self.dryrun:
                sys.stdout.write(f"{self.output_file.resolve()}\n{self.parameter_study}\n")
            else:
                self.parameter_study.to_netcdf(path=self.output_file, mode='w', format="NETCDF4", engine='h5netcdf')
        else:
            for parameter_set_file in parameter_set_files:
                dataset = self.parameter_study.sel(parameter_sets=str(parameter_set_file))
                # If no output file template is provided, print to stdout
                if not self.provided_output_file_template:
                    sys.stdout.write(f"{parameter_set_file.name}\n{dataset}")
                    sys.stdout.write("\n")
                # If overwrite is specified or if file doesn't exist
                elif self.overwrite or not parameter_set_file.is_file():
                    # If dry run is specified, print the files that would have been written to stdout
                    if self.dryrun:
                        sys.stdout.write(f"{parameter_set_file.resolve()}:\n{dataset}")
                        sys.stdout.write("\n")
                    else:
                        # FIXME: mixed type samples are converted to match the first sample on write to file.
                        # Related to an open Xarray bug report: https://github.com/pydata/xarray/issues/2620
                        # WAVES issue: https://re-git.lanl.gov/aea/python-projects/waves/-/issues/239
                        dataset.to_netcdf(path=parameter_set_file, mode='w', format="NETCDF4", engine='h5netcdf')

    def _write_yaml(self, parameter_set_files):
        text_list = []
        # Construct the output text
        for parameter_set_file in parameter_set_files:
            text = yaml.safe_dump(
                self.parameter_study.sel(data_type='samples',
                                         parameter_sets=str(parameter_set_file)).to_array().to_series().to_dict()
            )
            text_list.append(text)
        # If no output file template is provided, printing to stdout or single file. Prepend set names.
        if not self.provided_output_file_template:
            # If no output file template is provided, printing to stdout or a single file
            # Adjust indentation for syntactically correct YAML.
            prefix = "  "
            # TODO: split up text prefix change for readability
            text_list = ["\n".join([f"{prefix}{item}" for item in text.split('\n')[:-1]])+"\n" for text in text_list]
            text_list = [f"{parameter_set_file.name}:\n{text}" for parameter_set_file, text in zip(parameter_set_files, text_list)]
            output_text = "".join(text_list)
            if self.output_file and not self.dryrun:
                with open(self.output_file, 'w') as outfile:
                    outfile.write(output_text)
            elif self.output_file and self.dryrun:
                sys.stdout.write(f"{self.output_file.resolve()}\n{output_text}")
            else:
                sys.stdout.write(output_text)
        # If output file template is provided, writing to parameter set files
        else:
            for parameter_set_file, text in zip(parameter_set_files, text_list):
                if self.overwrite or not parameter_set_file.is_file():
                    # If dry run is specified, print the files that would have been written to stdout
                    if self.dryrun:
                        sys.stdout.write(f"{parameter_set_file.resolve()}\n{text}")
                    else:
                        with open(parameter_set_file, 'w') as outfile:
                            outfile.write(text)

    def _write_meta(self, parameter_set_files):
        """Write the parameter study meta data file.

        The parameter study meta file is always overwritten. It should *NOT* be used to determine if the parameter study
        target or dependee is out-of-date. Parameter study file paths are written as absolute paths.

        :param list parameter_set_files: List of pathlib.Path parameter set file paths
        """
        # Always overwrite the meta data file to ensure that *all* parameter file names are included.
        with open(self.parameter_study_meta_file, 'w') as meta_file:
            if self.output_file:
                meta_file.write(f"{self.output_file.resolve()}\n")
            else:
                for parameter_set_file in parameter_set_files:
                    meta_file.write(f"{parameter_set_file.resolve()}\n")

    def _create_parameter_set_names(self, set_count):
        """Construct parameter set names from the output file template and number of parameter sets

        Creates the class attribute ``self.parameter_set_names`` required to populate the ``generate()`` method's
        parameter study Xarray dataset object.

        :param int set_count: Integer number of parameter sets
        """
        self.parameter_set_names = []
        for number in range(set_count):
            template = self.output_file_template
            self.parameter_set_names.append(template.substitute({'number': number}))

    def _create_parameter_array(self, data, name):
        """Create the standard structure for a parameter_study array

        requires:

        * ``self.parameter_set_names``: parameter set names used as rows of parameter study
        * ``self.parameter_names``: parameter names used as columns of parameter study

        :param numpy.array data: 2D array of parameter study samples with shape (number of parameter sets, number of
            parameters).
        :param str name: Name of the array. Used as a data variable name when converting to parameter study dataset.
        """
        array = xarray.DataArray(
            data,
            coords=[self.parameter_set_names, self.parameter_names],
            dims=["parameter_sets", "parameters"],
            name=name
        )
        return array

    def _create_parameter_study(self):
        """Create the standard structure for the parameter study dataset

        requires:

        * ``self.parameter_set_names``: parameter set names used as rows of parameter study
        * ``self.parameter_names``: parameter names used as columns of parameter study
        * ``self.samples``: The parameter study samples

        optional:

        * ``self.quantiles``: The quantiles associated with the paramter study sampling distributions

        creates attribute:

        * ``self.parameter_study``
        """
        samples = self._create_parameter_array(self.samples, name="samples")
        if hasattr(self, "quantiles"):
            quantiles = self._create_parameter_array(self.quantiles, name="quantiles")
            self.parameter_study = xarray.concat([quantiles, samples],
                    xarray.DataArray(["quantiles", "samples"], dims="data_type")).to_dataset("parameters")
        else:
            self.parameter_study = samples.to_dataset("parameters").expand_dims(data_type=["samples"])


class CartesianProduct(_ParameterGenerator):
    """Builds a cartesian product parameter study

    :param dict parameter_schema: The YAML loaded parameter study schema dictionary - {parameter_name: schema value}
        CartesianProduct expects "schema value" to be an iterable. For example, when read from a YAML file "schema
        value" will be a Python list.
    :param str output_file_template: Output file name template. Required if parameter sets will be written to files
        instead of printed to STDOUT. May contain pathseps for an absolute or relative path template. May contain the
        ``@number`` set number placeholder in the file basename but not in the path. If the placeholder is not found it
        will be appended to the template string.
    :param str output_file: Output file name for a single file output of the parameter study. May contain pathseps for
        an absolute or relative path. ``output_file`` and ``output_file_template`` are mutually exclusive. Output file
        is always overwritten.
    :param str output_file_type: Output file syntax or type. Options are: 'yaml', 'h5'.
    :param bool overwrite: Overwrite existing output files
    :param bool dryrun: Print contents of new parameter study output files to STDOUT and exit
    :param bool debug: Print internal variables to STDOUT and exit
    :param bool write_meta: Write a meta file named "parameter_study_meta.txt" containing the parameter set file names.
        Useful for command line execution with build systems that require an explicit file list for target creation.

    Example

    .. code-block::

       parameter_schema = {
           'parameter_1': [1, 2],
           'parameter_2': ['a', 'b']
       }
       parameter_generator = waves.parameter_generators.CartesianProduct(parameter_schema)
       parameter_generator.generate()
       print(parameter_generator.parameter_study)
       <xarray.Dataset>
       Dimensions:         (parameter_sets: 4, data_type: 1)
       Coordinates:
         * parameter_sets  (parameter_sets) <U14 'parameter_set0' ... 'parameter_set3'
         * data_type       (data_type) <U7 'samples'
       Data variables:
           parameter_1     (parameter_sets, data_type) object 1 1 2 2
           parameter_2     (parameter_sets, data_type) object 'a' 'b' 'a' 'b'

    Attributes after class instantiation

    * parameter_names: A list of parameter name strings

    Attributes after set generation

    * parameter_set_names: list of parameter set name strings
    * samples: The 2D parameter samples. Rows correspond to parameter set. Columns correspond to parameter names.
    * parameter_study: The final parameter study XArray Dataset object
    """

    def validate(self):
        """Validate the Cartesian Product parameter schema. Executed by class initiation."""
        # TODO: Settle on an input file schema and validation library
        self.parameter_names = list(self.parameter_schema.keys())
        # List, sets, and tuples are the supported PyYAML iterables that will support expected behavior
        for name in self.parameter_names:
            if not isinstance(self.parameter_schema[name], (list, set, tuple)):
                raise TypeError(f"Parameter '{name}' is not one of list, set, or tuple")

    def generate(self):
        """Generate the Cartesian Product parameter sets. Must be called directly to generate the parameter study."""
        self.samples = numpy.array(list(itertools.product(*self.parameter_schema.values())), dtype=object)
        set_count = self.samples.shape[0]
        self._create_parameter_set_names(set_count)
        self._create_parameter_study()

    def write(self):
        super().write()


class LatinHypercube(_ParameterGenerator):
    """Builds a Latin Hypercube parameter study

    The 'h5' output file type is the only output type that contains both the parameter samples *and* quantiles.

    :param dict parameter_schema: The YAML loaded parameter study schema dictionary - {parameter_name: schema value}
        LatinHypercube expects "schema value" to be a dictionary with a strict structure and several required keys.
        Validated on class instantiation.
    :param str output_file_template: Output file name template. Required if parameter sets will be written to files
        instead of printed to STDOUT. May contain pathseps for an absolute or relative path template. May contain the
        ``@number`` set number placeholder in the file basename but not in the path. If the placeholder is not found it
        will be appended to the template string.
    :param str output_file: Output file name for a single file output of the parameter study. May contain pathseps for
        an absolute or relative path. ``output_file`` and ``output_file_template`` are mutually exclusive. Output file
        is always overwritten.
    :param str output_file_type: Output file syntax or type. Options are: 'yaml', 'h5'.
    :param bool overwrite: Overwrite existing output files
    :param bool dryrun: Print contents of new parameter study output files to STDOUT and exit
    :param bool debug: Print internal variables to STDOUT and exit
    :param bool write_meta: Write a meta file named "parameter_study_meta.txt" containing the parameter set file names.
        Useful for command line execution with build systems that require an explicit file list for target creation.

    Example

    .. code-block::

       parameter_schema = {
           'num_simulations': 4,  # Required key. Value must be an integer.
           'parameter_1': {
               'distribution': 'norm',  # Required key. Value must be a valid scipy.stats
               'loc': 50,               # distribution name.
               'scale': 1
           },
           'parameter_2': {
               'distribution': 'skewnorm',
               'a': 4,
               'loc': 30,
               'scale': 2
           }
       }
       parameter_generator = waves.parameter_generators.LatinHypercube(parameter_schema)
       parameter_generator.generate()
       print(parameter_generator.parameter_study)
       <xarray.Dataset>
       Dimensions:         (parameter_sets: 4, data_type: 2)
       Coordinates:
         * parameter_sets  (parameter_sets) <U14 'parameter_set0' ... 'parameter_set3'
         * data_type       (data_type) <U9 'samples' 'quantiles'
       Data variables:
           parameter_1     (parameter_sets, data_type) float64 48.85 0.125 ... 0.375
           parameter_2     (parameter_sets, data_type) float64 30.97 0.375 ... 0.625

    Attributes after class instantiation

    * parameter_names: A list of parameter name strings
    * parameter_distributions: A dictionary mapping parameter names to the ``scipy.stats`` distribution

    Attributes after set generation

    * parameter_set_names: list of parameter set name strings
    * samples: The 2D parameter samples. Rows correspond to parameter set. Columns correspond to parameter names.
    * quantiles: The 2D parameter quantiles. Rows correspond to parameter set. Columns correspond to parameter names.
    * parameter_study: The final parameter study XArray Dataset object
    """

    def validate(self):
        """Validate the Latin Hypercube parameter schema. Executed by class initiation."""
        # TODO: Settle on an input file schema and validation library
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
        self.parameter_distributions = self._generate_parameter_distributions()

    def generate(self):
        """Generate the Latin Hypercube parameter sets. Must be called directly to generate the parameter study."""
        set_count = self.parameter_schema['num_simulations']
        parameter_count = len(self.parameter_names)
        self._create_parameter_set_names(set_count)
        self.quantiles = LHS(xlimits=numpy.repeat([[0, 1]], parameter_count, axis=0))(set_count)
        self.samples = numpy.zeros((set_count, parameter_count))
        for i, distribution in enumerate(self.parameter_distributions.values()):
            self.samples[:, i] = distribution.ppf(self.quantiles[:, i])
        self._create_parameter_study()

    def _generate_parameter_distributions(self):
        """Return dictionary containing the {parameter name: scipy.stats distribution} defined by the parameter schema.

        :return: parameter_distributions
        :rtype: dict
        """
        parameter_dictionary = copy.deepcopy({key: self.parameter_schema[key] for key in self.parameter_names})
        parameter_distributions = {}
        for parameter, attributes in parameter_dictionary.items():
            distribution_name = attributes.pop('distribution')
            parameter_distributions[parameter] = getattr(scipy.stats, distribution_name)(**attributes)
        return parameter_distributions

    def write(self):
        super().write()

    def _create_parameter_names(self):
        """Construct the Latin Hypercube parameter names"""
        self.parameter_names = [key for key in self.parameter_schema.keys() if key != 'num_simulations']


class CustomStudy(_ParameterGenerator):
    """Builds a custom parameter study from user-specified values

    An Xarray Dataset is used to store the parameter study. 

    :param array parameter_schema: Dictionary with two keys: ``parameter_samples`` and ``parameter_names``.
        Parameter samples in the form of a 2D array with shape M x N, where M is the number of parameter sets and N is
        the number of parameters. Parameter names in the form of a 1D array with length N. When creating a
        `parameter_samples` array with mixed type (e.g. string and floats) use `dtype=object` to preserve the mixed
        types and avoid casting all values to a common type (e.g. all your floats will become strings).
    :param str output_file_template: Output file name template. Required if parameter sets will be written to files
        instead of printed to STDOUT. May contain pathseps for an absolute or relative path template. May contain the
        ``@number`` set number placeholder in the file basename but not in the path. If the placeholder is not found it
        will be appended to the template string.
    :param str output_file: Output file name for a single file output of the parameter study. May contain pathseps for
        an absolute or relative path. ``output_file`` and ``output_file_template`` are mutually exclusive. Output file
        is always overwritten.
    :param str output_file_type: Output file syntax or type. Options are: 'yaml', 'h5'.
    :param bool overwrite: Overwrite existing output files
    :param bool dryrun: Print contents of new parameter study output files to STDOUT and exit
    :param bool debug: Print internal variables to STDOUT and exit
    :param bool write_meta: Write a meta file named "parameter_study_meta.txt" containing the parameter set file names.
        Useful for command line execution with build systems that require an explicit file list for target creation.

    Example

    .. code-block::

       parameter_schema = dict(
               parameter_samples = numpy.array([[1.0, 'a', 5], [2.0, 'b', 6]], dtype=object),
               parameter_names = numpy.array(['height', 'prefix', 'index']))
       parameter_generator = waves.parameter_generators.CustomStudy(parameter_schema)
       parameter_generator.generate()
       print(parameter_generator.parameter_study)
       <xarray.Dataset>
       Dimensions:         (data_type: 1, parameter_sets: 2)
       Coordinates:
         * data_type       (data_type) object 'samples'
         * parameter_sets  (parameter_sets) <U14 'parameter_set0' 'parameter_set1'
       Data variables:
           height          (data_type, parameter_sets) object 1.0 2.0
           prefix          (data_type, parameter_sets) object 'a' 'b'
           index           (data_type, parameter_sets) object 5 6

    Attributes after class instantiation

    * parameter_names: A list of parameter name strings

    Attributes after set generation

    * parameter_set_names: list of parameter set name strings
    * samples: The 2D parameter values. Rows correspond to parameter set. Columns correspond to parameter names.
    * parameter_study: The final parameter study XArray Dataset object
    """

    def validate(self):
        """Validate the Custom Study parameter samples and names. Executed by class initiation."""
        try:
            self.parameter_names = self.parameter_schema['parameter_names']
        except KeyError:
            raise KeyError('parameter_schema must contain the key: parameter_names')
        if 'parameter_samples' not in self.parameter_schema:
            raise KeyError('parameter_schema must contain the key: parameter_samples')
        if len(self.parameter_names) != self.parameter_schema['parameter_samples'].shape[1]:
            raise ValueError('The parameter samples must be an array of shape M x N, where N is the number of parameters.')
        return

    def generate(self):
        """Generate the parameter study dataset from the user provided parameter array. Must be called directly to
        generate the parameter study."""
        self.samples = numpy.array(self.parameter_schema['parameter_samples'], dtype=object)
        set_count = self.samples.shape[0]
        self._create_parameter_set_names(set_count)
        self._create_parameter_study()
