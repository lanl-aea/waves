import os
import sys
import shutil
import inspect
import tempfile
import argparse

import abaqus
import abaqusConstants
import job


default_model_name = "Model-1"
default_cpus = None


def main(input_file, job_name, model_name=default_model_name, cpus=default_cpus, write_inp=False, **kwargs):
    """Open an Abaqus CAE model file and submit the job.

    If the job already exists, ignore the model name and update the job options. If the job does not exist, create it
    using the job attributes passed in from the API/CLI, e.g. ``cpus`` and ``kwargs``.

    Because Abaqus modifies CAE files on open, a temporary copy of the file is created to avoid constant job rebuilds in
    build tools like SCons or Make.

    See ``mdb.Job`` in the "Abaqus Scripting Reference Guide" for job behavior and keyword arguments.

    :param str input_file: CAE file to open by absolute or relative path. Must include the extension.
    :param str job_name: The name of the Abaqus job
    :param str model_name: The name of the Abaqus model
    :param int cpus: The number of CPUs for the Abaqus solver
    :param bool write_inp: write an Abaqus ``job.inp`` file and exit without submitting the job
    :param kwargs: The ``abaqus.mdb.Job`` keyword arguments. If the job exists, these overwrite existing job
        attributes. If provided, the ``cpus`` argument overrides both existing job attributes _and_ the kwargs.
    """
    if cpus is not None:
        kwargs.update({"numCpus": cpus})

    with AbaqusNamedTemporaryFile(input_file=input_file, suffix=".cae", dir="."):

        if job in abaqus.mdb.jobs.keys():
            script_job = abaqus.mdb.jobs[job]
            script_job.setValues(**kwargs)
            model_name = script_job.model

        if model_name in abaqus.mdb.models.keys():
            script_job = abaqus.mdb.Job(name=job_name, model=model_name, **kwargs)
        else:
            raise RuntimeError("Could not find model name '{}' in file '{}'\n".format(model_name, input_file))

        if write_inp:
            script_job.writeInput(consistencyChecking=abaqusConstants.OFF)
        else:
            script_job.submit()
            script_job.waitForCompletion()


def get_parser():
    """Return parser for CLI options

    All options should use the double-hyphen ``--option VALUE`` syntax to avoid clashes with the Abaqus option syntax,
    including flag style arguments ``--flag``. Single hyphen ``-f`` flag syntax often clashes with the Abaqus command
    line options and should be avoided.

    :returns: parser
    :rtype: argparse.ArgumentParser
    """
    filename = inspect.getfile(lambda: None)
    basename = os.path.basename(filename)

    default_json_file = None

    prog = "abaqus cae -noGui {} --".format(basename)
    cli_description = (
        "Open an Abaqus CAE model file and submit the job."
        "If the job already exists, ignore the model name and update the job options. If the job does not exist, "
        "create it using the job attributes passed in from the API/CLI, e.g. ``cpus`` and ``kwargs``. "
        "Because Abaqus modifies CAE files on open, a temporary copy of the file is created to avoid constant job "
        "rebuilds in build tools like SCons or Make."
    )
    parser = argparse.ArgumentParser(description=cli_description, prog=prog)
    parser.add_argument(
        "--input-file",
        type=str,
        required=True,
        help="The Abaqus CAE model file with extension, e.g. ``input_file.cae``",
    )
    parser.add_argument(
        "--job-name",
        type=str,
        required=True,
        help="The name of the Abaqus job",
    )
    parser.add_argument(
        "--model-name",
        type=str,
        default=default_model_name,
        help="The name of the Abaqus model (default %(default)s)",
    )
    parser.add_argument(
        "--cpus",
        type=int,
        default=default_cpus,
        help="The number of cpus for the Abaqus simulation (default %(default)s)",
    )
    parser.add_argument(
        "--json-file",
        type=str,
        default=default_json_file,
        help="A JSON file containing a dictionary of keyword arguments for ``abaqus.mdb.Job`` " "(default %(default)s)",
    )
    parser.add_argument(
        "--write-inp",
        "--write-input",
        action="store_true",
        help="Write an Abaqus ``job.inp`` file and exit without submitting the job " "(default %(default)s)",
    )
    return parser


class AbaqusNamedTemporaryFile:
    """Open an Abaqus CAE ``input_file`` as a temporary file. Close and delete on exit of context manager.

    Provides Windows compatible temporary file handling. Required until Python 3.12 ``delete_on_close=False`` option is
    available in Abaqus Python.

    :param str input_file: The input file to copy before open
    """

    def __init__(self, input_file, *args, **kwargs):
        self.temporary_file = tempfile.NamedTemporaryFile(*args, delete=False, **kwargs)
        shutil.copyfile(input_file, self.temporary_file.name)
        abaqus.openMdb(pathName=self.temporary_file.name)

    def __enter__(self):
        return self.temporary_file

    def __exit__(self, exc_type, exc_val, exc_tb):
        abaqus.mdb.close()
        self.temporary_file.close()
        os.remove(self.temporary_file.name)


def return_json_dictionary(json_file):
    """Open a JSON file and return a dictionary compatible with Abaqus keyword arguments

    If the JSON file is ``None``, return an empty dictionary. Convert unicode strings to str. If a value is found in
    ``abaqusConstants`` convert the value.

    :param str json_file: path to a JSON file

    :returns: Abaqus compatible keyword argument dictionary
    :rtype: dict
    """
    kwargs = {}
    if json_file is not None:
        with open(json_file) as json_open:
            dictionary = json.load(json_open)
        for key, value in dictionary.items():
            if isinstance(key, unicode):
                key = str(key)
            if isinstance(value, unicode):
                value = str(value)
            if hasattr(abaqusConstants, value):
                value = getattr(abaqusConstants, value)
        kwargs[key] = value
    return kwargs


if __name__ == "__main__":
    parser = get_parser()
    try:
        args, unknown = parser.parse_known_args()
    except SystemExit as err:
        sys.exit(err.code)
    possible_typos = [argument for argument in unknown if argument.startswith("--")]
    if len(possible_typos) > 0:
        raise RuntimeError("Found possible typos in CLI option(s) {}".format(possible_typos))

    kwargs = return_json_dictionary(args.json_file)

    sys.exit(
        main(
            input_file=args.input_file,
            job_name=args.job_name,
            model_name=args.model_name,
            cpus=args.cpus,
            write_inp=args.write_inp,
            **kwargs  # fmt: skip
        )
    )
