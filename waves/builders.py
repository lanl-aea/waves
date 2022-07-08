#! /usr/bin/env python

import pathlib

import SCons.Defaults
import SCons.Builder
import SCons.Environment
import SCons.Node

from waves.abaqus import odb_extract
from waves._settings import _abaqus_environment_extension
from waves._settings import _stdout_extension


def _abaqus_journal_emitter(target, source, env):
    """Appends the abaqus_journal builder target list with the builder managed targets

    Appends ``target[0]``.stdout to the ``target`` list. The abaqus_journal Builder requires at least one target.

    The emitter will assume all emitted targets build in the current build directory. If the target(s) must be built in
    a build subdirectory, e.g. in a parameterized target build, then the first target must be provided with the build
    subdirectory, e.g. ``parameter_set1/target.ext``. When in doubt, provide the expected STDOUT redirected file as a
    target, e.g. ``target[0].stdout``.

    :param list target: The target file list of strings
    :param list source: The source file list of SCons.Node.FS.File objects
    :param SCons.Script.SConscript.SConsEnvironment env: The builder's SCons construction environment object

    :return: target, source
    :rtype: tuple with two lists
    """
    first_target = pathlib.Path(str(target[0]))
    try:
        build_subdirectory = first_target.parents[0]
    except IndexError as err:
        build_subdirectory = pathlib.Path('.')
    suffixes = [_stdout_extension, _abaqus_environment_extension]
    for suffix in suffixes:
        emitter_target = build_subdirectory / first_target.with_suffix(suffix).name
        target.append(str(emitter_target))
    return target, source


def abaqus_journal(abaqus_program='abaqus'):
    """Abaqus journal file SCons builder

    This builder requires that the journal file to execute is the first source in the list. The builder returned by this
    function accepts all SCons Builder arguments and adds the ``journal_options`` and ``abaqus_options`` string
    arguments.

    At least one target must be specified. The Builder emitter will append the builder managed targets automatically.
    Appends ``target[0]``.stdout and ``target[0]``.abaqus_v6.env to the ``target`` list.

    The emitter will assume all emitted targets build in the current build directory. If the target(s) must be built in
    a build subdirectory, e.g. in a parameterized target build, then the first target must be provided with the build
    subdirectory, e.g. ``parameter_set1/my_target.ext``. When in doubt, provide the expected STDOUT redirected file as a
    target, e.g. ``my_target.stdout``.

    .. code-block::
       :caption: Abaqus journal builder action
       :name: abaqus_journal_action

       abaqus cae -noGui ${SOURCE.abspath} ${abaqus_options} -- ${journal_options} > ${TARGET.filebase}.stdout 2>&1

    .. code-block::
       :caption: SConstruct
       :name: abaqus_journal_example

       import waves
       env = Environment()
       env.Append(BUILDERS={'AbaqusJournal': waves.builders.abaqus_journal()})
       AbaqusJournal(target=['my_journal.cae'], source=['my_journal.py'], journal_options='')

    :param str abaqus_program: An absolute path or basename string for the abaqus program.
    """
    abaqus_journal_builder = SCons.Builder.Builder(
        action=
            [f"cd ${{TARGET.dir.abspath}} && {abaqus_program} -information environment > " \
                 f"${{TARGET.filebase}}{_abaqus_environment_extension}",
             f"cd ${{TARGET.dir.abspath}} && {abaqus_program} cae -noGui ${{SOURCE.abspath}} ${{abaqus_options}} -- " \
                 f"${{journal_options}} > ${{TARGET.filebase}}{_stdout_extension} 2>&1"],
        emitter=_abaqus_journal_emitter)
    return abaqus_journal_builder


def _abaqus_solver_emitter(target, source, env):
    """Appends the abaqus_solver builder target list with the builder managed targets

    If no targets are provided to the Builder, the emitter will assume all emitted targets build in the current build
    directory. If the target(s) must be built in a build subdirectory, e.g. in a parameterized target build, then at
    least one target must be provided with the build subdirectory, e.g. ``parameter_set1/target.ext``. When in doubt,
    provide the output database as a target, e.g. ``job_name.odb``
    """
    if not 'job_name' in env or not env['job_name']:
        env['job_name'] = pathlib.Path(source[0].path).stem
    builder_suffixes = [_stdout_extension, _abaqus_environment_extension]
    abaqus_simulation_suffixes = ['.odb', '.dat', '.msg', '.com', '.prt']
    suffixes = builder_suffixes + abaqus_simulation_suffixes
    try:
        build_subdirectory = pathlib.Path(str(target[0])).parents[0]
    except IndexError as err:
        build_subdirectory = pathlib.Path('.')
    for suffix in suffixes:
        emitter_target = build_subdirectory / f"{env['job_name']}{suffix}"
        target.append(str(emitter_target))
    return target, source


def abaqus_solver(abaqus_program='abaqus', post_simulation=None):
    """Abaqus solver SCons builder

    This builder requires that the root input file is the first source in the list. The builder returned by this
    function accepts all SCons Builder arguments and adds optional Builder keyword arguments ``job_name`` and
    ``abaqus_options``. If not specified ``job_name`` defaults to the root input file stem. The Builder emitter will
    append common Abaqus output files as targets automatically from the ``job_name``, e.g. ``job_name.odb``.

    This builder is unique in that no targets are required. The Builder emitter will append the builder managed targets
    automatically. The target list only appends those extensions which are common to Abaqus analysis operations. Some
    extensions may need to be added explicitly according to the Abaqus simulation solver, type, or options. If you find
    that SCons isn't automatically cleaning some Abaqus output files, they are not in the automatically appended target
    list.

    The emitter will assume all emitted targets build in the current build directory. If the target(s) must be built in
    a build subdirectory, e.g. in a parameterized target build, then the first target must be provided with the build
    subdirectory, e.g. ``parameter_set1/job_name.odb``. When in doubt, provide the expected STDOUT redirected file as a
    target, e.g. ``my_target.stdout``.

    The ``-interactive`` option is always appended to the builder action to avoid exiting the Abaqus task before the
    simulation is complete.  The ``-ask_delete no`` option is always appended to the builder action to overwrite
    existing files in programmatic execution, where it is assumed that the Abaqus solver target(s) should be re-built
    when their source files change.

    .. code-block::
       :caption: SConstruct
       :name: abaqus_solver_example

       import waves
       env = Environment()
       env.Append(BUILDERS=
           {'AbaqusSolver': waves.builders.abaqus_solver(),
            'AbaqusOld': waves.builders.abaqus_solver(abaqus_program='abq2019'),
            'AbaqusPost': waves.builders.abaqus_solver(post_simulation='grep -E "\<SUCCESSFULLY" ${job_name}.sta')})
       AbaqusSolver(target=[], source=['input.inp'], job_name='my_job', abaqus_options='-cpus 4')

    .. code-block::
       :caption: Abaqus journal builder action
       :name: abaqus_solver_action

       ${abaqus_program} -job ${job_name} -input ${SOURCE.filebase} ${abaqus_options} -interactive -ask_delete no > ${job_name}.stdout 2>&1

    :param str abaqus_program: An absolute path or basename string for the abaqus program
    :param str post_simulation: Shell command string to execute after the simulation command finishes. Intended to allow
        modification of the Abaqus exit code, e.g. return a non-zero (error) exit code when Abaqus reports a simulation
        error or incomplete simulation. Builder keyword variables are available for substitution in the
        ``post_simulation`` action using the ``${}`` syntax.
    """
    action = [f"cd ${{TARGET.dir.abspath}} && {abaqus_program} -information environment > " \
                  f"${{job_name}}{_abaqus_environment_extension}",
              f"cd ${{TARGET.dir.abspath}} && {abaqus_program} -job ${{job_name}} -input ${{SOURCE.filebase}} " \
                  f"${{abaqus_options}} -interactive -ask_delete no > ${{job_name}}{_stdout_extension} 2>&1"]
    if post_simulation:
        action.append(f"cd ${{TARGET.dir.abspath}} && {post_simulation}")
    abaqus_solver_builder = SCons.Builder.Builder(
        action=action,
        emitter=_abaqus_solver_emitter)
    return abaqus_solver_builder


def copy_substitute(source_list, substitution_dictionary={}, env=SCons.Environment.Environment(), build_subdirectory='.'):
    """Copy source list to current variant directory and perform template substitutions on ``*.in`` filenames

    Creates an SCons Copy Builder for each source file. Files are copied to the current variant directory
    matching the calling SConscript parent directory. Files with the name convention ``*.in`` are also given an SCons
    Substfile Builder, which will perform template substitution with the provided dictionary in-place in the current
    variant directory and remove the ``.in`` suffix.

    .. code-block::
       :caption: SConstruct
       :name: copy_substitute_example

       import waves
       env = Environment()
       source_list = [
           'file_one.ext',  # File found in current SConscript directory
           'subdir2/file_two',  # File found below current SConscript directory
           '#/subdir3/file_three.ext',  # File found with respect to project root directory
           'file_four.ext.in'  # File with substitutions matching substitution dictionary keys
       ]
       substitution_dictionary = {
           '@variable_one@': 'value_one'
       }
       waves.builders.copy_substitution(source_list, substitution_dictionary, env)

    :param list source_list: List of pathlike objects or strings. Will be converted to list of pathlib.Path objects.
    :param dict substitution_dictionary: key: value pairs for template substitution. The keys must contain the template
        characters, e.g. @variable@. The template character can be anything that works in the SCons Substfile builder.
    :param SCons.Environment.Environment env: An SCons construction environment to use when defining the targets.

    :return: SCons NodeList of Copy and Substfile objects
    :rtype: SCons.Node.NodeList
    """
    build_subdirectory = pathlib.Path(build_subdirectory)
    target_list = SCons.Node.NodeList()
    source_list = [pathlib.Path(source_file) for source_file in source_list]
    for source_file in source_list:
        copy_target = build_subdirectory / source_file.name
        target_list += env.Command(
                target=str(copy_target),
                source=str(source_file),
                action=SCons.Defaults.Copy('${TARGET}', '${SOURCE}'))
        if source_file.suffix == '.in':
            substfile_target = build_subdirectory / source_file.name
            target_list += env.Substfile(str(substfile_target), SUBST_DICT=substitution_dictionary)
    return target_list


def _python_script_emitter(target, source, env):
    """Appends the python_script builder target list with the builder managed targets

    Appends ``target[0]``.stdout to the ``target`` list. The python_script Builder requires at least one target.

    The emitter will assume all emitted targets build in the current build directory. If the target(s) must be built in
    a build subdirectory, e.g. in a parameterized target build, then the first target must be provided with the build
    subdirectory, e.g. ``parameter_set1/target.ext``. When in doubt, provide the expected STDOUT redirected file as a
    target, e.g. ``target[0].stdout``.

    :param list target: The target file list of strings
    :param list source: The source file list of SCons.Node.FS.File objects
    :param SCons.Script.SConscript.SConsEnvironment env: The builder's SCons construction environment object

    :return: target, source
    :rtype: tuple with two lists
    """
    first_target = pathlib.Path(str(target[0]))
    try:
        build_subdirectory = first_target.parents[0]
    except IndexError as err:
        build_subdirectory = pathlib.Path('.')
    suffixes = [_stdout_extension]
    for suffix in suffixes:
        emitter_target = build_subdirectory / first_target.with_suffix(suffix).name
        target.append(str(emitter_target))
    return target, source

def python_script():
    """Python script SCons builder

    This builder requires that the python script to execute is the first source in the list. The builder returned by
    this function accepts all SCons Builder arguments and adds the ``script_options`` and ``python_options`` string
    arguments.

    At least one target must be specified. The Builder emitter will append the builder managed targets automatically.
    Appends ``target[0]``.stdout to the ``target`` list.

    The emitter will assume all emitted targets build in the current build directory. If the target(s) must be built in
    a build subdirectory, e.g. in a parameterized target build, then the first target must be provided with the build
    subdirectory, e.g. ``parameter_set1/my_target.ext``. When in doubt, provide the expected STDOUT redirected file as a
    target, e.g. ``my_target.stdout``.

    .. code-block::
       :caption: Python script builder action
       :name: python_script_action

       python ${python_options} ${SOURCE.abspath} ${script_options} > ${TARGET.filebase}.stdout 2>&1

    .. code-block::
       :caption: SConstruct
       :name: python_script_example

       import waves
       env = Environment()
       env.Append(BUILDERS={'PythonScript': waves.builders.python_script()})
       PythonScript(target=['my_output.stdout'], source=['my_script.py'], python_options='', script_options='')
    """
    python_builder = SCons.Builder.Builder(
        action=
            [f"cd ${{TARGET.dir.abspath}} && python ${{python_options}} ${{SOURCE.abspath}} " \
                f"${{script_options}} > ${{TARGET.filebase}}{_stdout_extension} 2>&1"],
        emitter=_python_script_emitter)
    return python_builder


def _abaqus_extract_emitter(target, source, env):
    """Prepends the abaqus extract builder target H5 file if none is specified. Always appends the source[0].csv file.
    Always appends the ``target[0]_datasets.h5`` file.

    If no targets are provided to the Builder, the emitter will assume all emitted targets build in the current build
    directory. If the target(s) must be built in a build subdirectory, e.g. in a parameterized target build, then at
    least one target must be provided with the build subdirectory, e.g. ``parameter_set1/target.h5``. When in doubt,
    provide the expected H5 file as a target, e.g. ``source[0].h5``.

    :param list target: The target file list of strings
    :param list source: The source file list of SCons.Node.FS.File objects
    :param SCons.Script.SConscript.SConsEnvironment env: The builder's SCons construction environment object

    :return: target, source
    :rtype: tuple with two lists
    """
    odb_file = pathlib.Path(source[0].path).name
    odb_file = pathlib.Path(odb_file)
    try:
        build_subdirectory = pathlib.Path(str(target[0])).parents[0]
    except IndexError as err:
        build_subdirectory = pathlib.Path('.')
    if not target or pathlib.Path(str(target[0])).suffix != '.h5':
        target.insert(0, str(build_subdirectory / odb_file.with_suffix('.h5')))
    target.append(f"{build_subdirectory / pathlib.Path(str(target[0])).stem}_datasets.h5")
    target.append(str(build_subdirectory / odb_file.with_suffix('.csv')))
    return target, source


def abaqus_extract(abaqus_program='abaqus'):
    """Abaqus ODB file extraction Builder

    This builder executes the ``odb_extract`` command line utility against an ODB file in the source list. The ODB file
    must be the first file in the source list. If there is more than one ODB file in the source list, all but the first
    file are ignored by ``odb_extract``.

    This builder is unique in that no targets are required. The Builder emitter will append the builder managed targets
    and ``odb_extract`` target name constructions automatically.

    The target list may specify an output H5 file name that differs from the ODB file base name as ``new_name.h5``. If
    the first file in the target list does not contain the ``*.h5`` extension, or if there is no file in the target
    list, the target list will be prepended with a name matching the ODB file base name and the ``*.h5`` extension.

    The builder emitter always appends the CSV file created by the ``abaqus odbreport`` command as executed by
    ``odb_extract``.

    .. code-block::
       :caption: SConstruct
       :name: odb_extract_script_example

       import waves
       env = Environment()
       env.Append(BUILDERS={'AbaqusExtract': waves.builders.abaqus_extract()})
       AbaqusExtract(target=['my_job.h5', 'my_job.csv'], source=['my_job.odb'])

    :param str abaqus_program: An absolute path or basename string for the abaqus program
    """
    abaqus_extract_builder = SCons.Builder.Builder(
        action = [
            "cd ${TARGET.dir.abspath} && rm ${SOURCE.filebase}.csv ${TARGET.filebase}.h5 ${TARGET.filebase}_datasets.h5 || true",
            _build_odb_extract
        ],
        emitter=_abaqus_extract_emitter,
        abaqus_program=abaqus_program)
    return abaqus_extract_builder


def _build_odb_extract(target, source, env):
    """Define the odb_extract action when used as an internal package and not a command line utility"""
    odb_extract.odb_extract([source[0].abspath], target[0].abspath, abaqus_command=env['abaqus_program'])
    return None
