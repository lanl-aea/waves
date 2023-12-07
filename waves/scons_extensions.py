#! /usr/bin/env python

import re
import sys
import yaml
import atexit
import pathlib
import functools
import subprocess

import SCons.Defaults
import SCons.Builder
import SCons.Environment
import SCons.Node
import SCons.Scanner

from waves import _utilities
from waves.abaqus import odb_extract
from waves._settings import _abaqus_environment_extension
from waves._settings import _abaqus_datacheck_extensions
from waves._settings import _abaqus_explicit_extensions
from waves._settings import _abaqus_standard_extensions
from waves._settings import _abaqus_solver_common_suffixes
from waves._settings import _scons_substfile_suffix
from waves._settings import _stdout_extension
from waves._settings import _cd_action_prefix
from waves._settings import _redirect_action_postfix
from waves._settings import _redirect_environment_postfix
from waves._settings import _matlab_environment_extension
from waves._settings import _sbatch_wrapper_options
from waves._settings import _sierra_environment_extension


def _print_failed_nodes_stdout():
    # FIXME: The program_operations throw their usual fit when this is a module-wide import
    # ``SCons.Errors.UserError: Calling Configure from Builders is not supported``
    import SCons.Script
    """Query the SCons reported build failures and print the associated node's STDOUT file, if it exists"""
    build_failures = SCons.Script.GetBuildFailures()
    for failure in build_failures:
        stdout_path = pathlib.Path(failure.node.abspath).with_suffix(_stdout_extension).resolve()
        if stdout_path.exists():
            with open(stdout_path, "r") as stdout_file:
                print(f"\n{failure.node} failed with STDOUT file '{stdout_path}'\n", file=sys.stderr)
                print(stdout_file.read(), file=sys.stderr)
        else:
            print(f"\n{failure.node} failed\n", file=sys.stderr)


def print_build_failures(print_stdout=True):
    """On exit, query the SCons reported build failures and print the associated node's STDOUT file, if it exists

    :param bool print_stdout: Boolean to set the exit behavior. If False, don't modify the exit behavior.
    """
    if print_stdout:
        atexit.register(_print_failed_nodes_stdout)


def _string_action_list(builder):
    """Return a builders action list as a list of str

    :param SCons.Builder.Builder builder: The builder to extract the action list from

    :returns: list of actions as str
    :rtype: list
    """
    action = builder.action
    if isinstance(action, SCons.Action.CommandAction):
        action_list = [action.cmd_list]
    else:
        action_list = [command.cmd_list for command in action.list]
    return action_list


def catenate_builder_actions(builder, program="", options=""):
    """Catenate a builder's arguments and prepend the program and options

    .. code-block::

       ${program} ${options} "action one && action two"

    :param SCons.Builder.Builder builder: The SCons builder to modify
    :param str program: wrapping executable
    :param str options: options for the wrapping executable
    """
    action_list = _string_action_list(builder)
    action = " && ".join(action_list)
    action = f"{program} {options} \"{action}\""
    builder.action = SCons.Action.CommandAction(action)
    return builder


def catenate_actions(**outer_kwargs):
    """Decorator factory to apply the ``catenate_builder_actions`` to a function that returns an SCons Builder.

    Accepts the same keyword arguments as the :meth:`waves.scons_extensions.catenate_builder_actions`

    .. code-block::

       import SCons.Builder
       import waves

       @waves.scons_extensions.catenate_actions
       def my_builder():
           return SCons.Builder.Builder(action=["echo $SOURCE > $TARGET", "echo $SOURCE >> $TARGET"])
    """
    def intermediate_decorator(function):
        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            return catenate_builder_actions(function(*args, **kwargs), **outer_kwargs)
        return wrapper
    return intermediate_decorator


def ssh_builder_actions(builder, remote_server="${remote_server}", remote_directory="${remote_directory}"):
    """Wrap a builder's action list with remote copy operations and ssh commands

    By default, the remote server and remote directory strings are written to accept (and *require*) task-by-task
    overrides via task keyword arguments. Any SCons replacement string patterns, ``${variable}``, will make that
    ``variable`` a *required* task keyword argument. Only if the remote server and/or remote directory are known to be
    constant across all possible tasks should those variables be overridden with a string literal containing no
    ``${variable}`` SCons keyword replacement patterns.

    .. include:: ssh_builder_actions_warning.txt

    Design assumptions

    * Creates the ``remote_directory`` with ``mkdir -p``. ``mkdir`` must exist on the ``remote_server``.
    * Copies all source files to a flat ``remote_directory`` with ``rsync -rlptv``. ``rsync`` must exist on the local
      system.
    * Replaces instances of ``cd ${TARGET.dir.abspath} &&`` with ``cd ${remote_directory} &&`` in the original builder
      actions.
    * Replaces instances of ``SOURCE.abspath`` or ``SOURCES.abspath`` with ``SOURCE[S].file`` in the original builder
      actions.
    * Prefixes all original builder actions with ``cd ${remote_directory} &&``.
    * All original builder actions are wrapped in single quotes as ``'{original action}'`` to preserve the ``&&`` as
      part of the ``remote_server`` command. Shell variables, e.g. ``$USER``, will not be expanded on the
      ``remote_server``. If quotes are included in the original builder actions, they should be double quotes.
    * Returns the entire ``remote_directory`` to the original builder ``${TARGET.dir.abspath}`` with ``rysnc``.
      ``rsync`` must exist on the local system.

    .. code-block::
       :caption: SConstruct

       import getpass
       import waves
       user = getpass.getuser()
       env = Environment()
       env.Append(BUILDERS={
           "SSHAbaqusSolver": waves.scons_extensions.ssh_builder_actions(
               waves.scons_extensions.abaqus_solver(program="/remote/server/installation/path/of/abaqus"),
               remote_server="myserver.mydomain.com"
           )
       })
       env.SSHAbaqusSolver(target=["myjob.sta"], source=["input.inp"], job_name="myjob", abaqus_options="-cpus 4",
                           remote_directory="/scratch/${user}/myproject/myworkflow", user=user)

    .. code-block::
       :caption: my_package.py

       import SCons.Builder
       import waves

       def print_builder_actions(builder):
           for action in builder.action.list:
               print(action.cmd_list)

       def cat(program="cat"):
           return SCons.Builder.Builder(action=
               [f"{program} ${{SOURCES.abspath}} | tee ${{TARGETS.file}}", "echo \\"Hello World!\\""]
           )

       build_cat = cat()

       ssh_build_cat = waves.scons_extensions.ssh_builder_actions(
           cat(), remote_server="myserver.mydomain.com", remote_directory="/scratch/roppenheimer/ssh_wrapper"
       )

    .. code-block::

       >>> import my_package
       >>> my_package.print_builder_actions(my_package.build_cat)
       cat ${SOURCES.abspath} | tee ${TARGETS.file}
       echo "Hello World!"
       >>> my_package.print_builder_actions(my_package.ssh_build_cat)
       ssh myserver.mydomain.com "mkdir -p /scratch/roppenheimer/ssh_wrapper"
       rsync -rlptv ${SOURCES.abspath} myserver.mydomain.com:/scratch/roppenheimer/ssh_wrapper
       ssh myserver.mydomain.com 'cd /scratch/roppenheimer/ssh_wrapper && cat ${SOURCES.file} | tee ${TARGETS.file}'
       ssh myserver.mydomain.com 'cd /scratch/roppenheimer/ssh_wrapper && echo "Hello World!"'
       rsync -rltpv myserver.mydomain.com:/scratch/roppenheimer/ssh_wrapper/ ${TARGET.dir.abspath}

    :param SCons.Builder.Builder builder: The SCons builder to modify
    :param str remote_server: remote server where the original builder's actions should be executed. The default string
        *requires* every task to specify a matching keyword argument string.
    :param str remote_directory: absolute or relative path where the original builder's actions should be executed. The
        default string *requires* every task to specify a matching keyword argument string.
    """
    action_list = _string_action_list(builder)
    cd_prefix = f"cd {remote_directory} &&"
    action_list = [action.replace("cd ${TARGET.dir.abspath} &&", cd_prefix) for action in action_list]
    action_list = [action.replace("SOURCE.abspath", "SOURCE.file") for action in action_list]
    action_list = [action.replace("SOURCES.abspath", "SOURCES.file") for action in action_list]
    action_list = [re.sub(r"(SOURCES\[[-0-9]+\])\.abspath", r"\1.file", action) for action in action_list]
    action_list = [f"{cd_prefix} {action}" if not action.startswith(cd_prefix) else action for action in action_list]
    action_list = [f"ssh {remote_server} '{action}'" for action in action_list]

    ssh_actions = [
        f"ssh {remote_server} \"mkdir -p {remote_directory}\"",
        f"rsync -rlptv ${{SOURCES.abspath}} {remote_server}:{remote_directory}"
    ]
    ssh_actions.extend(action_list)
    ssh_actions.append(f"rsync -rltpv {remote_server}:{remote_directory}/ ${{TARGET.dir.abspath}}")
    ssh_actions = [SCons.Action.CommandAction(action) for action in ssh_actions]

    builder.action = SCons.Action.ListAction(ssh_actions)
    return builder


# TODO: Remove the **kwargs check and warning for v1.0.0 release
# https://re-git.lanl.gov/aea/python-projects/waves/-/issues/508
def _warn_kwarg_change(kwargs, old_kwarg, new_kwarg="program"):
    """Return the value of an old kwarg and raise a deprecation warning pointing to the new kwarg

    Return None if the old keyword argument is not found in the keyword arguments dictionary.

    >>> def function_with_kwarg_change(new_kwarg="something", **kwargs):
    >>>     old_kwarg = waves.scons_extensions._warn_kwarg_change()
    >>>     new_kwarg = old_kwarg if old_kwarg is not None else new_kwarg

    :param dict kwargs: The ``**kwargs`` dictionary from a function interface
    :param str old_kwarg: The older kwarg key.

    :return: Value of the ``old_kwarg`` if it exists in the ``kwargs`` dictionary. ``None`` if the old keyword isn't
        found in the dictionary.
    """
    program = None
    if old_kwarg in kwargs:
        import warnings
        warnings.filterwarnings('always')
        message = f"The '{old_kwarg}' keyword argument will be deprecated in a future version. " \
                  f"Use the '{new_kwarg}' keyword argument instead."
        warnings.warn(message, DeprecationWarning)
        program = kwargs[old_kwarg]
    return program


def project_help_message(env=None, append=True, keep_local=True):
    """Add default targets and alias lists to project help message

    See the `SCons Help`_ documentation for appending behavior. Thin wrapper around

    * :meth:`waves.scons_extensions.default_targets_message`
    * :meth:`waves.scons_extensions.alias_list_message`

    :param SCons.Script.SConscript.SConsEnvironment env: The SCons construction environment object to modify
    :param bool append: append to the ``env.Help`` message (default). When False, the ``env.Help`` message will be
        overwritten if ``env.Help`` has not been previously called.
    :param bool keep_local: Limit help message to the project specific content when True. Only applies to SCons >=4.6.0
    """
    default_targets_message(env=env, append=append, keep_local=keep_local)
    alias_list_message(env=env, append=append, keep_local=keep_local)


def default_targets_message(env=None, append=True, keep_local=True):
    """Add a default targets list to the project's help message

    See the `SCons Help`_ documentation for appending behavior. Adds text to the project help message formatted as

    .. code-block::

       Default Targets:
           Default_Target_1
           Default_Target_2

    where the targets are recovered from ``SCons.Script.DEFAULT_TARGETS``.

    :param SCons.Script.SConscript.SConsEnvironment env: The SCons construction environment object to modify
    :param bool append: append to the ``env.Help`` message (default). When False, the ``env.Help`` message will be
        overwritten if ``env.Help`` has not been previously called.
    :param bool keep_local: Limit help message to the project specific content when True. Only applies to SCons >=4.6.0
    """
    import SCons.Script  # Required to get a full construction environment
    if not env:
        env = SCons.Environment.Environment()
    default_targets_help = "\nDefault Targets:\n"
    for target in SCons.Script.DEFAULT_TARGETS:
        default_targets_help += f"    {str(target)}\n"
    try:
        env.Help(default_targets_help, append=append, keep_local=keep_local)
    except TypeError as err:
        env.Help(default_targets_help, append=append)


def alias_list_message(env=None, append=True, keep_local=True):
    """Add the alias list to the project's help message

    See the `SCons Help`_ documentation for appending behavior. Adds text to the project help message formatted as

    .. code-block::

       Target Aliases:
           Alias_1
           Alias_2

    where the aliases are recovered from ``SCons.Node.Alias.default_ans``.

    :param SCons.Script.SConscript.SConsEnvironment env: The SCons construction environment object to modify
    :param bool append: append to the ``env.Help`` message (default). When False, the ``env.Help`` message will be
        overwritten if ``env.Help`` has not been previously called.
    :param bool keep_local: Limit help message to the project specific content when True. Only applies to SCons >=4.6.0
    """
    import SCons.Script  # Required to get a full construction environment
    if not env:
        env = SCons.Environment.Environment()
    alias_help = "\nTarget Aliases:\n"
    for alias in SCons.Node.Alias.default_ans:
        alias_help += f"    {alias}\n"
    try:
        env.Help(alias_help, append=append, keep_local=keep_local)
    except TypeError:
        env.Help(alias_help, append=append)


def append_env_path(program, env):
    """Append SCons contruction environment ``PATH`` with the program's parent directory

    Raises a ``FileNotFoundError`` if the ``program`` absolute path does not exist. Uses the `SCons AppendENVPath`_
    method. If the program parent directory is already on ``PATH``, the ``PATH`` directory order is preserved.

    .. code-block::
       :caption: Example environment modification

       import waves

       env = Environment()
       env["program"] = waves.scons_extensions.find_program(["program"], env)
       if env["program"]:
           waves.append_env_path(env["program"], env)

    :param str program: An absolute path for the program to add to SCons construction environment ``PATH``
    :param SCons.Script.SConscript.SConsEnvironment env: The SCons construction environment object to modify
    """
    program = pathlib.Path(program).resolve()
    if not program.exists():
        raise FileNotFoundError(f"The program '{program}' does not exist.")
    env.AppendENVPath("PATH", str(program.parent), delete_existing=False)


def substitution_syntax(substitution_dictionary, prefix="@", postfix="@"):
    """Return a dictionary copy with the pre/postfix added to the key strings

    Assumes a flat dictionary with keys of type str. Keys that aren't strings will be converted to their string
    representation. Nested dictionaries can be supplied, but only the first layer keys will be modified. Dictionary
    values are unchanged.

    :param dict substitution_dictionary: Original dictionary to copy
    :param string prefix: String to prepend to all dictionary keys
    :param string postfix: String to append to all dictionary keys

    :return: Copy of the dictionary with key strings modified by the pre/posfix
    :rtype: dict
    """
    return {f"{prefix}{key}{postfix}": value for key, value in substitution_dictionary.items()}


def find_program(names, env):
    """Search for a program from a list of possible program names.

    Returns the absolute path of the first program name found. If path parts contain spaces, the part will be wrapped in
    double quotes.

    :param list names: list of string program names. May include an absolute path.
    :param SCons.Script.SConscript.SConsEnvironment env: The SCons construction environment object to modify

    :return: Absolute path of the found program. None if none of the names are found.
    :rtype: str
    """
    if isinstance(names, str):
        names = [names]
    conf = env.Configure()
    program_paths = []
    for name in names:
        program_paths.append(conf.CheckProg(name))
    conf.Finish()
    # Return first non-None path. Default to None if no program path was found.
    first_found_path = next((path for path in program_paths if path is not None), None)
    if first_found_path:
        first_found_path = str(_utilities._quote_spaces_in_path(first_found_path))
    return first_found_path


def add_program(names, env):
    """Search for a program from a list of possible program names. Add first found to system ``PATH``.

    Returns the absolute path of the first program name found. Appends ``PATH`` with first program's parent directory
    if a program is found and the directory is not already on ``PATH``. Returns None if no program name is found.

    .. code-block::
       :caption: Example search for an executable named "program"

       import waves

       env = Environment()
       env["program"] = waves.scons_extensions.add_program(["program"], env)

    :param list names: list of string program names. May include an absolute path.
    :param SCons.Script.SConscript.SConsEnvironment env: The SCons construction environment object to modify

    :return: Absolute path of the found program. None if none of the names are found.
    :rtype: str
    """
    first_found_path = find_program(names, env)
    if first_found_path:
        append_env_path(first_found_path, env)
    return first_found_path


def add_cubit(names, env):
    """Modifies environment variables with the paths required to ``import cubit`` in a Python3 environment.

    Returns the absolute path of the first program name found. Appends ``PATH`` with first program's parent directory if
    a program is found and the directory is not already on ``PATH``. Prepends ``PYTHONPATH`` with ``parent/bin``.
    Prepends ``LD_LIBRARY_PATH`` with ``parent/bin/python3``.

    Returns None if no program name is found.

    .. code-block::
       :caption: Example Cubit environment modification

       import waves

       env = Environment()
       env["cubit"] = waves.scons_extensions.add_cubit(["cubit"], env)

    :param list names: list of string program names. May include an absolute path.
    :param SCons.Script.SConscript.SConsEnvironment env: The SCons construction environment object to modify

    :return: Absolute path of the found program. None if none of the names are found.
    :rtype: str
    """
    first_found_path = add_program(names, env)
    if first_found_path:
        cubit_bin = _utilities.find_cubit_bin([first_found_path])
        cubit_python_library_dir = cubit_bin / "python3"
        env.PrependENVPath("PYTHONPATH", str(cubit_bin))
        env.PrependENVPath("LD_LIBRARY_PATH", str(cubit_python_library_dir))
    return first_found_path


def _return_environment(command):
    """Run a shell command and return the shell environment as a dictionary

    .. warning::

       Currently only supports bash shells

    :param str command: the shell command to execute

    :returns: shell environment dictionary
    :rtype: dict
    """
    variables = subprocess.run(
        ["bash", "-c", f"trap 'env -0' exit; {command} > /dev/null 2>&1"],
        check=True,
        capture_output=True
    ).stdout.decode().split("\x00")

    environment = dict()
    for line in variables:
        if line != "":
            key, value = line.split("=", 1)
            environment[key] = value

    return environment


def _cache_environment(command, cache=None, overwrite_cache=False, verbose=False):
    """Retrieve cached environment dictionary or run a shell command to generate environment dictionary

    If the environment is created successfully and a cache file is requested, the cache file is _always_ written. The
    ``overwrite_cache`` behavior forces the shell ``command`` execution, even when the cache file is present.

    .. warning::

       Currently only supports bash shells

    :param str command: the shell command to execute
    :param str cache: absolute or relative path to read/write a shell environment dictionary. Will be written as YAML
        formatted file regardless of extension.
    :param bool overwrite_cache: Ignore previously cached files if they exist.
    :param bool verbose: Print SCons configuration-like action messages when True

    :returns: shell environment dictionary
    :rtype: dict
    """
    if cache:
        cache = pathlib.Path(cache).resolve()

    if cache and cache.exists() and not overwrite_cache:
        if verbose:
            print(f"Sourcing the shell environment from cached file '{cache}' ...")
        with open(cache, "r") as cache_file:
            environment = yaml.safe_load(cache_file)
    else:
        if verbose:
            print(f"Sourcing the shell environment with command '{command}' ...")
        environment = _return_environment(command)

    if cache:
        with open(cache, "w") as cache_file:
            yaml.safe_dump(environment, cache_file)

    return environment


def shell_environment(command, cache=None, overwrite_cache=False):
    """Return an SCons shell environment from a cached file or by running a shell command

    If the environment is created successfully and a cache file is requested, the cache file is _always_ written. The
    ``overwrite_cache`` behavior forces the shell ``command`` execution, even when the cache file is present.

    .. warning::

       Currently only supports bash shells

    .. code-block::
       :caption: SConstruct

       import waves
       env = waves.scons_extensions.shell_environment("source my_script.sh")

    :param str command: the shell command to execute
    :param str cache: absolute or relative path to read/write a shell environment dictionary. Will be written as YAML
        formatted file regardless of extension.
    :param bool overwrite_cache: Ignore previously cached files if they exist.

    :returns: SCons shell environment
    :rtype: SCons.Environment.Environment
    """
    shell_environment = _cache_environment(command, cache=cache, overwrite_cache=overwrite_cache, verbose=True)
    return SCons.Environment.Environment(ENV=shell_environment)


def _construct_post_action_list(post_action):
    """Return a post-action list

    Returns the constructed post-action list of strings with prepended directory change as

    .. code-block::

       f"cd ${{TARGET.dir.abspath}} && {new_action}"

    where action objects are converted to their string representation. If a string is passed instead of a list, it is
    first convert to a list. Other string-like objects, e.g. bytes, are not converted, but iterated on
    character-by-character. If an empty list is passed, and empty list is returned.

    :param list post_action: List of post-action strings

    :return: post-action list of strings
    :rtype: list
    """
    if isinstance(post_action, str):
        post_action = [post_action]
    try:
        iterator = iter(post_action)
    except TypeError:
        iterator = iter([post_action])
    new_actions = [f"{_cd_action_prefix} {action}" for action in iterator]
    return new_actions


def _build_subdirectory(target):
    """Return the build subdirectory of the first target file

    :param list target: The target file list of strings

    :return: build directory
    :rtype: pathlib.Path
    """
    try:
        build_subdirectory = pathlib.Path(str(target[0])).parent
    except IndexError as err:
        build_subdirectory = pathlib.Path(".")
    return build_subdirectory


def _first_target_emitter(target, source, env, suffixes=[], appending_suffixes=[], stdout_extension=_stdout_extension):
    """Appends the target list with the builder managed targets

    Searches for a file ending in the stdout extension. If none is found, creates a target by appending the stdout
    extension to the first target in the ``target`` list. The associated Builder requires at least one target for this
    reason. The stdout file is always placed at the end of the returned target list.

    The suffixes list are replacement operations on the first target's suffix. The appending suffixes list are appending
    operations on the first target's suffix.

    The emitter will assume all emitted targets build in the current build directory. If the target(s) must be built in
    a build subdirectory, e.g. in a parameterized target build, then the first target must be provided with the build
    subdirectory, e.g. ``parameter_set1/target.ext``. When in doubt, provide a STDOUT redirect file with the ``.stdout``
    extension as a target, e.g. ``target.stdout``.

    :param list target: The target file list of strings
    :param list source: The source file list of SCons.Node.FS.File objects
    :param SCons.Script.SConscript.SConsEnvironment env: The builder's SCons construction environment object
    :param list suffixes: Suffixes which should replace the first target's extension
    :param list appending_suffixes: Suffixes which should append the first target's extension

    :return: target, source
    :rtype: tuple with two lists
    """
    string_targets = [str(target_file) for target_file in target]
    first_target = pathlib.Path(string_targets[0])

    # Search for a user specified stdout file. Fall back to first target with appended stdout extension
    stdout_target = next((target_file for target_file in string_targets if target_file.endswith(stdout_extension)),
                         f"{first_target}{stdout_extension}")

    replacing_targets = [str(first_target.with_suffix(suffix)) for suffix in suffixes]
    appending_targets = [f"{first_target}{suffix}" for suffix in appending_suffixes]
    string_targets = string_targets + replacing_targets + appending_targets

    # Get a list of unique targets,  less the stdout target. Preserve the target list order.
    string_targets = [target_file for target_file in string_targets if target_file != stdout_target]
    string_targets = list(dict.fromkeys(string_targets))

    # Always append the stdout target for easier use in the action string
    string_targets.append(stdout_target)

    return string_targets, source


def _abaqus_journal_emitter(target, source, env):
    """Appends the abaqus_journal builder target list with the builder managed targets

    Appends ``target[0]``.abaqus_v6.env and ``target[0]``.stdout to the ``target`` list. The abaqus_journal Builder
    requires at least one target.

    The emitter will assume all emitted targets build in the current build directory. If the target(s) must be built in
    a build subdirectory, e.g. in a parameterized target build, then the first target must be provided with the build
    subdirectory, e.g. ``parameter_set1/target.ext``. When in doubt, provide a STDOUT redirect file as a target, e.g.
    ``target.stdout``.

    :param list target: The target file list of strings
    :param list source: The source file list of SCons.Node.FS.File objects
    :param SCons.Script.SConscript.SConsEnvironment env: The builder's SCons construction environment object

    :return: target, source
    :rtype: tuple with two lists
    """
    appending_suffixes = [_abaqus_environment_extension]
    return _first_target_emitter(target, source, env, appending_suffixes=appending_suffixes)


def abaqus_journal(program="abaqus", post_action=[], **kwargs):
    """Abaqus journal file SCons builder

    This builder requires that the journal file to execute is the first source in the list. The builder returned by this
    function accepts all SCons Builder arguments and adds the keyword argument(s):

    * ``journal_options``: The journal file command line options provided as a string.
    * ``abaqus_options``: The Abaqus command line options provided as a string.

    At least one target must be specified. The first target determines the working directory for the builder's action,
    as shown in the action code snippet below. The action changes the working directory to the first target's parent
    directory prior to executing the journal file.

    The Builder emitter will append the builder managed targets automatically. Appends ``target[0]``.abaqus_v6.env and
    ``target[0]``.stdout to the ``target`` list.

    The emitter will assume all emitted targets build in the current build directory. If the target(s) must be built in
    a build subdirectory, e.g. in a parameterized target build, then the first target must be provided with the build
    subdirectory, e.g. ``parameter_set1/my_target.ext``. When in doubt, provide a STDOUT redirect file as a target, e.g.
    ``target.stdout``.

    .. code-block::
       :caption: Abaqus journal builder action

       cd ${TARGET.dir.abspath} && abaqus cae -noGui ${SOURCE.abspath} ${abaqus_options} -- ${journal_options} > ${TARGETS[-1].abspath} 2>&1

    .. code-block::
       :caption: SConstruct

       import waves
       env = Environment()
       env["abaqus"] = waves.scons_extensions.add_program(["abaqus"], env)
       env.Append(BUILDERS={"AbaqusJournal": waves.scons_extensions.abaqus_journal()})
       env.AbaqusJournal(target=["my_journal.cae"], source=["my_journal.py"], journal_options="")

    :param str program: An absolute path or basename string for the abaqus program.
    :param list post_action: List of shell command string(s) to append to the builder's action list. Implemented to
        allow post target modification or introspection, e.g. inspect the Abaqus log for error keywords and throw a
        non-zero exit code even if Abaqus does not. Builder keyword variables are available for substitution in the
        ``post_action`` action using the ``${}`` syntax. Actions are executed in the first target's directory as ``cd
        ${TARGET.dir.abspath} && ${post_action}``

    :return: Abaqus journal builder
    :rtype: SCons.Builder.Builder
    """
    # TODO: Remove the **kwargs and abaqus_program check for v1.0.0 release
    # https://re-git.lanl.gov/aea/python-projects/waves/-/issues/508
    abaqus_program = _warn_kwarg_change(kwargs, "abaqus_program")
    program = abaqus_program if abaqus_program is not None else program
    action = [f"{_cd_action_prefix} {program} -information environment " \
                 f"{_redirect_environment_postfix}",
              f"{_cd_action_prefix} {program} cae -noGui ${{SOURCE.abspath}} ${{abaqus_options}} -- " \
                 f"${{journal_options}} {_redirect_action_postfix}"]
    action.extend(_construct_post_action_list(post_action))
    abaqus_journal_builder = SCons.Builder.Builder(
        action=action,
        emitter=_abaqus_journal_emitter)
    return abaqus_journal_builder


@catenate_actions(program="sbatch", options=_sbatch_wrapper_options)
def sbatch_abaqus_journal(*args, **kwargs):
    """Thin pass through wrapper of :meth:`waves.scons_extensions.abaqus_journal`

    Catenate the actions and submit with `SLURM`_ `sbatch`_. Accepts the ``sbatch_options`` builder keyword argument to
    modify sbatch behavior.

    .. code-block::
       :caption: Sbatch Abaqus journal builder action

       sbatch --wait --output=${TARGET.base}.slurm.out ${sbatch_options} --wrap "cd ${TARGET.dir.abspath} && abaqus cae -noGui ${SOURCE.abspath} ${abaqus_options} -- ${journal_options} > ${TARGETS[-1].abspath} 2>&1"
    """
    return abaqus_journal(*args, **kwargs)


def _abaqus_solver_emitter(target, source, env, suffixes=_abaqus_solver_common_suffixes, stdout_extension=_stdout_extension):
    """Appends the abaqus_solver builder target list with the builder managed targets

    If no targets are provided to the Builder, the emitter will assume all emitted targets build in the current build
    directory. If the target(s) must be built in a build subdirectory, e.g. in a parameterized target build, then at
    least one target must be provided with the build subdirectory, e.g. ``parameter_set1/target.ext``. When in doubt,
    provide the output database as a target, e.g. ``job_name.odb``

    If "suffixes" is a key in the environment, ``env``, then the suffixes list will override the ``suffixes_to_extend``
    argument.

    :param list target: The target file list of strings
    :param list source: The source file list of SCons.Node.FS.File objects
    :param SCons.Script.SConscript.SConsEnvironment env: The builder's SCons construction environment object
    :param list suffixes_to_extend: List of strings to use as emitted file suffixes. Must contain the leading period,
        e.g. ``.extension``

    :return: target, source
    :rtype: tuple with two lists
    """
    if "suffixes" in env and env["suffixes"] is not None:
        suffixes = env["suffixes"]
    primary_input_file = pathlib.Path(source[0].path)
    if "job_name" not in env or not env["job_name"]:
        env["job_name"] = primary_input_file.stem
    if isinstance(suffixes, str):
        suffixes = [suffixes]
    suffixes.append(_abaqus_environment_extension)
    build_subdirectory = _build_subdirectory(target)

    # Search for a user specified stdout file. Fall back to job name with appended stdout extension
    string_targets = [str(target_file) for target_file in target]
    constructed_stdout_target = str(build_subdirectory / f"{env['job_name']}{stdout_extension}")
    stdout_target = next((target_file for target_file in string_targets if target_file.endswith(stdout_extension)),
                         constructed_stdout_target)

    job_targets = [str(build_subdirectory / f"{env['job_name']}{suffix}") for suffix in suffixes]

    # Get a list of unique targets,  less the stdout target. Preserve the target list order.
    string_targets = string_targets + job_targets
    string_targets = [target_file for target_file in string_targets if target_file != stdout_target]
    string_targets = list(dict.fromkeys(string_targets))

    # Always append the stdout target for easier use in the action string
    string_targets.append(stdout_target)

    return string_targets, source


def _abaqus_standard_solver_emitter(target, source, env):
    """Passes the standard specific extensions to :meth:`_abaqus_solver_emitter`"""
    return _abaqus_solver_emitter(target, source, env, _abaqus_standard_extensions)


def _abaqus_explicit_solver_emitter(target, source, env):
    """Passes the explicit specific extensions to :meth:`_abaqus_solver_emitter`"""
    return _abaqus_solver_emitter(target, source, env, _abaqus_explicit_extensions)


def _abaqus_datacheck_solver_emitter(target, source, env):
    """Passes the datacheck specific extensions to :meth:`_abaqus_solver_emitter`"""
    return _abaqus_solver_emitter(target, source, env, _abaqus_datacheck_extensions)


def abaqus_solver(program="abaqus", post_action=[], emitter=None, **kwargs):
    """Abaqus solver SCons builder

    This builder requires that the root input file is the first source in the list. The builder returned by this
    function accepts all SCons Builder arguments and adds the keyword argument(s):

    * ``job_name``: The job name string. If not specified ``job_name`` defaults to the root input file stem. The Builder
      emitter will append common Abaqus output files as targets automatically from the ``job_name``, e.g. ``job_name.odb``.
    * ``abaqus_options``: The Abaqus command line options provided as a string.
    * ``suffixes``: override the emitter targets with a new list of extensions, e.g.
      ``AbaqusSolver(target=[], source=["input.inp"], suffixes=[".odb"])`` will emit only one file named
      ``job_name.odb``.

    The first target determines the working directory for the builder's action, as shown in the action code snippet
    below. The action changes the working directory to the first target's parent directory prior to executing the
    journal file.

    This builder is unique in that no targets are required. The Builder emitter will append the builder managed targets
    automatically. The target list only appends those extensions which are common to Abaqus analysis operations. Some
    extensions may need to be added explicitly according to the Abaqus simulation solver, type, or options. If you find
    that SCons isn't automatically cleaning some Abaqus output files, they are not in the automatically appended target
    list.

    The emitter will assume all emitted targets build in the current build directory. If the target(s) must be built in
    a build subdirectory, e.g. in a parameterized target build, then the first target must be provided with the build
    subdirectory, e.g. ``parameter_set1/job_name.odb``. When in doubt, provide a STDOUT redirect file as a target, e.g.
    ``target.stdout``.

    The ``-interactive`` option is always appended to the builder action to avoid exiting the Abaqus task before the
    simulation is complete.  The ``-ask_delete no`` option is always appended to the builder action to overwrite
    existing files in programmatic execution, where it is assumed that the Abaqus solver target(s) should be re-built
    when their source files change.

    .. code-block::
       :caption: SConstruct

       import waves
       env = Environment()
       env["abaqus"] = waves.scons_extensions.add_program(["abaqus"], env)
       env.Append(BUILDERS={
           "AbaqusSolver": waves.scons_extensions.abaqus_solver(),
           "AbaqusStandard": waves.scons_extensions.abaqus_solver(emitter='standard'),
           "AbaqusOld": waves.scons_extensions.abaqus_solver(program="abq2019"),
           "AbaqusPost": waves.scons_extensions.abaqus_solver(post_action="grep -E "\<SUCCESSFULLY" ${job_name}.sta")
       })
       env.AbaqusSolver(target=[], source=["input.inp"], job_name="my_job", abaqus_options="-cpus 4")
       env.AbaqusSolver(target=[], source=["input.inp"], job_name="my_job", suffixes=[".odb"])

    .. code-block::
       :caption: Abaqus solver builder action

       cd ${TARGET.dir.abspath} && ${program} -job ${job_name} -input ${SOURCE.filebase} ${abaqus_options} -interactive -ask_delete no > ${TARGETS[-1].abspath} 2>&1

    :param str program: An absolute path or basename string for the abaqus program
    :param list post_action: List of shell command string(s) to append to the builder's action list. Implemented to
        allow post target modification or introspection, e.g. inspect the Abaqus log for error keywords and throw a
        non-zero exit code even if Abaqus does not. Builder keyword variables are available for substitution in the
        ``post_action`` action using the ``${}`` syntax. Actions are executed in the first target's directory as ``cd
        ${TARGET.dir.abspath} && ${post_action}``.
    :param str emitter: emit file extensions based on the value of this variable. Overridden by the ``suffixes`` keyword
        argument that may be provided in the Task definition.

        * "standard": [".odb", ".dat", ".msg", ".com", ".prt", ".sta"]
        * "explicit": [".odb", ".dat", ".msg", ".com", ".prt", ".sta"]
        * "datacheck": [".odb", ".dat", ".msg", ".com", ".prt", ".023", ".mdl", ".sim", ".stt"]
        * default value: [".odb", ".dat", ".msg", ".com", ".prt"]

    :return: Abaqus solver builder
    :rtype: SCons.Builder.Builder
    """
    # TODO: Remove the **kwargs and abaqus_program check for v1.0.0 release
    # https://re-git.lanl.gov/aea/python-projects/waves/-/issues/508
    abaqus_program = _warn_kwarg_change(kwargs, "abaqus_program")
    program = abaqus_program if abaqus_program is not None else program
    action = [f"{_cd_action_prefix} {program} -information environment " \
                  f"{_redirect_environment_postfix}",
              f"{_cd_action_prefix} {program} -job ${{job_name}} -input ${{SOURCE.filebase}} " \
                  f"${{abaqus_options}} -interactive -ask_delete no {_redirect_action_postfix}"]
    action.extend(_construct_post_action_list(post_action))
    if emitter:
        emitter = emitter.lower()
    if emitter == 'standard':
        abaqus_emitter = _abaqus_standard_solver_emitter
    elif emitter == 'explicit':
        abaqus_emitter = _abaqus_explicit_solver_emitter
    elif emitter == 'datacheck':
        abaqus_emitter = _abaqus_datacheck_solver_emitter
    else:
        abaqus_emitter = _abaqus_solver_emitter
    abaqus_solver_builder = SCons.Builder.Builder(
        action=action,
        emitter=abaqus_emitter)
    return abaqus_solver_builder


@catenate_actions(program="sbatch", options=_sbatch_wrapper_options)
def sbatch_abaqus_solver(*args, **kwargs):
    """Thin pass through wrapper of :meth:`waves.scons_extensions.abaqus_solver`

    Catenate the actions and submit with `SLURM`_ `sbatch`_. Accepts the ``sbatch_options`` builder keyword argument to
    modify sbatch behavior.

    .. code-block::
       :caption: Sbatch Abaqus solver builder action

       sbatch --wait --output=${TARGET.base}.slurm.out ${sbatch_options} --wrap "cd ${TARGET.dir.abspath} && ${program} -job ${job_name} -input ${SOURCE.filebase} ${abaqus_options} -interactive -ask_delete no > ${TARGETS[-1].abspath} 2>&1"
    """
    return abaqus_solver(*args, **kwargs)


def _sierra_emitter(target, source, env):
    """Appends the sierra builder target list with the builder managed targets

    Appends ``target[0]``.env and ``target[0]``.stdout  to the ``target`` list. The Sierra Builder requires
    at least one target.

    The emitter will assume all emitted targets build in the current build directory. If the target(s) must be built in
    a build subdirectory, e.g. in a parameterized target build, then the first target must be provided with the build
    subdirectory, e.g. ``parameter_set1/target.ext``. When in doubt, provide a STDOUT redirect file as a target, e.g.
    ``target.stdout``.

    :param list target: The target file list of strings
    :param list source: The source file list of SCons.Node.FS.File objects
    :param SCons.Script.SConscript.SConsEnvironment env: The builder's SCons construction environment object

    :return: target, source
    :rtype: tuple with two lists
    """
    appending_suffixes = [_sierra_environment_extension]
    return _first_target_emitter(target, source, env, appending_suffixes=appending_suffixes)


def sierra(program="sierra", application="adagio", post_action=[]):
    """Sierra SCons builder

    This builder requires that the root input file is the first source in the list. The builder returned by this
    function accepts all SCons Builder arguments and adds the keyword argument(s):

    * ``sierra_options``: The Sierra command line options provided as a string.
    * ``application_options``: The application (e.g. adagio) command line options provided as a string.

    The first target determines the working directory for the builder's action, as shown in the action code snippet
    below. The action changes the working directory to the first target's parent directory prior to executing sierra.

    The emitter will assume all emitted targets build in the current build directory. If the target(s) must be built in
    a build subdirectory, e.g. in a parameterized target build, then the first target must be provided with the build
    subdirectory, e.g. ``parameter_set1/target.ext``. When in doubt, provide a STDOUT redirect file as a target, e.g.
    ``target.stdout``.

    .. warning::

       This is an experimental builder for Sierra support. The only emitted file is the application's version report in
       ``target[0].env`` and the ``target[0].stdout`` redirected STDOUT and STDERR file. All relevant application output
       files, e.g. ``genesis_output.e`` must be specified in the target list.

    .. code-block::
       :caption: SConstruct

       import waves
       env = waves.scons_extensions.shell_environment("module load sierra")
       env.Append(BUILDERS={
           "Sierra": waves.scons_extensions.sierra(),
       })
       env.Sierra(target=["output.e"], source=["input.i"])

    .. code-block::
       :caption: Sierra builder action

       cd ${TARGET.dir.abspath} && ${program} ${sierra_options} ${application} ${application_options} -i ${SOURCE.file} > ${TARGETS[-1].abspath} 2>&1

    :param str program: An absolute path or basename string for the Sierra program
    :param str application: The string name for the Sierra application
    :param list post_action: List of shell command string(s) to append to the builder's action list. Implemented to
        allow post target modification or introspection, e.g. inspect the Sierra log for error keywords and throw a
        non-zero exit code even if Sierra does not. Builder keyword variables are available for substitution in the
        ``post_action`` action using the ``${}`` syntax. Actions are executed in the first target's directory as ``cd
        ${TARGET.dir.abspath} && ${post_action}``.

    :return: Sierra builder
    :rtype: SCons.Builder.Builder
    """
    action = [f"{_cd_action_prefix} {program} {application} --version " \
                  f"{_redirect_environment_postfix}",
              f"{_cd_action_prefix} {program} ${{sierra_options}} {application} ${{application_options}} " \
                  f"-i ${{SOURCE.file}} {_redirect_action_postfix}"]
    action.extend(_construct_post_action_list(post_action))
    sierra_builder = SCons.Builder.Builder(
        action=action,
        emitter=_sierra_emitter
    )
    return sierra_builder


@catenate_actions(program="sbatch", options=_sbatch_wrapper_options)
def sbatch_sierra(*args, **kwargs):
    """Thin pass through wrapper of :meth:`waves.scons_extensions.sierra`

    Catenate the actions and submit with `SLURM`_ `sbatch`_. Accepts the ``sbatch_options`` builder keyword argument to
    modify sbatch behavior.

    .. code-block::
       :caption: sbatch Sierra builder action

       sbatch --wait --output=${TARGET.base}.slurm.out ${sbatch_options} --wrap "cd ${TARGET.dir.abspath} && ${program} ${sierra_options} ${application} ${application_options} -i ${SOURCE.file} > ${TARGETS[-1].abspath} 2>&1"
    """
    return sierra(*args, **kwargs)


def copy_substitute(source_list, substitution_dictionary=None, env=SCons.Environment.Environment(),
                    build_subdirectory=".", symlink=False):
    """Copy source list to current variant directory and perform template substitutions on ``*.in`` filenames

    .. warning::

       This is a Python function and not an SCons builder. It cannot be added to the construction environment
       ``BUILDERS`` list. The function returns a list of targets instead of a Builder object.

    Creates an SCons Copy task for each source file. Files are copied to the current variant directory
    matching the calling SConscript parent directory. Files with the name convention ``*.in`` are also given an SCons
    Substfile Builder, which will perform template substitution with the provided dictionary in-place in the current
    variant directory and remove the ``.in`` suffix.

    To avoid dependency cycles, the source file(s) should be passed by absolute path.

    .. code-block::
       :caption: SConstruct

       import pathlib
       import waves
       env = Environment()
       current_directory = pathlib.Path(Dir(".").abspath)
       source_list = [
           "#/subdir3/file_three.ext",              # File found with respect to project root directory using SCons notation
           current_directory / file_one.ext,        # File found in current SConscript directory
           current_directory / "subdir2/file_two",  # File found below current SConscript directory
           current_directory / "file_four.ext.in"   # File with substitutions matching substitution dictionary keys
       ]
       substitution_dictionary = {
           "@variable_one@": "value_one"
       }
       waves.scons_extensions.copy_substitute(source_list, substitution_dictionary, env)

    :param list source_list: List of pathlike objects or strings. Will be converted to list of pathlib.Path objects.
    :param dict substitution_dictionary: key: value pairs for template substitution. The keys must contain the optional
        template characters if present, e.g. ``@variable@``. The template character, e.g. ``@``, can be anything that
        works in the `SCons Substfile`_ builder.
    :param SCons.Environment.Environment env: An SCons construction environment to use when defining the targets.
    :param str build_subdirectory: build subdirectory relative path prepended to target files
    :param bool symlink: Whether symbolic links are created as new symbolic links. If true, symbolic links are shallow
        copies as a new symbolic link. If false, symbolic links are copied as a new file (dereferenced).

    :return: SCons NodeList of Copy and Substfile target nodes
    :rtype: SCons.Node.NodeList
    """
    if not substitution_dictionary:
        substitution_dictionary = {}
    build_subdirectory = pathlib.Path(build_subdirectory)
    target_list = SCons.Node.NodeList()
    source_list = [pathlib.Path(source_file) for source_file in source_list]
    for source_file in source_list:
        copy_target = build_subdirectory / source_file.name
        target_list += env.Command(
                target=str(copy_target),
                source=str(source_file),
                action=SCons.Defaults.Copy("${TARGET}", "${SOURCE}", symlink))
        if source_file.suffix == _scons_substfile_suffix:
            substfile_target = build_subdirectory / source_file.name
            target_list += env.Substfile(str(substfile_target), SUBST_DICT=substitution_dictionary)
    return target_list


def python_script(post_action=[]):
    """Python script SCons builder

    This builder requires that the python script to execute is the first source in the list. The builder returned by
    this function accepts all SCons Builder arguments and adds the keyword argument(s):

    * ``script_options``: The Python script command line arguments provided as a string.
    * ``python_options``: The Python command line arguments provided as a string.

    At least one target must be specified. The first target determines the working directory for the builder's action,
    as shown in the action code snippet below. The action changes the working directory to the first target's parent
    directory prior to executing the python script.

    The Builder emitter will append the builder managed targets automatically. Appends ``target[0]``.stdout to the
    ``target`` list.

    The emitter will assume all emitted targets build in the current build directory. If the target(s) must be built in
    a build subdirectory, e.g. in a parameterized target build, then the first target must be provided with the build
    subdirectory, e.g. ``parameter_set1/my_target.ext``. When in doubt, provide a STDOUT redirect file as a target, e.g.
    ``target.stdout``.

    .. code-block::
       :caption: Python script builder action

       cd ${TARGET.dir.abspath} && python ${python_options} ${SOURCE.abspath} ${script_options} > ${TARGETS[-1].abspath} 2>&1

    .. code-block::
       :caption: SConstruct

       import waves
       env = Environment()
       env.Append(BUILDERS={"PythonScript": waves.scons_extensions.python_script()})
       env.PythonScript(target=["my_output.stdout"], source=["my_script.py"], python_options="", script_options="")

    :param list post_action: List of shell command string(s) to append to the builder's action list. Implemented to
        allow post target modification or introspection, e.g. inspect a log for error keywords and throw a
        non-zero exit code even if Python does not. Builder keyword variables are available for substitution in the
        ``post_action`` action using the ``${}`` syntax. Actions are executed in the first target's directory as ``cd
        ${TARGET.dir.abspath} && ${post_action}``

    :return: Python script builder
    :rtype: SCons.Builder.Builder
    """
    action = [f"{_cd_action_prefix} python ${{python_options}} ${{SOURCE.abspath}} " \
                f"${{script_options}} {_redirect_action_postfix}"]
    action.extend(_construct_post_action_list(post_action))
    python_builder = SCons.Builder.Builder(
        action=action,
        emitter=_first_target_emitter
    )
    return python_builder


@catenate_actions(program="sbatch", options=_sbatch_wrapper_options)
def sbatch_python_script(*args, **kwargs):
    """Thin pass through wrapper of :meth:`waves.scons_extensions.python_script`

    Catenate the actions and submit with `SLURM`_ `sbatch`_. Accepts the ``sbatch_options`` builder keyword argument to
    modify sbatch behavior.

    .. code-block::
       :caption: Sbatch Python script builder action

       sbatch --wait --output=${TARGET.base}.slurm.out ${sbatch_options} --wrap "cd ${TARGET.dir.abspath} && python ${python_options} ${SOURCE.abspath} ${script_options} > ${TARGETS[-1].abspath} 2>&1"
    """
    return python_script(*args, **kwargs)


def _matlab_script_emitter(target, source, env):
    """Appends the matlab_script builder target list with the builder managed targets

    Appends ``target[0]``.matlab.env and ``target[0]``.stdout to the ``target`` list. The matlab_script Builder requires
    at least one target. The build tree copy of the Matlab script is not added to the target list to avoid multiply
    defined targets when the script is used more than once in the same build directory.

    The emitter will assume all emitted targets build in the current build directory. If the target(s) must be built in
    a build subdirectory, e.g. in a parameterized target build, then the first target must be provided with the build
    subdirectory, e.g. ``parameter_set1/target.ext``. When in doubt, provide a STDOUT redirect file as a target, e.g.
    ``target.stdout``.

    :param list target: The target file list of strings
    :param list source: The source file list of SCons.Node.FS.File objects
    :param SCons.Script.SConscript.SConsEnvironment env: The builder's SCons construction environment object

    :return: target, source
    :rtype: tuple with two lists
    """
    appending_suffixes = [_matlab_environment_extension]
    return _first_target_emitter(target, source, env, appending_suffixes=appending_suffixes)


def matlab_script(program="matlab", post_action=[], **kwargs):
    """Matlab script SCons builder

    .. warning::

       Experimental implementation is subject to change

    This builder requires that the Matlab script is the first source in the list. The builder returned by this function
    accepts all SCons Builder arguments and adds the keyword argument(s):

    * ``script_options``: The Matlab function interface options in Matlab syntax and provided as a string.
    * ``matlab_options``: The Matlab command line options provided as a string.

    The parent directory absolute path is added to the Matlab ``path`` variable prior to execution. All required Matlab
    files should be co-located in the same source directory.

    At least one target must be specified. The first target determines the working directory for the builder's action,
    as shown in the action code snippet below. The action changes the working directory to the first target's parent
    directory prior to executing the python script.

    The Builder emitter will append the builder managed targets automatically. Appends ``target[0].matlab.env and
    ``target[0]``.stdout to the ``target`` list.

    The emitter will assume all emitted targets build in the current build directory. If the target(s) must be built in
    a build subdirectory, e.g. in a parameterized target build, then the first target must be provided with the build
    subdirectory, e.g. ``parameter_set1/my_target.ext``. When in doubt, provide a STDOUT redirect file as a target, e.g.
    ``target.stdout``.

    .. code-block::
       :caption: Matlab script builder action

       cd ${TARGET.dir.abspath} && {program} ${matlab_options} -batch "path(path, '${SOURCE.dir.abspath}'); ${SOURCE.filebase}(${script_options})" > ${TARGETS[-1].abspath} 2>&1

    :param str program: An absolute path or basename string for the Matlab program.
    :param list post_action: List of shell command string(s) to append to the builder's action list. Implemented to
        allow post target modification or introspection, e.g. inspect a log for error keywords and throw a
        non-zero exit code even if Matlab does not. Builder keyword variables are available for substitution in the
        ``post_action`` action using the ``${}`` syntax. Actions are executed in the first target's directory as ``cd
        ${TARGET.dir.abspath} && ${post_action}``

    :return: Matlab script builder
    :rtype: SCons.Builder.Builder
    """
    # TODO: Remove the **kwargs and matlab_program check for v1.0.0 release
    # https://re-git.lanl.gov/aea/python-projects/waves/-/issues/508
    matlab_program = _warn_kwarg_change(kwargs, "matlab_program")
    program = matlab_program if matlab_program is not None else program
    action = [f"{_cd_action_prefix} {program} ${{matlab_options}} -batch " \
                  "\"path(path, '${SOURCE.dir.abspath}'); " \
                  "[fileList, productList] = matlab.codetools.requiredFilesAndProducts('${SOURCE.file}'); " \
                  "disp(cell2table(fileList)); disp(struct2table(productList, 'AsArray', true)); exit;\" " \
                  f"{_redirect_environment_postfix}",
              f"{_cd_action_prefix} {program} ${{matlab_options}} -batch " \
                  "\"path(path, '${SOURCE.dir.abspath}'); " \
                  "${SOURCE.filebase}(${script_options})\" " \
                  f"{_redirect_action_postfix}"]
    action.extend(_construct_post_action_list(post_action))
    matlab_builder = SCons.Builder.Builder(
        action=action,
        emitter=_matlab_script_emitter)
    return matlab_builder


def conda_environment():
    """Create a Conda environment file with ``conda env export``

    This builder is intended to help WAVES workflows document the Conda environment used in the current build. At least
    one target file must be specified for the ``conda env export --file ${TARGET}`` output. Additional options to the
    Conda ``env export`` subcommand may be passed as the builder keyword argument ``conda_env_export_options``.

    At least one target must be specified. The first target determines the working directory for the builder's action,
    as shown in the action code snippet below. The action changes the working directory to the first target's parent
    directory prior to creating the Conda environment file.

    .. code-block::
       :caption: Conda environment builder action

       cd ${TARGET.dir.abspath} && conda env export ${conda_env_export_options} --file ${TARGET.file}

    The modsim owner may choose to re-use this builder throughout their project configuration to provide various levels
    of granularity in the recorded Conda environment state. It's recommended to include this builder at least once for
    any workflows that also use the :meth:`waves.scons_extensions.python_builder`. The builder may be re-used once per build
    sub-directory to provide more granular build environment reproducibility in the event that sub-builds are run at
    different times with variations in the active Conda environment. For per-Python script task environment
    reproducibility, the builder source list can be linked to the output of a :meth:`waves.scons_extensions.python_builder` task
    with a target environment file name to match.

    The first recommendation, always building the project wide Conda environment file, is demonstrated in the example
    usage below.

    .. code-block::
       :caption: SConstruct

       import waves
       env = Environment()
       env.Append(BUILDERS={"CondaEnvironment": waves.scons_extensions.conda_environment()})
       environment_target = env.CondaEnvironment(target=["environment.yaml"])
       env.AlwaysBuild(environment_target)

    :return: Conda environment builder
    :rtype: SCons.Builder.Builder
    """
    conda_environment_builder = SCons.Builder.Builder(
        action=
            [f"{_cd_action_prefix} conda env export ${{conda_env_export_options}} --file ${{TARGET.file}}"])
    return conda_environment_builder


def _abaqus_extract_emitter(target, source, env):
    """Prepends the abaqus extract builder target H5 file if none is specified. Appends the source[0].csv file unless
    ``delete_report_file`` is ``True``.  Always appends the ``target[0]_datasets.h5`` file.

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
    build_subdirectory = _build_subdirectory(target)
    if not target or pathlib.Path(str(target[0])).suffix != ".h5":
        target.insert(0, str(build_subdirectory / odb_file.with_suffix(".h5")))
    first_target = pathlib.Path(str(target[0]))
    target.append(f"{build_subdirectory / first_target.stem}_datasets.h5")
    if not "delete_report_file" in env or not env["delete_report_file"]:
        target.append(str(build_subdirectory / first_target.with_suffix(".csv").name))
    return target, source


def abaqus_extract(program="abaqus", **kwargs):
    """Abaqus ODB file extraction Builder

    This builder executes the ``odb_extract`` command line utility against an ODB file in the source list. The ODB file
    must be the first file in the source list. If there is more than one ODB file in the source list, all but the first
    file are ignored by ``odb_extract``.

    This builder is unique in that no targets are required. The Builder emitter will append the builder managed targets
    and ``odb_extract`` target name constructions automatically. The first target determines the working directory for
    the emitter targets. If the target(s) must be built in a build subdirectory, e.g. in a parameterized target build,
    then at least one target must be provided with the build subdirectory, e.g. ``parameter_set1/target.h5``. When in
    doubt, provide the expected H5 file as a target, e.g. ``source[0].h5``.

    The target list may specify an output H5 file name that differs from the ODB file base name as ``new_name.h5``. If
    the first file in the target list does not contain the ``*.h5`` extension, or if there is no file in the target
    list, the target list will be prepended with a name matching the ODB file base name and the ``*.h5`` extension.

    The builder emitter appends the CSV file created by the ``abaqus odbreport`` command as executed by
    ``odb_extract`` unless ``delete_report_file`` is set to ``True``.

    This builder supports the keyword arguments: ``output_type``, ``odb_report_args``, ``delete_report_file`` with
    behavior as described in the :ref:`odb_extract_cli` command line interface.

    .. warning::

       ``odb_extract`` *requires* Abaqus arguments for ``odb_report_args`` in the form of ``option=value``, e.g.
       ``step=step_name``.

    .. code-block::
       :caption: SConstruct

       import waves
       env = Environment()
       env["abaqus"] = waves.scons_extensions.add_program(["abaqus"], env)
       env.Append(BUILDERS={"AbaqusExtract": waves.scons_extensions.abaqus_extract()})
       env.AbaqusExtract(target=["my_job.h5", "my_job.csv"], source=["my_job.odb"])

    :param str program: An absolute path or basename string for the abaqus program

    :return: Abaqus extract builder
    :rtype: SCons.Builder.Builder
    """
    # TODO: Remove the **kwargs and abaqus_program check for v1.0.0 release
    # https://re-git.lanl.gov/aea/python-projects/waves/-/issues/508
    abaqus_program = _warn_kwarg_change(kwargs, "abaqus_program")
    program = abaqus_program if abaqus_program is not None else program
    abaqus_extract_builder = SCons.Builder.Builder(
        action = [
            SCons.Action.Action(_build_odb_extract, varlist=["output_type", "odb_report_args", "delete_report_file"])
        ],
        emitter=_abaqus_extract_emitter,
        program=program)
    return abaqus_extract_builder


def _build_odb_extract(target, source, env):
    """Define the odb_extract action when used as an internal package and not a command line utility

    :param list target: The target file list of strings
    :param list source: The source file list of SCons.Node.FS.File objects
    :param SCons.Script.SConscript.SConsEnvironment env: The builder's SCons construction environment object
    """
    # Default odb_extract arguments
    output_type = "h5"
    odb_report_args = None
    delete_report_file = False

    # Grab arguments from environment if they exist
    if "output_type" in env:
        output_type = env["output_type"]
    if "odb_report_args" in env:
        odb_report_args = env["odb_report_args"]
    if "delete_report_file" in env:
        delete_report_file = env["delete_report_file"]

    # Remove existing target files that are not overwritten by odb_extract
    files_to_remove = [pathlib.Path(path.abspath) for path in target]
    for path in files_to_remove:
        path.unlink(missing_ok=True)

    odb_extract.odb_extract([source[0].abspath], target[0].abspath,
                            output_type=output_type,
                            odb_report_args=odb_report_args,
                            abaqus_command=env["program"],
                            delete_report_file=delete_report_file)
    return None


def sbatch(program="sbatch", post_action=[], **kwargs):
    """`SLURM`_ `sbatch`_ SCons builder

    The builder does not use a SLURM batch script. Instead, it requires the ``slurm_job`` variable to be defined with
    the command string to execute.

    At least one target must be specified. The first target determines the working directory for the builder's action,
    as shown in the action code snippet below. The action changes the working directory to the first target's parent
    directory prior to executing the journal file.

    The Builder emitter will append the builder managed targets automatically. Appends ``target[0]``.stdout to the
    ``target`` list.

    .. code-block::
       :caption: SLURM sbatch builder action

       cd ${TARGET.dir.abspath} && sbatch --wait --output=${TARGETS[-1].abspath} ${sbatch_options} --wrap ${slurm_job}

    .. code-block::
       :caption: SConstruct

       import waves
       env = Environment()
       env.Append(BUILDERS={"SlurmSbatch": waves.scons_extensions.sbatch()})
       env.SlurmSbatch(target=["my_output.stdout"], source=["my_source.input"], slurm_job="cat $SOURCE > $TARGET")

    :param str program: An absolute path or basename string for the sbatch program.
    :param list post_action: List of shell command string(s) to append to the builder's action list. Implemented to
        allow post target modification or introspection, e.g. inspect the Abaqus log for error keywords and throw a
        non-zero exit code even if Abaqus does not. Builder keyword variables are available for substitution in the
        ``post_action`` action using the ``${}`` syntax. Actions are executed in the first target's directory as ``cd
        ${TARGET.dir.abspath} && ${post_action}``

    :return: SLURM sbatch builder
    :rtype: SCons.Builder.Builder
    """
    # TODO: Remove the **kwargs and sbatch_program check for v1.0.0 release
    # https://re-git.lanl.gov/aea/python-projects/waves/-/issues/508
    sbatch_program = _warn_kwarg_change(kwargs, "sbatch_program")
    program = sbatch_program if sbatch_program is not None else program
    action = [f"{_cd_action_prefix} {program} --wait --output=${{TARGETS[-1].abspath}} " \
              f"${{sbatch_options}} --wrap \"${{slurm_job}}\""]
    action.extend(_construct_post_action_list(post_action))
    sbatch_builder = SCons.Builder.Builder(
        action=action,
        emitter=_first_target_emitter
    )
    return sbatch_builder


def abaqus_input_scanner():
    """Abaqus input file dependency scanner

    Custom SCons scanner that searches for ``*INCLUDE`` keyword inside Abaqus ``.inp`` files.

    :return: Abaqus input file dependency Scanner
    :rtype: SCons.Scanner.Scanner
    """
    flags = re.IGNORECASE
    return _custom_scanner(r'^\*[^*]*,\s*input=(.+)$', ['.inp'], flags)


def sphinx_scanner():
    """SCons scanner that searches for directives

    * ``.. include::``
    * ``.. literalinclude::``
    * ``.. image::``
    * ``.. figure::``
    * ``.. bibliography::``

    inside ``.rst`` and ``.txt`` files

    :return: Abaqus input file dependency Scanner
    :rtype: SCons.Scanner.Scanner
    """
    return _custom_scanner(r'^\s*\.\. (?:include|literalinclude|image|figure|bibliography)::\s*(.+)$', ['.rst', '.txt'])


def sphinx_build(program="sphinx-build", options="", builder="html", tags=""):
    """Sphinx builder using the ``-b`` specifier

    This builder does not have an emitter. It requires at least one target.

    .. code-block::
       :caption: action

       ${program} ${options} -b ${builder} ${TARGET.dir.dir.abspath} ${TARGET.dir.abspath} ${tags}

    .. code-block::
       :caption: SConstruct

       import waves
       env = Environment()
       env.Append(BUILDERS={
           "SphinxBuild": waves.scons_extensions.sphinx_build(options="-W"),
       })
       sources = ["conf.py", "index.rst"]
       targets = ["html/index.html"]
       html = env.SphinxBuild(
           target=targets,
           source=sources,
       )
       env.Clean(html, [Dir("html")] + sources)
       env.Alias("html", html)

    :param str program: sphinx-build executable
    :param str options: sphinx-build options
    :param str builder: builder name. See the `Sphinx`_ documentation for options
    :param str tags: sphinx-build tags
    """
    sphinx_builder = SCons.Builder.Builder(
        action=["${program} ${options} -b ${builder} ${TARGET.dir.dir.abspath} ${TARGET.dir.abspath} ${tags}"],
        program=program,
        options=options,
        builder=builder,
        tags=tags
    )
    return sphinx_builder


def sphinx_latexpdf(program="sphinx-build", options="", builder="latexpdf", tags=""):
    """Sphinx builder using the ``-M`` specifier. Intended for ``latexpdf`` builds.

    This builder does not have an emitter. It requires at least one target.

    .. code-block::
       :caption: action

       ${program} -M ${builder} ${TARGET.dir.dir.abspath} ${TARGET.dir.dir.abspath} ${tags} ${options}"

    .. code-block::
       :caption: SConstruct

       import waves
       env = Environment()
       env.Append(BUILDERS={
           "SphinxPDF": waves.scons_extensions.sphinx_latexpdf(options="-W"),
       })
       sources = ["conf.py", "index.rst"]
       targets = ["latex/project.pdf"]
       latexpdf = env.SphinxBuild(
           target=targets,
           source=sources,
       )
       env.Clean(latexpdf, [Dir("latex")] + sources)
       env.Alias("latexpdf", latexpdf)

    :param str program: sphinx-build executable
    :param str options: sphinx-build options
    :param str builder: builder name. See the `Sphinx`_ documentation for options
    :param str tags: sphinx-build tags
    """
    sphinx_latex = SCons.Builder.Builder(
        action=["${program} -M ${builder} ${TARGET.dir.dir.abspath} ${TARGET.dir.dir.abspath} ${tags} ${options}"],
        program=program,
        options=options,
        builder=builder,
        tags=tags
    )
    return sphinx_latex


def _custom_scanner(pattern, suffixes, flags=None):
    """Custom Scons scanner

    constructs a scanner object based on a regular expression pattern. Will only search for files matching the list of
    suffixes provided. ``_custom_scanner`` will always use the ``re.MULTILINE`` flag
    https://docs.python.org/3/library/re.html#re.MULTILINE

    :param str pattern: Regular expression pattern.
    :param list suffixes: List of suffixes of files to search
    :param int flags: An integer representing the combination of re module flags to be used during compilation.
                      Additional flags can be combined using the bitwise OR (|) operator. The re.MULTILINE flag is
                      automatically added to the combination.

    :return: Custom Scons scanner
    :rtype: Scons.Scanner.Scanner
    """
    flags = re.MULTILINE if not flags else re.MULTILINE | flags
    expression = re.compile(pattern, flags)

    def suffix_only(node_list):
        """Recursively search for files that end in the given suffixes

        :param list node_list: List of SCons Node objects representing the nodes to process

        :return: List of file dependencies to include for recursive scanning
        :rtype: list
        """
        return [node for node in node_list if node.path.endswith(tuple(suffixes))]

    def regex_scan(node, env, path):
        """Scan function for extracting dependencies from the content of a file based on the given regular expression.

        The interface of the scan function is fixed by SCons. It must include ``node``, ``env`` and ``path``. It may
        contain additional arguments if needed. For more information please read the SCons Scanner tutorial:
        https://scons.org/doc/1.2.0/HTML/scons-user/c3755.html

        :param SCons.Node.FS node: SCons Node object representing the file to scan
        :param SCons.Environment.Environment env: SCons Environment object
        :param str path: Path argument passed to the scan function

        :return: List of file dependencies found during scanning
        :rtype: list
        """
        contents = node.get_text_contents()
        includes = expression.findall(contents)
        includes = [file.strip() for file in includes]
        return includes

    custom_scanner = SCons.Scanner.Scanner(function=regex_scan, skeys=suffixes, recursive=suffix_only)
    return custom_scanner


def quinoa_solver(charmrun="charmrun", inciter="inciter", charmrun_options="+p1", inciter_options="",
                  prefix_command="", post_action=[]):
    """Quinoa solver SCons builder

    This builder requires at least two source files provided in the order

    1. Quinoa control file: ``*.q``
    2. Exodus mesh file: ``*.exo``

    The builder returned by this function accepts all SCons Builder arguments.  Except for the ``post_action``, the
    arguments of this function are also available as keyword arguments of the builder. When provided during task
    definition, the keyword arguments override the builder returned by this function.

    The first target determines the working directory for the builder's action, as shown in the action code snippet
    below. The action changes the working directory to the first target's parent directory prior to executing quinoa.

    The emitter will assume all emitted targets build in the current build directory. If the target(s) must be built in
    a build subdirectory, e.g. in a parameterized target build, then the first target must be provided with the build
    subdirectory, e.g. ``parameter_set1/target.ext``. When in doubt, provide a STDOUT redirect file as a target, e.g.
    ``target.stdout``.

    .. warning::

       This is an experimental builder for Quinoa support. The only emitted file is the ``target[0].stdout`` redirected
       STDOUT and STDERR file. All relevant application output files, e.g. ``out.*`` must be specified in the target list.

    .. code-block::
       :caption: SConstruct

       import waves
       env = waves.scons_extensions.shell_environment("module load quinoa")
       env.Append(BUILDERS={
           "QuinoaSolver": waves.scons_extensions.quinoa_solver(charmrun_options="+p1"),
       })
       # Serial execution with "+p1"
       env.QuinoaSolver(target=["flow.stdout"], source=["flow.q", "box.exo"])
       # Parallel execution with "+p4"
       env.QuinoaSolver(target=["flow.stdout"], source=["flow.q", "box.exo"], charmrun_options="+p4")

    .. code-block::
       :caption: Quinoa builder action

       ${prefix_command} ${TARGET.dir.abspath} && ${charmrun} ${charmrun_options} ${inciter} ${inciter_options} --control ${SOURCES[0].abspath} --input ${SOURCES[1].abspath} > ${TARGETS[-1].abspath} 2>&1

    :param str charmrun: The relative or absolute path to the charmrun executable
    :param str charmrun_options: The charmrun command line interface options
    :param str inciter: The relative or absolute path to the inciter (quinoa) executable
    :param str inciter_options: The inciter (quinoa executable) command line interface options
    :param str prefix_command: Optional prefix command intended for environment preparation. Primarily intended for use
        with :meth:`waves.scons_extensions.sbatch_quinoa_solver` or when wrapping the builder with
        :meth:`waves.scons_extensions.ssh_builder_actions`. For local, direct execution, user's should prefer to create
        an SCons construction environment with :meth:`waves.scons_extensions.shell_environment`. When overriding in a
        task definition, the prefix command *must* end with ``' &&'``.
    :param list post_action: List of shell command string(s) to append to the builder's action list. Implemented to
        allow post target modification or introspection, e.g. inspect the Abaqus log for error keywords and throw a
        non-zero exit code even if Abaqus does not. Builder keyword variables are available for substitution in the
        ``post_action`` action using the ``${}`` syntax. Actions are executed in the first target's directory as ``cd
        ${TARGET.dir.abspath} && ${post_action}``

    :return: Quinoa builder
    :rtype: SCons.Builder.Builder
    """
    if prefix_command and not prefix_command.strip().endswith(" &&"):
        prefix_command = prefix_command.strip()
        prefix_command += " &&"
    action=[
        f"${{prefix_command}} {_cd_action_prefix} ${{charmrun}} ${{charmrun_options}} " \
            "${inciter} ${inciter_options} --control ${SOURCES[0].abspath} --input ${SOURCES[1].abspath} " \
            f"{_redirect_action_postfix}"
    ]
    action.extend(_construct_post_action_list(post_action))
    quinoa_builder = SCons.Builder.Builder(
        action=action,
        emitter=_first_target_emitter,
        prefix_command=prefix_command,
        charmrun=charmrun,
        charmrun_options=charmrun_options,
        inciter=inciter,
        inciter_options=inciter_options
    )
    return quinoa_builder


@catenate_actions(program="sbatch", options=_sbatch_wrapper_options)
def sbatch_quinoa_solver(*args, **kwargs):
    """Thin pass through wrapper of :meth:`waves.scons_extensions.quinoa_solver`

    Catenate the actions and submit with `SLURM`_ `sbatch`_. Accepts the ``sbatch_options`` builder keyword argument to
    modify sbatch behavior.

    .. code-block::
       :caption: Sbatch Quinoa solver builder action

       sbatch --wait --output=${TARGET.base}.slurm.out ${sbatch_options} --wrap ""
    """
    return quinoa_solver(*args, **kwargs)
