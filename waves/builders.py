#! /usr/bin/env python

import pathlib

import SCons.Defaults
import SCons.Builder
import SCons.Environment
import SCons.Node

# Construct an absolute path to the WAVES project wrappers.
# Can't use pass through from SConstruct when installed as a package.
# TODO: Move project settings to a waves setting file and out of SConstruct
# https://re-git.lanl.gov/kbrindley/scons-simulation/-/issues/64
waves_source_dir = pathlib.Path(__file__).parent.resolve()
abaqus_wrapper_internal_abspath = waves_source_dir / 'bin/abaqus_wrapper'


def _abaqus_journal_emitter(target, source, env):
    """Appends the abaqus_journal builder target list with the builder managed targets

    Appends ``source[0]``.jnl and ``source[0]``.log to the ``target`` list. The abaqus_journal Builder requires that the
    journal file to execute is the first source in the list.

    :return: target, source
    :rtype: tuple with two lists
    """
    journal_file = pathlib.Path(source[0].path).name
    journal_file = pathlib.Path(journal_file)
    target.append(f"{str(journal_file.with_suffix('.jnl'))}")
    target.append(f"{str(journal_file.with_suffix('.log'))}")
    return target, source


def abaqus_journal(abaqus_program='abaqus'):
    """Abaqus journal file SCons builder

    This builder requires that the journal file to execute is the first source in the list. The builder returned by this
    function accepts all SCons Builder arguments and adds the ``journal_options`` and ``abaqus_options`` string
    arguments. The Builder emitter will append the builder managed targets automatically.

    .. code-block::
       :caption: Abaqus journal builder action
       :name: abaqus_journal_action

       abaqus cae -noGui ${SOURCE.abspath} ${abaqus_options} -- ${journal_options} > ${SOURCE.filebase}.log 2>&1

    .. code-block::
       :caption: SConstruct
       :name: abaqus_journal_example

       import waves
       env = Environment()
       env.Append(BUILDERS={'AbaqusJournal': waves.builders.abaqus_journal()})
       AbaqusJournal(target=['my_journal.cae'], source=['my_journal.py'], journal_options='')
    """
    abaqus_journal_builder = SCons.Builder.Builder(
        chdir=1,
        action=f"{abaqus_program} cae -noGui ${{SOURCE.abspath}} ${{abaqus_options}} -- ${{journal_options}} > ${{SOURCE.filebase}}.log 2>&1",
        emitter=_abaqus_journal_emitter)
    return abaqus_journal_builder


def _abaqus_solver_emitter(target, source, env):
    """Appends the abaqus_solver builder target list with the builder managed targets
    """
    if not 'job_name' in env or not env['job_name']:
        raise RuntimeError('Builder is missing required keyword argument "job_name".')
    builder_suffixes = ['log']
    abaqus_simulation_suffixes = ['odb', 'dat', 'msg', 'com', 'prt']
    suffixes = builder_suffixes + abaqus_simulation_suffixes
    for suffix in suffixes:
        target.append(f"{env['job_name']}.{suffix}")
    return target, source


def abaqus_solver(abaqus_program='abaqus', env=SCons.Environment.Environment()):
    """Abaqus solver SCons builder

    This builder requires that the root input file is the first source in the list. The builder returned by this
    functions accepts all SCons Builder arguments and adds the required string argument ``job_name`` and optional string
    argument ``abaqus_options``.  The Builder emitter will append common Abaqus output files as targets automatically
    from the ``job_name``, e.g. ``job_name.odb``, ``job_name.dat``, ``job_name.msg``, etc.

    The target list only appends those extensions which are common to all Abaqus operations. Some extensions may need to
    be added explicitly according to the Abaqus simulation solver, type, or options. If you find that SCons isn't
    automatically cleaning some Abaqus output files, they are not in the automatically appended target list.

    Abaqus is not called directly. Instead the |PROJECT| :ref:`abaqus_wrapper` is executed to help control the Abaqus
    return code and return timing.

    .. code-block::
       :caption: Abaqus journal builder action
       :name: abaqus_solver_action

       abaqus_wrapper ${job_name} abaqus -job ${job_name} -input ${SOURCE} ${abaqus_options}'

    .. code-block::
       :caption: SConstruct
       :name: abaqus_solver_example

       import waves
       env = Environment()
       env.Append(BUILDERS={'AbaqusSolver': waves.builders.abaqus_solver()})
       AbaqusSolver(target=[], source=['input.inp'], job_name='my_job', abaqus_options='-cpus 4')
    """
    conf = env.Configure()
    abaqus_wrapper_program = conf.CheckProg('abaqus_wrapper') 
    if not abaqus_wrapper_program:
        abaqus_wrapper_program = abaqus_wrapper_internal_abspath
        print("Could not find 'abaqus_wrapper' in construction environment. " \
              f"Using WAVES internal path...{abaqus_wrapper_program}")
    conf.Finish()
    abaqus_solver_builder = SCons.Builder.Builder(
        chdir=1,
        action=f"{abaqus_wrapper_program} ${{job_name}} {abaqus_program} -job ${{job_name}} -input ${{SOURCE.filebase}} ${{abaqus_options}}",
        emitter=_abaqus_solver_emitter)
    return abaqus_solver_builder


def copy_substitute(source_list, substitution_dictionary={}, env=SCons.Environment.Environment()):
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
    target_list = SCons.Node.NodeList()
    source_list = [pathlib.Path(source_file) for source_file in source_list]
    for source_file in source_list:
        target_list += env.Command(
                target=source_file.name,
                source=str(source_file),
                action=SCons.Defaults.Copy('${TARGET}', '${SOURCE}'))
        if source_file.suffix == '.in':
            target_list += env.Substfile(source_file.name, SUBST_DICT=substitution_dictionary)
    return target_list
