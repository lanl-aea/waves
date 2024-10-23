"""External API module

Will raise ``RuntimeError`` or a derived class of :class:`waves.exceptions.WAVESError` to allow the CLI implementation
to convert stack-trace/exceptions into STDERR message and non-zero exit codes.
"""
from abc import ABC, abstractmethod
import sys
import copy
import typing
import hashlib
import pathlib
import warnings
import itertools

import yaml
import numpy
import xarray
import scipy.stats
import SALib

from waves import _settings
from waves import _utilities
from waves._settings import _hash_coordinate_key
from waves._settings import _parameter_coordinate_key
from waves._settings import _set_coordinate_key
from waves.exceptions import ChoicesError, MutuallyExclusiveError, SchemaValidationError


_exclude_from_namespace = set(globals().keys())


class ParameterGenerator(ABC):
    """Abstract base class for parameter study generators

    Parameters must be scalar valued integers, floats, strings, or booleans

    :param parameter_schema: The YAML loaded parameter study schema dictionary, e.g.
        ``{parameter_name: schema_value}``.  Validated on class instantiation.
    :param output_file_template: Output file name template for multiple file output of the parameter study. Required if
        parameter sets will be written to files instead of printed to STDOUT. May contain pathseps for an absolute or
        relative path template. May contain the ``@number`` set number placeholder in the file basename but not in the
        path. If the placeholder is not found it will be appended to the template string. Output files are overwritten
        if the content of the file has changed or if ``overwrite`` is True. ``output_file_template`` and ``output_file``
        are mutually exclusive.
    :param output_file: Output file name for single file output of the parameter study. Required if parameter sets will
        be written to a file instead of printed to STDOUT. May contain pathseps for an absolute or relative path.
        Output file is overwritten if the content of the file has changed or if ``overwrite`` is True. ``output_file``
        and ``output_file_template`` are mutually exclusive.
    :param output_file_type: Output file syntax or type. Options are: 'yaml', 'h5'.
    :param set_name_template: Parameter set name template. Overridden by ``output_file_template``, if provided.
    :param previous_parameter_study: A relative or absolute file path to a previously created parameter
        study Xarray Dataset
    :param require_previous_parameter_study: Raise a ``RuntimeError`` if the previous parameter study file is missing.
    :param overwrite: Overwrite existing output files
    :param dry_run: Print contents of new parameter study output files to STDOUT and exit
    :param write_meta: Write a meta file named "parameter_study_meta.txt" containing the parameter set file names.
        Useful for command line execution with build systems that require an explicit file list for target creation.

    :raises waves.exceptions.MutuallyExclusiveError: If the mutually exclusive output file template and output file
        options are both specified
    :raises waves.exceptions.APIError: If an unknown output file type is requested
    :raises RuntimeError: If a previous parameter study file is specified and missing, and
        ``require_previous_parameter_study`` is ``True``
    """
    def __init__(
        self,
        parameter_schema: dict,
        output_file_template: typing.Optional[str] = _settings._default_output_file_template,
        output_file: typing.Optional[str] = _settings._default_output_file,
        output_file_type: _settings._allowable_output_file_typing = _settings._default_output_file_type_api,
        set_name_template: str = _settings._default_set_name_template,
        previous_parameter_study: typing.Optional[str] = _settings._default_previous_parameter_study,
        require_previous_parameter_study: bool = _settings._default_require_previous_parameter_study,
        overwrite: bool = _settings._default_overwrite,
        dry_run: bool = _settings._default_dry_run,
        write_meta: bool = _settings._default_write_meta,
        **kwargs
    ) -> None:
        self.parameter_schema = parameter_schema
        self.output_file_template = output_file_template
        self.output_file = output_file
        self.output_file_type = output_file_type
        self.set_name_template = _utilities._AtSignTemplate(set_name_template)
        self.previous_parameter_study = previous_parameter_study
        self.require_previous_parameter_study = require_previous_parameter_study
        self.overwrite = overwrite
        self.dry_run = dry_run
        self.write_meta = write_meta

        if self.output_file_template is not None and self.output_file is not None:
            raise MutuallyExclusiveError(
                "The options 'output_file_template' and 'output_file' are mutually exclusive. " \
                "Please specify one or the other."
            )

        if self.output_file_type not in _settings._allowable_output_file_types:
            raise ChoicesError(
                f"Unsupported 'output_file_type': '{self.output_file_type}. " \
                f"The 'output_file_type' must be one of {_settings._allowable_output_file_types}"
            )

        if self.output_file:
            self.output_file = pathlib.Path(self.output_file)

        if self.previous_parameter_study:
            self.previous_parameter_study = pathlib.Path(self.previous_parameter_study)
            if not self.previous_parameter_study.is_file():
                message = f"Previous parameter study file '{self.previous_parameter_study}' does not exist."
                if self.require_previous_parameter_study:
                    raise RuntimeError(message)
                else:
                    warnings.warn(message)

        # Override set name template if output name template is provided.
        self.provided_output_file_template = False
        if self.output_file_template:
            self.provided_output_file_template = True
            # Append the set number placeholder if missing
            if f'{_settings._template_placeholder}' not in self.output_file_template:
                self.output_file_template = f"{self.output_file_template}{_settings._template_placeholder}"
            self.output_file_template = _utilities._AtSignTemplate(self.output_file_template)
            self.set_name_template = self.output_file_template

        # Infer output directory from output file template if provided. Set to PWD otherwise.
        if self.output_file_template:
            self.output_directory = pathlib.Path(self.output_file_template.safe_substitute()).parent
        else:
            self.output_directory = pathlib.Path('.').resolve()
        self.parameter_study_meta_file = self.output_directory / _settings._parameter_study_meta_file

        self._validate()
        self._generate(**kwargs)

    @abstractmethod
    def _validate(self) -> None:
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
    def _generate(self, **kwargs) -> None:
        """Generate the parameter study definition

        All implemented class method should accept kwargs as ``_generate(self, **kwargs)``. The ABC class accepts, but
        does not use any ``kwargs``.

        Must set the class attributes:

        * ``self._samples``: The parameter study samples. A 2D numpy array in the shape (number of parameter sets,
            number of parameters). If it's possible that the samples may be of mixed type,
            ``numpy.array(..., dtype=object)`` should be used to preserve the original Python types.
        * ``self._parameter_set_hashes``: list of parameter set content hashes created by calling
          ``self._create_parameter_set_hashes`` after populating the ``self._samples`` parameter study values.
        * ``self._parameter_set_names``: Dictionary mapping parameter set hash to parameter set name strings created by
            calling ``self._create_parameter_set_names`` after populating ``self._parameter_set_hashes``.
        * ``self.parameter_study``: The Xarray Dataset parameter study object, created by calling
          ``self._create_parameter_study()`` after defining ``self._samples``.

        Minimum necessary work example:

        .. code-block::

           # Work unique to the parameter generator schema and set generation
           set_count = 5  # Normally set according to the parameter schema
           parameter_count = len(self._parameter_names)
           self._samples = numpy.zeros((set_count, parameter_count))

           # Work performed by common ABC methods
           super()._generate()
        """
        self._create_parameter_set_hashes()
        self._create_parameter_set_names()
        self._create_parameter_study()
        if self.previous_parameter_study is not None and self.previous_parameter_study.is_file():
            self._merge_parameter_studies()

    def write(
        self,
        output_file_type: typing.Union[_settings._allowable_output_file_typing, None] = None
    ) -> None:
        """Write the parameter study to STDOUT or an output file.

        Writes to STDOUT by default. Requires non-default ``output_file_template`` or ``output_file`` specification to
        write to files.

        If printing to STDOUT, print all parameter sets together. If printing to files, overwrite when contents of
        existing files have changed. If overwrite is specified, overwrite all parameter set files.
        If a dry run is requested print file-content associations for files that would have been written.

        Writes parameter set files in YAML syntax by default. Output formatting is controlled by
        ``output_file_type``.

        .. code-block::

           parameter_1: 1
           parameter_2: a

        :param output_file_type: Output file syntax or type. Options are: 'yaml', 'h5'.

        :raises waves.exceptions.ChoicesError: If an unsupported output file type is requested
        """
        if output_file_type is None:
            output_file_type = self.output_file_type

        self.output_directory.mkdir(parents=True, exist_ok=True)
        if self.write_meta and self.provided_output_file_template:
            self._write_meta()
        if output_file_type == "h5":
            self._write_dataset()
        elif output_file_type == "yaml":
            self._write_yaml()
        else:
            raise ChoicesError(f"Unsupported 'output_file_type': '{self.output_file_type}. " \
                               f"The 'output_file_type' must be one of {_settings._allowable_output_file_types}")

    def scons_write(self, target: list, source: list, env) -> None:
        """`SCons Python build function`_ wrapper for the parameter generator's write() function.

        Reference: https://scons.org/doc/production/HTML/scons-user/ch17s04.html

        :param target: The target file list of strings
        :param source: The source file list of SCons.Node.FS.File objects
        :param SCons.Script.SConscript.SConsEnvironment env: The builder's SCons construction environment object
        """
        self.write()

    def _write_dataset(self) -> None:
        """Write Xarray Dataset formatted output to STDOUT, separate set files, or a single file

        Behavior as specified in :meth:`waves.parameter_generators.ParameterGenerator.write`
        """
        if self.output_file_type == "h5":
            parameter_study_object = self.parameter_study
            parameter_study_iterator = parameter_study_object.groupby(_set_coordinate_key)
            conditional_write_function = self._conditionally_write_dataset
        # If no output file template is provided, printing to stdout or single file. Prepend set names.
        if not self.provided_output_file_template:
            # If no output file template is provided, printing to stdout or a single file
            output_text = f"{parameter_study_object}\n"
            if self.output_file and not self.dry_run:
                conditional_write_function(self.output_file, parameter_study_object)
            elif self.output_file and self.dry_run:
                sys.stdout.write(f"{self.output_file.resolve()}\n{output_text}")
            else:
                sys.stdout.write(output_text)
        # If output file template is provided, writing to parameter set files
        else:
            for parameter_set_file, parameter_set in parameter_study_iterator:
                parameter_set_path = pathlib.Path(parameter_set_file)
                text = f"{parameter_set}\n"
                if self.overwrite or not parameter_set_path.is_file():
                    # If dry run is specified, print the files that would have been written to stdout
                    if self.dry_run:
                        sys.stdout.write(f"{parameter_set_path.resolve()}\n{text}")
                    else:
                        conditional_write_function(parameter_set_path, parameter_set)

    def _conditionally_write_dataset(self, existing_parameter_study: str, parameter_study: xarray.Dataset) -> None:
        """Write NetCDF file over previous study if the datasets have changed or self.overwrite is True

        :param existing_parameter_study: A relative or absolute file path to a previously created parameter
            study Xarray Dataset
        :param parameter_study: Parameter study xarray dataset
        """
        write = True
        if not self.overwrite and pathlib.Path(existing_parameter_study).is_file():
            with xarray.open_dataset(existing_parameter_study, engine='h5netcdf') as existing_dataset:
                if parameter_study.equals(existing_dataset):
                    write = False
        if write:
            parameter_study.to_netcdf(path=existing_parameter_study, mode='w', format="NETCDF4", engine='h5netcdf')

    def _write_yaml(self) -> None:
        """Write YAML formatted output to STDOUT, separate set files, or a single file

        Behavior as specified in :meth:`waves.parameter_generators.ParameterGenerator.write`
        """
        if self.output_file_type == "yaml":
            parameter_study_object = self.parameter_study_to_dict()
            parameter_study_iterator = parameter_study_object.items()
            conditional_write_function = self._conditionally_write_yaml
        # If no output file template is provided, printing to stdout or single file. Prepend set names.
        if not self.provided_output_file_template:
            # If no output file template is provided, printing to stdout or a single file
            output_text = yaml.safe_dump(parameter_study_object)
            if self.output_file and not self.dry_run:
                conditional_write_function(self.output_file, parameter_study_object)
            elif self.output_file and self.dry_run:
                sys.stdout.write(f"{self.output_file.resolve()}\n{output_text}")
            else:
                sys.stdout.write(output_text)
        # If output file template is provided, writing to parameter set files
        else:
            for parameter_set_file, parameter_set in parameter_study_iterator:
                parameter_set_path = pathlib.Path(parameter_set_file)
                text = yaml.safe_dump(parameter_set)
                if self.overwrite or not parameter_set_path.is_file():
                    # If dry run is specified, print the files that would have been written to stdout
                    if self.dry_run:
                        sys.stdout.write(f"{parameter_set_path.resolve()}\n{text}")
                    else:
                        conditional_write_function(parameter_set_path, parameter_set)

    def _conditionally_write_yaml(
        self,
        output_file: typing.Union[str, pathlib.Path],
        parameter_dictionary: dict
    ) -> None:
        """Write YAML file over previous study if the datasets have changed or self.overwrite is True

        :param output_file: A relative or absolute file path to the output YAML file
        :param parameter_dictionary: dictionary containing parameter set data
        """
        write = True
        if not self.overwrite and pathlib.Path(output_file).is_file():
            with open(output_file, 'r') as existing_file:
                existing_yaml_object = yaml.safe_load(existing_file)
                if existing_yaml_object == parameter_dictionary:
                    write = False
        if write:
            with open(output_file, 'w') as outfile:
                outfile.write(yaml.dump(parameter_dictionary))

    def _write_meta(self) -> None:
        """Write the parameter study meta data file.

        The parameter study meta file is always overwritten. It should *NOT* be used to determine if the parameter study
        target or dependee is out-of-date. Parameter study file paths are written as absolute paths.
        """
        parameter_set_files = [pathlib.Path(set_name) for set_name in
                               self.parameter_study.coords[_set_coordinate_key].values]
        # Always overwrite the meta data file to ensure that *all* parameter file names are included.
        with open(self.parameter_study_meta_file, 'w') as meta_file:
            if self.output_file:
                meta_file.write(f"{self.output_file.resolve()}\n")
            else:
                for parameter_set_file in parameter_set_files:
                    meta_file.write(f"{parameter_set_file.resolve()}\n")

    def _create_parameter_set_hashes(self) -> None:
        """Construct unique, repeatable parameter set content hashes from ``self._samples``.

        Creates an md5 hash from the concatenated string representation of parameter ``name:value`` associations.

        requires:

        * ``self._samples``: The parameter study samples. Rows are sets. Columns are parameters.

        creates attribute:

        * ``self._parameter_set_hashes``: parameter set content hashes identifying rows of parameter study
        """
        self._parameter_set_hashes = []
        for sample_row in self._samples:
            sorted_contents = sorted(zip(self._parameter_names, sample_row))
            set_catenation = "\n".join(f"{name}:{repr(sample)}" for name, sample in sorted_contents)
            set_hash = hashlib.md5(set_catenation.encode('utf-8')).hexdigest()
            self._parameter_set_hashes.append(set_hash)

    def _create_parameter_set_names(self) -> None:
        """Construct parameter set names from the set name template and number of parameter sets in ``self._samples``

        Creates the class attribute ``self._parameter_set_names`` required to populate the ``_generate()`` method's
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

    def _update_parameter_set_names(self) -> None:
        """Update the parameter set names after a parameter study dataset merge operation.

        Resets attributes:

        * ``self.parameter_study``
        * ``self._parameter_set_names``
        """
        self._create_parameter_set_names()
        new_set_names = set(self._parameter_set_names.values()) - \
                        set(self.parameter_study.coords[_set_coordinate_key].values)
        null_set_names = self.parameter_study.coords[_set_coordinate_key].isnull()
        if any(null_set_names):
            self.parameter_study.coords[_set_coordinate_key][null_set_names] = list(new_set_names)
        self._parameter_set_names = self.parameter_study[_set_coordinate_key].to_series().to_dict()

    def _create_parameter_set_names_array(self) -> xarray.DataArray:
        """Create an Xarray DataArray with the parameter set names using parameter set hashes as the coordinate

        :return: parameter_set_names_array
        """
        return xarray.DataArray(list(self._parameter_set_names.values()),
                                coords=[list(self._parameter_set_names.keys())],
                                dims=[_hash_coordinate_key],
                                name=_set_coordinate_key)

    def _merge_parameter_set_names_array(self) -> None:
        """Merge the parameter set names array into the parameter study dataset as a non-index coordinate"""
        parameter_set_names_array = self._create_parameter_set_names_array()
        self.parameter_study = xarray.merge(
            [self.parameter_study.reset_coords(), parameter_set_names_array]).set_coords(_set_coordinate_key)

    def _create_parameter_study(self) -> None:
        """Create the standard structure for the parameter study dataset

        requires:

        * ``self._parameter_set_hashes``: parameter set content hashes identifying rows of parameter study
        * ``self._parameter_names``: parameter names used as columns of parameter study
        * ``self._samples``: The parameter study samples. Rows are sets. Columns are parameters.

        creates attribute:

        * ``self.parameter_study``
        """
        sample_arrays = [
            xarray.DataArray(
                list(values),
                name=name,
                dims=[_hash_coordinate_key],
                coords={_hash_coordinate_key: self._parameter_set_hashes}
            )
            for name, values in zip(self._parameter_names, self._samples.T)
        ]
        self.parameter_study = xarray.merge(sample_arrays)
        self._merge_parameter_set_names_array()
        self.parameter_study = self.parameter_study.swap_dims({_hash_coordinate_key: _set_coordinate_key})

    def _parameter_study_to_numpy(self) -> numpy.ndarray:
        """Return the parameter study data as a 2D numpy array

        :return: data
        """
        data = []
        for set_hash, data_row in self.parameter_study.groupby(_hash_coordinate_key):
            data.append(data_row.squeeze().to_array().to_numpy())
        return numpy.array(data, dtype=object)

    def parameter_study_to_dict(self) -> typing.Dict[str, typing.Dict[str, typing.Any]]:
        """Return parameter study as a dictionary

        Used for iterating on parameter sets in an SCons workflow with parameter substitution dictionaries, e.g.

        .. code-block::

           >>> for set_name, parameters in parameter_generator.parameter_study_to_dict().items():
           ...     print(f"{set_name}: {parameters}")
           ...
           parameter_set0: {'parameter_1': 1, 'parameter_2': 'a'}
           parameter_set1: {'parameter_1': 1, 'parameter_2': 'b'}
           parameter_set2: {'parameter_1': 2, 'parameter_2': 'a'}
           parameter_set3: {'parameter_1': 2, 'parameter_2': 'b'}

        :return: parameter study sets and samples as a dictionary: {set_name: {parameter: value}, ...}
        """
        parameter_study_dictionary = {}
        for set_name, parameter_set in self.parameter_study.groupby(_set_coordinate_key):
            parameter_dict = {key: array.values.item() for key, array in parameter_set.items()}
            parameter_study_dictionary[str(set_name)] = parameter_dict
        return parameter_study_dictionary

    def _merge_parameter_studies(self) -> None:
        """Merge the current parameter study into a previous parameter study.

        Preserve the previous parameter study set name to set contents associations by dropping the current study's set
        names during merge. Resets attributes:

        * ``self.parameter_study``
        * ``self._samples``
        * ``self._parameter_set_hashes``
        * ``self._parameter_set_names``

        :raises RuntimeError: If the ``self.parameter_study`` attribute is None
        """
        if self.previous_parameter_study is None:
            raise RuntimeError("Called without a previous parameter study")

        # Swap dimensions from the set name to the set hash to merge identical sets
        swap_to_hash_index = {_set_coordinate_key: _hash_coordinate_key}
        previous_parameter_study = xarray.open_dataset(self.previous_parameter_study)
        previous_parameter_study = previous_parameter_study.swap_dims(swap_to_hash_index)
        self.parameter_study = self.parameter_study.swap_dims(swap_to_hash_index)

        # Favor the set names of the prior study. Leaves new set names as NaN.
        self.parameter_study = xarray.merge(
            [previous_parameter_study, self.parameter_study.drop_vars(_set_coordinate_key)])
        previous_parameter_study.close()

        # Recover parameter study numpy array(s) to match merged study
        self._samples = self._parameter_study_to_numpy()

        # Recalculate attributes with lengths matching the number of parameter sets
        self._parameter_set_hashes = list(self.parameter_study.coords[_hash_coordinate_key].values)
        self._update_parameter_set_names()
        self.parameter_study = self.parameter_study.swap_dims({_hash_coordinate_key: _set_coordinate_key})


class _ScipyGenerator(ParameterGenerator, ABC):

    def _validate(self) -> None:
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

        :raises waves.exceptions.SchemaValidationError:

            * Parameter schema is not a dictionary
            * Parameter schema ``num_simulations`` key is not an integer
            * Parameter definition distribution value is not a valid Python identifier
            * Parameter definition key(s) is not a valid Python identifier
            * Parameter schema does not have a ``num_simulations`` key
            * Parameter definition does not contain a ``distribution`` key
        """
        if not isinstance(self.parameter_schema, dict):
            raise SchemaValidationError("parameter_schema must be a dictionary")
        # TODO: Settle on an input file schema and validation library
        if 'num_simulations' not in self.parameter_schema.keys():
            raise SchemaValidationError("Parameter schema is missing the required 'num_simulations' key")
        elif not isinstance(self.parameter_schema['num_simulations'], int):
            raise SchemaValidationError("Parameter schema 'num_simulations' must be an integer.")
        self._create_parameter_names()
        for name in self._parameter_names:
            parameter_keys = self.parameter_schema[name].keys()
            parameter_definition = self.parameter_schema[name]
            if 'distribution' not in parameter_keys:
                raise SchemaValidationError(f"Parameter '{name}' does not contain the required 'distribution' key")
            elif not isinstance(parameter_definition['distribution'], str) or \
                 not parameter_definition['distribution'].isidentifier():
                raise SchemaValidationError(f"Parameter '{name}' distribution '{parameter_definition['distribution']}' "
                                             "is not a valid Python identifier")
            else:
                for key in parameter_keys:
                    if not isinstance(key, str) or not key.isidentifier():
                        raise SchemaValidationError(f"Parameter '{name}' keyword argument '{key}' is not a valid "
                                                     "Python identifier")
        # TODO: Raise an execption if the current parameter distributions don't match the previous_parameter_study
        self.parameter_distributions = self._generate_parameter_distributions()

    def _generate(self, **kwargs) -> None:
        set_count = self.parameter_schema['num_simulations']
        parameter_count = len(self._parameter_names)
        override_kwargs = {'d': parameter_count}
        if kwargs:
            kwargs.update(override_kwargs)
        else:
            kwargs = override_kwargs
        sampler = getattr(scipy.stats.qmc, self.sampler_class)(**kwargs)
        self._generate_distribution_samples(sampler, set_count, parameter_count)
        super()._generate()

    def _generate_parameter_distributions(self) -> dict:
        """Return dictionary containing the {parameter name: scipy.stats distribution} defined by the parameter schema.

        :return: parameter_distributions
        """
        parameter_dictionary = copy.deepcopy({key: self.parameter_schema[key] for key in self._parameter_names})
        parameter_distributions = {}
        for parameter, attributes in parameter_dictionary.items():
            distribution_name = attributes.pop('distribution')
            parameter_distributions[parameter] = getattr(scipy.stats, distribution_name)(**attributes)
        return parameter_distributions

    def _generate_distribution_samples(self, sampler, set_count, parameter_count) -> None:
        """Create parameter distribution samples

        Requires attibrutes:

        * ``self.parameter_distributions``: dictionary containing the {parameter name: scipy.stats distribution} defined
          by the parameter schema. Set by
          :meth:`waves.parameter_generators._ScipyGenerator._generate_parameter_distributions`.

        Sets attribute(s):

        * ``self._samples``: The parameter study samples. A 2D numpy array in the shape (number of parameter sets,
            number of parameters).
        """
        self._samples = numpy.zeros((set_count, parameter_count))
        quantiles = sampler.random(set_count)
        for i, distribution in enumerate(self.parameter_distributions.values()):
            self._samples[:, i] = distribution.ppf(quantiles[:, i])

    def _create_parameter_names(self) -> None:
        """Construct the parameter names from a distribution parameter schema"""
        self._parameter_names = [key for key in self.parameter_schema.keys() if key != 'num_simulations']


class CartesianProduct(ParameterGenerator):
    """Builds a cartesian product parameter study

    Parameters must be scalar valued integers, floats, strings, or booleans

    :param parameter_schema: The YAML loaded parameter study schema dictionary - {parameter_name: schema value}
        CartesianProduct expects "schema value" to be an iterable. For example, when read from a YAML file "schema
        value" will be a Python list.
    :param output_file_template: Output file name template for multiple file output of the parameter study. Required if
        parameter sets will be written to files instead of printed to STDOUT. May contain pathseps for an absolute or
        relative path template. May contain the ``@number`` set number placeholder in the file basename but not in the
        path. If the placeholder is not found it will be appended to the template string. Output files are overwritten
        if the content of the file has changed or if ``overwrite`` is True. ``output_file_template`` and ``output_file``
        are mutually exclusive.
    :param output_file: Output file name for single file output of the parameter study. Required if parameter sets will
        be written to a file instead of printed to STDOUT. May contain pathseps for an absolute or relative path.
        Output file is overwritten if the content of the file has changed or if ``overwrite`` is True. ``output_file``
        and ``output_file_template`` are mutually exclusive.
    :param output_file_type: Output file syntax or type. Options are: 'yaml', 'h5'.
    :param set_name_template: Parameter set name template. Overridden by ``output_file_template``, if provided.
    :param previous_parameter_study: A relative or absolute file path to a previously created parameter
        study Xarray Dataset
    :param overwrite: Overwrite existing output files
    :param dry_run: Print contents of new parameter study output files to STDOUT and exit
    :param write_meta: Write a meta file named "parameter_study_meta.txt" containing the parameter set file names.
        Useful for command line execution with build systems that require an explicit file list for target creation.

    :var self.parameter_study: The final parameter study XArray Dataset object

    :raises waves.exceptions.MutuallyExclusiveError: If the mutually exclusive output file template and output file
        options are both specified
    :raises waves.exceptions.APIError: If an unknown output file type is requested
    :raises RuntimeError: If a previous parameter study file is specified and missing, and
        ``require_previous_parameter_study`` is ``True``
    :raises waves.exceptions.SchemaValidationError:

        * Parameter schema is not a dictionary
        * Parameter key is not a supported iterable: set, tuple, list

    Example

    .. code-block::

       >>> import waves
       >>> parameter_schema = {
       ...     'parameter_1': [1, 2],
       ...     'parameter_2': ['a', 'b']
       ... }
       >>> parameter_generator = waves.parameter_generators.CartesianProduct(parameter_schema)
       >>> print(parameter_generator.parameter_study)
       <xarray.Dataset>
       Dimensions:             (parameter_set_hash: 4)
       Coordinates:
           parameter_set_hash  (parameter_set_hash) <U32 'de3cb3eaecb767ff63973820b2...
         * parameter_sets      (parameter_set_hash) <U14 'parameter_set0' ... 'param...
       Data variables:
           parameter_1         (parameter_set_hash) object 1 1 2 2
           parameter_2         (parameter_set_hash) object 'a' 'b' 'a' 'b'
    """

    def _validate(self) -> None:
        """Validate the Cartesian Product parameter schema. Executed by class initiation."""
        if not isinstance(self.parameter_schema, dict):
            raise SchemaValidationError("parameter_schema must be a dictionary")
        # TODO: Settle on an input file schema and validation library
        self._parameter_names = list(self.parameter_schema.keys())
        # List, sets, and tuples are the supported PyYAML iterables that will support expected behavior
        for name in self._parameter_names:
            if not isinstance(self.parameter_schema[name], (list, set, tuple)):
                raise SchemaValidationError(f"Parameter '{name}' is not one of list, set, or tuple")

    def _generate(self, **kwargs) -> None:
        """Generate the Cartesian Product parameter sets."""
        self._samples = numpy.array(list(itertools.product(*self.parameter_schema.values())), dtype=object)
        super()._generate()


class LatinHypercube(_ScipyGenerator):
    """Builds a Latin-Hypercube parameter study from the `scipy Latin Hypercube`_ class

    .. warning::

       The merged parameter study feature does *not* check for consistent parameter distributions. Changing the
       parameter definitions and merging with a previous parameter study will result in incorrect relationships between
       parameter schema and the parameter study samples.

    :param parameter_schema: The YAML loaded parameter study schema dictionary - {parameter_name: schema value}
        LatinHypercube expects "schema value" to be a dictionary with a strict structure and several required keys.
        Validated on class instantiation.
    :param output_file_template: Output file name template for multiple file output of the parameter study. Required if
        parameter sets will be written to files instead of printed to STDOUT. May contain pathseps for an absolute or
        relative path template. May contain the ``@number`` set number placeholder in the file basename but not in the
        path. If the placeholder is not found it will be appended to the template string. Output files are overwritten
        if the content of the file has changed or if ``overwrite`` is True. ``output_file_template`` and ``output_file``
        are mutually exclusive.
    :param output_file: Output file name for single file output of the parameter study. Required if parameter sets will
        be written to a file instead of printed to STDOUT. May contain pathseps for an absolute or relative path.
        Output file is overwritten if the content of the file has changed or if ``overwrite`` is True. ``output_file``
        and ``output_file_template`` are mutually exclusive.
    :param output_file_type: Output file syntax or type. Options are: 'yaml', 'h5'.
    :param set_name_template: Parameter set name template. Overridden by ``output_file_template``, if provided.
    :param previous_parameter_study: A relative or absolute file path to a previously created parameter
        study Xarray Dataset
    :param overwrite: Overwrite existing output files
    :param dry_run: Print contents of new parameter study output files to STDOUT and exit
    :param write_meta: Write a meta file named "parameter_study_meta.txt" containing the parameter set file names.
        Useful for command line execution with build systems that require an explicit file list for target creation.
    :param kwargs: Any additional keyword arguments are passed through to the sampler method

    :var self.parameter_distributions: A dictionary mapping parameter names to the `scipy.stats`_ distribution
    :var self.parameter_study: The final parameter study XArray Dataset object

    :raises waves.exceptions.MutuallyExclusiveError: If the mutually exclusive output file template and output file
        options are both specified
    :raises waves.exceptions.APIError: If an unknown output file type is requested
    :raises RuntimeError: If a previous parameter study file is specified and missing, and
        ``require_previous_parameter_study`` is ``True``

    To produce consistent Latin Hypercubes on repeat instantiations, the ``**kwargs`` must include ``{'seed': <int>}``.
    See the `scipy Latin Hypercube`_ ``scipy.stats.qmc.LatinHypercube`` class documentation for details The ``d``
    keyword argument is internally managed and will be overwritten to match the number of parameters defined in the
    parameter schema.

    Example

    .. code-block::

       >>> import waves
       >>> parameter_schema = {
       ...     'num_simulations': 4,  # Required key. Value must be an integer.
       ...     'parameter_1': {
       ...         'distribution': 'norm',  # Required key. Value must be a valid scipy.stats
       ...         'loc': 50,               # distribution name.
       ...         'scale': 1
       ...     },
       ...     'parameter_2': {
       ...         'distribution': 'skewnorm',
       ...         'a': 4,
       ...         'loc': 30,
       ...         'scale': 2
       ...     }
       ... }
       >>> parameter_generator = waves.parameter_generators.LatinHypercube(parameter_schema)
       >>> print(parameter_generator.parameter_study)
       <xarray.Dataset>
       Dimensions:             (parameter_set_hash: 4)
       Coordinates:
           parameter_set_hash  (parameter_set_hash) <U32 '1e8219dae27faa5388328e225a...
         * parameter_sets      (parameter_set_hash) <U14 'parameter_set0' ... 'param...
       Data variables:
           parameter_1         (parameter_set_hash) float64 0.125 ... 51.15
           parameter_2         (parameter_set_hash) float64 0.625 ... 30.97
    """

    def __init__(self, *args, **kwargs) -> None:
        self.sampler_class = "LatinHypercube"
        super().__init__(*args, **kwargs)

    def _generate(self, **kwargs) -> None:
        """Generate the Latin Hypercube parameter sets"""
        super()._generate(**kwargs)


class CustomStudy(ParameterGenerator):
    """Builds a custom parameter study from user-specified values

    Parameters must be scalar valued integers, floats, strings, or booleans

    :param parameter_schema: Dictionary with two keys: ``parameter_samples`` and ``parameter_names``.
        Parameter samples in the form of a 2D array with shape M x N, where M is the number of parameter sets and N is
        the number of parameters. Parameter names in the form of a 1D array with length N. When creating a
        `parameter_samples` array with mixed type (e.g. string and floats) use `dtype=object` to preserve the mixed
        types and avoid casting all values to a common type (e.g. all your floats will become strings).
    :param output_file_template: Output file name template for multiple file output of the parameter study. Required if
        parameter sets will be written to files instead of printed to STDOUT. May contain pathseps for an absolute or
        relative path template. May contain the ``@number`` set number placeholder in the file basename but not in the
        path. If the placeholder is not found it will be appended to the template string. Output files are overwritten
        if the content of the file has changed or if ``overwrite`` is True. ``output_file_template`` and ``output_file``
        are mutually exclusive.
    :param output_file: Output file name for single file output of the parameter study. Required if parameter sets will
        be written to a file instead of printed to STDOUT. May contain pathseps for an absolute or relative path.
        Output file is overwritten if the content of the file has changed or if ``overwrite`` is True. ``output_file``
        and ``output_file_template`` are mutually exclusive.
    :param output_file_type: Output file syntax or type. Options are: 'yaml', 'h5'.
    :param set_name_template: Parameter set name template. Overridden by ``output_file_template``, if provided.
    :param previous_parameter_study: A relative or absolute file path to a previously created parameter
        study Xarray Dataset
    :param overwrite: Overwrite existing output files
    :param dry_run: Print contents of new parameter study output files to STDOUT and exit
    :param write_meta: Write a meta file named "parameter_study_meta.txt" containing the parameter set file names.
        Useful for command line execution with build systems that require an explicit file list for target creation.

    :var self.parameter_study: The final parameter study XArray Dataset object

    :raises waves.exceptions.MutuallyExclusiveError: If the mutually exclusive output file template and output file
        options are both specified
    :raises waves.exceptions.APIError: If an unknown output file type is requested
    :raises RuntimeError: If a previous parameter study file is specified and missing, and
        ``require_previous_parameter_study`` is ``True``
    :raises waves.exceptions.SchemaValidationError:

        * Parameter schema is not a dictionary
        * Parameter schema does not contain the ``parameter_names`` key
        * Parameter schema does not contain the ``parameter_samples`` key
        * The ``parameter_samples`` value is an improperly shaped array

    Example

    .. code-block::

       >>> import waves
       >>> import numpy
       >>> parameter_schema = dict(
       ...     parameter_samples = numpy.array([[1.0, 'a', 5], [2.0, 'b', 6]], dtype=object),
       ...     parameter_names = numpy.array(['height', 'prefix', 'index']))
       >>> parameter_generator = waves.parameter_generators.CustomStudy(parameter_schema)
       >>> print(parameter_generator.parameter_study)
       <xarray.Dataset>
       Dimensions:             (parameter_set_hash: 2)
       Coordinates:
           parameter_set_hash  (parameter_set_hash) <U32 '50ba1a2716e42f8c4fcc34a90a...
        *  parameter_sets      (parameter_set_hash) <U14 'parameter_set0' 'parameter...
       Data variables:
           height              (parameter_set_hash) object 1.0 2.0
           prefix              (parameter_set_hash) object 'a' 'b'
           index               (parameter_set_hash) object 5 6
    """

    def _validate(self) -> None:
        """Validate the Custom Study parameter samples and names. Executed by class initiation."""
        if not isinstance(self.parameter_schema, dict):
            raise SchemaValidationError("parameter_schema must be a dictionary")
        try:
            self._parameter_names = self.parameter_schema['parameter_names']
        except KeyError:
            raise SchemaValidationError('parameter_schema must contain the key: parameter_names')
        if 'parameter_samples' not in self.parameter_schema:
            raise SchemaValidationError('parameter_schema must contain the key: parameter_samples')
        # Always convert to numpy array for shape check and _generate()
        else:
            self.parameter_schema['parameter_samples'] = numpy.array(self.parameter_schema['parameter_samples'],
                                                                     dtype=object)
        if self.parameter_schema['parameter_samples'].ndim != 2 or \
           len(self._parameter_names) != self.parameter_schema['parameter_samples'].shape[1]:
            raise SchemaValidationError("The parameter samples must be an array of shape MxN, "
                                        "where N is the number of parameters.")
        return

    def _generate(self, **kwargs) -> None:
        """Generate the parameter study dataset from the user provided parameter array."""
        # Converted to numpy array by _validate. Simply assign to correct attribute
        self._samples = self.parameter_schema['parameter_samples']
        super()._generate()


class SobolSequence(_ScipyGenerator):
    """Builds a Sobol sequence parameter study from the `scipy Sobol`_ class ``random`` method.

    .. warning::

       The merged parameter study feature does *not* check for consistent parameter distributions. Changing the
       parameter definitions and merging with a previous parameter study will result in incorrect relationships between
       parameter schema and the parameter study samples.

    :param parameter_schema: The YAML loaded parameter study schema dictionary - {parameter_name: schema value}
        SobolSequence expects "schema value" to be a dictionary with a strict structure and several required keys.
        Validated on class instantiation.
    :param output_file_template: Output file name template for multiple file output of the parameter study. Required if
        parameter sets will be written to files instead of printed to STDOUT. May contain pathseps for an absolute or
        relative path template. May contain the ``@number`` set number placeholder in the file basename but not in the
        path. If the placeholder is not found it will be appended to the template string. Output files are overwritten
        if the content of the file has changed or if ``overwrite`` is True. ``output_file_template`` and ``output_file``
        are mutually exclusive.
    :param output_file: Output file name for single file output of the parameter study. Required if parameter sets will
        be written to a file instead of printed to STDOUT. May contain pathseps for an absolute or relative path.
        Output file is overwritten if the content of the file has changed or if ``overwrite`` is True. ``output_file``
        and ``output_file_template`` are mutually exclusive.
    :param output_file_type: Output file syntax or type. Options are: 'yaml', 'h5'.
    :param set_name_template: Parameter set name template. Overridden by ``output_file_template``, if provided.
    :param previous_parameter_study: A relative or absolute file path to a previously created parameter
        study Xarray Dataset
    :param overwrite: Overwrite existing output files
    :param dry_run: Print contents of new parameter study output files to STDOUT and exit
    :param write_meta: Write a meta file named "parameter_study_meta.txt" containing the parameter set file names.
        Useful for command line execution with build systems that require an explicit file list for target creation.
    :param kwargs: Any additional keyword arguments are passed through to the sampler method

    :raises waves.exceptions.MutuallyExclusiveError: If the mutually exclusive output file template and output file
        options are both specified
    :raises waves.exceptions.APIError: If an unknown output file type is requested
    :raises RuntimeError: If a previous parameter study file is specified and missing, and
        ``require_previous_parameter_study`` is ``True``

    To produce consistent Sobol sequences on repeat instantiations, the ``**kwargs`` must include either
    ``scramble=False`` or ``seed=<int>``. See the `scipy Sobol`_ ``scipy.stats.qmc.Sobol`` class documentation for
    details.  The ``d`` keyword argument is internally managed and will be overwritten to match the number of parameters
    defined in the parameter schema.

    Example

    .. code-block::

       >>> import waves
       >>> parameter_schema = {
       ...     'num_simulations': 4,  # Required key. Value must be an integer.
       ...     'parameter_1': {
       ...         'distribution': 'uniform',  # Required key. Value must be a valid scipy.stats
       ...         'loc': 0,                   # distribution name.
       ...         'scale': 10
       ...     },
       ...     'parameter_2': {
       ...         'distribution': 'uniform',
       ...         'loc': 2,
       ...         'scale': 3
       ...     }
       ... }
       >>> parameter_generator = waves.parameter_generators.SobolSequence(parameter_schema)
       >>> print(parameter_generator.parameter_study)
       <xarray.Dataset>
       Dimensions:             (parameter_sets: 4)
       Coordinates:
           parameter_set_hash  (parameter_sets) <U32 'c1fa74da12c0991379d1df6541c421...
         * parameter_sets      (parameter_sets) <U14 'parameter_set0' ... 'parameter...
       Data variables:
           parameter_1         (parameter_sets) float64 0.0 0.5 ... 7.5 2.5
           parameter_2         (parameter_sets) float64 0.0 0.5 ... 4.25
    """

    def __init__(self, *args, **kwargs) -> None:
        self.sampler_class = "Sobol"
        super().__init__(*args, **kwargs)

    def _generate(self, **kwargs) -> None:
        """Generate the parameter study dataset from the user provided parameter array"""
        super()._generate(**kwargs)


class ScipySampler(_ScipyGenerator):
    """Builds a scipy sampler parameter study from a `scipy.stats.qmc`_ ``sampler_class``

    Samplers must use the ``d`` parameter space dimension keyword argument. The following samplers are tested for
    parameter study shape and merge behavior:

    * Sobol
    * Halton
    * LatinHypercube
    * PoissonDisk

    .. warning::

       The merged parameter study feature does *not* check for consistent parameter distributions. Changing the
       parameter definitions and merging with a previous parameter study will result in incorrect relationships between
       parameter schema and the parameter study samples.

    :param sampler_class: The `scipy.stats.qmc`_ sampler class name. Case sensitive.
    :param parameter_schema: The YAML loaded parameter study schema dictionary - {parameter_name: schema value}
        ScipySampler expects "schema value" to be a dictionary with a strict structure and several required keys.
        Validated on class instantiation.
    :param output_file_template: Output file name template for multiple file output of the parameter study. Required if
        parameter sets will be written to files instead of printed to STDOUT. May contain pathseps for an absolute or
        relative path template. May contain the ``@number`` set number placeholder in the file basename but not in the
        path. If the placeholder is not found it will be appended to the template string. Output files are overwritten
        if the content of the file has changed or if ``overwrite`` is True. ``output_file_template`` and ``output_file``
        are mutually exclusive.
    :param output_file: Output file name for single file output of the parameter study. Required if parameter sets will
        be written to a file instead of printed to STDOUT. May contain pathseps for an absolute or relative path.
        Output file is overwritten if the content of the file has changed or if ``overwrite`` is True. ``output_file``
        and ``output_file_template`` are mutually exclusive.
    :param output_file_type: Output file syntax or type. Options are: 'yaml', 'h5'.
    :param set_name_template: Parameter set name template. Overridden by ``output_file_template``, if provided.
    :param previous_parameter_study: A relative or absolute file path to a previously created parameter
        study Xarray Dataset
    :param overwrite: Overwrite existing output files
    :param dry_run: Print contents of new parameter study output files to STDOUT and exit
    :param write_meta: Write a meta file named "parameter_study_meta.txt" containing the parameter set file names.
        Useful for command line execution with build systems that require an explicit file list for target creation.
    :param kwargs: Any additional keyword arguments are passed through to the sampler method

    :var self.parameter_distributions: A dictionary mapping parameter names to the ``scipy.stats`` distribution
    :var self.parameter_study: The final parameter study XArray Dataset object

    :raises waves.exceptions.MutuallyExclusiveError: If the mutually exclusive output file template and output file
        options are both specified
    :raises waves.exceptions.APIError: If an unknown output file type is requested
    :raises RuntimeError: If a previous parameter study file is specified and missing, and
        ``require_previous_parameter_study`` is ``True``

    Keyword arguments for the ``scipy.stats.qmc`` ``sampler_class``. The ``d`` keyword argument is internally managed
    and will be overwritten to match the number of parameters defined in the parameter schema.

    Example

    .. code-block::

       >>> import waves
       >>> parameter_schema = {
       ...     'num_simulations': 4,  # Required key. Value must be an integer.
       ...     'parameter_1': {
       ...         'distribution': 'norm',  # Required key. Value must be a valid scipy.stats
       ...         'loc': 50,               # distribution name.
       ...         'scale': 1
       ...     },
       ...     'parameter_2': {
       ...         'distribution': 'skewnorm',
       ...         'a': 4,
       ...         'loc': 30,
       ...         'scale': 2
       ...     }
       ... }
       >>> parameter_generator = waves.parameter_generators.ScipySampler("LatinHypercube", parameter_schema)
       >>> print(parameter_generator.parameter_study)
       <xarray.Dataset>
       Dimensions:             (parameter_set_hash: 4)
       Coordinates:
           parameter_set_hash  (parameter_set_hash) <U32 '1e8219dae27faa5388328e225a...
         * parameter_sets      (parameter_set_hash) <U14 'parameter_set0' ... 'param...
       Data variables:
           parameter_1         (parameter_set_hash) float64 0.125 ... 51.15
           parameter_2         (parameter_set_hash) float64 0.625 ... 30.97
    """

    def __init__(self, sampler_class, *args, **kwargs) -> None:
        self.sampler_class = sampler_class
        super().__init__(*args, **kwargs)

    def _generate(self, **kwargs) -> None:
        """Generate the `scipy.stats.qmc`_ ``sampler_class`` parameter sets"""
        super()._generate(**kwargs)


class SALibSampler(ParameterGenerator, ABC):
    """Builds a SALib sampler parameter study from a `SALib.sample`_ ``sampler_class``

    Samplers must use the ``N`` sample count argument. Note that in `SALib.sample`_ ``N`` is *not* always equivalent to
    the number of simulations. The following samplers are tested for parameter study shape and merge behavior:

    * fast_sampler
    * finite_diff
    * latin
    * sobol
    * morris

    .. warning::

       For small numbers of parameters, some SALib generators produce duplicate parameter sets. These duplicate sets are
       removed during parameter study generation. This may cause the SALib analyze method(s) to raise errors related to
       the expected parameter set count.

    .. warning::

       The merged parameter study feature does *not* check for consistent parameter distributions. Changing the
       parameter definitions and merging with a previous parameter study will result in incorrect relationships between
       parameter schema and the parameter study samples.

    :param sampler_class: The `SALib.sample`_ sampler class name. Case sensitive.
    :param parameter_schema: The YAML loaded parameter study schema dictionary - {parameter_name: schema value}
        SALibSampler expects "schema value" to be a dictionary with a strict structure and several required keys.
        Validated on class instantiation.
    :param output_file_template: Output file name template for multiple file output of the parameter study. Required if
        parameter sets will be written to files instead of printed to STDOUT. May contain pathseps for an absolute or
        relative path template. May contain the ``@number`` set number placeholder in the file basename but not in the
        path. If the placeholder is not found it will be appended to the template string. Output files are overwritten
        if the content of the file has changed or if ``overwrite`` is True. ``output_file_template`` and ``output_file``
        are mutually exclusive.
    :param output_file: Output file name for single file output of the parameter study. Required if parameter sets will
        be written to a file instead of printed to STDOUT. May contain pathseps for an absolute or relative path.
        Output file is overwritten if the content of the file has changed or if ``overwrite`` is True. ``output_file``
        and ``output_file_template`` are mutually exclusive.
    :param output_file_type: Output file syntax or type. Options are: 'yaml', 'h5'.
    :param set_name_template: Parameter set name template. Overridden by ``output_file_template``, if provided.
    :param previous_parameter_study: A relative or absolute file path to a previously created parameter
        study Xarray Dataset
    :param overwrite: Overwrite existing output files
    :param dry_run: Print contents of new parameter study output files to STDOUT and exit
    :param write_meta: Write a meta file named "parameter_study_meta.txt" containing the parameter set file names.
        Useful for command line execution with build systems that require an explicit file list for target creation.
    :param kwargs: Any additional keyword arguments are passed through to the sampler method

    :var self.parameter_study: The final parameter study XArray Dataset object

    :raises waves.exceptions.MutuallyExclusiveError: If the mutually exclusive output file template and output file
        options are both specified
    :raises waves.exceptions.APIError: If an unknown output file type is requested
    :raises RuntimeError: If a previous parameter study file is specified and missing, and
        ``require_previous_parameter_study`` is ``True``
    :raises waves.exceptions.SchemaValidationError:

        * If the `SALib sobol`_ or `SALib morris`_ sampler is specified and there are fewer than 2 parameters.
        * ``N`` is not a key of ``parameter_schema``
        * ``problem`` is not a key of ``parameter_schema``
        * ``names`` is not a key of ``parameter_schema['problem']``
        * ``parameter_schema`` is not a dictionary
        * ``parameter_schema['N']`` is not an integer
        * ``parameter_schema['problem']`` is not a dictionary
        * ``parameter_schema['problem']['names']`` is not a YAML compliant iterable (list, set, tuple)

    Keyword arguments for the `SALib.sample`_ ``sampler_class`` ``sample`` method.

    *Example*

    .. code-block::

       >>> import waves
       >>> parameter_schema = {
       ...     "N": 4,  # Required key. Value must be an integer.
       ...     "problem": {  # Required key. See the SALib sampler interface documentation
       ...         "num_vars": 3,
       ...         "names": ["parameter_1", "parameter_2", "parameter_3"],
       ...         "bounds": [[-1, 1], [-2, 2], [-3, 3]]
       ...     }
       ... }
       >>> parameter_generator = waves.parameter_generators.SALibSampler("sobol", parameter_schema)
       >>> print(parameter_generator.parameter_study)
       <xarray.Dataset>
       Dimensions:             (parameter_sets: 32)
       Coordinates:
           parameter_set_hash  (parameter_sets) <U32 'e0cb1990f9d70070eaf5638101dcaf...
         * parameter_sets      (parameter_sets) <U15 'parameter_set0' ... 'parameter...
       Data variables:
           parameter_1         (parameter_sets) float64 -0.2029 ... 0.187
           parameter_2         (parameter_sets) float64 -0.801 ... 0.6682
           parameter_3         (parameter_sets) float64 0.4287 ... -2.871
    """

    def __init__(self, sampler_class, *args, **kwargs) -> None:
        self.sampler_class = sampler_class
        super().__init__(*args, **kwargs)

    def _validate(self) -> None:
        if not isinstance(self.parameter_schema, dict):
            raise SchemaValidationError("parameter_schema must be a dictionary")
        # TODO: Settle on an input file schema and validation library
        if 'N' not in self.parameter_schema.keys():
            raise SchemaValidationError("Parameter schema is missing the required 'N' key")
        elif not isinstance(self.parameter_schema['N'], int):
            raise SchemaValidationError("Parameter schema 'N' must be an integer.")
        # Check the SALib owned "problem" dictionary for necessary WAVES elements
        if "problem" not in self.parameter_schema.keys():
            raise SchemaValidationError("Parameter schema is missing the required 'problem' key")
        elif not isinstance(self.parameter_schema["problem"], dict):
            raise SchemaValidationError("'problem' must be a dictionary")
        if "names" not in self.parameter_schema["problem"].keys():
            raise SchemaValidationError("Parameter schema 'problem' dict is missing the required 'names' key")
        if not isinstance(self.parameter_schema["problem"]["names"], (list, set, tuple)):
            raise SchemaValidationError(f"Parameter 'names' is not one of list, set, or tuple")
        self._create_parameter_names()
        # Sampler specific validation
        self._sampler_validation()

    def _sampler_validation(self) -> None:
        """Call campler specific schema validation check methods

        * sobol requires at least two parameters

        Requires attributes:

        * ``self._sampler_class`` set by class initiation
        * ``self._parameter_names`` set by ``self._create_parameter_names()``

        :raises waves.exceptions.SchemaValidationError: A sobol or morris sampler contains fewer than two parameters
        """
        parameter_count = len(self._parameter_names)
        if self.sampler_class == "sobol" and parameter_count < 2:
            raise SchemaValidationError("The SALib Sobol sampler requires at least two parameters")
        if self.sampler_class == "morris" and parameter_count < 2:
            raise SchemaValidationError("The SALib Morris sampler requires at least two parameters")

    def _sampler_overrides(self, override_kwargs: dict = {}) -> dict:
        """Provide sampler specific kwarg override dictionaries

        * sobol produces duplicate parameter sets for two parameters when ``calc_second_order`` is ``True``. Override
          this kwarg to be ``False`` if there are only two parameters.

        :param override_kwargs: any common kwargs to include in the override dictionary

        :return: override kwarg dictionary
        """
        parameter_count = len(self._parameter_names)
        if self.sampler_class == "sobol" and parameter_count == 2:
            override_kwargs = {**override_kwargs, "calc_second_order": False}
        return override_kwargs

    def _create_parameter_names(self) -> None:
        """Construct the parameter names from a distribution parameter schema"""
        self._parameter_names = self.parameter_schema["problem"]["names"]

    def _generate(self, **kwargs) -> None:
        """Generate the `SALib.sample`_ ``sampler_class`` parameter sets"""
        N = self.parameter_schema['N']
        parameter_count = len(self._parameter_names)
        override_kwargs = self._sampler_overrides({})
        if kwargs:
            kwargs.update(override_kwargs)
        else:
            kwargs = override_kwargs
        __import__("SALib.sample", fromlist=[self.sampler_class])
        sampler = getattr(SALib.sample, self.sampler_class)
        problem = self.parameter_schema["problem"]
        self._samples = sampler.sample(problem, N, **kwargs)
        self._samples = numpy.unique(self._samples, axis=0)
        super()._generate()


_module_objects = set(globals().keys()) - _exclude_from_namespace
__all__ = [name for name in _module_objects if not name.startswith("_")]
