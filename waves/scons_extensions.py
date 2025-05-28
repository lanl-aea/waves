import re
import sys
import copy
import atexit
import shutil
import typing
import pathlib
import warnings
import functools
import collections

import SCons.Node
import SCons.Script
import SCons.Builder
import SCons.Scanner
import SCons.Defaults
import SCons.Environment
from SCons.Script.SConscript import SConsEnvironment

from waves import _settings
from waves import _utilities


_exclude_from_namespace = set(globals().keys())


def print_action_signature_string(s, target, source, env) -> None:
    """Print the action string used to calculate the action signature

    Designed to behave similarly to SCons ``--debug=presub`` option using ``PRINT_CMD_LINE_FUNC`` feature:
    https://scons.org/doc/production/HTML/scons-man.html#cv-PRINT_CMD_LINE_FUNC

    .. code-block::
       :caption: SConstruct

       import waves
       env = Environment(PRINT_CMD_LINE_FUNC=waves.scons_extensions.print_action_signature_string)
       env.Command(
           target=["target.txt"],
           source=["SConstruct"],
           action=["echo 'Hello World!' > ${TARGET.relpath}"]
       )

       .. code-block::
          :caption: shell

          $ scons target.txt
          scons: Reading SConscript files ...
          scons: done reading SConscript files.
          scons: Building targets ...
          Building target.txt with action signature string:
            echo 'Hello World!' > target.txt_relpath
          echo 'Hello World!' > target.txt
          scons: done building targets.
    """
    try:
        action_signature_string = target[0].get_executor().get_contents().decode()
    except UnicodeDecodeError:
        action_signature_string = target[0].get_executor().get_contents()
    target_text = " and ".join([str(node) for node in target])
    print(f"Building {target_text} with action signature string:\n  {action_signature_string}\n{s}")
    return


def _print_failed_nodes_stdout() -> None:
    """Query the SCons reported build failures and print the associated node's STDOUT file, if it exists"""
    build_failures = SCons.Script.GetBuildFailures()
    for failure in build_failures:
        node_path = pathlib.Path(failure.node.abspath)
        stdout_path_options = [
            node_path.parent / f"{node_path}{_settings._stdout_extension}",
            node_path.with_suffix(_settings._stdout_extension),
        ]
        stdout_path_options = [path.resolve() for path in stdout_path_options]
        try:
            stdout_path = next((path for path in stdout_path_options if path.exists()))
            with open(stdout_path, "r") as stdout_file:
                print(
                    f"\n{failure.node} failed with STDOUT file '{stdout_path}'\n{stdout_file.read()}", file=sys.stderr
                )
        except StopIteration:
            print(f"\n{failure.node} failed\n", file=sys.stderr)


def print_build_failures(
    env: SCons.Environment.Environment = SCons.Environment.Environment(),
    print_stdout: bool = True,
) -> None:
    """On exit, query the SCons reported build failures and print the associated node's STDOUT file, if it exists

    .. code-block::
       :caption: SConstruct

       AddOption(
           "--print-build-failures",
           dest="print_build_failures",
           default=False,
           action="store_true",
           help="Print task *.stdout target file(s) on build failures. (default: '%default')"
       )
       env = Environment(
           print_build_failures=GetOption("print_build_failures")
       )
       env.AddMethod(waves.scons_extensions.print_build_failures, "PrintBuildFailures")
       env.PrintBuildFailures(print_stdout=env["print_build_failures"])

    :param env: SCons construction environment
    :param print_stdout: Boolean to set the exit behavior. If False, don't modify the exit behavior.
    """
    if print_stdout:
        atexit.register(_print_failed_nodes_stdout)


def action_list_scons(actions: typing.Iterable[str]) -> SCons.Action.ListAction:
    """Convert a list of action strings to an SCons.Action.ListAction object

    :param actions: List of action strings

    :returns: SCons.Action.ListAction object of SCons.Action.CommandAction
    """
    command_actions = [SCons.Action.CommandAction(action) for action in actions]
    return SCons.Action.ListAction(command_actions)


def action_list_strings(builder: SCons.Builder.Builder) -> typing.List[str]:
    """Return a builder's action list as a list of str

    :param builder: The builder to extract the action list from

    :returns: list of builder actions
    """
    action = builder.action
    if isinstance(action, SCons.Action.CommandAction):
        action_list = [action.cmd_list]
    else:
        action_list = [command.cmd_list for command in action.list]
    return action_list


def catenate_builder_actions(
    builder: SCons.Builder.Builder,
    program: str = "",
    options: str = "",
) -> SCons.Builder.Builder:
    """Catenate a builder's arguments and prepend the program and options

    .. code-block::

       ${program} ${options} "action one && action two"

    :param builder: The SCons builder to modify
    :param program: wrapping executable
    :param options: options for the wrapping executable

    :returns: modified builder
    """
    action_list = action_list_strings(builder)
    action = " && ".join(action_list)
    action = f'{program} {options} "{action}"'
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


def ssh_builder_actions(
    builder: SCons.Builder.Builder,
    remote_server: str = "",
    remote_directory: str = "",
    rsync_push_options: str = "-rlptv",
    rsync_pull_options: str = "-rlptv",
    ssh_options: str = "",
) -> SCons.Builder.Builder:
    """Wrap and modify a builder's action list with remote copy operations and SSH commands

    .. warning::

       This builder does *not* provide asynchronous server-client behavior. The local/client machine must maintain the
       SSH connection continuously throughout the duration of the task. If the SSH connection is interrupted, the task
       will fail. This makes SSH wrapped builders fragile with respect to network connectivity. Users are strongly
       encouraged to seek solutions that allow full software installation and full workflow execution on the
       target compute server. If mixed server execution is required, a build directory on a shared network drive
       and interrupted workflow execution should be preferred over SSH wrapped builders.

    If the remote server and remote directory strings are not specified at builder instantation, then the task
    definitions *must* specify these keyword arguments. If a portion of the remote server and/or remote directory are
    known to be constant across all possible tasks, users may define their own substitution keyword arguments. For
    example, the following remote directory uses common leading path elements and introduces a new keyword variable
    ``task_directory`` to allow per-task changes to the remote directory:
    ``remote_directory="/path/to/base/build/${task_directory}"``.

    .. include:: ssh_builder_actions_warning.txt

    *Builder/Task keyword arguments*

    * ``remote_server``: remote server where the original builder's actions should be executed
    * ``remote_directory``: absolute or relative path where the original builder's actions should be executed.
    * ``rsync_push_options``: rsync options when pushing sources to the remote server
    * ``rsync_pull_options``: rsync options when pulling remote directory from the remote server
    * ``ssh_options``: SSH options when running the original builder's actions on the remote server

    Design assumptions

    * Creates the ``remote_directory`` with ``mkdir -p``. ``mkdir`` must exist on the ``remote_server``.
    * Copies all source files to a flat ``remote_directory`` with ``rsync``. ``rsync`` must exist on the local system.
    * Replaces instances of ``cd ${TARGET.dir.abspath} &&`` with ``cd ${remote_directory} &&`` in the original builder
      actions and keyword arguments.
    * Replaces instances of ``SOURCE.abspath`` or ``SOURCES.abspath`` with ``SOURCE[S].file`` in the original builder
      actions and keyword arguments.
    * Replaces instances of ``SOURCES[0-9]/TARGETS[0-9].abspath`` with  ``SOURCES[0-9]/TARGETS[0-9].file`` in the
      original builder action and keyword arguments.
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
               waves.scons_extensions.abaqus_solver(
                   program="/remote/server/installation/path/of/abaqus"
               ),
               remote_server="myserver.mydomain.com",
               remote_directory="/scratch/${user}/myproject/myworkflow/${task_directory}"
           )
       })
       env.SSHAbaqusSolver(
           target=["myjob.sta"],
           source=["input.inp"],
           job_name="myjob",
           abaqus_options="-cpus 4",
           task_directory="myjob",
           user=user
       )

    .. code-block::
       :caption: my_package.py

       import SCons.Builder
       import waves

       def print_builder_actions(builder):
           for action in builder.action.list:
               print(action.cmd_list)

       def cat():
           builder = SCons.Builder.Builder(
               action=[
                   "cat ${SOURCES.abspath} | tee ${TARGETS[0].abspath}", "echo \\"Hello World!\\""
               ]
           )
           return builder

       build_cat = cat()

       ssh_build_cat = waves.scons_extensions.ssh_builder_actions(
           cat(), remote_server="myserver.mydomain.com", remote_directory="/scratch/roppenheimer/ssh_wrapper"
       )

    .. code-block::

       >>> import my_package
       >>> my_package.print_builder_actions(my_package.build_cat)
       cat ${SOURCES.abspath} | tee ${TARGETS[0].abspath}
       echo "Hello World!"
       >>> my_package.print_builder_actions(my_package.ssh_build_cat)
       ssh ${ssh_options} ${remote_server} "mkdir -p /scratch/roppenheimer/ssh_wrapper"
       rsync ${rsync_push_options} ${SOURCES.abspath} ${remote_server}:${remote_directory}
       ssh ${ssh_options} ${remote_server} 'cd ${remote_directory} && cat ${SOURCES.file} | tee ${TARGETS[0].file}'
       ssh ${ssh_options} ${remote_server} 'cd ${remote_directory} && echo "Hello World!"'
       rsync ${rsync_pull_options} ${remote_server}:${remote_directory} ${TARGET.dir.abspath}

    :param builder: The SCons builder to modify
    :param remote_server: remote server where the original builder's actions should be executed
    :param remote_directory: absolute or relative path where the original builder's actions should be executed.
    :param rsync_push_options: rsync options when pushing sources to the remote server
    :param rsync_pull_options: rsync options when pulling remote directory from the remote server
    :param ssh_options: SSH options when running the original builder's actions on the remote server

    :returns: modified builder
    """
    cd_prefix = "cd ${remote_directory} &&"

    def ssh_action_substitutions(action: str, cd_prefix: str = cd_prefix) -> str:
        """Perform the SSH action string substitutions

        :param action: The original action string
        :param cd_prefix: The SSH remote directory ``cd`` operation

        :returns: Modified action string with SSH action substitutions
        """
        action = action.replace("cd ${TARGET.dir.abspath} &&", cd_prefix)
        action = action.replace("SOURCE.abspath", "SOURCE.file")
        action = action.replace("SOURCES.abspath", "SOURCES.file")
        action = re.sub(r"(SOURCES\[[-0-9]+\])\.abspath", r"\1.file", action)
        action = re.sub(r"(TARGETS\[[-0-9]+\])\.abspath", r"\1.file", action)
        return action

    # Retrieve original builder actions and modify for design assumptions
    action_list = action_list_strings(builder)
    action_list = [ssh_action_substitutions(action) for action in action_list]
    action_list = [
        (
            f"{cd_prefix} {action}"
            if not action.startswith(cd_prefix) and not action.startswith("${action_prefix}")
            else action
        )
        for action in action_list
    ]
    action_list = [f"ssh ${{ssh_options}} ${{remote_server}} '{action}'" for action in action_list]

    # Pre/Append SSH wrapper actions
    ssh_actions = [
        'ssh ${ssh_options} ${remote_server} "mkdir -p ${remote_directory}"',
        "rsync ${rsync_push_options} ${SOURCES.abspath} ${remote_server}:${remote_directory}",
    ]
    ssh_actions.extend(action_list)
    ssh_actions.append("rsync ${rsync_pull_options} ${remote_server}:${remote_directory}/ ${TARGET.dir.abspath}")

    # Override oroginal builder actions with SSH wrapped action updates
    builder.action = action_list_scons(ssh_actions)

    # Modify builder keyword arguments for design assumptions
    for key, value in builder.overrides.items():
        builder.overrides[key] = ssh_action_substitutions(value)

    # Add or override builder keyword arguments with SSH wrapper added keyword arguments
    builder.overrides.update(
        {
            "remote_server": remote_server,
            "remote_directory": remote_directory,
            "rsync_push_options": rsync_push_options,
            "rsync_pull_options": rsync_pull_options,
            "ssh_options": ssh_options,
        }
    )

    return builder


def project_help(
    env: SCons.Environment.Environment = SCons.Environment.Environment(),
    append: bool = True,
    local_only: bool = True,
    target_descriptions: typing.Optional[dict] = None,
) -> None:
    """Add default targets and alias lists to project help message

    See the `SCons Help`_ documentation for appending behavior. Thin wrapper around

    * :meth:`waves.scons_extensions.project_help_default_targets`
    * :meth:`waves.scons_extensions.project_help_aliases`

    :param env: The SCons construction environment object to modify
    :param append: append to the ``env.Help`` message (default). When False, the ``env.Help`` message will be
        overwritten if ``env.Help`` has not been previously called.
    :param local_only: Limit help message to the project specific content when True. Only applies to SCons >=4.6.0
    :param target_descriptions: dictionary containing target metadata.
    """
    project_help_default_targets(env=env, append=append, local_only=local_only, target_descriptions=target_descriptions)
    project_help_aliases(env=env, append=append, local_only=local_only, target_descriptions=target_descriptions)


def project_help_default_targets(
    env: SCons.Environment.Environment = SCons.Environment.Environment(),
    append: bool = True,
    local_only: bool = True,
    target_descriptions: typing.Optional[dict] = None,
) -> None:
    """Add a default targets list to the project's help message

    See the `SCons Help`_ documentation for appending behavior. Adds text to the project help message formatted as

    .. code-block::

       Default Targets:
           Default_Target_1
           Default_Target_2

    where the targets are recovered from ``SCons.Script.DEFAULT_TARGETS``.

    :param env: The SCons construction environment object to modify
    :param append: append to the ``env.Help`` message (default). When False, the ``env.Help`` message will be
        overwritten if ``env.Help`` has not been previously called.
    :param local_only: Limit help message to the project specific content when True. Only applies to SCons >=4.6.0
    :param target_descriptions: dictionary containing target metadata.
    """
    default_targets_help = _project_help_descriptions(
        SCons.Script.DEFAULT_TARGETS, message="\nDefault Targets:\n", target_descriptions=target_descriptions
    )
    try:
        # SCons >=4.9.0
        SConsEnvironment.Help(env, default_targets_help, append=append, local_only=local_only)
    except TypeError as err:
        try:
            # SCons >=4.6,<4.9.0
            SConsEnvironment.Help(env, default_targets_help, append=append, keep_local=local_only)
        except TypeError as err:
            # SCons <4.6
            SConsEnvironment.Help(env, default_targets_help, append=append)


def project_help_aliases(
    env: SCons.Environment.Environment = SCons.Environment.Environment(),
    append: bool = True,
    local_only: bool = True,
    target_descriptions: typing.Optional[dict] = None,
) -> None:
    """Add the alias list to the project's help message

    See the `SCons Help`_ documentation for appending behavior. Adds text to the project help message formatted as

    .. code-block::

       Target Aliases:
           Alias_1
           Alias_2

    where the aliases are recovered from ``SCons.Node.Alias.default_ans``.

    :param env: The SCons construction environment object to modify
    :param append: append to the ``env.Help`` message (default). When False, the ``env.Help`` message will be
        overwritten if ``env.Help`` has not been previously called.
    :param local_only: Limit help message to the project specific content when True. Only applies to SCons >=4.6.0
    :param target_descriptions: dictionary containing target metadata.
    """
    alias_help = _project_help_descriptions(
        SCons.Node.Alias.default_ans, message="\nTarget Aliases:\n", target_descriptions=target_descriptions
    )
    try:
        # SCons >=4.9.0
        SConsEnvironment.Help(env, alias_help, append=append, local_only=local_only)
    except TypeError:
        try:
            # SCons >=4.6,<4.9.0
            SConsEnvironment.Help(env, alias_help, append=append, keep_local=local_only)
        except TypeError:
            # SCons <4.6
            SConsEnvironment.Help(env, alias_help, append=append)


def project_alias(
    env: SCons.Environment.Environment = None,
    *args,
    description: str = "",
    target_descriptions: dict = dict(),
    **kwargs,
) -> dict:
    """Wrapper around the `SCons Alias`_ method. Appends and returns target descriptions dictionary.

    :param env: The SCons construction environment object to modify.
    :param args: All other positional arguments are passed to the `SCons Alias`_ method.
    :param description: String representing metadata of the alias.
    :param target_descriptions: Mutable dictionary used to keep track of all alias's metadata. If the function is
        called with a user-supplied dictionary, the accumulated target descriptions are reset to match the provided
        dictionary and all previously accumulated descriptions are discarded. If an existing alias is called it will
        overwrite the previous description.
    :param kwargs: All other keyword arguments are passed to the `SCons Alias`_ method.

    :returns: target descriptions dictionary
    """
    if len(args) >= 1 and args[0] is not None:
        nodes = env.Alias(*args, **kwargs)
        new_target_descriptions = {str(node): description for node in nodes}
        target_descriptions.update(new_target_descriptions)
    return target_descriptions


def _project_help_descriptions(
    nodes: SCons.Node.NodeList, target_descriptions: typing.Optional[dict] = None, message=""
) -> str:
    """Return a help message for all nodes found in the alias and target descriptions

    Alias descriptions are returned from the :meth:`project_alias`. When both the alias and target descriptions
    describe the same node, the provided target description dictionary is used.

    :param nodes: SCons node objects, e.g. targets and aliases.
    :param target_descriptions: dictionary containing description of targets. Will use project_alias() return value
        if not specified.
    :param message: current help message.

    :returns: appended help message
    """
    alias_descriptions = project_alias()
    if target_descriptions is None:
        target_descriptions = {}
    descriptions = {**alias_descriptions, **target_descriptions}
    keys = [str(node) for node in nodes]
    for key in keys:
        if key in descriptions.keys():
            message += f"    {key}: {descriptions[key]}\n"
        else:
            message += f"    {key}\n"
    return message


def substitution_syntax(
    env: SCons.Environment.Environment,
    substitution_dictionary: dict,
    prefix: str = "@",
    suffix: str = "@",
) -> dict:
    """Return a dictionary copy with the pre/suffix added to the key strings

    Assumes a flat dictionary with keys of type str. Keys that aren't strings will be converted to their string
    representation. Nested dictionaries can be supplied, but only the first layer keys will be modified. Dictionary
    values are unchanged.

    .. code-block::
       :caption: SConstruct

       env = Environment()
       env.AddMethod(waves.scons_extensions.substitution_syntax, "SubstitutionSyntax")
       original_dictionary = {"key": "value"}
       substitution_dictionary = env.SubstitutionSyntax(original_dictionary)

    :param dict substitution_dictionary: Original dictionary to copy
    :param string prefix: String to prepend to all dictionary keys
    :param string suffix: String to append to all dictionary keys

    :return: Copy of the dictionary with key strings modified by the pre/suffix
    """
    return {f"{prefix}{key}{suffix}": value for key, value in substitution_dictionary.items()}


def check_program(
    env: SCons.Environment.Environment,
    prog_name: str,
) -> str:
    """Replacement for `SCons CheckProg`_ like behavior without an SCons configure object

    .. code-block::
       :caption: Example search for an executable named "program"

       import waves

       env = Environment()
       env.AddMethod(waves.scons_extensions.check_program, "CheckProgram")
       env["PROGRAM"] = env.CheckProgram(["program"])

    :param env: The SCons construction environment object to modify
    :param prog_name: string program name to search in the construction environment path
    """
    absolute_path = shutil.which(prog_name, path=env["ENV"]["PATH"])
    string_program = absolute_path if absolute_path is not None else "no"
    print(f"Checking whether '{prog_name}' program exists...{string_program}")
    return absolute_path


def append_env_path(
    env: SCons.Environment.Environment,
    program: str,
) -> None:
    """Append SCons contruction environment ``PATH`` with the program's parent directory

    Uses the `SCons AppendENVPath`_ method. If the program parent directory is already on ``PATH``, the ``PATH``
    directory order is preserved.

    .. code-block::
       :caption: Example environment modification

       import waves

       env = Environment()
       env["PROGRAM"] = waves.scons_extensions.find_program(env, ["program"])
       if env["PROGRAM"]:
           waves.append_env_path(env, env["PROGRAM"])

    :param env: The SCons construction environment object to modify
    :param program: An absolute path for the program to add to SCons construction environment ``PATH``

    :raises FileNotFoundError: if the ``program`` absolute path does not exist.
    """
    program = pathlib.Path(program).resolve()
    if not program.exists():
        raise FileNotFoundError(f"The program '{program}' does not exist.")
    env.AppendENVPath("PATH", str(program.parent), delete_existing=False)


def find_program(
    env: SCons.Environment.Environment,
    names: typing.Iterable[str],
) -> str:
    """Search for a program from a list of possible program names.

    Returns the absolute path of the first program name found. If path parts contain spaces, the part will be wrapped in
    double quotes.

    .. code-block::
       :caption: Example search for an executable named "program"

       import waves

       env = Environment()
       env.AddMethod(waves.scons_extensions.find_program, "FindProgram")
       env["PROGRAM"] = env.FindProgram(["program"])

    :param env: The SCons construction environment object to modify
    :param names: list of string program names. May include an absolute path.

    :return: Absolute path of the found program. None if none of the names are found.
    """
    if isinstance(names, str):
        names = [names]
    program_paths = []
    for name in names:
        program_paths.append(check_program(env, name))
    # Return first non-None path. Default to None if no program path was found.
    first_found_path = next((path for path in program_paths if path is not None), None)
    if first_found_path:
        first_found_path = str(_utilities._quote_spaces_in_path(first_found_path))

    return first_found_path


def add_program(
    env: SCons.Environment.Environment,
    names: typing.Iterable[str],
) -> str:
    """Search for a program from a list of possible program names. Add first found to system ``PATH``.

    Returns the absolute path of the first program name found. Appends ``PATH`` with first program's parent directory
    if a program is found and the directory is not already on ``PATH``. Returns None if no program name is found.

    .. code-block::
       :caption: Example search for an executable named "program"

       import waves

       env = Environment()
       env.AddMethod(waves.scons_extensions.add_program, "AddProgram")
       env["PROGRAM"] = env.AddProgram(["program"])

    :param env: The SCons construction environment object to modify
    :param names: list of string program names. May include an absolute path.

    :return: Absolute path of the found program. None if none of the names are found.
    """
    first_found_path = find_program(env, names)
    if first_found_path:
        append_env_path(env, first_found_path)
    return first_found_path


def add_cubit(
    env: SCons.Environment.Environment,
    names: typing.Iterable[str],
) -> str:
    """Modifies environment variables with the paths required to ``import cubit`` in a Python3 environment.

    Returns the absolute path of the first program name found. Appends ``PATH`` with first program's parent directory if
    a program is found and the directory is not already on ``PATH``. Prepends ``PYTHONPATH`` with ``parent/bin``.
    Prepends ``LD_LIBRARY_PATH`` with ``parent/bin/python3``.

    Returns None if no program name is found.

    .. code-block::
       :caption: Example Cubit environment modification

       import waves

       env = Environment()
       env.AddMethod(waves.scons_extensions.add_cubit, "AddCubit")
       env["CUBIT_PROGRAM"] = env.AddCubit(["cubit"])

    :param env: The SCons construction environment object to modify
    :param names: list of string program names for the main Cubit executable. May include an absolute path.

    :return: Absolute path of the Cubit executable. None if none of the names are found.
    """
    first_found_path = add_program(env, names)
    if first_found_path:
        cubit_bin = _utilities.find_cubit_bin([first_found_path])
        cubit_python_library_dir = cubit_bin / "python3"
        env.PrependENVPath("PYTHONPATH", str(cubit_bin))
        env.PrependENVPath("LD_LIBRARY_PATH", str(cubit_python_library_dir))
    return first_found_path


def add_cubit_python(
    env: SCons.Environment.Environment,
    names: typing.Iterable[str],
) -> str:
    """Modifies environment variables with the paths required to ``import cubit`` with the Cubit Python interpreter.

    Returns the absolute path of the first Cubit Python intepreter found. Appends ``PATH`` with Cubit Python parent
    directory if a program is found and the directory is not already on ``PATH``. Prepends ``PYTHONPATH`` with
    ``parent/bin``.

    Returns None if no Cubit Python interpreter is found.

    .. code-block::
       :caption: Example Cubit environment modification

       import waves

       env = Environment()
       env.AddMethod(waves.scons_extensions.add_cubit_python, "AddCubitPython")
       env["CUBIT_PROGRAM"] = env.AddCubitPython(["cubit"])

    :param env: The SCons construction environment object to modify
    :param names: list of string program names for the main Cubit executable. May include an absolute path.

    :return: Absolute path of the Cubit Python intepreter. None if none of the names are found.
    """
    first_found_path = find_program(env, names)
    cubit_python = _utilities.find_cubit_python([first_found_path])
    cubit_python = add_program(env, [cubit_python])
    if cubit_python:
        cubit_bin = _utilities.find_cubit_bin([first_found_path])
        env.PrependENVPath("PYTHONPATH", str(cubit_bin))
    return cubit_python


def shell_environment(
    command: str,
    shell: str = "bash",
    cache: typing.Optional[str] = None,
    overwrite_cache: bool = False,
) -> SCons.Environment.Environment:
    """Return an SCons shell environment from a cached file or by running a shell command

    If the environment is created successfully and a cache file is requested, the cache file is _always_ written. The
    ``overwrite_cache`` behavior forces the shell ``command`` execution, even when the cache file is present. If the
    ``command`` fails (raising a ``subprocess.CalledProcessError``) the captured output is printed to STDERR before
    re-raising the exception.

    .. warning::

       Currently assumes a nix flavored shell: sh, bash, zsh, csh, tcsh. May work with any shell supporting command
       construction as below.

       .. code-block::

          {shell} -c "{command} && env -0"

       The method may fail if the command produces stdout that does not terminate in a newline. Redirect command output
       away from stdout if this causes problems, e.g. ``command = 'command > /dev/null && command two > /dev/null'`` in
       most shells.

    .. code-block::
       :caption: SConstruct

       import waves
       env = waves.scons_extensions.shell_environment("source my_script.sh")

    :param command: the shell command to execute
    :param shell: the shell to use when executing command by absolute or relative path
    :param cache: absolute or relative path to read/write a shell environment dictionary. Will be written as YAML
        formatted file regardless of extension.
    :param overwrite_cache: Ignore previously cached files if they exist.

    :returns: SCons shell environment

    :raises subprocess.CalledProcessError: Print the captured output and re-raise exception when the shell command
        returns a non-zero exit status.
    """
    shell_environment = _utilities.cache_environment(
        command,
        shell=shell,
        cache=cache,
        overwrite_cache=overwrite_cache,
        verbose=True,
    )
    return SCons.Environment.Environment(ENV=shell_environment)


def construct_action_list(
    actions: typing.Iterable[str],
    prefix: str = "${action_prefix}",
    suffix: str = "",
) -> typing.Iterable[str]:
    """Return an action list with a common pre/post-fix

    Returns the constructed action list with pre/post fix strings as

    .. code-block::

       f"{prefix} {new_action} {suffix}"

    where SCons action objects are converted to their string representation. If a string is passed instead of a list, it
    is first converted to a list. If an empty list is passed, and empty list is returned.

    :param actions: List of action strings
    :param prefix: Common prefix to prepend to each action
    :param suffix: Common suffix to append to each action

    :return: action list
    """
    if isinstance(actions, str):
        actions = [actions]
    try:
        iterator = iter(actions)
    except TypeError:
        iterator = iter([actions])
    if prefix:
        prefix = prefix + " "
    if suffix:
        suffix = " " + suffix
    new_actions = [f"{prefix}{action}{suffix}" for action in iterator]
    return new_actions


def _build_subdirectory(target: list) -> pathlib.Path:
    """Return the build subdirectory of the first target file

    :param target: The target file list of strings

    :return: build directory
    """
    try:
        build_subdirectory = pathlib.Path(str(target[0])).parent
    except IndexError as err:
        build_subdirectory = pathlib.Path(".")
    return build_subdirectory


def builder_factory(
    environment: str = "",
    action_prefix: str = "",
    program: str = "",
    program_required: str = "",
    program_options: str = "",
    subcommand: str = "",
    subcommand_required: str = "",
    subcommand_options: str = "",
    action_suffix: str = "",
    emitter=None,
    **kwargs,
) -> SCons.Builder.Builder:
    """Template builder factory returning a builder with no emitter

    This builder provides a template action string with placeholder keyword arguments in the action string. The
    default behavior will not do anything unless the ``program`` or ``subcommand`` argument is updated to include an
    executable program. Because this builder has no emitter, all task targets must be fully specified in the task
    definition. See :meth:`waves.scons_extensions.first_target_builder_factory` for an example of the default options
    used by most WAVES builders.

    .. code-block::
       :caption: action string construction

       ${environment} ${action_prefix} ${program} ${program_required} ${program_options} ${subcommand} ${subcommand_required} ${subcommand_options} ${action_suffix}

    .. code-block::
       :caption: action string default expansion

       ${environment} ${action_prefix} ${program} ${program_required} ${program_options} ${subcommand} ${subcommand_required} ${subcommand_options} ${action_suffix}

    :param environment: This variable is intended primarily for use with builders and tasks that can not execute from an
        SCons construction environment. For instance, when tasks execute on a remote server with SSH wrapped actions
        using :meth:`waves.scons_extensions.ssh_builder_actions` and therefore must initialize the remote environment as
        part of the builder action.
    :param action_prefix: This variable is intended to perform directory change operations prior to program execution. By
        default, SCons performs actions in the parent directory of the SConstruct file. However, many computational
        science and engineering programs leave output files in the current working directory, so it is convenient and
        sometimes necessary to change to the target's parent directory prior to execution.
    :param program: This variable is intended to contain the primary command line executable absolute or relative path
    :param program_required: This variable is intended to contain a space delimited string of required program options
        and arguments that are crucial to builder behavior and should not be modified except by advanced users.
    :param program_options: This variable is intended to contain a space delimited string of optional program options
        and arguments that can be freely modified by the user.
    :param subcommand: This variable is intended to contain the program's subcommand. If the program variable is set to
        a launch controlling program, e.g. ``mpirun`` or ``charmrun``, then the subcommand may need to contain the full
        target executable program and any subcommands.
    :param subcommand_required: This variable is intended to contain a space delimited string of required subcommand
        options and arguments that are crucial to builder behavior and should not be modified except by advanced users.
    :param subcommand_options: This variable is intended to contain a space delimited string of optional subcommand
        options and arguments that can be freely modified by the user.
    :param action_suffix: This variable is intended to perform program STDOUT and STDERR redirection operations. By
        default, SCons streams all STDOUT and STDERR to the terminal. However, in long or parallel workflows this may
        clutter the terminal and make it difficult to isolate critical debugging information, so it is convenient to
        redirect each program's output to a task specific log file for later inspection and troubleshooting.
    :param emitter: An SCons emitter function. This is not a keyword argument in the action string.
    :param kwargs: Any additional keyword arguments are passed directly to the SCons builder object.

    :returns: SCons template builder
    """  # noqa: E501
    action = [
        (
            "${environment} ${action_prefix} ${program} ${program_required} ${program_options} "
            "${subcommand} ${subcommand_required} ${subcommand_options} ${action_suffix}"
        ),
    ]
    builder = SCons.Builder.Builder(
        action=action,
        emitter=emitter,
        environment=environment,
        action_prefix=action_prefix,
        program=program,
        program_required=program_required,
        program_options=program_options,
        subcommand=subcommand,
        subcommand_required=subcommand_required,
        subcommand_options=subcommand_options,
        action_suffix=action_suffix,
        **kwargs,
    )
    return builder


def first_target_emitter(
    target: list,
    source: list,
    env: SCons.Environment.Environment,
    suffixes: typing.Optional[typing.Iterable[str]] = None,
    appending_suffixes: typing.Optional[typing.Iterable[str]] = None,
    stdout_extension: str = _settings._stdout_extension,
) -> typing.Tuple[list, list]:
    """SCons emitter function that emits new targets based on the first target

    Searches for a file ending in the stdout extension. If none is found, creates a target by appending the stdout
    extension to the first target in the ``target`` list. The associated Builder requires at least one target for this
    reason. The stdout file is always placed at the end of the returned target list.

    This is an SCons emitter function and not an emitter factory. The suffix arguments: ``suffixes`` and
    ``appending_suffixes`` are only relevant for developers writing new emitters which call this function as a base. The
    suffixes list emits targets where the suffix replaces the first target's suffix, e.g. for ``target.ext`` emit a new
    target ``target.suffix``. The appending suffixes list emits targets where the suffix appends the first target's
    suffix, e.g.  for ``target.ext`` emit a new target ``target.ext.appending_suffix``.

    The emitter will assume all emitted targets build in the current build directory. If the target(s) must be built in
    a build subdirectory, e.g. in a parameterized target build, then the first target must be provided with the build
    subdirectory, e.g. ``parameter_set1/target.ext``. When in doubt, provide a STDOUT redirect file with the ``.stdout``
    extension as a target, e.g. ``target.stdout`` or ``parameter_set1/target.stdout``.

    :param target: The target file list of strings
    :param source: The source file list of SCons.Node.FS.File objects
    :param env: The builder's SCons construction environment object
    :param suffixes: Suffixes which should replace the first target's extension
    :param appending_suffixes: Suffixes which should append the first target's extension
    :param stdout_extension: The extension used by the STDOUT/STDERR redirect file

    :return: target, source
    """
    if suffixes is None:
        suffixes = []
    if appending_suffixes is None:
        appending_suffixes = []
    string_targets = [str(target_file) for target_file in target]
    first_target = pathlib.Path(string_targets[0])

    # Search for a user specified stdout file. Fall back to first target with appended stdout extension
    stdout_target = next(
        (target_file for target_file in string_targets if target_file.endswith(stdout_extension)),
        f"{first_target}{stdout_extension}",
    )

    replacing_targets = [str(first_target.with_suffix(suffix)) for suffix in suffixes]
    appending_targets = [f"{first_target}{suffix}" for suffix in appending_suffixes]
    string_targets = string_targets + replacing_targets + appending_targets

    # Get a list of unique targets, less the stdout target. Preserve the target list order.
    string_targets = [target_file for target_file in string_targets if target_file != stdout_target]
    string_targets = list(dict.fromkeys(string_targets))

    # Always append the stdout target for easier use in the action string
    string_targets.append(stdout_target)

    return string_targets, source


def first_target_builder_factory(
    environment: str = "",
    action_prefix: str = _settings._cd_action_prefix,
    program: str = "",
    program_required: str = "",
    program_options: str = "",
    subcommand: str = "",
    subcommand_required: str = "",
    subcommand_options: str = "",
    action_suffix: str = _settings._redirect_action_suffix,
    emitter=first_target_emitter,
    **kwargs,
) -> SCons.Builder.Builder:
    """Template builder factory with WAVES default action behaviors and a task STDOUT file emitter

    This builder factory extends :meth:`waves.scons_extensions.builder_factory` to provide a template action string with
    placeholder keyword arguments and WAVES builder default behavior. The default behavior will not do anything unless
    the ``program`` or ``subcommand`` argument is updated to include an executable program. This builder factory uses
    the :meth:`waves.scons_extensions.first_target_emitter`. At least one task target must be specified in the task
    definition and the last target will always be the expected STDOUT and STDERR redirection output file,
    ``TARGETS[-1]`` ending in ``*.stdout``.

    .. warning::

       Users overriding the ``emitter`` keyword argument are responsible for providing an emitter with equivalent STDOUT
       file handling behavior as :meth:`waves.scons_extensions.first_target_emitter` or updating the ``action_suffix``
       option to match their emitter's behavior.

    .. code-block::
       :caption: action string construction

       ${environment} ${action_prefix} ${program} ${program_required} ${program_options} ${subcommand} ${subcommand_required} ${subcommand_options} ${action_suffix}

    .. code-block::
       :caption: action string default expansion

       ${environment} cd ${TARGET.dir.abspath} && ${program} ${program_required} ${program_options} ${subcommand} ${subcommand_required} ${subcommand_options} > ${TARGETS[-1].abspath} 2>&1

    :param environment: This variable is intended primarily for use with builders and tasks that can not execute from an
        SCons construction environment. For instance, when tasks execute on a remote server with SSH wrapped actions
        using :meth:`waves.scons_extensions.ssh_builder_actions` and therefore must initialize the remote environment as
        part of the builder action.
    :param action_prefix: This variable is intended to perform directory change operations prior to program execution. By
        default, SCons performs actions in the parent directory of the SConstruct file. However, many computational
        science and engineering programs leave output files in the current working directory, so it is convenient and
        sometimes necessary to change to the target's parent directory prior to execution.
    :param program: This variable is intended to containg the primary command line executable absolute or relative path
    :param program_required: This variable is intended to contain a space delimited string of required program options
        and arguments that are crucial to builder behavior and should not be modified except by advanced users.
    :param program_options: This variable is intended to contain a space delimited string of optional program options
        and arguments that can be freely modified by the user.
    :param subcommand: This variable is intended to contain the program's subcommand. If the program variable is set to
        a launch controlling program, e.g. ``mpirun`` or ``charmrun``, then the subcommand may need to contain the full
        target executable program and any subcommands.
    :param subcommand_required: This variable is intended to contain a space delimited string of subcommand required
        options and arguments that are crucial to builder behavior and should not be modified except by advanced users.
    :param subcommand_options: This variable is intended to contain a space delimited string of optional subcommand options
        and arguments that can be freely modified by the user.
    :param action_suffix: This variable is intended to perform program STDOUT and STDERR redirection operations. By
        default, SCons streams all STDOUT and STDERR to the terminal. However, in long or parallel workflows this may
        clutter the terminal and make it difficult to isolate critical debugging information, so it is convenient to
        redirect each program's output to a task specific log file for later inspection and troubleshooting.
    :param emitter: An SCons emitter function. This is not a keyword argument in the action string.
    :param kwargs: Any additional keyword arguments are passed directly to the SCons builder object.

    :returns: SCons template builder
    """  # noqa: E501
    builder = builder_factory(
        environment=environment,
        action_prefix=action_prefix,
        program=program,
        program_required=program_required,
        program_options=program_options,
        subcommand=subcommand,
        subcommand_required=subcommand_required,
        subcommand_options=subcommand_options,
        action_suffix=action_suffix,
        emitter=emitter,
        **kwargs,
    )
    return builder


def _abaqus_journal_emitter(
    target: list,
    source: list,
    env: SCons.Environment.Environment,
) -> typing.Tuple[list, list]:
    """Appends the abaqus_journal builder target list with the builder managed targets

    Appends ``target[0]``.abaqus_v6.env and ``target[0]``.stdout to the ``target`` list. The abaqus_journal Builder
    requires at least one target.

    The emitter will assume all emitted targets build in the current build directory. If the target(s) must be built in
    a build subdirectory, e.g. in a parameterized target build, then the first target must be provided with the build
    subdirectory, e.g. ``parameter_set1/target.ext``. When in doubt, provide a STDOUT redirect file as a target, e.g.
    ``target.stdout``.

    :param target: The target file list of strings
    :param source: The source file list of SCons.Node.FS.File objects
    :param env: The builder's SCons construction environment object

    :return: target, source
    """
    appending_suffixes = [_settings._abaqus_environment_extension]
    return first_target_emitter(target, source, env, appending_suffixes=appending_suffixes)


def abaqus_journal(
    program: str = "abaqus",
    required: str = "cae -noGUI ${SOURCE.abspath}",
    action_prefix: str = _settings._cd_action_prefix,
    action_suffix: str = _settings._redirect_action_suffix,
    environment_suffix: str = _settings._redirect_environment_suffix,
) -> SCons.Builder.Builder:
    """Construct and return an Abaqus journal file SCons builder

    This builder requires that the journal file to execute is the first source in the list. The builder returned by this
    function accepts all SCons Builder arguments. The arguments of this function are also available as keyword arguments
    of the builder. When provided during task definition, the keyword arguments override the builder returned by this
    function.

    *Builder/Task keyword arguments*

    * ``program``: The Abaqus command line executable absolute or relative path
    * ``required``: A space delimited string of Abaqus required arguments
    * ``abaqus_options``: The Abaqus command line options provided as a string
    * ``journal_options``: The journal file command line options provided as a string
    * ``action_prefix``: Advanced behavior. Most users should accept the defaults
    * ``action_suffix``: Advanced behavior. Most users should accept the defaults.
    * ``environment_suffix``: Advanced behavior. Most users should accept the defaults.

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
       :caption: Abaqus journal builder action keywords

       ${action_prefix} ${program} -information environment ${environment_suffix}
       ${action_prefix} ${program} ${required} ${abaqus_options} -- ${journal_options} ${action_suffix}

    With the default argument values, this expands to

    .. code-block::
       :caption: Abaqus journal builder action default expansion

       cd ${TARGET.dir.abspath} && abaqus -information environment > ${TARGETS[-2].abspath} 2>&1
       cd ${TARGET.dir.abspath} && abaqus cae -noGui ${SOURCE.abspath} ${abaqus_options} -- ${journal_options} > ${TARGETS[-1].abspath} 2>&1

    .. code-block::
       :caption: SConstruct

       import waves
       env = Environment()
       env.AddMethod(waves.scons_extensions.add_program, "AddProgram")
       env["ABAQUS_PROGRAM"] = env.AddProgram(["abaqus"])
       env.Append(BUILDERS={"AbaqusJournal": waves.scons_extensions.abaqus_journal()})
       env.AbaqusJournal(target=["my_journal.cae"], source=["my_journal.py"], journal_options="")

    :param program: The Abaqus command line executable absolute or relative path
    :param required: A space delimited string of Abaqus required arguments
    :param action_prefix: Advanced behavior. Most users should accept the defaults.
    :param action_suffix: Advanced behavior. Most users should accept the defaults.
    :param environment_suffix: Advanced behavior. Most users should accept the defaults.

    :return: Abaqus journal builder
    """  # noqa: E501
    action = [
        "${action_prefix} ${program} -information environment ${environment_suffix}",
        "${action_prefix} ${program} ${required} ${abaqus_options} -- ${journal_options} ${action_suffix}",
    ]
    builder = SCons.Builder.Builder(
        action=action,
        emitter=_abaqus_journal_emitter,
        program=program,
        required=required,
        action_prefix=action_prefix,
        action_suffix=action_suffix,
        environment_suffix=environment_suffix,
    )
    return builder


@catenate_actions(program="sbatch", options=_settings._sbatch_wrapper_options)
def sbatch_abaqus_journal(*args, **kwargs):
    """Thin pass through wrapper of :meth:`waves.scons_extensions.abaqus_journal`

    Catenate the actions and submit with `SLURM`_ `sbatch`_. Accepts the ``sbatch_options`` builder keyword argument to
    modify sbatch behavior.

    .. code-block::
       :caption: Sbatch Abaqus journal builder action keywords

       sbatch --wait --output=${TARGET.base}.slurm.out ${sbatch_options} --wrap "${action_prefix} ${program} -information environment ${environment_suffix} && ${action_prefix} ${program} ${required} ${abaqus_options} -- ${journal_options} ${action_suffix}"

    .. code-block::
       :caption: Sbatch Abaqus journal builder action default expansion

       sbatch --wait --output=${TARGET.base}.slurm.out ${sbatch_options} --wrap "cd ${TARGET.dir.abspath} && abaqus cae -noGui ${SOURCE.abspath} ${abaqus_options} -- ${journal_options} > ${TARGETS[-1].abspath} 2>&1"
    """  # noqa: E501
    return abaqus_journal(*args, **kwargs)


def abaqus_journal_builder_factory(
    environment: str = "",
    action_prefix: str = _settings._cd_action_prefix,
    program: str = "abaqus",
    program_required: str = "cae -noGUI ${SOURCES[0].abspath}",
    program_options: str = "",
    subcommand: str = "--",
    subcommand_required: str = "",
    subcommand_options: str = "",
    action_suffix: str = _settings._redirect_action_suffix,
    emitter=first_target_emitter,
    **kwargs,
) -> SCons.Builder.Builder:
    """Abaqus journal builder factory

    This builder factory extends :meth:`waves.scons_extensions.first_target_builder_factory`. This builder factory uses
    the :meth:`waves.scons_extensions.first_target_emitter`. At least one task target must be specified in the task
    definition and the last target will always be the expected STDOUT and STDERR redirection output file,
    ``TARGETS[-1]`` ending in ``*.stdout``.

    .. warning::

       Users overriding the ``emitter`` keyword argument are responsible for providing an emitter with equivalent STDOUT
       file handling behavior as :meth:`waves.scons_extensions.first_target_emitter` or updating the ``action_suffix``
       option to match their emitter's behavior.

    With the default options this builder requires the following sources file provided in the order:

    1. Abaqus journal file: ``*.py``

    .. code-block::
       :caption: action string construction

       ${environment} ${action_prefix} ${program} ${program_required} ${program_options} ${subcommand} ${subcommand_required} ${subcommand_options} ${action_suffix}

    .. code-block::
       :caption: action string default expansion

       ${environment} cd ${TARGET.dir.abspath} && abaqus cae -noGUI=${SOURCES[0].abspath} ${program_options} -- ${subcommand_required} ${subcommand_options} > ${TARGETS[-1].abspath} 2>&1

    .. code-block::
       :caption: SConstruct

       import waves
       env = Environment()
       env.AddMethod(waves.scons_extensions.add_program, "AddProgram")
       env["ABAQUS_PROGRAM"] = env.AddProgram(["abaqus"])
       env.Append(BUILDERS={
           "AbaqusJournal": waves.scons_extensions.abaqus_journal_builder_factory(
               program=env["ABAQUS_PROGRAM"]
           )
       })
       env.AbaqusJournal(target=["my_journal.cae"], source=["my_journal.py"])

    The builder returned by this factory accepts all SCons Builder arguments. The arguments of this function are also
    available as keyword arguments of the builder. When provided during task definition, the task keyword arguments
    override the builder keyword arguments.

    :param environment: This variable is intended primarily for use with builders and tasks that can not execute from an
        SCons construction environment. For instance, when tasks execute on a remote server with SSH wrapped actions
        using :meth:`waves.scons_extensions.ssh_builder_actions` and therefore must initialize the remote environment as
        part of the builder action.
    :param action_prefix: This variable is intended to perform directory change operations prior to program execution
    :param program: The Abaqus absolute or relative path
    :param program_required: Space delimited string of required Abaqus options and arguments that are crucial to
        builder behavior and should not be modified except by advanced users
    :param program_options: Space delimited string of optional Abaqus options and arguments that can be freely
        modified by the user
    :param subcommand: The shell separator for positional arguments used to separate Abaqus program from Abaqus journal
        file arguments and options
    :param subcommand_required: Space delimited string of required Abaqus journal file options and arguments
        that are crucial to builder behavior and should not be modified except by advanced users.
    :param subcommand_options: Space delimited string of optional Abaqus journal file options and arguments
        that can be freely modified by the user
    :param action_suffix: This variable is intended to perform program STDOUT and STDERR redirection operations.
    :param emitter: An SCons emitter function. This is not a keyword argument in the action string.
    :param kwargs: Any additional keyword arguments are passed directly to the SCons builder object.

    :return: Abaqus journal builder
    """  # noqa: E501
    builder = first_target_builder_factory(
        environment=environment,
        action_prefix=action_prefix,
        program=program,
        program_required=program_required,
        program_options=program_options,
        subcommand=subcommand,
        subcommand_required=subcommand_required,
        subcommand_options=subcommand_options,
        action_suffix=action_suffix,
        emitter=emitter,
        **kwargs,
    )
    return builder


@catenate_actions(program="sbatch", options=_settings._sbatch_wrapper_options)
def sbatch_abaqus_journal_builder_factory(*args, **kwargs):
    """Thin pass through wrapper of :meth:`waves.scons_extensions.abaqus_journal_builder_factory`

    Catenate the actions and submit with `SLURM`_ `sbatch`_. Accepts the ``sbatch_options`` builder keyword argument to
    modify sbatch behavior.

    .. code-block::
       :caption: action string construction

       sbatch --wait --output=${TARGET.base}.slurm.out ${sbatch_options} --wrap "${environment} ${action_prefix} ${program} ${program_required} ${program_options} ${subcommand} ${subcommand_required} ${subcommand_options} ${action_suffix}"
    """  # noqa: E501
    return abaqus_journal_builder_factory(*args, **kwargs)


def _abaqus_solver_emitter(
    target: list,
    source: list,
    env: SCons.Environment.Environment,
    suffixes: typing.Iterable[str] = _settings._abaqus_common_extensions,
    stdout_extension: str = _settings._stdout_extension,
) -> typing.Tuple[list, list]:
    """Appends the abaqus_solver builder target list with the builder managed targets

    If no targets are provided to the Builder, the emitter will assume all emitted targets build in the current build
    directory. If the target(s) must be built in a build subdirectory, e.g. in a parameterized target build, then at
    least one target must be provided with the build subdirectory, e.g. ``parameter_set1/target.ext``. When in doubt,
    provide the output database as a target, e.g. ``job_name.odb``

    If "suffixes" is a key in the environment, ``env``, then the suffixes list will override the ``suffixes`` argument.

    :param target: The target file list of strings
    :param source: The source file list of SCons.Node.FS.File objects
    :param env: The builder's SCons construction environment object
    :param suffixes: List of strings to use as emitted file suffixes. Must contain the leading period,
        e.g. ``.extension``
    :param stdout_extension: The extension used by the STDOUT/STDERR redirect file

    :return: target, source
    """
    suffixes_copy = list(copy.deepcopy(suffixes))
    if "suffixes" in env and env["suffixes"] is not None:
        suffixes_copy = copy.deepcopy(env["suffixes"])
    if isinstance(suffixes_copy, str):
        suffixes_copy = [suffixes_copy]
    suffixes_copy.append(_settings._abaqus_environment_extension)

    primary_input_file = pathlib.Path(source[0].path)
    if "job_name" not in env or not env["job_name"]:
        env["job_name"] = primary_input_file.stem
    build_subdirectory = _build_subdirectory(target)

    # Search for a user specified stdout file. Fall back to job name with appended stdout extension
    string_targets = [str(target_file) for target_file in target]
    constructed_stdout_target = str(build_subdirectory / f"{env['job_name']}{stdout_extension}")
    stdout_target = next(
        (target_file for target_file in string_targets if target_file.endswith(stdout_extension)),
        constructed_stdout_target,
    )

    job_targets = [str(build_subdirectory / f"{env['job_name']}{suffix}") for suffix in suffixes_copy]

    # Get a list of unique targets,  less the stdout target. Preserve the target list order.
    string_targets = string_targets + job_targets
    string_targets = [target_file for target_file in string_targets if target_file != stdout_target]
    string_targets = list(dict.fromkeys(string_targets))

    # Always append the stdout target for easier use in the action string
    string_targets.append(stdout_target)

    return string_targets, source


def _abaqus_standard_solver_emitter(target: list, source: list, env) -> typing.Tuple[list, list]:
    """Passes the standard specific extensions to :meth:`waves.scons_extensions._abaqus_solver_emitter`"""
    return _abaqus_solver_emitter(target, source, env, _settings._abaqus_standard_extensions)


def _abaqus_explicit_solver_emitter(target: list, source: list, env) -> typing.Tuple[list, list]:
    """Passes the explicit specific extensions to :meth:`waves.scons_extensions._abaqus_solver_emitter`"""
    return _abaqus_solver_emitter(target, source, env, _settings._abaqus_explicit_extensions)


def _abaqus_datacheck_solver_emitter(target: list, source: list, env) -> typing.Tuple[list, list]:
    """Passes the datacheck specific extensions to :meth:`waves.scons_extensions._abaqus_solver_emitter`"""
    return _abaqus_solver_emitter(target, source, env, _settings._abaqus_datacheck_extensions)


def abaqus_solver(
    program: str = "abaqus",
    required: str = "-interactive -ask_delete no -job ${job_name} -input ${SOURCE.filebase}",
    action_prefix: str = _settings._cd_action_prefix,
    action_suffix: str = _settings._redirect_action_suffix,
    environment_suffix: str = _settings._redirect_environment_suffix,
    emitter: typing.Literal["standard", "explicit", "datacheck", None] = None,
) -> SCons.Builder.Builder:
    """Construct and return an Abaqus solver SCons builder

    This builder requires that the root input file is the first source in the list. The builder returned by this
    function accepts all SCons Builder arguments. The arguments of this function are also available as keyword arguments
    of the builder. When provided during task definition, the keyword arguments override the builder returned by this
    function.

    *Builder/Task keyword arguments*

    * ``program``: The Abaqus command line executable absolute or relative path
    * ``required``: A space delimited string of Abaqus required arguments
    * ``job_name``: The job name string. If not specified ``job_name`` defaults to the root input file stem. The Builder
        emitter will append common Abaqus output files as targets automatically from the ``job_name``, e.g.
        ``job_name.odb``.
    * ``abaqus_options``: The Abaqus command line options provided as a string.
    * ``suffixes``: override the emitter targets with a new list of extensions, e.g.
      ``AbaqusSolver(target=[], source=["input.inp"], suffixes=[".odb"])`` will emit only one file named
      ``job_name.odb``.
    * ``action_prefix``: Advanced behavior. Most users should accept the defaults
    * ``action_suffix``: Advanced behavior. Most users should accept the defaults.
    * ``environment_suffix``: Advanced behavior. Most users should accept the defaults.

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
       env.AddMethod(waves.scons_extensions.add_program, "AddProgram")
       env["ABAQUS_PROGRAM"] = env.AddProgram(["abaqus"])
       env.Append(BUILDERS={
           "AbaqusSolver": waves.scons_extensions.abaqus_solver(),
           "AbaqusStandard": waves.scons_extensions.abaqus_solver(emitter='standard'),
           "AbaqusOld": waves.scons_extensions.abaqus_solver(program="abq2019")
       })
       env.AbaqusSolver(target=[], source=["input.inp"], job_name="my_job", abaqus_options="-cpus 4")
       env.AbaqusSolver(target=[], source=["input.inp"], job_name="my_job", suffixes=[".odb"])

    .. code-block::
       :caption: Abaqus solver builder action keywords

       ${action_prefix} ${program} -information environment ${environment_suffix}
       ${action_prefix} ${program} ${required} ${abaqus_options} ${action_suffix}

    .. code-block::
       :caption: Abaqus solver builder action default expansion

       cd ${TARGET.dir.abspath} && abaqus -information environment > ${TARGETS[-2].abspath} 2>&1
       cd ${TARGET.dir.abspath} && ${program} -interactive -ask_delete no -job ${job_name} -input ${SOURCE.filebase} ${abaqus_options} > ${TARGETS[-1].abspath} 2>&1

    :param program: An absolute path or basename string for the abaqus program
    :param required: A space delimited string of Abaqus required arguments
    :param action_prefix: Advanced behavior. Most users should accept the defaults.
    :param action_suffix: Advanced behavior. Most users should accept the defaults.
    :param environment_suffix: Advanced behavior. Most users should accept the defaults.
    :param emitter: emit file extensions based on the value of this variable. Overridden by the ``suffixes`` keyword
        argument that may be provided in the Task definition.

        * "standard": [".odb", ".dat", ".msg", ".com", ".prt", ".sta"]
        * "explicit": [".odb", ".dat", ".msg", ".com", ".prt", ".sta"]
        * "datacheck": [".odb", ".dat", ".msg", ".com", ".prt", ".023", ".mdl", ".sim", ".stt"]
        * default value: [".odb", ".dat", ".msg", ".com", ".prt"]

    :return: Abaqus solver builder
    """  # noqa: E501
    action = [
        "${action_prefix} ${program} -information environment ${environment_suffix}",
        "${action_prefix} ${program} ${required} ${abaqus_options} ${action_suffix}",
    ]
    if emitter:
        emitter = emitter.lower()
    if emitter == "standard":
        abaqus_emitter = _abaqus_standard_solver_emitter
    elif emitter == "explicit":
        abaqus_emitter = _abaqus_explicit_solver_emitter
    elif emitter == "datacheck":
        abaqus_emitter = _abaqus_datacheck_solver_emitter
    else:
        abaqus_emitter = _abaqus_solver_emitter
    abaqus_solver_builder = SCons.Builder.Builder(
        action=action,
        emitter=abaqus_emitter,
        program=program,
        required=required,
        action_prefix=action_prefix,
        action_suffix=action_suffix,
        environment_suffix=environment_suffix,
    )
    return abaqus_solver_builder


def _task_kwarg_emitter(
    target: list,
    source: list,
    env: SCons.Environment.Environment,
    suffixes: typing.Optional[typing.Iterable[str]] = None,
    appending_suffixes: typing.Optional[typing.Iterable[str]] = None,
    stdout_extension: str = _settings._stdout_extension,
    required_task_kwarg: str = "",
):
    """SCons emitter function template designed for :meth:`waves.scons_extensions.abaqus_solver_builder_factory` based
    builders.

    This emitter prepends the target list with the value of the ``env[required_task_kwarg]`` task keyword argument named
    targets before passing through the :meth:`waves.scons_extensions.first_target_emitter` emitter.

    Searches for the ``required_task_kwarg`` task keyword argument and appends the target list with
    ``f"{env[required_task_kwarg]}{suffix}"`` targets using the ``suffixes`` list.

    Searches for a file ending in the stdout extension. If none is found, creates a target by appending the stdout
    extension to the first target in the ``target`` list. The associated Builder requires at least one target for this
    reason. The stdout file is always placed at the end of the returned target list.

    This is an SCons emitter function and not an emitter factory. The suffix arguments: ``suffixes`` and
    ``appending_suffixes`` are only relevant for developers writing new emitters which call this function as a base. The
    suffixes list emits targets where the suffix replaces the first target's suffix, e.g. for ``target.ext`` emit a new
    target ``target.suffix``. The appending suffixes list emits targets where the suffix appends the first target's
    suffix, e.g.  for ``target.ext`` emit a new target ``target.ext.appending_suffix``.

    The emitter will assume all emitted targets build in the current build directory. If the target(s) must be built in
    a build subdirectory, e.g. in a parameterized target build, then the first target must be provided with the build
    subdirectory, e.g. ``parameter_set1/target.ext``. When in doubt, provide a STDOUT redirect file with the ``.stdout``
    extension as a target, e.g. ``target.stdout`` or ``parameter_set1/target.stdout``.

    :param target: The target file list of strings
    :param source: The source file list of SCons.Node.FS.File objects
    :param env: The builder's SCons construction environment object
    :param suffixes: Suffixes which should replace the first target's extension
    :param appending_suffixes: Suffixes which should append the first target's extension
    :param stdout_extension: The extension used by the STDOUT/STDERR redirect file
    :param required_task_kwarg: The task environment keyword used to construct emitted targets

    :return: target, source
    """
    if not required_task_kwarg:
        raise RuntimeError("Emitter requires a populated ``required_task_kwarg`` argument")
    if required_task_kwarg not in env or not env[required_task_kwarg]:
        raise RuntimeError(f"Emitter requires the '{required_task_kwarg}' task keyword argument")

    build_subdirectory = _build_subdirectory(target)
    if suffixes is not None:
        target = target + [build_subdirectory / f"{env[required_task_kwarg]}{suffix}" for suffix in suffixes]

    return first_target_emitter(
        target,
        source,
        env,
        suffixes=suffixes,
        appending_suffixes=appending_suffixes,
        stdout_extension=stdout_extension,
    )


def abaqus_solver_emitter_factory(
    suffixes: typing.Iterable[str] = _settings._abaqus_common_extensions,
    appending_suffixes: typing.Optional[typing.Iterable[str]] = None,
    stdout_extension: str = _settings._stdout_extension,
) -> collections.abc.Callable[[list, list, SCons.Environment.Environment], tuple]:
    """Abaqus solver emitter factory

    SCons emitter factory that returns emitters for :meth:`waves.scons_extensions.abaqus_solver_builder_factory` based
    builders.

    Emitters returned by this factory append the target list with ``job`` task keyword argument named targets before
    passing through the :meth:`waves.scons_extensions.first_target_emitter` emitter.

    Searches for the ``job`` task keyword argument and appends the target list with ``f"{job}{suffix}"`` targets using
    the ``suffixes`` list.

    Searches for a file ending in the stdout extension. If none is found, creates a target by appending the stdout
    extension to the first target in the ``target`` list. The associated Builder requires at least one target for this
    reason. The stdout file is always placed at the end of the returned target list.

    The ``suffixes`` list emits targets where the suffix replaces the first target's suffix, e.g. for ``target.ext``
    emit a new target ``target.suffix``. The appending suffixes list emits targets where the suffix appends the first
    target's suffix, e.g.  for ``target.ext`` emit a new target ``target.ext.appending_suffix``.

    The emitter will assume all emitted targets build in the current build directory. If the target(s) must be built in
    a build subdirectory, e.g. in a parameterized target build, then the first target must be provided with the build
    subdirectory, e.g. ``parameter_set1/target.ext``. When in doubt, provide a STDOUT redirect file with the ``.stdout``
    extension as a target, e.g. ``target.stdout`` or ``parameter_set1/target.stdout``.

    .. code-block::
       :caption: SConstruct

       import waves
       env = Environment()
       env.AddMethod(waves.scons_extensions.add_program, "AddProgram")
       env["ABAQUS_PROGRAM"] = env.AddProgram(["abaqus"])
       env.Append(BUILDERS={
           "AbaqusStandard": waves.scons_extensions.abaqus_solver_builder_factory(
               program=env["ABAQUS_PROGRAM"],
               emitter=waves.scons_extensions.abaqus_solver_emitter_factory(
                   suffixes=[".odb", ".dat", ".msg", ".com", ".prt", ".sta"],
               )
           )
       })
       env.AbaqusStandard(target=["job.odb"], source=["input.inp"], job="job")

    .. note::

       The ``job`` keyword argument *must* be provided in the task definition.

    :param suffixes: Suffixes which should replace the first target's extension
    :param appending_suffixes: Suffixes which should append the first target's extension
    :param stdout_extension: The extension used by the STDOUT/STDERR redirect file

    :return: emitter function
    """

    def emitter(target, source, env):
        return _task_kwarg_emitter(
            target,
            source,
            env,
            suffixes=suffixes,
            appending_suffixes=appending_suffixes,
            stdout_extension=stdout_extension,
            required_task_kwarg="job",
        )

    return emitter


def abaqus_datacheck_emitter(
    target: list,
    source: list,
    env: SCons.Environment.Environment,
    suffixes: typing.Iterable[str] = _settings._abaqus_datacheck_extensions,
    appending_suffixes: typing.Optional[typing.Iterable[str]] = None,
    stdout_extension: str = _settings._stdout_extension,
):
    """Abaqus solver emitter for datacheck targets

    SCons emitter for :meth:`waves.scons_extensions.abaqus_solver_builder_factory` based builders. Built on
    :meth:`waves.scons_extensions.abaqus_solver_emitter_factory`.

    Appends the target list with ``job`` task keyword argument named targets before passing through the
    :meth:`waves.scons_extensions.first_target_emitter` emitter.

    Searches for the ``job`` task keyword argument and appends the target list with ``f"{job}{suffix}"`` targets using
    the ``suffixes`` list.

    Searches for a file ending in the stdout extension. If none is found, creates a target by appending the stdout
    extension to the first target in the ``target`` list. The associated Builder requires at least one target for this
    reason. The stdout file is always placed at the end of the returned target list.

    This is an SCons emitter function and not an emitter factory. The suffix arguments: ``suffixes`` and
    ``appending_suffixes`` are only relevant for developers writing new emitters which call this function as a base. The
    suffixes list emits targets where the suffix replaces the first target's suffix, e.g. for ``target.ext`` emit a new
    target ``target.suffix``. The appending suffixes list emits targets where the suffix appends the first target's
    suffix, e.g.  for ``target.ext`` emit a new target ``target.ext.appending_suffix``.

    The emitter will assume all emitted targets build in the current build directory. If the target(s) must be built in
    a build subdirectory, e.g. in a parameterized target build, then the first target must be provided with the build
    subdirectory, e.g. ``parameter_set1/target.ext``. When in doubt, provide a STDOUT redirect file with the ``.stdout``
    extension as a target, e.g. ``target.stdout`` or ``parameter_set1/target.stdout``.

    .. code-block::
       :caption: SConstruct

       import waves
       env = Environment()
       env.AddMethod(waves.scons_extensions.add_program, "AddProgram")
       env["ABAQUS_PROGRAM"] = env.AddProgram(["abaqus"])
       env.Append(BUILDERS={
           "AbaqusDatacheck": waves.scons_extensions.abaqus_solver_builder_factory(
               program=env["ABAQUS_PROGRAM"],
               emitter=waves.scons_extensions.abaqus_datacheck_emitter,
           )
       })
       env.AbaqusDatacheck(target=["job.odb"], source=["input.inp"], job="job")

    .. note::

       The ``job`` keyword argument *must* be provided in the task definition.

    :param target: The target file list of strings
    :param source: The source file list of SCons.Node.FS.File objects
    :param env: The builder's SCons construction environment object
    :param suffixes: Suffixes which should replace the first target's extension
    :param appending_suffixes: Suffixes which should append the first target's extension
    :param stdout_extension: The extension used by the STDOUT/STDERR redirect file

    :return: target, source
    """
    emitter = abaqus_solver_emitter_factory(
        suffixes=suffixes,
        appending_suffixes=appending_suffixes,
        stdout_extension=stdout_extension,
    )
    return emitter(target, source, env)


def abaqus_explicit_emitter(
    target: list,
    source: list,
    env: SCons.Environment.Environment,
    suffixes: typing.Iterable[str] = _settings._abaqus_explicit_extensions,
    appending_suffixes: typing.Optional[typing.Iterable[str]] = None,
    stdout_extension: str = _settings._stdout_extension,
):
    """Abaqus solver emitter for Explicit targets

    SCons emitter for :meth:`waves.scons_extensions.abaqus_solver_builder_factory` based builders. Built on
    :meth:`waves.scons_extensions.abaqus_solver_emitter_factory`.

    Appends the target list with ``job`` task keyword argument named targets before passing through the
    :meth:`waves.scons_extensions.first_target_emitter` emitter.

    Searches for the ``job`` task keyword argument and appends the target list with ``f"{job}{suffix}"`` targets using
    the ``suffixes`` list.

    Searches for a file ending in the stdout extension. If none is found, creates a target by appending the stdout
    extension to the first target in the ``target`` list. The associated Builder requires at least one target for this
    reason. The stdout file is always placed at the end of the returned target list.

    This is an SCons emitter function and not an emitter factory. The suffix arguments: ``suffixes`` and
    ``appending_suffixes`` are only relevant for developers writing new emitters which call this function as a base. The
    suffixes list emits targets where the suffix replaces the first target's suffix, e.g. for ``target.ext`` emit a new
    target ``target.suffix``. The appending suffixes list emits targets where the suffix appends the first target's
    suffix, e.g.  for ``target.ext`` emit a new target ``target.ext.appending_suffix``.

    The emitter will assume all emitted targets build in the current build directory. If the target(s) must be built in
    a build subdirectory, e.g. in a parameterized target build, then the first target must be provided with the build
    subdirectory, e.g. ``parameter_set1/target.ext``. When in doubt, provide a STDOUT redirect file with the ``.stdout``
    extension as a target, e.g. ``target.stdout`` or ``parameter_set1/target.stdout``.

    .. code-block::
       :caption: SConstruct

       import waves
       env = Environment()
       env.AddMethod(waves.scons_extensions.add_program, "AddProgram")
       env["ABAQUS_PROGRAM"] = env.AddProgram(["abaqus"])
       env.Append(BUILDERS={
           "AbaqusExplicit": waves.scons_extensions.abaqus_solver_builder_factory(
               program=env["ABAQUS_PROGRAM"],
               emitter=waves.scons_extensions.abaqus_explicit_emitter,
           )
       })
       env.AbaqusExplicit(target=["job.odb"], source=["input.inp"], job="job")

    .. note::

       The ``job`` keyword argument *must* be provided in the task definition.

    :param target: The target file list of strings
    :param source: The source file list of SCons.Node.FS.File objects
    :param env: The builder's SCons construction environment object
    :param suffixes: Suffixes which should replace the first target's extension
    :param appending_suffixes: Suffixes which should append the first target's extension
    :param stdout_extension: The extension used by the STDOUT/STDERR redirect file

    :return: target, source
    """
    emitter = abaqus_solver_emitter_factory(
        suffixes=suffixes,
        appending_suffixes=appending_suffixes,
        stdout_extension=stdout_extension,
    )
    return emitter(target, source, env)


def abaqus_standard_emitter(
    target: list,
    source: list,
    env: SCons.Environment.Environment,
    suffixes: typing.Iterable[str] = _settings._abaqus_standard_extensions,
    appending_suffixes: typing.Optional[typing.Iterable[str]] = None,
    stdout_extension: str = _settings._stdout_extension,
):
    """Abaqus solver emitter for Standard targets

    SCons emitter for :meth:`waves.scons_extensions.abaqus_solver_builder_factory` based builders. Built on
    :meth:`waves.scons_extensions.abaqus_solver_emitter_factory`.

    Appends the target list with ``job`` task keyword argument named targets before passing through the
    :meth:`waves.scons_extensions.first_target_emitter` emitter.

    Searches for the ``job`` task keyword argument and appends the target list with ``f"{job}{suffix}"`` targets using
    the ``suffixes`` list.

    Searches for a file ending in the stdout extension. If none is found, creates a target by appending the stdout
    extension to the first target in the ``target`` list. The associated Builder requires at least one target for this
    reason. The stdout file is always placed at the end of the returned target list.

    This is an SCons emitter function and not an emitter factory. The suffix arguments: ``suffixes`` and
    ``appending_suffixes`` are only relevant for developers writing new emitters which call this function as a base. The
    suffixes list emits targets where the suffix replaces the first target's suffix, e.g. for ``target.ext`` emit a new
    target ``target.suffix``. The appending suffixes list emits targets where the suffix appends the first target's
    suffix, e.g.  for ``target.ext`` emit a new target ``target.ext.appending_suffix``.

    The emitter will assume all emitted targets build in the current build directory. If the target(s) must be built in
    a build subdirectory, e.g. in a parameterized target build, then the first target must be provided with the build
    subdirectory, e.g. ``parameter_set1/target.ext``. When in doubt, provide a STDOUT redirect file with the ``.stdout``
    extension as a target, e.g. ``target.stdout`` or ``parameter_set1/target.stdout``.

    .. code-block::
       :caption: SConstruct

       import waves
       env = Environment()
       env.AddMethod(waves.scons_extensions.add_program, "AddProgram")
       env["ABAQUS_PROGRAM"] = env.AddProgram(["abaqus"])
       env.Append(BUILDERS={
           "AbaqusStandard": waves.scons_extensions.abaqus_solver_builder_factory(
               program=env["ABAQUS_PROGRAM"],
               emitter=waves.scons_extensions.abaqus_standard_emitter,
           )
       })
       env.AbaqusStandard(target=["job.odb"], source=["input.inp"], job="job")

    .. note::

       The ``job`` keyword argument *must* be provided in the task definition.

    :param target: The target file list of strings
    :param source: The source file list of SCons.Node.FS.File objects
    :param env: The builder's SCons construction environment object
    :param suffixes: Suffixes which should replace the first target's extension
    :param appending_suffixes: Suffixes which should append the first target's extension
    :param stdout_extension: The extension used by the STDOUT/STDERR redirect file

    :return: target, source
    """
    emitter = abaqus_solver_emitter_factory(
        suffixes=suffixes,
        appending_suffixes=appending_suffixes,
        stdout_extension=stdout_extension,
    )
    return emitter(target, source, env)


def abaqus_solver_builder_factory(
    environment: str = "",
    action_prefix: str = _settings._cd_action_prefix,
    program: str = "abaqus",
    program_required: str = "-interactive -ask_delete no -job ${job} -input ${SOURCE.filebase}",
    program_options: str = "",
    subcommand: str = "",
    subcommand_required: str = "",
    subcommand_options: str = "",
    action_suffix: str = _settings._redirect_action_suffix,
    emitter=first_target_emitter,
    **kwargs,
) -> SCons.Builder.Builder:
    """Abaqus solver builder factory

    This builder factory extends :meth:`waves.scons_extensions.first_target_builder_factory`. This builder factory uses
    the :meth:`waves.scons_extensions.first_target_emitter`. At least one task target must be specified in the task
    definition and the last target will always be the expected STDOUT and STDERR redirection output file,
    ``TARGETS[-1]`` ending in ``*.stdout``.

    .. warning::

       Users overriding the ``emitter`` keyword argument are responsible for providing an emitter with equivalent STDOUT
       file handling behavior as :meth:`waves.scons_extensions.first_target_emitter` or updating the ``action_suffix``
       option to match their emitter's behavior.

    With the default options this builder requires the following sources file provided in the order:

    1. Abaqus solver file: ``*.inp``

    .. code-block::
       :caption: action string construction

       ${environment} ${action_prefix} ${program} ${program_required} ${program_options} ${subcommand} ${subcommand_required} ${subcommand_options} ${action_suffix}

    .. code-block::
       :caption: action string default expansion

       ${environment} cd ${TARGET.dir.abspath} && abaqus -interactive -ask_delete no -job ${job} -input ${SOURCE.filebase} ${program_options} ${subcommand} ${subcommand_required} ${subcommand_options} > ${TARGETS[-1].abspath} 2>&1

    .. code-block::
       :caption: SConstruct

       import waves
       env = Environment()
       env.AddMethod(waves.scons_extensions.add_program, "AddProgram")
       env["ABAQUS_PROGRAM"] = env.AddProgram(["abaqus"])
       env.Append(BUILDERS={
           "AbaqusSolver": waves.scons_extensions.abaqus_solver_builder_factory(
               program=env["ABAQUS_PROGRAM"]
           )
       })
       env.AbaqusSolver(target=["job.odb"], source=["input.inp"], job="job")

    .. note::

       The ``job`` keyword argument *must* be provided in the task definition.

    The builder returned by this factory accepts all SCons Builder arguments. The arguments of this function are also
    available as keyword arguments of the builder. When provided during task definition, the task keyword arguments
    override the builder keyword arguments.

    :param environment: This variable is intended primarily for use with builders and tasks that can not execute from an
        SCons construction environment. For instance, when tasks execute on a remote server with SSH wrapped actions
        using :meth:`waves.scons_extensions.ssh_builder_actions` and therefore must initialize the remote environment as
        part of the builder action.
    :param action_prefix: This variable is intended to perform directory change operations prior to program execution
    :param program: The Abaqus absolute or relative path
    :param program_required: Space delimited string of required Abaqus options and arguments that are crucial to
        builder behavior and should not be modified except by advanced users
    :param program_options: Space delimited string of optional Abaqus options and arguments that can be freely
        modified by the user
    :param subcommand: The subcommand absolute or relative path
    :param subcommand_required: Space delimited string of required subcommand options and arguments
        that are crucial to builder behavior and should not be modified except by advanced users.
    :param subcommand_options: Space delimited string of optional subcommand options and arguments
        that can be freely modified by the user
    :param action_suffix: This variable is intended to perform program STDOUT and STDERR redirection operations.
    :param emitter: An SCons emitter function. This is not a keyword argument in the action string.
    :param kwargs: Any additional keyword arguments are passed directly to the SCons builder object.

    :return: Abaqus solver builder
    """  # noqa: E501
    builder = first_target_builder_factory(
        environment=environment,
        action_prefix=action_prefix,
        program=program,
        program_required=program_required,
        program_options=program_options,
        subcommand=subcommand,
        subcommand_required=subcommand_required,
        subcommand_options=subcommand_options,
        action_suffix=action_suffix,
        emitter=emitter,
        **kwargs,
    )
    return builder


class AbaqusPseudoBuilder:
    """Abaqus Pseudo-Builder class which allows users to customize the Abaqus Pseudo-Builder.

    :param builder: A Builder generated by :meth:`waves.scons_extensions.abaqus_solver_builder_factory`
    :param override_cpus: Override the task-specific default number of CPUs. This kwarg value is most useful if
        propagated from a user-specified option at execution time. If None, Abaqus Pseudo-Builder tasks will use the
        task-specific default.

    .. warning::
        You must use an AbaqusSolver Builder generated from
        :meth:`waves.scons_extensions.abaqus_solver_builder_factory`.
        Using the non-builder-factory :meth:`waves.scons_extensions.abaqus_solver` (i.e. a Builder that does not use the
        ``program_options`` kwarg) is not supported.
    """

    def __init__(
        self,
        builder: SCons.Builder.Builder,
        override_cpus: typing.Optional[int] = None,
    ) -> None:
        self.builder = builder
        self.override_cpus = override_cpus

    # TODO: address Explicit-specific restart files: ['abq', 'pac', 'sel']
    # https://re-git.lanl.gov/aea/python-projects/waves/-/issues/821
    # TODO: allow for import jobs that don't execute Abaqus with ``-oldjob {}``
    # https://re-git.lanl.gov/aea/python-projects/waves/-/issues/822
    def __call__(
        self,
        env: SCons.Environment.Environment,
        job: str,
        inp: typing.Optional[str] = None,
        user: typing.Optional[str] = None,
        cpus: int = 1,
        oldjob: typing.Optional[str] = None,
        write_restart: bool = False,
        double: str = "both",
        extra_sources: typing.Optional[typing.List[str]] = None,
        extra_targets: typing.Optional[typing.List[str]] = None,
        extra_options: str = "",
        **kwargs,
    ) -> SCons.Node.NodeList:
        """SCons Pseudo-Builder for running Abaqus jobs.

        This SCons Pseudo-Builder wraps the WAVES Abaqus builders to automatically adjust the Abaqus command, sources
        list, and target list when specifying restart jobs and user subroutines.

        .. note::
            Restart files that are only used by Abaqus/Explicit (i.e. ``.abq``, ``.pac``, and ``.sel``) are not
            currently added to the source and target lists when specifying ``oldjob`` or ``write_restart``. Use
            ``extra_sources`` and ``extra_targets`` to manually add them when needed.

        :param job: Abaqus job name *without* file extension.
        :param inp: Abaqus input file name *with* file extension. Defaults to ``job``.inp.
        :param user: User subroutine.
        :param cpus: CPUs to use for simulation. Is superceded by ``override_cpus`` if provided during object
            instantiation.  The CPUs option is escaped in the action string, i.e. changing the number of CPUs will not
            trigger a rebuild.
        :param oldjob: Name of job to restart/import.
        :param write_restart: If True, add restart files to target list. This is required if you want to use these
            restart files for a restart job.
        :param double: Passthrough option for Abaqus' ``-double ${double}``.
        :param extra_sources: Additional sources to supply to builder.
        :param extra_targets: Additional targets to supply to builder.
        :param extra_options: Additional Abaqus options to supply to builder. Should not include any Abaqus options
            available as kwargs, e.g. cpus, oldjob, user, input, job.
        :param kwargs: Any additional kwargs are passed through to the builder.

        :returns: All targets associated with Abaqus simulation.

        .. code-block::
            :caption: SConstruct

            import waves
            # Allow user to override simulation-specific default number of CPUs
            AddOption('--solve-cpus', type='int')
            env = Environment()
            env.AddMethod(waves.scons_extensions.add_program, "AddProgram")
            env["ABAQUS_PROGRAM"] = env.AddProgram(["abaqus"])
            env.Append(BUILDERS={
                "AbaqusSolver": waves.scons_extensions.abaqus_solver_builder_factory(
                    program=env["ABAQUS_PROGRAM"]
                )
            })
            env.AddMethod(
                waves.scons_extensions.AbaqusPseudoBuilder(
                    builder=env.AbaqusSolver,
                    override_cpus=env.GetOption("solve_cpus")),
                "Abaqus",
            )

        To define a simple Abaqus simulation:

        .. code-block:: python

            env.Abaqus(job='simulation_1')

        The job name can differ from the input file name:

        .. code-block:: python

            env.Abaqus(job='assembly_simulation_1', inp='simulation_1.inp')

        Specifying a user subroutine automatically adds the user subroutine to the source list:

        .. code-block:: python

            env.Abaqus(job='simulation_1', user='user.f')

        If you write restart files, you can add the restart files to the target list with:

        .. code-block:: python

            env.Abaqus(job='simulation_1', write_restart=True)

        This is important when you expect to use the restart files, as SCons will know to check that the required
        restart files exist and are up-to-date:

        .. code-block:: python

            env.Abaqus(job='simulation_2', oldjob='simulation_1')

        If your Abaqus job depends on files which aren't detected by an implicit dependency scanner, you can add them to
        the source list directly:

        .. code-block:: python

            env.Abaqus(job='simulation_1', user='user.f', extra_sources=['user_subroutine_input.csv'])

        You can specify the default number of CPUs for the simulation:

        .. code-block:: python

            env.Abaqus(job='simulation_1', cpus=4)
        """
        # Initialize with empty arguments for AbaqusSolver builder
        sources = list()
        targets = list()
        options = ""

        # Specify job name
        job_option = pathlib.Path(job).name

        # Specify "double" option, if requested
        if double:
            options += f" -double {double}"

        # Like Abaqus, assume input file is <job>.inp unless otherwise specified
        if inp is None:
            inp = f"{job}.inp"
        # Include input file as first source. Root input file *must* be first file is sources list.
        sources.insert(0, inp)

        targets.extend([f"{job}{extension}" for extension in _settings._abaqus_standard_extensions])

        # Always allow user to override CPUs with CLI option and exclude CPUs from build signature
        options += f" $(-cpus {self.override_cpus or cpus}$)"

        # If restarting a job, add old job restart files to sources
        if oldjob:
            sources.extend([f"{oldjob}{extension}" for extension in _settings._abaqus_standard_restart_extensions])
            options += f" -oldjob {oldjob}"

        # If writing restart files, add restart files to targets
        if write_restart:
            targets.extend([f"{job}{extension}" for extension in _settings._abaqus_standard_restart_extensions])

        # If user subroutine is specified, add user subroutine to sources
        if user:
            sources.append(user)
            options += f" -user {user}"

        # Append user-specified arguments for builder
        if extra_sources is not None:
            sources.extend(extra_sources)
        if extra_targets is not None:
            targets.extend(extra_targets)
        if extra_options:
            options += f" {extra_options}"

        return self.builder(target=targets, source=sources, job=job_option, program_options=options, **kwargs)


@catenate_actions(program="sbatch", options=_settings._sbatch_wrapper_options)
def sbatch_abaqus_solver_builder_factory(*args, **kwargs):
    """Thin pass through wrapper of :meth:`waves.scons_extensions.abaqus_solver_builder_factory`

    Catenate the actions and submit with `SLURM`_ `sbatch`_. Accepts the ``sbatch_options`` builder keyword argument to
    modify sbatch behavior.

    .. code-block::
       :caption: action string construction

       sbatch --wait --output=${TARGET.base}.slurm.out ${sbatch_options} --wrap "${environment} ${action_prefix} ${program} ${program_required} ${program_options} ${subcommand} ${subcommand_required} ${subcommand_options} ${action_suffix}"
    """  # noqa: E501
    return abaqus_solver_builder_factory(*args, **kwargs)


@catenate_actions(program="sbatch", options=_settings._sbatch_wrapper_options)
def sbatch_abaqus_solver(*args, **kwargs):
    """Thin pass through wrapper of :meth:`waves.scons_extensions.abaqus_solver`

    Catenate the actions and submit with `SLURM`_ `sbatch`_. Accepts the ``sbatch_options`` builder keyword argument to
    modify sbatch behavior.

    .. code-block::
       :caption: Sbatch Abaqus solver builder action default expansion

       sbatch --wait --output=${TARGET.base}.slurm.out ${sbatch_options} --wrap "${action_prefix} ${program} -job ${job_name} -input ${SOURCE.filebase} ${abaqus_options} ${required} ${action_suffix}"

    .. code-block::
       :caption: Sbatch Abaqus solver builder action default expansion

       sbatch --wait --output=${TARGET.base}.slurm.out ${sbatch_options} --wrap "cd ${TARGET.dir.abspath} && ${program} -job ${job_name} -input ${SOURCE.filebase} ${abaqus_options} -interactive -ask_delete no > ${TARGETS[-1].abspath} 2>&1"
    """  # noqa: E501
    return abaqus_solver(*args, **kwargs)


def copy_substfile(
    env: SCons.Environment.Environment,
    source_list: list,
    substitution_dictionary: typing.Optional[dict] = None,
    build_subdirectory: str = ".",
    symlink: bool = False,
) -> SCons.Node.NodeList:
    """Pseudo-builder to copy source list to build directory and perform template substitutions on ``*.in`` filenames

    `SCons Pseudo-Builder`_ to chain two builders:  a builder with the `SCons Copy`_ action and the `SCons Substfile`_
    builders. Files are first copied to the build (variant) directory and then template substitution is performed on
    template files (any file ending with ``*.in`` suffix) to create a file without the template suffix.

    When pseudo-builders are added to the environment with the `SCons AddMethod`_ function they can be accessed with the
    same syntax as a normal builder. When called from the construction environment, the ``env`` argument is omitted. See
    the example below.

    To avoid dependency cycles, the source file(s) should be passed by absolute path.

    .. code-block::
       :caption: SConstruct

       import pathlib
       import waves
       current_directory = pathlib.Path(Dir(".").abspath)
       env = Environment()
       env.AddMethod(waves.scons_extensions.copy_substfile, "CopySubstfile")
       source_list = [
           "#/subdir3/file_three.ext",              # File found with respect to project root directory using SCons notation
           current_directory / file_one.ext,        # File found in current SConscript directory
           current_directory / "subdir2/file_two",  # File found below current SConscript directory
           current_directory / "file_four.ext.in"   # File with substitutions matching substitution dictionary keys
       ]
       substitution_dictionary = {
           "@variable_one@": "value_one"
       }
       env.CopySubstfile(source_list, substitution_dictionary=substitution_dictionary)

    :param env: An SCons construction environment to use when defining the targets.
    :param source_list: List of pathlike objects or strings. Will be converted to list of pathlib.Path objects.
    :param substitution_dictionary: key: value pairs for template substitution. The keys must contain the optional
        template characters if present, e.g. ``@variable@``. The template character, e.g. ``@``, can be anything that
        works in the `SCons Substfile`_ builder.
    :param build_subdirectory: build subdirectory relative path prepended to target files
    :param symlink: Whether symbolic links are created as new symbolic links. If true, symbolic links are shallow
        copies as a new symbolic link. If false, symbolic links are copied as a new file (dereferenced).

    :return: SCons NodeList of Copy and Substfile target nodes
    """  # noqa: E501
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
            action=SCons.Defaults.Copy("${TARGET}", "${SOURCE}", symlink),
        )
        if source_file.suffix == _settings._scons_substfile_suffix:
            substfile_target = build_subdirectory / source_file.name
            target_list += env.Substfile(str(substfile_target), SUBST_DICT=substitution_dictionary)
    return target_list


def python_builder_factory(
    environment: str = "",
    action_prefix: str = _settings._cd_action_prefix,
    program: str = "python",
    program_required: str = "",
    program_options: str = "",
    subcommand: str = "${SOURCE.abspath}",
    subcommand_required: str = "",
    subcommand_options: str = "",
    action_suffix: str = _settings._redirect_action_suffix,
    emitter=first_target_emitter,
    **kwargs,
) -> SCons.Builder.Builder:
    """Python builder factory

    This builder factory extends :meth:`waves.scons_extensions.first_target_builder_factory`. This builder factory uses
    the :meth:`waves.scons_extensions.first_target_emitter`. At least one task target must be specified in the task
    definition and the last target will always be the expected STDOUT and STDERR redirection output file,
    ``TARGETS[-1]`` ending in ``*.stdout``.

    .. warning::

       Users overriding the ``emitter`` keyword argument are responsible for providing an emitter with equivalent STDOUT
       file handling behavior as :meth:`waves.scons_extensions.first_target_emitter` or updating the ``action_suffix``
       option to match their emitter's behavior.

    With the default options this builder requires the following sources file provided in the order:

    1. Python script: ``*.py``

    .. code-block::
       :caption: action string construction

       ${environment} ${action_prefix} ${program} ${program_required} ${program_options} ${subcommand} ${subcommand_required} ${subcommand_options} ${action_suffix}

    .. code-block::
       :caption: action string default expansion

       ${environment} cd ${TARGET.dir.abspath} && python ${program_required} ${program_options} ${SOURCE.abspath} ${subcommand_required} ${subcommand_options} > ${TARGETS[-1].abspath} 2>&1

    .. code-block::
       :caption: SConstruct

       import waves
       env = Environment()
       env.Append(BUILDERS={"PythonScript": waves.scons_extensions.python_builder_factory()})
       env.PythonScript(target=["my_output.stdout"], source=["my_script.py"])

    The builder returned by this factory accepts all SCons Builder arguments. The arguments of this function are also
    available as keyword arguments of the builder. When provided during task definition, the task keyword arguments
    override the builder keyword arguments.

    :param environment: This variable is intended primarily for use with builders and tasks that can not execute from an
        SCons construction environment. For instance, when tasks execute on a remote server with SSH wrapped actions
        using :meth:`waves.scons_extensions.ssh_builder_actions` and therefore must initialize the remote environment as
        part of the builder action.
    :param action_prefix: This variable is intended to perform directory change operations prior to program execution
    :param program: The Python interpreter absolute or relative path
    :param program_required: Space delimited string of required Python interpreter options and arguments that are
        crucial to builder behavior and should not be modified except by advanced users
    :param program_options: Space delimited string of optional Python interpreter options and arguments that can be
        freely modified by the user
    :param subcommand: The Python script absolute or relative path
    :param subcommand_required: Space delimited string of required Python script options and arguments
        that are crucial to builder behavior and should not be modified except by advanced users.
    :param subcommand_options: Space delimited string of optional Python script options and arguments
        that can be freely modified by the user
    :param action_suffix: This variable is intended to perform program STDOUT and STDERR redirection operations.
    :param emitter: An SCons emitter function. This is not a keyword argument in the action string.
    :param kwargs: Any additional keyword arguments are passed directly to the SCons builder object.

    :return: Python builder
    """  # noqa: E501
    builder = first_target_builder_factory(
        environment=environment,
        action_prefix=action_prefix,
        program=program,
        program_required=program_required,
        program_options=program_options,
        subcommand=subcommand,
        subcommand_required=subcommand_required,
        subcommand_options=subcommand_options,
        action_suffix=action_suffix,
        emitter=emitter,
        **kwargs,
    )
    return builder


@catenate_actions(program="sbatch", options=_settings._sbatch_wrapper_options)
def sbatch_python_builder_factory(*args, **kwargs):
    """Thin pass through wrapper of :meth:`waves.scons_extensions.python_builder_factory`

    Catenate the actions and submit with `SLURM`_ `sbatch`_. Accepts the ``sbatch_options`` builder keyword argument to
    modify sbatch behavior.

    .. code-block::
       :caption: action string construction

       sbatch --wait --output=${TARGET.base}.slurm.out ${sbatch_options} --wrap "${environment} ${action_prefix} ${program} ${program_required} ${program_options} ${subcommand} ${subcommand_required} ${subcommand_options} ${action_suffix}"
    """  # noqa: E501
    return python_builder_factory(*args, **kwargs)


def _matlab_script_emitter(
    target: list,
    source: list,
    env: SCons.Environment.Environment,
) -> typing.Tuple[list, list]:
    """Appends the matlab_script builder target list with the builder managed targets

    Appends ``target[0]``.matlab.env and ``target[0]``.stdout to the ``target`` list. The matlab_script Builder requires
    at least one target. The build tree copy of the Matlab script is not added to the target list to avoid multiply
    defined targets when the script is used more than once in the same build directory.

    The emitter will assume all emitted targets build in the current build directory. If the target(s) must be built in
    a build subdirectory, e.g. in a parameterized target build, then the first target must be provided with the build
    subdirectory, e.g. ``parameter_set1/target.ext``. When in doubt, provide a STDOUT redirect file as a target, e.g.
    ``target.stdout``.

    :param target: The target file list of strings
    :param source: The source file list of SCons.Node.FS.File objects
    :param env: The builder's SCons construction environment object

    :return: target, source
    """
    appending_suffixes = [_settings._matlab_environment_extension]
    return first_target_emitter(target, source, env, appending_suffixes=appending_suffixes)


def matlab_script(
    program: str = "matlab",
    action_prefix: str = _settings._cd_action_prefix,
    action_suffix: str = _settings._redirect_action_suffix,
    environment_suffix: str = _settings._redirect_environment_suffix,
) -> SCons.Builder.Builder:
    """Matlab script SCons builder

    .. warning::

       Experimental implementation is subject to change

    This builder requires that the Matlab script to execute is the first source in the list. The builder returned by
    this function accepts all SCons Builder arguments. The arguments of this function are also available as keyword
    arguments of the builder. When provided during task definition, the keyword arguments override the builder returned
    by this function.

    *Builder/Task keyword arguments*

    * ``program``: The Matlab command line executable absolute or relative path
    * ``matlab_options``: The Matlab command line options provided as a string.
    * ``script_options``: The Matlab function interface options in Matlab syntax and provided as a string.
    * ``action_prefix``: Advanced behavior. Most users should accept the defaults
    * ``action_suffix``: Advanced behavior. Most users should accept the defaults.
    * ``environment_suffix``: Advanced behavior. Most users should accept the defaults.

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
       :caption: Matlab script builder action keywords

       ${action_prefix} ${program} ${matlab_options} -batch "path(path, '${SOURCE.dir.abspath}'); [fileList, productList] = matlab.codetools.requiredFilesAndProducts('${SOURCE.file}'); disp(cell2table(fileList)); disp(struct2table(productList, 'AsArray', true)); exit;" ${environment_suffix}
       ${action_prefix} ${program} ${matlab_options} -batch "path(path, '${SOURCE.dir.abspath}'); ${SOURCE.filebase}(${script_options})" ${action_suffix}

    .. code-block::
       :caption: Matlab script builder action default expansion

       cd ${TARGET.dir.abspath} && matlab ${matlab_options} -batch "path(path, '${SOURCE.dir.abspath}'); [fileList, productList] = matlab.codetools.requiredFilesAndProducts('${SOURCE.file}'); disp(cell2table(fileList)); disp(struct2table(productList, 'AsArray', true)); exit;" > ${TARGETS[-2].abspath} 2>&1
       cd ${TARGET.dir.abspath} && matlab ${matlab_options} -batch "path(path, '${SOURCE.dir.abspath}'); ${SOURCE.filebase}(${script_options})" > ${TARGETS[-1].abspath} 2>&1

    :param program: An absolute path or basename string for the Matlab program.
    :param action_prefix: Advanced behavior. Most users should accept the defaults.
    :param action_suffix: Advanced behavior. Most users should accept the defaults.
    :param environment_suffix: Advanced behavior. Most users should accept the defaults.

    :return: Matlab script builder
    """  # noqa: E501
    action = [
        (
            "${action_prefix} ${program} ${matlab_options} -batch "
            "\"path(path, '${SOURCE.dir.abspath}'); "
            "[fileList, productList] = matlab.codetools.requiredFilesAndProducts('${SOURCE.file}'); "
            "disp(cell2table(fileList)); disp(struct2table(productList, 'AsArray', true)); exit;\" "
            "${environment_suffix}"
        ),
        (
            "${action_prefix} ${program} ${matlab_options} -batch "
            "\"path(path, '${SOURCE.dir.abspath}'); "
            '${SOURCE.filebase}(${script_options})" '
            "${action_suffix}"
        ),
    ]
    matlab_builder = SCons.Builder.Builder(
        action=action,
        emitter=_matlab_script_emitter,
        program=program,
        action_prefix=action_prefix,
        action_suffix=action_suffix,
        environment_suffix=environment_suffix,
    )
    return matlab_builder


def conda_environment(
    program: str = "conda",
    subcommand: str = "env export",
    required: str = "--file ${TARGET.abspath}",
    options: str = "",
    action_prefix: str = _settings._cd_action_prefix,
) -> SCons.Builder.Builder:
    """Create a Conda environment file with ``conda env export``

    This builder is intended to help WAVES workflows document the Conda environment used in the current build. The
    arguments of this function are also available as keyword arguments of the builder. When provided during task
    definition, the keyword arguments override the builder returned by this function.

    *Builder/Task keyword arguments*

    * ``program``: The Conda command line executable absolute or relative path
    * ``subcommand``: The Conda environment export subcommand
    * ``required``: A space delimited string of subcommand required arguments
    * ``options``: A space delimited string of subcommand optional arguments
    * ``action_prefix``: Advanced behavior. Most users should accept the defaults

    At least one target must be specified. The first target determines the working directory for the builder's action,
    as shown in the action code snippet below. The action changes the working directory to the first target's parent
    directory prior to creating the Conda environment file.

    .. code-block::
       :caption: Conda environment builder action default expansion

       ${action_prefix} ${program} ${subcommand} ${required} ${options}"

    .. code-block::
       :caption: Conda environment builder action default expansion

       cd ${TARGET.dir.abspath} && conda env export --file ${TARGET.abspath} ${options}

    The modsim owner may choose to re-use this builder throughout their project configuration to provide various levels
    of granularity in the recorded Conda environment state. It's recommended to include this builder at least once for
    any workflows that also use the :meth:`waves.scons_extensions.python_builder_factory`. The builder may be re-used
    once per build sub-directory to provide more granular build environment reproducibility in the event that sub-builds
    are run at different times with variations in the active Conda environment. For per-Python script task environment
    reproducibility, the builder source list can be linked to the output of a
    :meth:`waves.scons_extensions.python_builder_factory` task with a target environment file name to match.

    The first recommendation, always building the project wide Conda environment file, is demonstrated in the example
    usage below.

    .. code-block::
       :caption: SConstruct

       import waves
       env = Environment()
       env.Append(BUILDERS={"CondaEnvironment": waves.scons_extensions.conda_environment()})
       environment_target = env.CondaEnvironment(target=["environment.yaml"])
       env.AlwaysBuild(environment_target)

    :param program: The Conda command line executable absolute or relative path
    :param subcommand: The Conda environment export subcommand
    :param required: A space delimited string of subcommand required arguments
    :param options: A space delimited string of subcommand optional arguments
    :param action_prefix: Advanced behavior. Most users should accept the defaults

    :return: Conda environment builder
    """
    action = ["${action_prefix} ${program} ${subcommand} ${required} ${options}"]
    conda_environment_builder = SCons.Builder.Builder(
        action=action,
        program=program,
        subcommand=subcommand,
        required=required,
        options=options,
        action_prefix=action_prefix,
    )
    return conda_environment_builder


def _abaqus_extract_emitter(
    target: list,
    source: list,
    env: SCons.Environment.Environment,
) -> typing.Tuple[list, list]:
    """Prepends the abaqus extract builder target H5 file if none is specified. Appends the source[0].csv file unless
    ``delete_report_file`` is ``True``.  Always appends the ``target[0]_datasets.h5`` file.

    If no targets are provided to the Builder, the emitter will assume all emitted targets build in the current build
    directory. If the target(s) must be built in a build subdirectory, e.g. in a parameterized target build, then at
    least one target must be provided with the build subdirectory, e.g. ``parameter_set1/target.h5``. When in doubt,
    provide the expected H5 file as a target, e.g. ``source[0].h5``.

    :param target: The target file list of strings
    :param source: The source file list of SCons.Node.FS.File objects
    :param env: The builder's SCons construction environment object

    :return: target, source
    """
    odb_file = pathlib.Path(source[0].path).name
    odb_file = pathlib.Path(odb_file)
    build_subdirectory = _build_subdirectory(target)
    if not target or pathlib.Path(str(target[0])).suffix != ".h5":
        target.insert(0, str(build_subdirectory / odb_file.with_suffix(".h5")))
    first_target = pathlib.Path(str(target[0]))
    target.append(f"{build_subdirectory / first_target.stem}_datasets.h5")
    if "delete_report_file" not in env or not env["delete_report_file"]:
        target.append(str(build_subdirectory / first_target.with_suffix(".csv").name))
    return target, source


def abaqus_extract(program: str = "abaqus") -> SCons.Builder.Builder:
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

    .. code-block::
       :caption: Format of HDF5 file

       /                 # Top level group required in all hdf5 files
       /<instance name>/ # Groups containing data of each instance found in an odb
           FieldOutputs/      # Group with multiple xarray datasets for each field output
               <field name>/  # Group with datasets containing field output data for a specified set or surface
                              # If no set or surface is specified, the <field name> will be
                              # 'ALL_NODES' or 'ALL_ELEMENTS'
           HistoryOutputs/    # Group with multiple xarray datasets for each history output
               <region name>/ # Group with datasets containing history output data for specified history region name
                              # If no history region name is specified, the <region name> will be 'ALL NODES'
           Mesh/              # Group written from an xarray dataset with all mesh information for this instance
       /<instance name>_Assembly/ # Group containing data of assembly instance found in an odb
           Mesh/              # Group written from an xarray dataset with all mesh information for this instance
       /odb/             # Catch all group for data found in the odbreport file not already organized by instance
           info/              # Group with datasets that mostly give odb meta-data like name, path, etc.
           jobData/           # Group with datasets that contain additional odb meta-data
           rootAssembly/      # Group with datasets that match odb file organization per Abaqus documentation
           sectionCategories/ # Group with datasets that match odb file organization per Abaqus documentation
       /xarray/          # Group with a dataset that lists the location of all data written from xarray datasets

    .. code-block::
       :caption: SConstruct

       import waves
       env = Environment()
       env.AddMethod(waves.scons_extensions.add_program, "AddProgram")
       env["ABAQUS_PROGRAM"] = env.AddProgram(["abaqus"])
       env.Append(BUILDERS={"AbaqusExtract": waves.scons_extensions.abaqus_extract()})
       env.AbaqusExtract(target=["my_job.h5", "my_job.csv"], source=["my_job.odb"])

    :param program: An absolute path or basename string for the abaqus program

    :return: Abaqus extract builder
    """
    abaqus_extract_builder = SCons.Builder.Builder(
        action=[
            SCons.Action.Action(_build_odb_extract, varlist=["output_type", "odb_report_args", "delete_report_file"])
        ],
        emitter=_abaqus_extract_emitter,
        program=program,
    )
    return abaqus_extract_builder


def _build_odb_extract(
    target: list,
    source: list,
    env: SCons.Environment.Environment,
) -> None:
    """Define the odb_extract action when used as an internal package and not a command line utility

    :param target: The target file list of strings
    :param source: The source file list of SCons.Node.FS.File objects
    :param env: The builder's SCons construction environment object
    """
    # Avoid importing odb extract module (heavy) unless necessary
    from waves._abaqus import odb_extract

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

    odb_extract.odb_extract(
        [source[0].abspath],
        target[0].abspath,
        output_type=output_type,
        odb_report_args=odb_report_args,
        abaqus_command=env["program"],
        delete_report_file=delete_report_file,
    )
    return None


def sbatch(
    program: str = "sbatch",
    required: str = "--wait --output=${TARGETS[-1].abspath}",
    action_prefix: str = _settings._cd_action_prefix,
) -> SCons.Builder.Builder:
    """`SLURM`_ `sbatch`_ SCons builder

    The builder returned by this function accepts all SCons Builder arguments. The arguments of this function are also
    available as keyword arguments of the builder. When provided during task definition, the keyword arguments override
    the builder returned by this function.

    *Builder/Task keyword arguments*

    * ``program``: The sbatch command line executable absolute or relative path
    * ``required``: A space delimited string of sbatch required arguments
    * ``slurm_job``: The command to submit with sbatch
    * ``sbatch_options``: Optional sbatch options
    * ``action_prefix``: Advanced behavior. Most users should accept the defaults

    The builder does not use a SLURM batch script. Instead, it requires the ``slurm_job`` variable to be defined with
    the command string to execute.

    At least one target must be specified. The first target determines the working directory for the builder's action,
    as shown in the action code snippet below. The action changes the working directory to the first target's parent
    directory prior to executing the journal file.

    The Builder emitter will append the builder managed targets automatically. Appends ``target[0]``.stdout to the
    ``target`` list.

    .. code-block::
       :caption: SLURM sbatch builder action keywords

       ${action_prefix} ${program} ${required} ${sbatch_options} --wrap "${slurm_job}"

    .. code-block::
       :caption: SLURM sbatch builder action default expansion

       cd ${TARGET.dir.abspath} && sbatch --wait --output=${TARGETS[-1].abspath} ${sbatch_options} --wrap "${slurm_job}"

    .. code-block::
       :caption: SConstruct

       import waves
       env = Environment()
       env.Append(BUILDERS={"SlurmSbatch": waves.scons_extensions.sbatch()})
       env.SlurmSbatch(target=["my_output.stdout"], source=["my_source.input"], slurm_job="cat $SOURCE > $TARGET")

    :param program: An absolute path or basename string for the sbatch program.
    :param required: A space delimited string of sbatch required arguments
    :param action_prefix: Advanced behavior. Most users should accept the defaults.

    :return: SLURM sbatch builder
    """
    action = ['${action_prefix} ${program} ${required} ${sbatch_options} --wrap "${slurm_job}"']
    sbatch_builder = SCons.Builder.Builder(
        action=action,
        emitter=first_target_emitter,
        program=program,
        required=required,
        action_prefix=action_prefix,
    )
    return sbatch_builder


def abaqus_input_scanner() -> SCons.Scanner.Scanner:
    """Abaqus input file dependency scanner

    Custom SCons scanner that searches for the ``INPUT=`` parameter and associated file dependencies inside Abaqus
    ``*.inp`` files.

    :return: Abaqus input file dependency Scanner
    """
    flags = re.IGNORECASE
    return _custom_scanner(r"^\*[^*]*,\s*input=(.+)$", [".inp"], flags)


def sphinx_scanner() -> SCons.Scanner.Scanner:
    """SCons scanner that searches for directives

    * ``.. include::``
    * ``.. literalinclude::``
    * ``.. image::``
    * ``.. figure::``
    * ``.. bibliography::``

    inside ``.rst`` and ``.txt`` files

    :return: Sphinx source file dependency Scanner
    """
    return _custom_scanner(r"^\s*\.\. (?:include|literalinclude|image|figure|bibliography)::\s*(.+)$", [".rst", ".txt"])


def sphinx_build(
    program: str = "sphinx-build",
    options: str = "",
    builder: str = "html",
    tags: str = "",
) -> SCons.Builder.Builder:
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

    :param program: sphinx-build executable
    :param options: sphinx-build options
    :param builder: builder name. See the `Sphinx`_ documentation for options
    :param tags: sphinx-build tags

    :returns: Sphinx builder
    """
    sphinx_builder = SCons.Builder.Builder(
        action=["${program} ${options} -b ${builder} ${TARGET.dir.dir.abspath} ${TARGET.dir.abspath} ${tags}"],
        program=program,
        options=options,
        builder=builder,
        tags=tags,
    )
    return sphinx_builder


def sphinx_latexpdf(
    program: str = "sphinx-build",
    options: str = "",
    builder: str = "latexpdf",
    tags: str = "",
) -> SCons.Builder.Builder:
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

    :returns: Sphinx latexpdf builder
    """
    sphinx_latex = SCons.Builder.Builder(
        action=["${program} -M ${builder} ${TARGET.dir.dir.abspath} ${TARGET.dir.dir.abspath} ${tags} ${options}"],
        program=program,
        options=options,
        builder=builder,
        tags=tags,
    )
    return sphinx_latex


def _custom_scanner(
    pattern: str,
    suffixes: typing.Iterable[str],
    flags: typing.Optional[int] = None,
) -> SCons.Scanner.Scanner:
    """Custom Scons scanner

    constructs a scanner object based on a regular expression pattern. Will only search for files matching the list of
    suffixes provided. ``_custom_scanner`` will always use the ``re.MULTILINE`` flag
    https://docs.python.org/3/library/re.html#re.MULTILINE

    :param pattern: Regular expression pattern.
    :param suffixes: List of suffixes of files to search
    :param flags: An integer representing the combination of re module flags to be used during compilation.
        Additional flags can be combined using the bitwise OR (|) operator. The re.MULTILINE flag is automatically added
        to the combination.

    :return: Custom Scons scanner
    """
    flags = re.MULTILINE if not flags else re.MULTILINE | flags
    expression = re.compile(pattern, flags)

    def suffix_only(node_list: list) -> list:
        """Recursively search for files that end in the given suffixes

        :param node_list: List of SCons Node objects representing the nodes to process

        :return: List of file dependencies to include for recursive scanning
        """
        return [node for node in node_list if node.path.endswith(tuple(suffixes))]

    def regex_scan(node: SCons.Node.FS, env: SCons.Environment.Environment, path: str) -> list:
        """Scan function for extracting dependencies from the content of a file based on the given regular expression.

        The interface of the scan function is fixed by SCons. It must include ``node``, ``env`` and ``path``. It may
        contain additional arguments if needed. For more information please read the SCons Scanner tutorial:
        https://scons.org/doc/1.2.0/HTML/scons-user/c3755.html

        :param node: SCons Node object representing the file to scan
        :param env: SCons Environment object
        :param path: Path argument passed to the scan function

        :return: List of file dependencies found during scanning
        """
        contents = node.get_text_contents()
        includes = expression.findall(contents)
        includes = [file.strip() for file in includes]
        return includes

    custom_scanner = SCons.Scanner.Scanner(function=regex_scan, skeys=suffixes, recursive=suffix_only)
    return custom_scanner


def quinoa_builder_factory(
    environment: str = "",
    action_prefix: str = _settings._cd_action_prefix,
    program: str = "charmrun",
    program_required: str = "",
    program_options: str = "+p1",
    subcommand: str = "inciter",
    subcommand_required: str = "--control ${SOURCES[0].abspath} --input ${SOURCES[1].abspath}",
    subcommand_options: str = "",
    action_suffix: str = _settings._redirect_action_suffix,
    emitter=first_target_emitter,
    **kwargs,
) -> SCons.Builder.Builder:
    """Quinoa builder factory

    This builder factory extends :meth:`waves.scons_extensions.first_target_builder_factory`. This builder factory uses
    the :meth:`waves.scons_extensions.first_target_emitter`. At least one task target must be specified in the task
    definition and the last target will always be the expected STDOUT and STDERR redirection output file,
    ``TARGETS[-1]`` ending in ``*.stdout``.

    .. warning::

       Users overriding the ``emitter`` keyword argument are responsible for providing an emitter with equivalent STDOUT
       file handling behavior as :meth:`waves.scons_extensions.first_target_emitter` or updating the ``action_suffix``
       option to match their emitter's behavior.

    With the default options this builder requires the following sources file provided in the order:

    1. Quinoa control file: ``*.q``
    2. Exodus mesh file: ``*.exo``

    .. code-block::
       :caption: action string construction

       ${environment} ${action_prefix} ${program} ${program_required} ${program_options} ${subcommand} ${subcommand_required} ${subcommand_options} ${action_suffix}

    .. code-block::
       :caption: action string default expansion

       ${environment} cd ${TARGET.dir.abspath} && charmrun ${program_required} +p1 inciter --control ${SOURCES[0].abspath} --input ${SOURCES[1].abspath} ${subcommand_options} > ${TARGETS[-1].abspath} 2>&1

    .. code-block::
       :caption: SConstruct

       import waves
       env = waves.scons_extensions.shell_environment("module load quinoa")
       env.Append(BUILDERS={
           "QuinoaSolver": waves.scons_extensions.quinoa_builder_factory(),
       })
       # Serial execution with "+p1"
       env.QuinoaSolver(target=["flow.stdout"], source=["flow.lua", "box.exo"])
       # Parallel execution with "+p4"
       env.QuinoaSolver(target=["flow.stdout"], source=["flow.lua", "box.exo"], program_options="+p4")

    The builder returned by this factory accepts all SCons Builder arguments. The arguments of this function are also
    available as keyword arguments of the builder. When provided during task definition, the task keyword arguments
    override the builder keyword arguments.

    :param environment: This variable is intended primarily for use with builders and tasks that can not execute from an
        SCons construction environment. For instance, when tasks execute on a remote server with SSH wrapped actions
        using :meth:`waves.scons_extensions.ssh_builder_actions` and therefore must initialize the remote environment as
        part of the builder action.
    :param action_prefix: This variable is intended to perform directory change operations prior to program execution
    :param program: The charmrun absolute or relative path
    :param program_required: Space delimited string of required charmrun options and arguments that are crucial to
        builder behavior and should not be modified except by advanced users
    :param program_options: Space delimited string of optional charmrun options and arguments that can be freely
        modified by the user
    :param subcommand: The inciter (quinoa executable) absolute or relative path
    :param subcommand_required: Space delimited string of required inciter (quinoa executable) options and arguments
        that are crucial to builder behavior and should not be modified except by advanced users.
    :param subcommand_options: Space delimited string of optional inciter (quinoa executable) options and arguments
        that can be freely modified by the user
    :param action_suffix: This variable is intended to perform program STDOUT and STDERR redirection operations.
    :param emitter: An SCons emitter function. This is not a keyword argument in the action string.
    :param kwargs: Any additional keyword arguments are passed directly to the SCons builder object.

    :return: Quinoa builder
    """  # noqa: E501
    builder = first_target_builder_factory(
        environment=environment,
        action_prefix=action_prefix,
        program=program,
        program_required=program_required,
        program_options=program_options,
        subcommand=subcommand,
        subcommand_required=subcommand_required,
        subcommand_options=subcommand_options,
        action_suffix=action_suffix,
        emitter=emitter,
        **kwargs,
    )
    return builder


@catenate_actions(program="sbatch", options=_settings._sbatch_wrapper_options)
def sbatch_quinoa_builder_factory(*args, **kwargs):
    """Thin pass through wrapper of :meth:`waves.scons_extensions.quinoa_builder_factory`

    Catenate the actions and submit with `SLURM`_ `sbatch`_. Accepts the ``sbatch_options`` builder keyword argument to
    modify sbatch behavior.

    .. code-block::
       :caption: action string construction

       sbatch --wait --output=${TARGET.base}.slurm.out ${sbatch_options} --wrap "${environment} ${action_prefix} ${program} ${program_required} ${program_options} ${subcommand} ${subcommand_required} ${subcommand_options} ${action_suffix}"
    """  # noqa: E501
    return quinoa_builder_factory(*args, **kwargs)


def calculix_builder_factory(
    environment: str = "",
    action_prefix: str = _settings._cd_action_prefix,
    program: str = "ccx",
    program_required: str = "-i ${SOURCE.filebase}",
    program_options: str = "",
    subcommand: str = "",
    subcommand_required: str = "",
    subcommand_options: str = "",
    action_suffix: str = _settings._redirect_action_suffix,
    emitter=first_target_emitter,
    **kwargs,
) -> SCons.Builder.Builder:
    """CalculiX builder factory.

    .. warning::

       This is an experimental builder. It is subject to change without warning.

    This builder factory extends :meth:`waves.scons_extensions.first_target_builder_factory`. This builder factory uses
    the :meth:`waves.scons_extensions.first_target_emitter`. At least one task target must be specified in the task
    definition and the last target will always be the expected STDOUT and STDERR redirection output file,
    ``TARGETS[-1]`` ending in ``*.stdout``.

    .. warning::

       Users overriding the ``emitter`` keyword argument are responsible for providing an emitter with equivalent STDOUT
       file handling behavior as :meth:`waves.scons_extensions.first_target_emitter` or updating the ``action_suffix``
       option to match their emitter's behavior.

    .. warning::

       CalculiX always appends the ``.inp`` extension to the input file argument. Stripping the extension in the builder
       requires a file basename without preceding relative or absolute path. This builder is fragile to current working
       directory. Most users should not modify the ``action_prefix``.

    With the default options this builder requires the following sources file provided in the order:

    1. CalculiX input file: ``*.inp``

    .. code-block::
       :caption: action string construction

       ${environment} ${action_prefix} ${program} ${program_required} ${program_options} ${subcommand} ${subcommand_required} ${subcommand_options} ${action_suffix}

    .. code-block::
       :caption: action string default expansion

       ${environment} cd ${TARGET.dir.abspath} && ccx -i ${SOURCE.filebase} ${program_required} ${subcommand} ${subcommand_required} ${subcommand_options} > ${TARGETS[-1].abspath} 2>&1

    .. code-block::
       :caption: SConstruct

       import waves
       env = Environment()
       env.AddMethod(waves.scons_extensions.add_program, "AddProgram")
       env["CCX_PROGRAM"] = env.AddProgram(["ccx"])
       env.Append(BUILDERS={
           "CalculiX": waves.scons_extensions.calculix_builder_factory(
               subcommand=env["CCX_PROGRAM"]
           )
       })
       env.CalculiX(
           target=["target.stdout"],
           source=["source.inp"],
       )

    The builder returned by this factory accepts all SCons Builder arguments. The arguments of this function are also
    available as keyword arguments of the builder. When provided during task definition, the task keyword arguments
    override the builder keyword arguments.

    :param environment: This variable is intended primarily for use with builders and tasks that can not execute from an
        SCons construction environment. For instance, when tasks execute on a remote server with SSH wrapped actions
        using :meth:`waves.scons_extensions.ssh_builder_actions` and therefore must initialize the remote environment as
        part of the builder action.
    :param action_prefix: This variable is intended to perform directory change operations prior to program execution
    :param program: The CalculiX ``ccx`` absolute or relative path
    :param program_required: Space delimited string of required CalculiX options and arguments that are crucial to
        builder behavior and should not be modified except by advanced users
    :param program_options: Space delimited string of optional CalculiX options and arguments that can be freely
        modified by the user
    :param subcommand: A subcommand absolute or relative path
    :param subcommand_required: Space delimited string of required subcommand options and arguments
        that are crucial to builder behavior and should not be modified except by advanced users.
    :param subcommand_options: Space delimited string of optional subcommand options and arguments
        that can be freely modified by the user
    :param action_suffix: This variable is intended to perform program STDOUT and STDERR redirection operations.
    :param emitter: An SCons emitter function. This is not a keyword argument in the action string.
    :param kwargs: Any additional keyword arguments are passed directly to the SCons builder object.

    :returns: CalculiX builder
    """  # noqa: E501
    builder = first_target_builder_factory(
        environment=environment,
        action_prefix=action_prefix,
        program=program,
        program_required=program_required,
        program_options=program_options,
        subcommand=subcommand,
        subcommand_required=subcommand_required,
        subcommand_options=subcommand_options,
        action_suffix=action_suffix,
        emitter=emitter,
        **kwargs,
    )
    return builder


def fierro_explicit_builder_factory(
    environment: str = "",
    action_prefix: str = _settings._cd_action_prefix,
    program: str = "mpirun",
    program_required: str = "",
    program_options: str = "-np 1",
    subcommand: str = "fierro-parallel-explicit",
    subcommand_required: str = "${SOURCE.abspath}",
    subcommand_options: str = "",
    action_suffix: str = _settings._redirect_action_suffix,
    emitter=first_target_emitter,
    **kwargs,
) -> SCons.Builder.Builder:
    """Fierro explicit builder factory.

    .. warning::

       This is an experimental builder. It is subject to change without warning.

    This builder factory extends :meth:`waves.scons_extensions.first_target_builder_factory`. This builder factory uses
    the :meth:`waves.scons_extensions.first_target_emitter`. At least one task target must be specified in the task
    definition and the last target will always be the expected STDOUT and STDERR redirection output file,
    ``TARGETS[-1]`` ending in ``*.stdout``.

    .. warning::

       Users overriding the ``emitter`` keyword argument are responsible for providing an emitter with equivalent STDOUT
       file handling behavior as :meth:`waves.scons_extensions.first_target_emitter` or updating the ``action_suffix``
       option to match their emitter's behavior.

    With the default options this builder requires the following sources file provided in the order:

    1. Fierro input file: ``*.yaml``

    .. code-block::
       :caption: action string construction

       ${environment} ${action_prefix} ${program} ${program_required} ${program_options} ${subcommand} ${subcommand_required} ${subcommand_options} ${action_suffix}

    .. code-block::
       :caption: action string default expansion

       ${environment} cd ${TARGET.dir.abspath} && mpirun ${program_required} -np 1 fierro-parallel-explicit ${SOURCE.abspath} ${subcommand_options} > ${TARGETS[-1].abspath} 2>&1

    .. code-block::
       :caption: SConstruct

       import waves
       env = Environment()
       env.AddMethod(waves.scons_extensions.add_program, "AddProgram")
       env["FIERRO_EXPLICIT_PROGRAM"] = env.AddProgram(["fierro-parallel-explicit"])
       env.Append(BUILDERS={
           "FierroExplicit": waves.scons_extensions.fierro_explicit_builder_factory(
               subcommand=env["FIERRO_EXPLICIT_PROGRAM"]
           )
       })
       env.FierroExplicit(
           target=["target.stdout"],
           source=["source.yaml"],
       )

    The builder returned by this factory accepts all SCons Builder arguments. The arguments of this function are also
    available as keyword arguments of the builder. When provided during task definition, the task keyword arguments
    override the builder keyword arguments.

    :param environment: This variable is intended primarily for use with builders and tasks that can not execute from an
        SCons construction environment. For instance, when tasks execute on a remote server with SSH wrapped actions
        using :meth:`waves.scons_extensions.ssh_builder_actions` and therefore must initialize the remote environment as
        part of the builder action.
    :param action_prefix: This variable is intended to perform directory change operations prior to program execution
    :param program: The mpirun absolute or relative path
    :param program_required: Space delimited string of required mpirun options and arguments that are crucial to
        builder behavior and should not be modified except by advanced users
    :param program_options: Space delimited string of optional mpirun options and arguments that can be freely
        modified by the user
    :param subcommand: The Fierro absolute or relative path
    :param subcommand_required: Space delimited string of required Fierro options and arguments
        that are crucial to builder behavior and should not be modified except by advanced users.
    :param subcommand_options: Space delimited string of optional Fierro options and arguments
        that can be freely modified by the user
    :param action_suffix: This variable is intended to perform program STDOUT and STDERR redirection operations.
    :param emitter: An SCons emitter function. This is not a keyword argument in the action string.
    :param kwargs: Any additional keyword arguments are passed directly to the SCons builder object.

    :returns: Fierro explicit builder
    """  # noqa: E501
    builder = first_target_builder_factory(
        environment=environment,
        action_prefix=action_prefix,
        program=program,
        program_required=program_required,
        program_options=program_options,
        subcommand=subcommand,
        subcommand_required=subcommand_required,
        subcommand_options=subcommand_options,
        action_suffix=action_suffix,
        emitter=emitter,
        **kwargs,
    )
    return builder


def fierro_implicit_builder_factory(
    environment: str = "",
    action_prefix: str = _settings._cd_action_prefix,
    program: str = "mpirun",
    program_required: str = "",
    program_options: str = "-np 1",
    subcommand: str = "fierro-parallel-implicit",
    subcommand_required: str = "${SOURCE.abspath}",
    subcommand_options: str = "",
    action_suffix: str = _settings._redirect_action_suffix,
    emitter=first_target_emitter,
    **kwargs,
) -> SCons.Builder.Builder:
    """Fierro implicit builder factory.

    .. warning::

       This is an experimental builder. It is subject to change without warning.

    This builder factory extends :meth:`waves.scons_extensions.first_target_builder_factory`. This builder factory uses
    the :meth:`waves.scons_extensions.first_target_emitter`. At least one task target must be specified in the task
    definition and the last target will always be the expected STDOUT and STDERR redirection output file,
    ``TARGETS[-1]`` ending in ``*.stdout``.

    With the default options this builder requires the following sources file provided in the order:

    1. Fierro input file: ``*.yaml``

    .. code-block::
       :caption: action string construction

       ${environment} ${action_prefix} ${program} ${program_required} ${program_options} ${subcommand} ${subcommand_required} ${subcommand_options} ${action_suffix}

    .. code-block::
       :caption: action string default expansion

       ${environment} cd ${TARGET.dir.abspath} && mpirun ${program_required} -np 1 fierro-parallel-implicit ${SOURCE.abspath} ${subcommand_options} > ${TARGETS[-1].abspath} 2>&1

    .. code-block::
       :caption: SConstruct

       import waves
       env = Environment()
       env.AddMethod(waves.scons_extensions.add_program, "AddProgram")
       env["FIERRO_IMPLICIT_PROGRAM"] = env.AddProgram(["fierro-parallel-implicit"])
       env.Append(BUILDERS={
           "FierroImplicit": waves.scons_extensions.fierro_implicit_builder_factory(
               subcommand=env["FIERRO_IMPLICIT_PROGRAM"]
           )
       })
       env.FierroImplicit(
           target=["target.stdout"],
           source=["source.yaml"],
       )

    The builder returned by this factory accepts all SCons Builder arguments. The arguments of this function are also
    available as keyword arguments of the builder. When provided during task definition, the task keyword arguments
    override the builder keyword arguments.

    :param environment: This variable is intended primarily for use with builders and tasks that can not execute from an
        SCons construction environment. For instance, when tasks execute on a remote server with SSH wrapped actions
        using :meth:`waves.scons_extensions.ssh_builder_actions` and therefore must initialize the remote environment as
        part of the builder action.
    :param action_prefix: This variable is intended to perform directory change operations prior to program execution
    :param program: The mpirun absolute or relative path
    :param program_required: Space delimited string of required mpirun options and arguments that are crucial to
        builder behavior and should not be modified except by advanced users
    :param program_options: Space delimited string of optional mpirun options and arguments that can be freely
        modified by the user
    :param subcommand: The Fierro absolute or relative path
    :param subcommand_required: Space delimited string of required Fierro options and arguments
        that are crucial to builder behavior and should not be modified except by advanced users.
    :param subcommand_options: Space delimited string of optional Fierro options and arguments
        that can be freely modified by the user
    :param action_suffix: This variable is intended to perform program STDOUT and STDERR redirection operations.
    :param emitter: An SCons emitter function. This is not a keyword argument in the action string.
    :param kwargs: Any additional keyword arguments are passed directly to the SCons builder object.

    :returns: Fierro implicit builder
    """  # noqa: E501
    builder = first_target_builder_factory(
        environment=environment,
        action_prefix=action_prefix,
        program=program,
        program_required=program_required,
        program_options=program_options,
        subcommand=subcommand,
        subcommand_required=subcommand_required,
        subcommand_options=subcommand_options,
        action_suffix=action_suffix,
        emitter=emitter,
        **kwargs,
    )
    return builder


def sierra_builder_factory(
    environment: str = "",
    action_prefix: str = _settings._cd_action_prefix,
    program: str = "sierra",
    program_required: str = "",
    program_options: str = "",
    subcommand: str = "adagio",
    subcommand_required: str = "-i ${SOURCE.abspath}",
    subcommand_options: str = "",
    action_suffix: str = _settings._redirect_action_suffix,
    emitter=first_target_emitter,
    **kwargs,
) -> SCons.Builder.Builder:
    """Sierra builder factory

    This builder factory extends :meth:`waves.scons_extensions.first_target_builder_factory`. This builder factory uses
    the :meth:`waves.scons_extensions.first_target_emitter`. At least one task target must be specified in the task
    definition and the last target will always be the expected STDOUT and STDERR redirection output file,
    ``TARGETS[-1]`` ending in ``*.stdout``.

    .. warning::

       Users overriding the ``emitter`` keyword argument are responsible for providing an emitter with equivalent STDOUT
       file handling behavior as :meth:`waves.scons_extensions.first_target_emitter` or updating the ``action_suffix``
       option to match their emitter's behavior.

    With the default options this builder requires the following sources file provided in the order:

    1. Sierra input file: ``*.i``

    .. code-block::
       :caption: action string construction

       ${environment} ${action_prefix} ${program} ${program_required} ${program_options} ${subcommand} ${subcommand_required} ${subcommand_options} ${action_suffix}

    .. code-block::
       :caption: action string default expansion

       ${environment} cd ${TARGET.dir.abspath} && sierra ${program_required} ${program_options} adagio ${SOURCE.abspath} ${subcommand_options} > ${TARGETS[-1].abspath} 2>&1

    The builder returned by this factory accepts all SCons Builder arguments. The arguments of this function are also
    available as keyword arguments of the builder. When provided during task definition, the task keyword arguments
    override the builder keyword arguments.

    :param environment: This variable is intended primarily for use with builders and tasks that can not execute from an
        SCons construction environment. For instance, when tasks execute on a remote server with SSH wrapped actions
        using :meth:`waves.scons_extensions.ssh_builder_actions` and therefore must initialize the remote environment as
        part of the builder action.
    :param action_prefix: This variable is intended to perform directory change operations prior to program execution
    :param program: The Sierra absolute or relative path
    :param program_required: Space delimited string of required Sierra options and arguments that are crucial to
        builder behavior and should not be modified except by advanced users
    :param program_options: Space delimited string of optional Sierra options and arguments that can be freely
        modified by the user
    :param subcommand: The Sierra application absolute or relative path
    :param subcommand_required: Space delimited string of required Sierra application options and arguments
        that are crucial to builder behavior and should not be modified except by advanced users.
    :param subcommand_options: Space delimited string of optional Sierra application options and arguments
        that can be freely modified by the user
    :param action_suffix: This variable is intended to perform program STDOUT and STDERR redirection operations.
    :param emitter: An SCons emitter function. This is not a keyword argument in the action string.
    :param kwargs: Any additional keyword arguments are passed directly to the SCons builder object.

    :returns: Sierra builder
    """  # noqa: E501
    builder = first_target_builder_factory(
        environment=environment,
        action_prefix=action_prefix,
        program=program,
        program_required=program_required,
        program_options=program_options,
        subcommand=subcommand,
        subcommand_required=subcommand_required,
        subcommand_options=subcommand_options,
        action_suffix=action_suffix,
        emitter=emitter,
        **kwargs,
    )
    return builder


@catenate_actions(program="sbatch", options=_settings._sbatch_wrapper_options)
def sbatch_sierra_builder_factory(*args, **kwargs):
    """Thin pass through wrapper of :meth:`waves.scons_extensions.sierra_builder_factory`

    Catenate the actions and submit with `SLURM`_ `sbatch`_. Accepts the ``sbatch_options`` builder keyword argument to
    modify sbatch behavior.

    .. code-block::
       :caption: action string construction

       sbatch --wait --output=${TARGET.base}.slurm.out ${sbatch_options} --wrap "${environment} ${action_prefix} ${program} ${program_required} ${program_options} ${subcommand} ${subcommand_required} ${subcommand_options} ${action_suffix}"
    """  # noqa: E501
    return sierra_builder_factory(*args, **kwargs)


def ansys_apdl_builder_factory(
    environment: str = "",
    action_prefix: str = _settings._cd_action_prefix,
    program: str = "ansys",
    program_required: str = "-i ${SOURCES[0].abspath} -o ${TARGETS[-1].abspath}",
    program_options: str = "",
    subcommand: str = "",
    subcommand_required: str = "",
    subcommand_options: str = "",
    action_suffix: str = "",
    emitter=first_target_emitter,
    **kwargs,
) -> SCons.Builder.Builder:
    """Ansys APDL builder factory.

    .. warning::

       This is an experimental builder. It is subject to change without warning.

    .. warning::

       This builder does not have a tutorial and is not included in the regression test suite yet. Contact the
       development team if you encounter problems or have recommendations for improved design behavior.

    This builder factory extends :meth:`waves.scons_extensions.first_target_builder_factory`. This builder factory uses
    the :meth:`waves.scons_extensions.first_target_emitter`. At least one task target must be specified in the task
    definition and the last target will always be the expected STDOUT and STDERR redirection output file,
    ``TARGETS[-1]`` ending in ``*.stdout``.

    .. warning::

       Users overriding the ``emitter`` keyword argument are responsible for providing an emitter with equivalent STDOUT
       file handling behavior as :meth:`waves.scons_extensions.first_target_emitter` or updating the ``program_required``
       option to match their emitter's behavior.

    With the default options this builder requires the following sources file provided in the order:

    1. Ansys APDL file: ``*.dat``

    .. code-block::
       :caption: action string construction

       ${environment} ${action_prefix} ${program} ${program_required} ${program_options} ${subcommand} ${subcommand_required} ${subcommand_options} ${action_suffix}

    .. code-block::
       :caption: action string default expansion

       ${environment} cd ${TARGET.dir.abspath} && ansys -i ${SOURCES[0].abspath} -o ${TARGETS[-1].abspath} ${program_options} ${subcommand} ${subcommand_required} ${subcommand_options} ${action_suffix}

    .. code-block::
       :caption: SConstruct

       import waves
       env = Environment()
       env.AddMethod(waves.scons_extensions.add_program, "AddProgram")
       env["ANSYS_PROGRAM"] = env.AddProgram(["ansys232"])
       env.Append(BUILDERS={
            "AnsysAPDL": waves.scons_extensions.ansys_apdl_builder_factory(
                program=env["ANSYS_PROGRAM"]
            )
       })
       env.AnsysAPDL(
           target=["job.rst"],
           source=["source.dat"],
           program_options="-j job"
       )

    The builder returned by this factory accepts all SCons Builder arguments. The arguments of this function are also
    available as keyword arguments of the builder. When provided during task definition, the task keyword arguments
    override the builder keyword arguments.

    :param environment: This variable is intended primarily for use with builders and tasks that can not execute from an
        SCons construction environment. For instance, when tasks execute on a remote server with SSH wrapped actions
        using :meth:`waves.scons_extensions.ssh_builder_actions` and therefore must initialize the remote environment as
        part of the builder action.
    :param action_prefix: This variable is intended to perform directory change operations prior to program execution
    :param program: The Ansys absolute or relative path
    :param program_required: Space delimited string of required Ansys options and arguments that are crucial to
        builder behavior and should not be modified except by advanced users
    :param program_options: Space delimited string of optional Ansys options and arguments that can be freely
        modified by the user
    :param subcommand: A subcommand absolute or relative path
    :param subcommand_required: Space delimited string of required subcommand options and arguments
        that are crucial to builder behavior and should not be modified except by advanced users.
    :param subcommand_options: Space delimited string of optional subcommand options and arguments
        that can be freely modified by the user
    :param action_suffix: This variable is intended to perform program STDOUT and STDERR redirection operations.
    :param emitter: An SCons emitter function. This is not a keyword argument in the action string.
    :param kwargs: Any additional keyword arguments are passed directly to the SCons builder object.

    :returns: Ansys builder
    """  # noqa: E501
    builder = first_target_builder_factory(
        environment=environment,
        action_prefix=action_prefix,
        program=program,
        program_required=program_required,
        program_options=program_options,
        subcommand=subcommand,
        subcommand_required=subcommand_required,
        subcommand_options=subcommand_options,
        action_suffix=action_suffix,
        emitter=emitter,
        **kwargs,
    )
    return builder


def truchas_builder_factory(
    environment: str = "",
    action_prefix: str = "cd ${TARGET.dir.dir.abspath} &&",
    program: str = "mpirun",
    program_required: str = "",
    program_options: str = "-np 1",
    subcommand: str = "truchas",
    subcommand_required: str = "-f -o:${TARGET.dir.filebase} ${SOURCE.abspath}",
    subcommand_options: str = "",
    action_suffix: str = _settings._redirect_action_suffix,
    emitter=first_target_emitter,
    **kwargs,
) -> SCons.Builder.Builder:
    """Truchas builder factory.

    .. warning::

       This is an experimental builder. It is subject to change without warning.

    .. warning::

       This builder is not included in the regression test suite yet. Contact the development team if you encounter
       problems or have recommendations for improved design behavior.

    This builder factory extends :meth:`waves.scons_extensions.first_target_builder_factory`. This builder factory uses
    the :meth:`waves.scons_extensions.first_target_emitter`. At least one task target must be specified in the task
    definition and the last target will always be the expected STDOUT and STDERR redirection output file,
    ``TARGETS[-1]`` ending in ``*.stdout``.

    .. warning::

       Note that this builder's action prefix is different from other builders. Truchas output control produces a
       build subdirectory, so the action prefix moves up *two* directories above the expected output instead of one.
       All Truchas output targets must include the requested output directory and the output directory name must match
       the target file basename, e.g. ``target/target.log`` and ``parameter_set1/target/target.log``.

    With the default options this builder requires the following sources file provided in the order:

    1. Truchas input file: ``*.inp``

    With the default options this builder requires the following target file provided in the order:

    1. Truchas output log with desired output directory: ``target/target.log``

    .. code-block::
       :caption: action string construction

       ${environment} ${action_prefix} ${program} ${program_required} ${program_options} ${subcommand} ${subcommand_required} ${subcommand_options} ${action_suffix}

    .. code-block::
       :caption: action string default expansion

       ${environment} cd ${TARGET.dir.dir.abspath} && mpirun ${program_required} -np 1 truchas -f -o:${TARGET.dir.filebase} ${SOURCE.abspath} ${subcommand_options} > ${TARGETS[-1].abspath} 2>&1

    .. code-block::
       :caption: SConstruct

       import waves
       env = Environment()
       env.AddMethod(waves.scons_extensions.add_program, "AddProgram")
       env["TRUCHAS_PROGRAM"] = env.AddProgram(["truchas"])
       env.Append(BUILDERS={
           "Truchas": waves.scons_extensions.truchas_builder_factory(
               subcommand=env["TRUCHAS_PROGRAM"]
           )
       })
       env.Truchas(
           target=[
               "target/target.log"
               "target/target.h5"
           ],
           source=["source.inp"],
       )

    The builder returned by this factory accepts all SCons Builder arguments. The arguments of this function are also
    available as keyword arguments of the builder. When provided during task definition, the task keyword arguments
    override the builder keyword arguments.

    :param environment: This variable is intended primarily for use with builders and tasks that can not execute from an
        SCons construction environment. For instance, when tasks execute on a remote server with SSH wrapped actions
        using :meth:`waves.scons_extensions.ssh_builder_actions` and therefore must initialize the remote environment as
        part of the builder action.
    :param action_prefix: This variable is intended to perform directory change operations prior to program execution
    :param program: The mpirun absolute or relative path
    :param program_required: Space delimited string of required mpirun options and arguments that are crucial to
        builder behavior and should not be modified except by advanced users
    :param program_options: Space delimited string of optional mpirun options and arguments that can be freely
        modified by the user
    :param subcommand: The Truchas absolute or relative path
    :param subcommand_required: Space delimited string of required Truchas options and arguments
        that are crucial to builder behavior and should not be modified except by advanced users.
    :param subcommand_options: Space delimited string of optional Truchas options and arguments
        that can be freely modified by the user
    :param action_suffix: This variable is intended to perform program STDOUT and STDERR redirection operations.
    :param emitter: An SCons emitter function. This is not a keyword argument in the action string.
    :param kwargs: Any additional keyword arguments are passed directly to the SCons builder object.

    :returns: Truchas builder
    """  # noqa: E501
    builder = first_target_builder_factory(
        environment=environment,
        action_prefix=action_prefix,
        program=program,
        program_required=program_required,
        program_options=program_options,
        subcommand=subcommand,
        subcommand_required=subcommand_required,
        subcommand_options=subcommand_options,
        action_suffix=action_suffix,
        emitter=emitter,
        **kwargs,
    )
    return builder


def parameter_study_task(
    env: SCons.Environment.Environment,
    builder: SCons.Builder.Builder,
    *args,
    study=None,
    subdirectories: bool = False,
    **kwargs,
) -> SCons.Node.NodeList:
    """Parameter study pseudo-builder.

    `SCons Pseudo-Builder`_ aids in task construction for WAVES parameter studies with any SCons builder. Works with
    WAVES parameter generators or parameter dictionaries to reduce parameter study task definition boilerplate and
    make nominal workflow definitions directly re-usable in parameter studies.

    * If the study is a WAVES parameter generator object, loop over the parameter sets and replace ``@{set_name}`` in
      any ``*args`` and ``**kwargs`` that are strings, paths, or lists of strings and paths.
    * If the study is a ``dict()``, unpack the dictionary as keyword arguments directly into the builder.
    * In all other cases, the task is passed through unchanged to the builder and the study variable is ignored.

    When chaining parameter study tasks, arguments belonging to the parameter study can be prefixed by the template
    ``@{set_name}source.ext``. If the task uses a parameter study, the set name prefix will be replaced to match
    the task path modifications, e.g.  ``parameter_set0_source.ext`` or ``parameter_set0/source.ext`` depending on the
    ``subdirectories`` boolean. If the task is not part of a parameter study, the set name will be removed from the
    source, e.g. ``source.ext``. The ``@`` symbol is used as the delimiter to reduce with clashes in shell variable
    syntax and SCons substitution syntax.

    When pseudo-builders are added to the environment with the `SCons AddMethod`_ function they can be accessed with the
    same syntax as a normal builder. When called from the construction environment, the ``env`` argument is omitted.

    This pseudo-builder is most powerful when used in an SConscript call to a separate workflow configuration file. The
    SConscript file can then be called with a nominal parameter dictionary or with a parameter generator object. See the
    example below.

    .. code-block::
       :caption: SConstruct

       import pathlib
       import waves

       env = Environment()
       env.Append(BUILDERS={
           "AbaqusJournal": waves.scons_extensions.abaqus_journal(),
           "AbaqusSolver": waves.scons_extensions.abaqus_solver()
       })
       env.AddMethod(waves.scons_extensions.parameter_study_task, "ParameterStudyTask")

       parameter_study_file = pathlib.Path("parameter_study.h5")
       parameter_generator = waves.parameter_generators.CartesianProduct(
           {"parameter_one": [1, 2, 3]},
           output_file=parameter_study_file,
           previous_parameter_study=parameter_study_file
       )

       studies = (
           ("SConscript", parameter_generator),
           ("SConscript", {"parameter_one": 1})
       )
       for workflow, study in studies:
           SConscript(workflow, exports={"env": env, "study": study})

    .. code-block::
       :caption: SConscript

       Import("env", "study")

       env.ParameterStudyTask(
           env.AbaqusJournal,
           target=["@{set_name}job.inp"],
           source=["journal.py"],
           journal_options="--input=${SOURCE.abspath} --output=${TARGET.abspath} --option ${parameter_one}"
           study=study,
           subdirectories=True,
       )

       env.ParameterStudyTask(
           env.AbaqusSolver,
           target=["@{set_name}job.odb"],
           source=["@{set_name}job.inp"],
           job="job",
           study=study,
           subdirectories=True,
       )

    :param env: An SCons construction environment to use when defining the targets.
    :param builder: The builder to parameterize
    :param args: All other positional arguments are passed through to the builder after ``@{set_name}`` string
        substitutions
    :param study: Parameter generator or dictionary parameter set to provide to the builder. Parameter generators are
        unpacked with set name directory prefixes. Dictionaries are unpacked as keyword arguments.
    :param subdirectories: Switch to use parameter generator ``study`` set names as subdirectories. Ignored when
        ``study`` is not a parameter generator.
    :param kwargs: all other keyword arguments are passed through to the builder after ``@{set_name}`` string
        substitutions

    :return: SCons NodeList of target nodes
    """  # noqa: E501
    # Avoid importing parameter generator module (heavy) unless necessary
    from waves import parameter_generators

    if subdirectories:
        suffix = "/"
    else:
        suffix = "_"

    return_targets = list()
    if isinstance(study, parameter_generators.ParameterGenerator):
        for set_name, parameters in study.parameter_study_to_dict().items():
            modified_args = (
                _utilities.set_name_substitution(positional, set_name, suffix=suffix) for positional in args
            )
            modified_kwargs = {
                key: _utilities.set_name_substitution(value, set_name, suffix=suffix) for key, value in kwargs.items()
            }
            return_targets.extend(builder(*modified_args, **modified_kwargs, **parameters))
    # Is it better to accept a dictionary of nominal variables or to add a "Nominal" parameter generator?
    elif isinstance(study, dict):
        modified_args = (_utilities.set_name_substitution(positional, "", suffix="") for positional in args)
        modified_kwargs = {key: _utilities.set_name_substitution(value, "", suffix="") for key, value in kwargs.items()}
        return_targets.extend(builder(*modified_args, **modified_kwargs, **study))
    else:
        modified_args = (_utilities.set_name_substitution(positional, "", suffix="") for positional in args)
        modified_kwargs = {key: _utilities.set_name_substitution(value, "", suffix="") for key, value in kwargs.items()}
        return_targets.extend(builder(*modified_args, **modified_kwargs))
    return return_targets


def parameter_study_sconscript(
    env: SCons.Environment.Environment,
    *args,
    variant_dir=None,
    exports: typing.Optional[dict] = None,
    study=None,
    set_name: str = "",
    subdirectories: bool = False,
    **kwargs,
):
    """Wrap the SCons SConscript call to unpack parameter generators

    Always overrides the ``exports`` dictionary with ``set_name`` and ``parameters`` keys. When ``study`` is a
    dictionary or parameter generator, the ``parameters`` are overridden. When ``study`` is a parameter generator, the
    ``set_name`` is overridden.

    * If the study is a WAVES parameter generator object, call SConscript once per ``set_name`` and ``parameters`` in
      the generator's parameter study dictionary.
    * If the study is a ``dict``, call SConscript with the study as ``parameters`` and use the ``set_name`` from the
      method API.
    * In all other cases, the SConscript call is given the ``set_name`` from the method API and an empty ``parameters``
      dictionary.


    .. code-block::
       :caption: SConstruct

       import pathlib
       import waves

       env = Environment()
       env.Append(BUILDERS={
           "AbaqusJournal": waves.scons_extensions.abaqus_journal(),
           "AbaqusSolver": waves.scons_extensions.abaqus_solver()
       })
       env.AddMethod(waves.scons_extensions.parameter_study_sconscript, "ParameterStudySConscript")

       parameter_study_file = pathlib.Path("parameter_study.h5")
       parameter_generator = waves.parameter_generators.CartesianProduct(
           {"parameter_one": [1, 2, 3]},
           output_file=parameter_study_file,
           previous_parameter_study=parameter_study_file
       )

       studies = (
           ("SConscript", parameter_generator),
           ("SConscript", {"parameter_one": 1})
       )
       for workflow, study in studies:
           env.ParameterStudySConscript(workflow, variant_dir="build", study=study, subdirectories=True)

    .. code-block::
       :caption: SConscript

       Import("env", "set_name", "parameters")

       env.AbaqusJournal(
           target=["job.inp"],
           source=["journal.py"],
           journal_options="--input=${SOURCE.abspath} --output=${TARGET.abspath} --option ${parameter_one}"
           **parameters
       )

       env.AbaqusSolver(
           target=["job.odb"],
           source=["job.inp"],
           job="job",
           **parameters
       )

    :param env: SCons construction environment. Do not provide when using this function as a construction environment
        method, e.g. ``env.ParameterStudySConscript``.
    :param args: All positional arguments are passed through to the SConscript call directly
    :param variant_dir: The SConscript API variant directory argument
    :param exports: Dictionary of ``{key: value}`` pairs for the ``exports`` variables. *Must* use the dictionary style
        because the calling script's namespace is not available to the function namespace.
    :param study: Parameter generator or dictionary simulation parameters
    :param set_name: Set name to use when not provided a ``study``. Overridden by the ``study`` set names when ``study``
        is a parameter generator.
    :param kwargs: All other keyword arguments are passed through to the SConscript call directly
    :param subdirectories: Switch to use parameter generator ``study`` set names as subdirectories. Ignored when
        ``study`` is not a parameter generator.

    :returns: SConscript ``Export()`` variables. When called with a parameter generator study, the ``Export()``
        variables are returned as a list with one entry per parameter set.

    :raises TypeError: if ``exports`` is not a dictionary
    """
    if exports is None:
        exports = dict()

    # Avoid importing parameter generator module (heavy) unless necessary
    from waves import parameter_generators

    if not isinstance(exports, dict):
        import warnings

        message = (
            f"``exports`` keyword argument {exports} *must* be a dictionary of '{{key: value}}' pairs because "
            "this function does not have access to the calling script's namespace."
        )
        raise TypeError(message)
    exports.update({"set_name": set_name, "parameters": dict()})

    sconscript_output = list()

    if variant_dir is not None:
        variant_dir = pathlib.Path(variant_dir)

    def _variant_subdirectory(
        variant_directory: typing.Optional[pathlib.Path],
        subdirectory: str,
        subdirectories: bool = subdirectories,
    ) -> typing.Union[pathlib.Path, None]:
        """Determine the variant subdirectory

        :param variant_directory: The requested root ``variant_dir``
        :param subdirectory: The requested subdirectory
        :param subdirectories: Boolean to request subdirectory creation

        :returns: variant directory
        """
        if subdirectories:
            if variant_dir is not None:
                build_directory = variant_dir / subdirectory
            else:
                build_directory = pathlib.Path(subdirectory)
        else:
            build_directory = variant_dir
        return build_directory

    if isinstance(study, parameter_generators.ParameterGenerator):
        for set_name, parameters in study.parameter_study_to_dict().items():
            exports.update({"set_name": set_name, "parameters": parameters})
            build_directory = _variant_subdirectory(variant_dir, set_name)
            sconscript_output.append(env.SConscript(*args, variant_dir=build_directory, exports=exports, **kwargs))
    elif isinstance(study, dict):
        exports.update({"parameters": study})
        sconscript_output = env.SConscript(*args, variant_dir=variant_dir, exports=exports, **kwargs)
    else:
        sconscript_output = env.SConscript(*args, variant_dir=variant_dir, exports=exports, **kwargs)
    return sconscript_output


def parameter_study_write(
    env: SCons.Environment.Environment,
    parameter_generator,
    **kwargs,
) -> SCons.Node.NodeList:
    """Pseudo-builder to write a parameter generator's parameter study file

    .. code-block::
       :caption: SConstruct

       import pathlib
       import waves

       env = Environment()
       env.AddMethod(waves.scons_extensions.parameter_study_write, "ParameterStudyWrite")

       parameter_study_file = pathlib.Path("parameter_study.h5")
       parameter_generator = waves.parameter_generators.CartesianProduct(
           {"parameter_one": [1, 2, 3]},
           output_file=parameter_study_file,
           previous_parameter_study=parameter_study_file
       )

       env.ParameterStudyWrite(parameter_generator)

    :param parameter_generator: WAVES ParameterGenerator class
    :param kwargs: All other keyword arguments are passed directly to the
        :meth:`waves.parameter_generators.ParameterGenerator.write` method.

    :return: SCons NodeList of target nodes
    """
    import yaml

    # TODO: Refactor write/output file logic to avoid duplication here
    if parameter_generator.output_file is not None:
        output_files = [parameter_generator.output_file]
    else:
        output_files = list(parameter_generator.parameter_study[_settings._set_coordinate_key].values)

    targets = env.Command(
        target=output_files,
        source=[env.Value(yaml.dump(parameter_generator.parameter_study.to_dict()))],
        action=[SCons.Action.Action(parameter_generator._scons_write, varlist=["output_file_type"])],
        **kwargs,
    )

    return targets


class QOIPseudoBuilder:
    """SCons Pseudo-Builder class which allows users to customize the QOI Pseudo-Builder.

    .. warning::

       This pseudo-builder is considered experimental pending early adopter end user trial and feedback.

       The QOI xarray data array and dataset handling for expected/calculated comparisons should be stable, but the
       output plotting and reporting formatting is subject to change.

    :param collection_dir: Root directory of QOI archive artifacts.
    :param build_dir: Root directory of SCons project build artifacts.
    :param updated_expected: Update the expected QOI CSV source files to match the calculated QOI values instead of
        comparing the calculated and expected values.
    :param _program: The WAVES command line program call. Intended for internal use by developers to perform
        in-repository system testing. End users should not change the default value of this argument.
    """

    def __init__(
        self,
        collection_dir: pathlib.Path,
        build_dir: pathlib.Path,
        update_expected: bool = False,
        _program: str = "waves",
    ) -> None:
        self.collection_dir = collection_dir
        self.build_dir = build_dir
        self.update_expected = update_expected
        self._program = _program

    def __call__(
        self,
        env: SCons.Environment.Environment,
        calculated: pathlib.Path,
        expected: typing.Optional[pathlib.Path],
        archive: bool = False,
    ) -> SCons.Node.NodeList:
        """SCons Pseudo-Builder for regression testing and archiving quantities of interest (QOIs).

        This SCons Pseudo-Builder provides a convenient method for archiving and regression testing QOIs (such as
        critical simulation outputs). When requested, it aggregates the calculated values in a directory for easy
        archival. If expected values are specified, it compares them to the calculated values and reports any
        differences to a CSV file. If there are differences which exceed the user-specified tolerances, an error is
        raised. If ``self.update_expected`` is ``True``, the expected CSV files (in the source tree)
        will be updated to match the calculated QOI values, and no comparison between the two will be performed.

        :param calculated: Path to CSV file containing calculated QOIs. See :py:func:`qoi.read_qoi_set` for the CSV
            format.

        :param expected: Path to CSV file containing expected QOI values and tolerances. See :py:func:`qoi.read_qoi_set`
            for the CSV format. See :py:func:`qoi.create_qoi` for the types of tolerances allowed. See :ref:`qoi_cli`
            for how tolerances are checked.

            Each of the tolerances are checked independently. If any fail, an error is raised.

            If ``expected`` is not specified, then QOIs are archived but not compared to expected values. Either
            ``expected`` or ``archive=True`` must be specified. An expected QOI file without tolerances is meaningless;
            the regression test will always pass.

        :param archive: If True, add the calculated QOIs to ``self.collection_dir`` alongside other archived QOIs. To
            complete the archive, the QOI files collected in ``self.collection_dir`` should be copied to a read-only
            central location using ``waves qoi archive``

        :returns: list of SCons Target.
            The list of targets associated with regression testing and archiving the QOIs. Building these targets will
            regression test the QOIs and output a CSV file which contains the exact differences between calculated and
            expected values. If ``archive == True``, these targets will also include moving the calculated QOIs CSV file
            to the collection directory.
        """
        if not expected and not archive:
            return ValueError("Either expected or archive=True must be specified.")
        targets = list()
        collection_dir = pathlib.Path(self.collection_dir)
        file_to_archive = calculated
        if expected and self.update_expected:
            # If requested, update expected values with calculated values
            # This overwrites the expected values in the source tree. Don't tell SCons we're modifying the source
            # because that would create a dependency cycle. After this operation, the user needs to manually stage and
            # commit these changes to the expected values.
            # The action signature contains an absolute path (which interferes with caching), but this is not something
            # that should ever be cached.
            # Get expected CSV file in source directory
            expected_source = env.File(expected).srcnode().abspath
            accept_qoi_target = env.Command(
                target=[f"{expected}.stdout"],
                source=[calculated, expected],
                action=(
                    f"{self._program} qoi accept"
                    + f" --calculated {calculated}"  # noqa: W503
                    + f" --expected {expected_source}"  # noqa: W503
                    + " > ${TARGETS[-1].abspath} 2>&1"  # noqa: W503
                ),
            )
            # Because SCons doesn't know the real target (the expected CSV file in the source tree), it can't know if
            # the target is out of date, so use AlwaysBuild().
            env.AlwaysBuild(accept_qoi_target)
            targets.extend(accept_qoi_target)

        # Only perform the comparison if not updating expected values to match the calculated values
        elif expected:
            name = pathlib.Path(calculated).stem
            diff = pathlib.Path(calculated).parent / f"{name}_diff.csv"
            file_to_archive = diff
            # Do the comparison and write results to file
            comparison_target = env.Command(
                target=[diff],
                source=[calculated, expected],
                action=f"{self._program} qoi diff --expected {expected} --calculated {calculated} --output {diff}",
            )
            targets.extend(comparison_target)
            # Check the comparison results and raise error if not all QOIs are within tolerance
            check_target = env.Command(
                target=[f"{name}_check.stdout"],
                source=[diff],
                action=(f"{self._program} qoi check --diff {diff}" + " > ${TARGETS[-1].abspath} 2>&1"),
            )
            targets.extend(check_target)

        # Add to collection_dir if requested
        if archive:
            # Archive the QOI diff results if it's available, otherwise archive the calculated values
            # Keep directory hierarchy within build/qoi to avoid name conflicts
            archive_location = collection_dir / pathlib.Path(file_to_archive).resolve().relative_to(self.build_dir)
            targets.extend(
                env.Command(
                    target=archive_location,
                    source=file_to_archive,
                    action=SCons.Script.Copy("$TARGET", "$SOURCE"),
                )
            )
        return targets


class WAVESEnvironment(SConsEnvironment):
    """Thin overload of SConsEnvironment with WAVES construction environment methods and builders"""

    def __init__(
        self,
        *args,
        ABAQUS_PROGRAM: str = "abaqus",
        ANSYS_PROGRAM: str = "ansys",
        CCX_PROGRAM: str = "ccx",
        CHARMRUN_PROGRAM: str = "charmrun",
        FIERRO_EXPLICIT_PROGRAM: str = "fierro-parallel-explicit",
        FIERRO_IMPLICIT_PROGRAM: str = "fierro-parallel-implicit",
        INCITER_PROGRAM: str = "inciter",
        MPIRUN_PROGRAM: str = "mpirun",
        PYTHON_PROGRAM: str = "python",
        SIERRA_PROGRAM: str = "sierra",
        SPHINX_BUILD_PROGRAM: str = "sphinx-build",
        **kwargs,
    ):
        super().__init__(
            *args,
            ABAQUS_PROGRAM=ABAQUS_PROGRAM,
            ANSYS_PROGRAM=ANSYS_PROGRAM,
            CCX_PROGRAM=CCX_PROGRAM,
            CHARMRUN_PROGRAM=CHARMRUN_PROGRAM,
            FIERRO_EXPLICIT_PROGRAM=FIERRO_EXPLICIT_PROGRAM,
            FIERRO_IMPLICIT_PROGRAM=FIERRO_IMPLICIT_PROGRAM,
            INCITER_PROGRAM=INCITER_PROGRAM,
            MPIRUN_PROGRAM=MPIRUN_PROGRAM,
            PYTHON_PROGRAM=PYTHON_PROGRAM,
            SIERRA_PROGRAM=SIERRA_PROGRAM,
            SPHINX_BUILD_PROGRAM=SPHINX_BUILD_PROGRAM,
            **kwargs,
        )

    def PrintBuildFailures(self, *args, **kwargs):
        """Construction environment method from :meth:`waves.scons_extensions.print_build_failures`

        When using this environment method, do not provide the first ``env`` argument
        """
        return print_build_failures(self, *args, **kwargs)

    def CheckProgram(self, *args, **kwargs):
        """Construction environment method from :meth:`waves.scons_extensions.check_program`

        When using this environment method, do not provide the first ``env`` argument
        """
        return check_program(self, *args, **kwargs)

    def FindProgram(self, *args, **kwargs):
        """Construction environment method from :meth:`waves.scons_extensions.find_program`

        When using this environment method, do not provide the first ``env`` argument
        """
        return find_program(self, *args, **kwargs)

    def AddProgram(self, *args, **kwargs):
        """Construction environment method from :meth:`waves.scons_extensions.add_program`

        When using this environment method, do not provide the first ``env`` argument
        """
        return add_program(self, *args, **kwargs)

    def AddCubit(self, *args, **kwargs):
        """Construction environment method from :meth:`waves.scons_extensions.add_cubit`

        When using this environment method, do not provide the first ``env`` argument
        """
        return add_cubit(self, *args, **kwargs)

    def AddCubitPython(self, *args, **kwargs):
        """Construction environment method from :meth:`waves.scons_extensions.add_cubit_python`

        When using this environment method, do not provide the first ``env`` argument
        """
        return add_cubit_python(self, *args, **kwargs)

    def CopySubstfile(self, *args, **kwargs):
        """Construction environment method from :meth:`waves.scons_extensions.copy_substfile`

        When using this environment method, do not provide the first ``env`` argument
        """
        return copy_substfile(self, *args, **kwargs)

    def ProjectHelp(self, *args, **kwargs):
        """Construction environment method from :meth:`waves.scons_extensions.project_help`

        When using this environment method, do not provide the first ``env`` argument
        """
        return project_help(self, *args, **kwargs)

    def ProjectAlias(self, *args, **kwargs):
        """Construction environment method from :meth:`waves.scons_extensions.project_alias`

        When using this environment method, do not provide the first ``env`` argument
        """
        return project_alias(self, *args, **kwargs)

    def SubstitutionSyntax(self, *args, **kwargs):
        """Construction environment method from :meth:`waves.scons_extensions.substitution_syntax`

        When using this environment method, do not provide the first ``env`` argument
        """
        return substitution_syntax(self, *args, **kwargs)

    def ParameterStudyTask(self, *args, **kwargs):
        """Construction environment pseudo-builder from :meth:`waves.scons_extensions.parameter_study_task`

        When using this environment pseudo-builder, do not provide the first ``env`` argument
        """
        return parameter_study_task(self, *args, **kwargs)

    def ParameterStudySConscript(self, *args, **kwargs):
        """Construction environment method from :meth:`waves.scons_extensions.parameter_study_sconscript`

        When using this environment method, do not provide the first ``env`` argument
        """
        return parameter_study_sconscript(self, *args, **kwargs)

    def ParameterStudyWrite(self, *args, **kwargs):
        """Construction environment method from :meth:`waves.scons_extensions.parameter_study_write`

        When using this environment method, do not provide the first ``env`` argument
        """
        return parameter_study_write(self, *args, **kwargs)

    def FirstTargetBuilder(self, target, source, *args, **kwargs):
        """Builder from factory :meth:`waves.scons_extensions.first_target_builder_factory`

        :param target: The task target list
        :param source: The task source list
        :param args: All positional arguments are passed through to the builder (*not* to the builder factory)
        :param kwargs: All keyword arguments are passed through to the builder (*not* to the builder factory)
        """
        builder = first_target_builder_factory()
        return builder(self, *args, target=target, source=source, **kwargs)

    def AbaqusJournal(self, target, source, *args, **kwargs):
        """Builder from factory :meth:`waves.scons_extensions.abaqus_journal_builder_factory`

        :var program: ``${ABAQUS_PROGRAM}``

        :param target: The task target list
        :param source: The task source list
        :param args: All positional arguments are passed through to the builder (*not* to the builder factory)
        :param kwargs: All keyword arguments are passed through to the builder (*not* to the builder factory)
        """
        builder = abaqus_journal_builder_factory(program="${ABAQUS_PROGRAM}")
        return builder(self, *args, target=target, source=source, **kwargs)

    def AbaqusSolver(self, target, source, *args, **kwargs):
        """Builder from factory :meth:`waves.scons_extensions.abaqus_solver_builder_factory`

        :var program: ``${ABAQUS_PROGRAM}``

        :param target: The task target list
        :param source: The task source list
        :param args: All positional arguments are passed through to the builder (*not* to the builder factory)
        :param kwargs: All keyword arguments are passed through to the builder (*not* to the builder factory)
        """
        builder = abaqus_solver_builder_factory(program="${ABAQUS_PROGRAM}")
        return builder(self, *args, target=target, source=source, **kwargs)

    def AbaqusDatacheck(self, target, source, *args, **kwargs):
        """Builder from factory :meth:`waves.scons_extensions.abaqus_solver_builder_factory` using the
        :meth:`waves.scons_extensions.abaqus_datacheck_emitter`.

        :var program: ``${ABAQUS_PROGRAM}``
        :var emitter: :meth:`waves.scons_extensions.abaqus_datacheck_emitter`

        :param target: The task target list
        :param source: The task source list
        :param args: All positional arguments are passed through to the builder (*not* to the builder factory)
        :param kwargs: All keyword arguments are passed through to the builder (*not* to the builder factory)
        """
        builder = abaqus_solver_builder_factory(
            program="${ABAQUS_PROGRAM}",
            emitter=abaqus_datacheck_emitter,
        )
        return builder(self, *args, target=target, source=source, **kwargs)

    def AbaqusExplicit(self, target, source, *args, **kwargs):
        """Builder from factory :meth:`waves.scons_extensions.abaqus_solver_builder_factory` using the
        :meth:`waves.scons_extensions.abaqus_explicit_emitter`.

        :var program: ``${ABAQUS_PROGRAM}``
        :var emitter: :meth:`waves.scons_extensions.abaqus_explicit_emitter`

        :param target: The task target list
        :param source: The task source list
        :param args: All positional arguments are passed through to the builder (*not* to the builder factory)
        :param kwargs: All keyword arguments are passed through to the builder (*not* to the builder factory)
        """
        builder = abaqus_solver_builder_factory(
            program="${ABAQUS_PROGRAM}",
            emitter=abaqus_explicit_emitter,
        )
        return builder(self, *args, target=target, source=source, **kwargs)

    def AbaqusStandard(self, target, source, *args, **kwargs):
        """Builder from factory :meth:`waves.scons_extensions.abaqus_solver_builder_factory` using the
        :meth:`waves.scons_extensions.abaqus_standard_emitter`.

        :var program: ``${ABAQUS_PROGRAM}``
        :var emitter: :meth:`waves.scons_extensions.abaqus_standard_emitter`

        :param target: The task target list
        :param source: The task source list
        :param args: All positional arguments are passed through to the builder (*not* to the builder factory)
        :param kwargs: All keyword arguments are passed through to the builder (*not* to the builder factory)
        """
        builder = abaqus_solver_builder_factory(
            program="${ABAQUS_PROGRAM}",
            emitter=abaqus_standard_emitter,
        )
        return builder(self, *args, target=target, source=source, **kwargs)

    def AbaqusPseudoBuilder(self, job, *args, override_cpus: typing.Optional[int] = None, **kwargs):
        """Construction environment pseudo-builder from :class:`waves.scons_extensions.AbaqusPseudoBuilder`

        When using this environment pseudo-builder, do not provide the first ``env`` argument

        :param job: Abaqus job name.
        :param override_cpus: Override the task-specific default number of CPUs. This kwarg value is most useful if
            propagated from a user-specified option at execution time. If None, Abaqus Pseudo-Builder tasks will use the
            task-specific default.
        :param args: All other positional arguments are passed through to
            :meth:`waves.scons_extensions.AbaqusPseudoBuilder.__call__``
        :param kwargs: All other keyword arguments are passed through to
            :meth:`waves.scons_extensions.AbaqusPseudoBuilder.__call__``
        """
        pseudo_builder = AbaqusPseudoBuilder(builder=self.AbaqusSolver, override_cpus=override_cpus)
        return pseudo_builder(self, job, *args, **kwargs)

    def PythonScript(self, target, source, *args, **kwargs):
        """Builder from factory :meth:`waves.scons_extensions.python_builder_factory`

        :var program: ``${PYTHON_PROGRAM}``

        :param target: The task target list
        :param source: The task source list
        :param args: All positional arguments are passed through to the builder (*not* to the builder factory)
        :param kwargs: All keyword arguments are passed through to the builder (*not* to the builder factory)
        """
        builder = python_builder_factory(program="${PYTHON_PROGRAM}")
        return builder(self, *args, target=target, source=source, **kwargs)

    def QuinoaSolver(self, target, source, *args, **kwargs):
        """Builder from factory :meth:`waves.scons_extensions.quinoa_builder_factory`

        :var program: ``${CHARMRUN_PROGRAM}``
        :var subcommand: ``${INCITER_PROGRAM}``

        :param target: The task target list
        :param source: The task source list
        :param args: All positional arguments are passed through to the builder (*not* to the builder factory)
        :param kwargs: All keyword arguments are passed through to the builder (*not* to the builder factory)
        """
        builder = quinoa_builder_factory(program="${CHARMRUN_PROGRAM}", subcommand="${INCITER_PROGRAM}")
        return builder(self, *args, target=target, source=source, **kwargs)

    def CalculiX(self, target, source, *args, **kwargs):
        """Builder from factory :meth:`waves.scons_extensions.calculix_builder_factory`

        :var program: ``${CCX_PROGRAM}``

        :param target: The task target list
        :param source: The task source list
        :param args: All positional arguments are passed through to the builder (*not* to the builder factory)
        :param kwargs: All keyword arguments are passed through to the builder (*not* to the builder factory)
        """
        builder = calculix_builder_factory(program="${CCX_PROGRAM}")
        return builder(self, *args, target=target, source=source, **kwargs)

    def FierroExplicit(self, target, source, *args, **kwargs):
        """Builder from factory :meth:`waves.scons_extensions.fierro_explicit_builder_factory`

        :var program: ``${MPIRUN_PROGRAM}``
        :var subcommand: ``${FIERRO_EXPLICIT_PROGRAM}``

        :param target: The task target list
        :param source: The task source list
        :param args: All positional arguments are passed through to the builder (*not* to the builder factory)
        :param kwargs: All keyword arguments are passed through to the builder (*not* to the builder factory)
        """
        builder = fierro_explicit_builder_factory(program="${MPIRUN_PROGRAM}", subcommand="${FIERRO_EXPLICIT_PROGRAM}")
        return builder(self, *args, target=target, source=source, **kwargs)

    def FierroImplicit(self, target, source, *args, **kwargs):
        """Builder from factory :meth:`waves.scons_extensions.fierro_implicit_builder_factory`

        :var program: ``${MPIRUN_PROGRAM}``
        :var subcommand: ``${FIERRO_IMPLICIT_PROGRAM}``

        :param target: The task target list
        :param source: The task source list
        :param args: All positional arguments are passed through to the builder (*not* to the builder factory)
        :param kwargs: All keyword arguments are passed through to the builder (*not* to the builder factory)
        """
        builder = fierro_implicit_builder_factory(program="${MPIRUN_PROGRAM}", subcommand="${FIERRO_IMPLICIT_PROGRAM}")
        return builder(self, *args, target=target, source=source, **kwargs)

    def Sierra(self, target, source, *args, **kwargs):
        """Builder from factory :meth:`waves.scons_extensions.sierra_builder_factory`

        :var program: ``${SIERRA_PROGRAM}``

        :param target: The task target list
        :param source: The task source list
        :param args: All positional arguments are passed through to the builder (*not* to the builder factory)
        :param kwargs: All keyword arguments are passed through to the builder (*not* to the builder factory)
        """
        builder = sierra_builder_factory(program="${SIERRA_PROGRAM}")
        return builder(self, *args, target=target, source=source, **kwargs)

    def AnsysAPDL(self, target, source, *args, **kwargs):
        """Builder from factory :meth:`waves.scons_extensions.ansys_apdl_builder_factory`

        :var program: ``${ANSYS_PROGRAM}``

        :param target: The task target list
        :param source: The task source list
        :param args: All positional arguments are passed through to the builder (*not* to the builder factory)
        :param kwargs: All keyword arguments are passed through to the builder (*not* to the builder factory)
        """
        builder = ansys_apdl_builder_factory(program="${ANSYS_PROGRAM}")
        return builder(self, *args, target=target, source=source, **kwargs)

    def Truchas(self, target, source, *args, **kwargs):
        """Builder from factory :meth:`waves.scons_extensions.truchas_builder_factory`

        :var program: ``${MPIRUN_PROGRAM}``
        :var subcommand: ``${TRUCHAS_PROGRAM}``

        :param target: The task target list
        :param source: The task source list
        :param args: All positional arguments are passed through to the builder (*not* to the builder factory)
        :param kwargs: All keyword arguments are passed through to the builder (*not* to the builder factory)
        """
        builder = truchas_builder_factory(program="${MPIRUN_PROGRAM}", subcommand="${TRUCHAS_PROGRAM}")
        return builder(self, *args, target=target, source=source, **kwargs)

    def SphinxBuild(self, target, source, *args, **kwargs):
        """Builder from factory :meth:`waves.scons_extensions.sphinx_build`

        :var program: ``${SPHINX_BUILD_PROGRAM}``

        :param target: The task target list
        :param source: The task source list
        :param args: All positional arguments are passed through to the builder (*not* to the builder factory)
        :param kwargs: All keyword arguments are passed through to the builder (*not* to the builder factory)
        """
        builder = sphinx_build(program="${SPHINX_BUILD_PROGRAM}")
        return builder(self, *args, target=target, source=source, **kwargs)

    def SphinxPDF(self, target, source, *args, **kwargs):
        """Builder from factory :meth:`waves.scons_extensions.sphinx_latexpdf`

        :var program: ``${SPHINX_BUILD_PROGRAM}``

        :param target: The task target list
        :param source: The task source list
        :param args: All positional arguments are passed through to the builder (*not* to the builder factory)
        :param kwargs: All keyword arguments are passed through to the builder (*not* to the builder factory)
        """
        builder = sphinx_latexpdf(program="${SPHINX_BUILD_PROGRAM}")
        return builder(self, *args, target=target, source=source, **kwargs)


_module_objects = set(globals().keys()) - _exclude_from_namespace
__all__ = [name for name in _module_objects if not name.startswith("_")]
