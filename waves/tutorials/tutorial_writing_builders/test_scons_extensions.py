import waves
import pytest
import SCons.Environment

import scons_extensions


def dummy_emitter_for_testing(target, source, env):
    return target, source


solver_builder_factory_tests = {
    "default behavior": ({}, {}, ["solver_builder_factory.out0"], False, 2, 1),
    "different emitter": ({}, {}, ["solver_builder_factory.out1"], dummy_emitter_for_testing, 1, 1),
    "builder kwargs overrides": (
        {
            "environment": "different environment",
            "action_prefix": "different action prefix",
            "program": "different program",
            "program_required": "different program required",
            "program_options": "different program options",
            "subcommand": "different subcommand",
            "subcommand_required": "different subcommand required",
            "subcommand_options": "different subcommand options",
            "action_suffix": "different action suffix",
        },
        {},
        ["solver_builder_factory.out2"],
        False,
        2,
        1,
    ),
    "task kwargs overrides": (
        {},
        {
            "environment": "different environment",
            "action_prefix": "different action prefix",
            "program": "different program",
            "program_required": "different program required",
            "program_options": "different program options",
            "subcommand": "different subcommand",
            "subcommand_required": "different subcommand required",
            "subcommand_options": "different subcommand options",
            "action_suffix": "different action suffix",
        },
        ["solver_builder_factory.out3"],
        False,
        2,
        1,
    ),
}


# TODO: Expose WAVES builder factory test functions for end users
@pytest.mark.parametrize(
    "builder_kwargs, task_kwargs, target, emitter, expected_node_count, expected_action_count",
    solver_builder_factory_tests.values(),
    ids=solver_builder_factory_tests.keys(),
)
def test_solver_builder_factory(
    builder_kwargs: dict,
    task_kwargs: dict,
    target: list,
    emitter,
    expected_node_count: int,
    expected_action_count: int,
) -> None:
    """Template test for builder factories based on :meth:`waves.scons_extensions.builder_factory`

    :param builder_kwargs: Keyword arguments unpacked at the builder instantiation
    :param task_kwargs: Keyword arguments unpacked at the task instantiation
    :param target: Explicit list of targets provided at the task instantiation
    :param emitter: A custom factory emitter. Mostly intended as a pass-through check. Set to ``False`` to avoid
        providing an emitter argument to the builder factory.
    :param expected_node_count: The expected number of target nodes.
    :param expected_action_count: The expected number of target node actions.
    """
    # Set default expectations to match default argument values
    expected_kwargs = {
        "environment": "",
        "action_prefix": "cd ${TARGET.dir.abspath} &&",
        "program": "solver.py",
        "program_required": "",
        "program_options": "",
        "subcommand": "implicit",
        "subcommand_required": "--input-file ${SOURCES[0].abspath} --output-file=${TARGETS[0].abspath} --overwrite",
        "subcommand_options": "",
        "action_suffix": "> ${TARGETS[-1].abspath} 2>&1",
    }

    # Update expected arguments to match test case
    expected_kwargs.update(builder_kwargs)
    expected_kwargs.update(task_kwargs)
    # Expected action matches the pre-SCons-substitution string with newline delimiter
    expected_action = (
        "${environment} ${action_prefix} ${program} ${program_required} ${program_options} "
        "${subcommand} ${subcommand_required} ${subcommand_options} ${action_suffix}"
    )

    # Handle additional builder kwargs without changing default behavior
    expected_emitter = waves.scons_extensions.first_target_emitter
    emitter_handling = {}
    if emitter is not False:
        expected_emitter = emitter
        emitter_handling.update({"emitter": emitter})

    # Test builder object attributes
    factory = getattr(scons_extensions, "solver_builder_factory")
    builder = factory(**builder_kwargs, **emitter_handling)
    assert builder.action.cmd_list == expected_action
    assert builder.emitter == expected_emitter

    # Assemble the builder and a task to interrogate
    env = SCons.Environment.Environment()
    env.Append(BUILDERS={"Builder": builder})
    nodes = env.Builder(
        target=target,
        source=["check_builder_factory.in"],
        **task_kwargs,
    )

    # Test task definition node counts, action(s), and task keyword arguments
    assert len(nodes) == expected_node_count
    for node in nodes:
        node.get_executor()
        assert len(node.executor.action_list) == expected_action_count
        assert str(node.executor.action_list[0]) == expected_action
    for node in nodes:
        for key, expected_value in expected_kwargs.items():
            assert node.env[key] == expected_value
