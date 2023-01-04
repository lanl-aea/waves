from abc import ABC, abstractmethod
import pathlib
import string
import sys
import itertools
import copy
import hashlib
import numbers

import yaml
import numpy
import xarray
import scipy.stats

from waves._settings import _hash_coordinate_key, _set_coordinate_key, _quantiles_attribute_key

# ========================================================================================================= SETTINGS ===
template_delimiter = '@'


class _AtSignTemplate(string.Template):
    """Use the CMake '@' delimiter in a Python 'string.Template' to avoid clashing with bash variable syntax"""
    delimiter = template_delimiter


template_placeholder = f"{template_delimiter}number"
default_set_name_template = f'parameter_set{template_placeholder}'
parameter_study_meta_file = "parameter_study_meta.txt"
allowable_output_file_types = ('h5', 'yaml')


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
    :param str set_name_template: Parameter set name template. Overridden by ``output_file_template``, if provided.
    :param str previous_parameter_study: A relative or absolute file path to a previously created parameter
        study Xarray Dataset
    :param bool overwrite: Overwrite existing output files
    :param bool dryrun: Print contents of new parameter study output files to STDOUT and exit
    :param bool debug: Print internal variables to STDOUT and exit
    :param bool write_meta: Write a meta file named "parameter_study_meta.txt" containing the parameter set file names.
        Useful for command line execution with build systems that require an explicit file list for target creation.
    """
    def __init__(self, parameter_schema, output_file_template=None, output_file=None, output_file_type='yaml',
                 set_name_template=default_set_name_template, previous_parameter_study=None,
                 overwrite=False, dryrun=False, debug=False, write_meta=False):
        self.parameter_schema = parameter_schema
        self.output_file_template = output_file_template
        self.output_file = output_file
        self.output_file_type = output_file_type
        self.set_name_template = _AtSignTemplate(set_name_template)
        self.previous_parameter_study = previous_parameter_study
        self.overwrite = overwrite
        self.dryrun = dryrun
        self.debug = debug
        self.write_meta = write_meta

        if self.output_file_template is not None and self.output_file is not None:
            raise RuntimeError("The options 'output_file_template' and 'output_file' are mutually exclusive. " \
                               "Please specify one or the other.")

        if self.output_file_type not in allowable_output_file_types:
            raise RuntimeError(f"Unsupported 'output_file_type': '{self.output_file_type}. " \
                               f"The 'output_file_type' must be one of {allowable_output_file_types}")

        if self.output_file:
            self.output_file = pathlib.Path(self.output_file)

        if self.previous_parameter_study:
            self.previous_parameter_study = pathlib.Path(self.previous_parameter_study)

        # Override set name template if output name template is provided.
        self.provided_output_file_template = False
        if self.output_file_template:
            self.provided_output_file_template = True
            # Append the set number placeholder if missing
            if f'{template_placeholder}' not in self.output_file_template:
                self.output_file_template = f"{self.output_file_template}{template_placeholder}"
            self.output_file_template = _AtSignTemplate(self.output_file_template)
            self.set_name_template = self.output_file_template

        # Infer output directory from output file template if provided. Set to PWD otherwise.
        if self.output_file_template:
            self.output_directory = pathlib.Path(self.output_file_template.safe_substitute()).parent
        else:
            self.output_directory = pathlib.Path('.').resolve()
        self.parameter_study_meta_file = self.output_directory / parameter_study_meta_file

        self._validate()

    @abstractmethod
    def _validate(self):
        """Process parameter study input to verify schema

        Must set the class attributes:

        * ``self._parameter_names``: list of strings containing the parameter study's parameter names

        Minimum necessary work example:

        .. code-block::

           # Work unique to the parameter generator schema. Example matches CartesianProduct schema.
           self._parameter_names = list(self.parameter_schema.keys())
        """
        pass

    @abstractmethod
    def generate(self):
        """Generate the parameter study definition

        Must set the class attributes:

        * ``self._samples``: The parameter study samples. A 2D numpy array in the shape (number of parameter sets, number
          of parameters). If it's possible that the samples may be of mixed type, ``numpy.array(..., dtype=object)``
          should be used to preserve the original Python types.
        * ``self._parameter_set_hashes``: list of parameter set content hashes created by calling
          ``self._create_parameter_set_hashes`` after populating the ``self._samples`` parameter study values.
        * ``self._parameter_set_names``: Dictionary mapping parameter set hash to parameter set name strings created by calling
          ``self._create_parameter_set_names`` after populating ``self._parameter_set_hashes``.
        * ``self.parameter_study``: The Xarray Dataset parameter study object, created by calling
          ``self._create_parameter_study()`` after defining ``self._samples`` and the optional ``self._quantiles`` class
          attribute.

        May set the class attributes:

        * ``self._quantiles``: The parameter study sample quantiles, if applicable. A 2D numpy array in the shape (number
          of parameter sets, number of parameters)

        Minimum necessary work example:

        .. code-block::

           # Work unique to the parameter generator schema and set generation
           set_count = 5  # Normally set according to the parameter schema
           parameter_count = len(self._parameter_names)
           self._samples = numpy.zeros((set_count, parameter_count))

           # Work performed by common ABC methods
           super().generate()
        """
        self._create_parameter_set_hashes()
        self._create_parameter_set_names()
        self._create_parameter_study()
        if self.previous_parameter_study:
            self._merge_parameter_studies()

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
        parameter_set_files = [pathlib.Path(set_name) for set_name in
                               self.parameter_study.coords[_set_coordinate_key].values]
        if self.write_meta and self.provided_output_file_template:
            self._write_meta(parameter_set_files)
        if self.output_file_type == 'h5':
            self._write_dataset()
        elif self.output_file_type == 'yaml':
            self._write_yaml(parameter_set_files)
        else:
            raise ValueError(f"Unsupported output file type '{self.output_file_type}'")

    def scons_write(self, target, source, env):
        """`SCons Python build function`_ wrapper for the parameter generator's write() function.

        Reference: https://scons.org/doc/production/HTML/scons-user/ch17s04.html

        :param list target: The target file list of strings
        :param list source: The source file list of SCons.Node.FS.File objects
        :param SCons.Script.SConscript.SConsEnvironment env: The builder's SCons construction environment object
        """
        self.write()

    def _write_dataset(self):
        """Write Xarray Datset formatted output to STDOUT, separate set files, or a single file

        Behavior as specified in :meth:`waves.parameter_generators._ParameterGenerator.write`
        """
        if self.output_file:
            if self.dryrun:
                sys.stdout.write(f"{self.output_file.resolve()}\n{self.parameter_study}\n")
            else:
                self.output_file.parent.mkdir(parents=True, exist_ok=True)
                self.parameter_study.to_netcdf(path=self.output_file, mode='w', format="NETCDF4", engine='h5netcdf')
        else:
            for parameter_set_file, parameter_set in self.parameter_study.groupby(_set_coordinate_key):
                parameter_set_file = pathlib.Path(parameter_set_file)
                # If no output file template is provided, print to stdout
                if not self.provided_output_file_template:
                    sys.stdout.write(f"{parameter_set_file.name}\n{parameter_set}")
                    sys.stdout.write("\n")
                # If overwrite is specified or if file doesn't exist
                elif self.overwrite or not parameter_set_file.is_file():
                    # If dry run is specified, print the files that would have been written to stdout
                    if self.dryrun:
                        sys.stdout.write(f"{parameter_set_file.resolve()}:\n{parameter_set}")
                        sys.stdout.write("\n")
                    else:
                        parameter_set.to_netcdf(path=parameter_set_file, mode='w', format="NETCDF4", engine='h5netcdf')

    def _write_yaml(self, parameter_set_files):
        """Write YAML formatted output to STDOUT, separate set files, or a single file

        Behavior as specified in :meth:`waves.parameter_generators._ParameterGenerator.write`

        :param list parameter_set_files: List of pathlib.Path parameter set file paths
        """
        text_list = []
        # Construct the output text
        for parameter_set_file, parameter_set in self.parameter_study.groupby(_set_coordinate_key):
            text = yaml.safe_dump(
                parameter_set.squeeze().to_array().to_series().to_dict()
            )
            text_list.append(text)
        # If no output file template is provided, printing to stdout or single file. Prepend set names.
        if not self.provided_output_file_template:
            # If no output file template is provided, printing to stdout or a single file
            # Adjust indentation for syntactically correct YAML.
            prefix = "  "
            # TODO: split up text prefix change for readability
            text_list = ["\n".join([f"{prefix}{item}" for item in text.split('\n')[:-1]])+"\n" for text in text_list]
            text_list = [f"{parameter_set_file.name}:\n{text}" for parameter_set_file, text in
                         zip(parameter_set_files, text_list)]
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

    def _create_parameter_set_hashes(self):
        """Construct unique, repeatable parameter set content hashes from ``self._samples``.

        Creates an md5 hash from the concatenated string representation of parameter values.

        requires:

        * ``self._samples``: The parameter study samples. Rows are sets. Columns are parameters.

        creates attribute:

        * ``self._parameter_set_hashes``: parameter set content hashes identifying rows of parameter study
        """
        self._parameter_set_hashes = []
        for row in self._samples:
            set_values_catenation = ''.join(repr(element) for element in row)
            set_hash = hashlib.md5(set_values_catenation.encode('utf-8')).hexdigest()
            self._parameter_set_hashes.append(set_hash)

    def _create_parameter_set_names(self):
        """Construct parameter set names from the set name template and number of parameter sets in ``self._samples``

        Creates the class attribute ``self._parameter_set_names`` required to populate the ``generate()`` method's
        parameter study Xarray dataset object.

        requires:

        * ``self._parameter_set_hashes``: parameter set content hashes identifying rows of parameter study

        creates attribute:

        * ``self._parameter_set_names``: Dictionary mapping parameter set hash to parameter set name
        """
        self._parameter_set_names = {}
        for number, set_hash in enumerate(self._parameter_set_hashes):
            template = self.set_name_template
            self._parameter_set_names[set_hash] = (template.substitute({'number': number}))

    def _update_parameter_set_names(self):
        """Update the parameter set names after a parameter study dataset merge operation.

        Resets attributes:

        * ``self.parameter_study``
        * ``self._parameter_set_names``
        """
        self._create_parameter_set_names()
        new_set_names = set(self._parameter_set_names.values()) - set(self.parameter_study.coords[_set_coordinate_key].values)
        null_set_names = self.parameter_study.coords[_set_coordinate_key].isnull()
        if any(null_set_names):
            self.parameter_study.coords[_set_coordinate_key][null_set_names] = list(new_set_names)
        self._parameter_set_names = self.parameter_study[_set_coordinate_key].squeeze().to_series().to_dict()

    def _create_parameter_set_names_array(self):
        """Create an Xarray DataArray with the parameter set names using parameter set hashes as the coordinate

        :return: parameter_set_names_array
        :rtype: xarray.DataArray
        """
        return xarray.DataArray(list(self._parameter_set_names.values()),
               coords=[list(self._parameter_set_names.keys())],
               dims=[_hash_coordinate_key],
               name=_set_coordinate_key)

    def _merge_parameter_set_names_array(self):
        """Merge the parameter set names array into the parameter study dataset as a non-index coordinate"""
        parameter_set_names_array = self._create_parameter_set_names_array()
        self.parameter_study = xarray.merge(
            [self.parameter_study.reset_coords(), parameter_set_names_array]).set_coords(_set_coordinate_key)

    def _create_parameter_array(self, data, name):
        """Create the standard structure for a parameter_study array

        requires:

        * ``self._parameter_set_hashes``: parameter set content hashes identifying rows of parameter study
        * ``self._parameter_names``: parameter names used as columns of parameter study

        :param numpy.array data: 2D array of parameter study samples with shape (number of parameter sets, number of
            parameters).
        :param str name: Name of the array. Used as a data variable name when converting to parameter study dataset.
        """
        array = xarray.DataArray(
            data,
            coords=[self._parameter_set_hashes, self._parameter_names],
            dims=["parameter_set_hash", "parameters"],
            name=name
        )
        return array

    def _create_parameter_study(self):
        """Create the standard structure for the parameter study dataset

        requires:

        * ``self._parameter_set_hashes``: parameter set content hashes identifying rows of parameter study
        * ``self._parameter_names``: parameter names used as columns of parameter study
        * ``self._samples``: The parameter study samples. Rows are sets. Columns are parameters.

        optional:

        * ``self._quantiles``: The quantiles associated with the paramter study sampling distributions

        creates attribute:

        * ``self.parameter_study``
        """
        samples = self._create_parameter_array(self._samples, name="samples")
        if hasattr(self, _quantiles_attribute_key):
            quantiles = self._create_parameter_array(self._quantiles, name="quantiles")
            self.parameter_study = xarray.concat([quantiles, samples],
                    xarray.DataArray(["quantiles", "samples"], dims="data_type")).to_dataset("parameters")
        else:
            self.parameter_study = samples.to_dataset("parameters").expand_dims(data_type=["samples"])
        self._merge_parameter_set_names_array()
        self.parameter_study = self.parameter_study.swap_dims({_hash_coordinate_key: _set_coordinate_key})

    def _parameter_study_to_numpy(self, data_type):
        """Return the parameter study data as a 2D numpy array

        :param str data_type: The data_type selection to return - samples or quantiles

        :return: data
        :rtype: numpy.array
        """
        data = []
        for set_hash, data_row in self.parameter_study.sel(data_type=data_type).groupby(_hash_coordinate_key):
            data.append(data_row.squeeze().to_array().to_numpy())
        return numpy.array(data, dtype=object)

    def parameter_study_to_dict(self, data_type='samples'):
        """Return parameter study as a dictionary

        Used for iterating on parameter sets in an SCons workflow with parameter substitution dictionaries, e.g.

        .. code-block::

           >>> import waves
           >>> parameter_schema = {'parameter_1': [1, 2], 'parameter_2': ['a', 'b']}
           >>> parameter_generator = waves.parameter_generators.CartesianProduct(parameter_schema)
           >>> parameter_generator.generate()
           >>> for set_name, parameters in parameter_generator.parameter_study_to_dict().items():
           ...     print(f"{set_name}: {parameters}")
           ...
           parameter_set0: {'parameter_1': 1, 'parameter_2': 'a'}
           parameter_set1: {'parameter_1': 1, 'parameter_2': 'b'}
           parameter_set2: {'parameter_1': 2, 'parameter_2': 'a'}
           parameter_set3: {'parameter_1': 2, 'parameter_2': 'b'}

        :param str data_type: The data_type selection to return - samples or quantiles

        :return: parameter study sets and samples as a dictionary: {set_name: {parameter: value}, ...}
        :rtype: dict - {str: {str: value}}
        """
        parameter_study_dictionary = {}
        for set_name, parameters in self.parameter_study.sel(data_type=data_type).groupby(_set_coordinate_key):
            parameter_dict = parameters.squeeze().to_array().to_series().to_dict()
            parameter_study_dictionary[set_name] = parameter_dict
        return parameter_study_dictionary

    def _merge_parameter_studies(self):
        """Merge the current parameter study into a previous parameter study.

        Preserve the previous parameter study set name to set contents associations by dropping the current study's set
        names during merge. Resets attributes:

        * ``self.parameter_study``
        * ``self._samples``
        * ``self._quantiles``: if it exists
        * ``self._parameter_set_hashes``
        * ``self._parameter_set_names``
        """
        # Swap dimensions from the set name to the set hash to merge identical sets
        swap_to_hash_index = {_set_coordinate_key: _hash_coordinate_key}
        previous_parameter_study = xarray.open_dataset(self.previous_parameter_study).astype(object)
        previous_parameter_study = previous_parameter_study.swap_dims(swap_to_hash_index)
        self.parameter_study = self.parameter_study.swap_dims(swap_to_hash_index)

        # Favor the set names of the prior study. Leaves new set names as NaN.
        self.parameter_study = xarray.merge(
            [previous_parameter_study, self.parameter_study.drop_vars(_set_coordinate_key)])
        previous_parameter_study.close()

        # Recover parameter study numpy array(s) to match merged study
        self._samples = self._parameter_study_to_numpy('samples')
        if hasattr(self, _quantiles_attribute_key):
            self._quantiles = self._parameter_study_to_numpy('quantiles')

        # Recalculate attributes with lengths matching the number of parameter sets
        self._parameter_set_hashes = list(self.parameter_study.coords[_hash_coordinate_key].values)
        self._update_parameter_set_names()
        self.parameter_study = self.parameter_study.swap_dims({_hash_coordinate_key: _set_coordinate_key})


class _ScipyGenerator(_ParameterGenerator, ABC):

    def _validate(self):
        """Validate the parameter distribution schema. Executed by class initiation.

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
        """
        if not isinstance(self.parameter_schema, dict):
            raise TypeError("parameter_schema must be a dictionary")
        # TODO: Settle on an input file schema and validation library
        if 'num_simulations' not in self.parameter_schema.keys():
            raise AttributeError("Parameter schema is missing the required 'num_simulations' key")
        elif not isinstance(self.parameter_schema['num_simulations'], int):
            raise TypeError("Parameter schema 'num_simulations' must be an integer.")
        self._create_parameter_names()
        for name in self._parameter_names:
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
        # TODO: Raise an execption if the current parameter distributions don't match the previous_parameter_study
        self.parameter_distributions = self._generate_parameter_distributions()

    def _generate(self, kwargs=None, sampler_class=None):
        set_count = self.parameter_schema['num_simulations']
        parameter_count = len(self._parameter_names)
        override_kwargs = {'d': parameter_count}
        if kwargs:
            kwargs.update(override_kwargs)
        else:
            kwargs = override_kwargs
        sampler = getattr(scipy.stats.qmc, sampler_class)(**kwargs)
        self._quantiles = sampler.random(set_count)
        self._generate_distribution_samples(set_count, parameter_count)
        super().generate()

    def _generate_parameter_distributions(self):
        """Return dictionary containing the {parameter name: scipy.stats distribution} defined by the parameter schema.

        :return: parameter_distributions
        :rtype: dict
        """
        parameter_dictionary = copy.deepcopy({key: self.parameter_schema[key] for key in self._parameter_names})
        parameter_distributions = {}
        for parameter, attributes in parameter_dictionary.items():
            distribution_name = attributes.pop('distribution')
            parameter_distributions[parameter] = getattr(scipy.stats, distribution_name)(**attributes)
        return parameter_distributions

    def _generate_distribution_samples(self, set_count, parameter_count):
        """Convert quantiles to parameter distribution samples

        Requires attibrutes:

        * ``self.parameter_distributions``: dictionary containing the {parameter name: scipy.stats distribution} defined
          by the parameter schema. Set by
          :meth:`waves.parameter_generators._ScipyGenerator._generate_parameter_distributions`.

        Sets attribute(s):

        * ``self._samples``: The parameter study samples. A 2D numpy array in the shape (number of parameter sets, number
          of parameters).
        """
        self._samples = numpy.zeros((set_count, parameter_count))
        for i, distribution in enumerate(self.parameter_distributions.values()):
            self._samples[:, i] = distribution.ppf(self._quantiles[:, i])

    def _create_parameter_names(self):
        """Construct the parameter names from a distribution parameter schema"""
        self._parameter_names = [key for key in self.parameter_schema.keys() if key != 'num_simulations']


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
    :param str set_name_template: Parameter set name template. Overridden by ``output_file_template``, if provided.
    :param str previous_parameter_study: A relative or absolute file path to a previously created parameter
        study Xarray Dataset
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
       Dimensions:             (data_type: 1, parameter_set_hash: 4)
       Coordinates:
         * data_type           (data_type) object 'samples'
           parameter_set_hash  (parameter_set_hash) <U32 'de3cb3eaecb767ff63973820b2...
         * parameter_sets      (parameter_set_hash) <U14 'parameter_set0' ... 'param...
       Data variables:
           parameter_1         (data_type, parameter_set_hash) object 1 1 2 2
           parameter_2         (data_type, parameter_set_hash) object 'a' 'b' 'a' 'b'

    Attributes after set generation

    * parameter_study: The final parameter study XArray Dataset object
    """

    def _validate(self):
        """Validate the Cartesian Product parameter schema. Executed by class initiation."""
        if not isinstance(self.parameter_schema, dict):
            raise TypeError("parameter_schema must be a dictionary")
        # TODO: Settle on an input file schema and validation library
        self._parameter_names = list(self.parameter_schema.keys())
        # List, sets, and tuples are the supported PyYAML iterables that will support expected behavior
        for name in self._parameter_names:
            if not isinstance(self.parameter_schema[name], (list, set, tuple)):
                raise TypeError(f"Parameter '{name}' is not one of list, set, or tuple")

    def generate(self):
        """Generate the Cartesian Product parameter sets. Must be called directly to generate the parameter study."""
        self._samples = numpy.array(list(itertools.product(*self.parameter_schema.values())), dtype=object)
        super().generate()

    def write(self):
        # Get the ABC docstring into each paramter generator API
        super().write()


class LatinHypercube(_ScipyGenerator):
    """Builds a Latin-Hypercube parameter study from the `scipy Latin Hypercube`_ class

    The ``h5`` ``output_file_type`` is the only output type that contains both the parameter samples *and* quantiles.

    .. warning::

       The merged parameter study feature does *not* check for consistent parameter distributions. Changing the
       parameter definitions will result in incorrect relationships between parameters and the parameter study samples
       and quantiles.

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
    :param str set_name_template: Parameter set name template. Overridden by ``output_file_template``, if provided.
    :param str previous_parameter_study: A relative or absolute file path to a previously created parameter
        study Xarray Dataset
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
       Dimensions:             (data_type: 2, parameter_set_hash: 4)
       Coordinates:
           parameter_set_hash  (parameter_set_hash) <U32 '1e8219dae27faa5388328e225a...
         * data_type           (data_type) <U9 'quantiles' 'samples'
         * parameter_sets      (parameter_set_hash) <U14 'parameter_set0' ... 'param...
       Data variables:
           parameter_1         (data_type, parameter_set_hash) float64 0.125 ... 51.15
           parameter_2         (data_type, parameter_set_hash) float64 0.625 ... 30.97

    Attributes after class instantiation

    * parameter_distributions: A dictionary mapping parameter names to the ``scipy.stats`` distribution

    Attributes after set generation

    * parameter_study: The final parameter study XArray Dataset object
    """

    def generate(self, kwargs=None):
        """Generate the Latin Hypercube parameter sets. Must be called directly to generate the parameter study.

        To produce consistent Latin Hypercubes on repeat instantiations, the ``kwargs`` must include
        ``{'seed': <int>}``. See the `scipy Latin Hypercube`_ documentation for details.

        :param dict kwargs: Keyword arguments for the ``scipy.stats.qmc.LatinHypercube`` LatinHypercube class. The
            ``d`` keyword argument is internally managed and will be overwritten to match the number of parameters
            defined in the parameter schema.
        """
        super()._generate(kwargs=kwargs, sampler_class="LatinHypercube")

    def write(self):
        # Get the ABC docstring into each paramter generator API
        super().write()


class CustomStudy(_ParameterGenerator):
    """Builds a custom parameter study from user-specified values

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
    :param str set_name_template: Parameter set name template. Overridden by ``output_file_template``, if provided.
    :param str previous_parameter_study: A relative or absolute file path to a previously created parameter
        study Xarray Dataset
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
       Dimensions:             (data_type: 1, parameter_set_hash: 2)
       Coordinates:
         * data_type           (data_type) object 'samples'
           parameter_set_hash  (parameter_set_hash) <U32 '50ba1a2716e42f8c4fcc34a90a...
        *  parameter_sets      (parameter_set_hash) <U14 'parameter_set0' 'parameter...
       Data variables:
           height              (data_type, parameter_set_hash) object 1.0 2.0
           prefix              (data_type, parameter_set_hash) object 'a' 'b'
           index               (data_type, parameter_set_hash) object 5 6

    Attributes after set generation

    * parameter_study: The final parameter study XArray Dataset object
    """

    def _validate(self):
        """Validate the Custom Study parameter samples and names. Executed by class initiation."""
        if not isinstance(self.parameter_schema, dict):
            raise TypeError("parameter_schema must be a dictionary")
        try:
            self._parameter_names = self.parameter_schema['parameter_names']
        except KeyError:
            raise KeyError('parameter_schema must contain the key: parameter_names')
        if 'parameter_samples' not in self.parameter_schema:
            raise KeyError('parameter_schema must contain the key: parameter_samples')
        # Always convert to numpy array for shape check and generate()
        else:
            self.parameter_schema['parameter_samples'] = numpy.array(self.parameter_schema['parameter_samples'],
                                                                     dtype=object)
        if len(self._parameter_names) != self.parameter_schema['parameter_samples'].shape[1]:
            raise ValueError("The parameter samples must be an array of shape MxN, "
                             "where N is the number of parameters.")
        return

    def generate(self):
        """Generate the parameter study dataset from the user provided parameter array. Must be called directly to
        generate the parameter study."""
        # Converted to numpy array by _validate. Simply assign to correct attribute
        self._samples = self.parameter_schema['parameter_samples']
        super().generate()

    def write(self):
        # Get the ABC docstring into each paramter generator API
        super().write()


class SobolSequence(_ScipyGenerator):
    """Builds a Sobol sequence parameter study from the `scipy Sobol`_ class ``random`` method.

    .. TODO: Remove the warning when the scipy runtime requirement minimum is implemented
    .. https://re-git.lanl.gov/aea/python-projects/waves/-/issues/278

    .. warning::

       WAVES does not currently enforce a minimum version of scipy, but this class requires scipy >=1.7.0. Conda may
       install WAVES even if the minimum version of scipy required by this class can't be met during environment
       dependency resolution. If the minimum scipy version is not met, this class will raise a runtime error.

    The ``h5`` ``output_file_type`` is the only output type that contains both the parameter samples *and* quantiles.

    .. warning::

       The merged parameter study feature does *not* check for consistent parameter distributions. Changing the
       parameter definitions will result in incorrect relationships between parameters and the parameter study samples
       and quantiles.

    :param dict parameter_schema: The YAML loaded parameter study schema dictionary - {parameter_name: schema value}
        SobolSequence expects "schema value" to be a dictionary with a strict structure and several required keys.
        Validated on class instantiation.
    :param str output_file_template: Output file name template. Required if parameter sets will be written to files
        instead of printed to STDOUT. May contain pathseps for an absolute or relative path template. May contain the
        ``@number`` set number placeholder in the file basename but not in the path. If the placeholder is not found it
        will be appended to the template string.
    :param str output_file: Output file name for a single file output of the parameter study. May contain pathseps for
        an absolute or relative path. ``output_file`` and ``output_file_template`` are mutually exclusive. Output file
        is always overwritten.
    :param str output_file_type: Output file syntax or type. Options are: 'yaml', 'h5'.
    :param str set_name_template: Parameter set name template. Overridden by ``output_file_template``, if provided.
    :param str previous_parameter_study: A relative or absolute file path to a previously created parameter
        study Xarray Dataset
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
               'distribution': 'uniform',  # Required key. Value must be a valid scipy.stats
               'loc': 0,                   # distribution name.
               'scale': 10
           },
           'parameter_2': {
               'distribution': 'uniform',
               'loc': 2,
               'scale': 3
           }
       }
       parameter_generator = waves.parameter_generators.SobolSequence(parameter_schema)
       parameter_generator.generate(kwargs={'scramble': False})
       print(parameter_generator.parameter_study)
       <xarray.Dataset>
       Dimensions:             (data_type: 2, parameter_sets: 4)
       Coordinates:
           parameter_set_hash  (parameter_sets) <U32 'c1fa74da12c0991379d1df6541c421...
         * data_type           (data_type) <U9 'quantiles' 'samples'
         * parameter_sets      (parameter_sets) <U14 'parameter_set0' ... 'parameter...
       Data variables:
           parameter_1         (data_type, parameter_sets) float64 0.0 0.5 ... 7.5 2.5
           parameter_2         (data_type, parameter_sets) float64 0.0 0.5 ... 4.25
    """

    def _validate(self):
        """Validate the Sobol sequence parameter schema. Executed by class initiation."""
        # TODO: Add ``scipy>=1.7.0`` runtime requirement to recipe/meta.yaml and remove this conditional when
        # aea-beta supports this minimum version of scipy. May also be possible to remove the setuptools runtime
        # requirement if there are no other uses of pkg_resources in WAVES.
        # https://re-git.lanl.gov/aea/python-projects/waves/-/issues/278
        import pkg_resources
        current_scipy = pkg_resources.parse_version(pkg_resources.get_distribution('scipy').version)
        minimum_scipy = pkg_resources.parse_version('1.7.0')
        if current_scipy < minimum_scipy:
            raise RuntimeError(f"The SobolSequence class requires scipy >={minimum_scipy}. Found {current_scipy}.")
        super()._validate()


    def generate(self, kwargs=None):
        """Generate the parameter study dataset from the user provided parameter array. Must be called directly to
        generate the parameter study.

        To produce consistent Sobol sequences on repeat instantiations, the ``kwargs`` must include either
        ``{'scramble': False}`` or ``{'seed': <int>}``. See the `scipy Sobol`_ documentation for details.

        :param dict kwargs: Keyword arguments for the ``scipy.stats.qmc.Sobol`` Sobol class. The ``d`` keyword
            argument is internally managed and will be overwritten to match the number of parameters defined in the
            parameter schema.
        """
        super()._generate(kwargs=kwargs, sampler_class="Sobol")

    def write(self):
        # Get the ABC docstring into each paramter generator API
        super().write()
