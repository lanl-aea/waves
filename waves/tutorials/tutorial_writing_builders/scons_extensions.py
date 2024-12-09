import waves
import SCons.Builder


# Write an example custom builder using the WAVES builder factory template
def solver_builder_factory(
    environment: str = "",
    action_prefix: str = "cd ${TARGET.dir.abspath} &&",
    program: str = "solver.py",
    program_required: str = "",
    program_options: str = "",
    subcommand: str = "implicit",
    subcommand_required: str = "--input-file ${SOURCES[0].abspath} --output-file=${TARGETS[0].abspath} --overwrite",
    subcommand_options: str = "",
    action_suffix: str = "> ${TARGETS[-1].abspath} 2>&1",
    emitter=waves.scons_extensions.first_target_emitter,
    **kwargs,
) -> SCons.Builder.Builder:
    """
    This builder factory extends :meth:`waves.scons_extensions.first_target_builder_factory`. This builder factory uses
    the :meth:`waves.scons_extensions.first_target_emitter`. At least one task target must be specified in the task
    definition and the last target will always be the expected STDOUT and STDERR redirection output file,
    ``TARGETS[-1]`` ending in ``*.stdout``.

    .. warning::

       Users overriding the ``emitter`` keyword argument are responsible for providing an emitter with equivalent STDOUT
       file handling behavior as :meth:`waves.scons_extensions.first_target_emitter` or updating the ``action_suffix``
       option to match their emitter's behavior.

    With the default options this builder requires the following sources file provided in the order:

    1. solver program's routine subcommand input file: ``*.yaml``

    .. code-block::
       :caption: action string construction

       ${environment} ${action_prefix} ${program} ${program_required} ${program_options} ${subcommand} ${subcommand_required} ${subcommand_options} ${action_suffix}

    .. code-block::
       :caption: action string default expansion

       ${environment} cd ${TARGET.dir.abspath} && solver.py ${program_required} ${program_optional} implicit --input-file ${SOURCE.abspath} --output-file ${TARGETS[0].abspath} ${subcommand_options} > ${TARGETS[-1].abspath} 2>&1

    .. code-block::
       :caption: SConstruct

       import waves
       env = waves.scons_extensions.WAVESEnvironment()
       env.AddMethod(waves.scons_extensions.add_program, "AddProgram")
       env["solver"] = env.AddProgram(["solver"])
       env.Append(BUILDERS={"Solver": solver_explicit_builder_factory()})
       env.Solver(
           target=["target.out"],
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
    :param program: The solver program absolute or relative path
    :param program_required: Space delimited string of required solver program options and arguments that are crucial to
        builder behavior and should not be modified except by advanced users
    :param program_options: Space delimited string of optional solver program options and arguments that can be freely
        modified by the user
    :param subcommand: The solver program's routine subcommand absolute or relative path
    :param subcommand_required: Space delimited string of required solver program's routine subcommand options and
        arguments that are crucial to builder behavior and should not be modified except by advanced users.
    :param subcommand_options: Space delimited string of optional solver program's routine subcommand options and
        arguments that can be freely modified by the user
    :param action_suffix: This variable is intended to perform program STDOUT and STDERR redirection operations.
    :param emitter: An SCons emitter function. This is not a keyword argument in the action string.
    :param kwargs: Any additional keyword arguments are passed directly to the SCons builder object.

    :return: Solver journal builder
    """  # noqa: E501
    builder = waves.scons_extensions.first_target_builder_factory(
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
