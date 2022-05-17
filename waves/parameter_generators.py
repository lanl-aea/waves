from abc import ABC, abstractmethod
import pathlib
import string
import sys
import itertools

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

    :param dict parameter_schema: The YAML loaded parameter study schema dictionary - {parameter_name: schema value}
    :param str output_file_template: Output file name template
    :param bool overwrite: Overwrite existing output files
    :param bool dryrun: Print contents of new parameter study output files to STDOUT and exit
    :param bool debug: Print internal variables to STDOUT and exit
    """
    def __init__(self, parameter_schema, output_file_template, overwrite, dryrun, debug):
        self.parameter_schema = parameter_schema
        self.output_file_template = output_file_template
        self.overwrite = overwrite
        self.dryrun = dryrun
        self.debug = debug

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

        Must set ``self.parameter_study`` as a dictionary of {parameter_set_file_name: text} where
        ``parameter_set_file_name`` is a pathlib.Path object of the files to write and ``text`` is the file contents of
        parameter names and their values.

        :returns: List of ``parameter_set_file_name``s pathlib.Path objects
        :rtype: list
        """
        pass

    def write(self):
        """Write the parameter study to STDOUT or an output file.

        If printing to STDOUT, print all parameter sets together. If printing to files, don't overwrite existing files.
        If overwrite is specified, overwrite all parameter set files. If a dry run is requested print file-content
        associations for files that would have been written.

        Writes parameter set files in YAML syntax. Alternate syntax options are a WIP.

        .. code-block::

           parameter_1: 1
           parameter_2: a
        """
        self.write_meta()
        for parameter_set_file, text in self.parameter_study.items():
            # If no output file template is provided, print to stdout
            if not self.provided_template:
                sys.stdout.write(f"{parameter_set_file.name}:\n{text}")
            # If overwrite is specified or if file doesn't exist
            elif self.overwrite or not parameter_set_file.is_file():
                # If dry run is specified, print the files that would have been written to stdout
                if self.dryrun:
                    sys.stdout.write(f"{parameter_set_file.absolute()}:\n{text}")
                else:
                    with open(parameter_set_file, 'w') as outfile:
                        outfile.write(text)

    def write_meta(self):
        """Write the parameter study meta data file.

        The parameter study meta file is always overwritten. It should *NOT* be used to determine if the parameter study
        target or dependee is out-of-date.
        """
        # TODO: Don't write meta for STDOUT output stream
        # Always overwrite the meta data file to ensure that *all* parameter file names are included.
        with open(f'{parameter_study_meta_file}', 'w') as meta_file:
            for parameter_set_file in self.parameter_study.keys():
                meta_file.write(f"{parameter_set_file.name}\n")


class CartesianProduct(ParameterGenerator):
    """Builds a cartesian product parameter study

    :param dict parameter_schema: The YAML loaded parameter study schema dictionary - {parameter_name: schema value}
        CartesianProduct expects "schema value" to be an iterable. For example, when read from a YAML file "schema
        value" will be a Python list.
    :param str output_file_template: Output file name template
    :param bool overwrite: Overwrite existing output files
    :param bool dryrun: Print contents of new parameter study output files to STDOUT and exit
    :param bool debug: Print internal variables to STDOUT and exit
    """

    def validate(self):
        # TODO: Settle on an input file schema and validation library
        # https://re-git.lanl.gov/kbrindley/scons-simulation/-/issues/80
        return True

    def generate(self):
        parameter_names = list(self.parameter_schema.keys())
        parameter_sets = list(itertools.product(*self.parameter_schema.values()))
        parameter_set_names = []
        parameter_set_text = []
        # TODO: Separate the parameter study object from the output file syntax
        # https://re-git.lanl.gov/kbrindley/cmake-simulation/-/issues/36
        for number, parameter_set in enumerate(parameter_sets):
            template = self.output_file_template
            parameter_set_names.append(template.substitute({'number': number}))
            text = ''
            for name, value in zip(parameter_names, parameter_set):
                text = f'{text}{name}: {value}\n'
            parameter_set_text.append(text)
        self.parameter_study = {pathlib.Path(set_name): set_text for set_name, set_text in
                                zip(parameter_set_names, parameter_set_text)}

        return list(self.parameter_study.keys())
