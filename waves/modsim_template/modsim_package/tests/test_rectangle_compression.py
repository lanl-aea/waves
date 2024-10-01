import pytest

from modsim_package import rectangle_compression


nominal_tests = {
    "default": (
        {"width": 1.0, "height": 1.0, "global_seed": 1.0, "displacement": -0.01},
        {},
        {"width": 1.0, "height": 1.0, "global_seed": 1.0, "displacement": -0.01},
    ),
    "override all": (
        {"width": 1.0, "height": 1.0, "global_seed": 1.0, "displacement": -0.01},
        {"width": 2.0, "height": 3.0, "global_seed": 4.0, "displacement": -0.05},
        {"width": 2.0, "height": 3.0, "global_seed": 4.0, "displacement": -0.05},
    )
}


@pytest.mark.parametrize("default_kwargs, kwargs, expected",
                         nominal_tests.values(),
                         ids=nominal_tests.keys())
def test_nominal(default_kwargs, kwargs, expected):
    # Set default expectations to match default argument values
    expected_kwargs = default_kwargs
    # Update expected arguments to match test case
    expected_kwargs.update(kwargs)

    simulation_variables = rectangle_compression.nominal(**kwargs)
    assert simulation_variables == expected


mesh_convergence_tests = {
    "default": (
        {"width": [1.0], "height": [1.0], "global_seed": [1.0, 0.5, 0.25, 0.125], "displacement": [-0.01]},
        {},
        {"width": [1.0], "height": [1.0], "global_seed": [1.0, 0.5, 0.25, 0.125], "displacement": [-0.01]},
    ),
    "override all": (
        {"width": [1.0], "height": [1.0], "global_seed": [1.0, 0.5, 0.25, 0.125], "displacement": [-0.01]},
        {"width": [2.0], "height": [3.0], "global_seed": [4.0, 2.0], "displacement": [-0.05]},
        {"width": [2.0], "height": [3.0], "global_seed": [4.0, 2.0], "displacement": [-0.05]},
    )
}


@pytest.mark.parametrize("default_kwargs, kwargs, expected",
                         mesh_convergence_tests.values(),
                         ids=mesh_convergence_tests.keys())
def test_mesh_convergence(default_kwargs, kwargs, expected):
    # Set default expectations to match default argument values
    expected_kwargs = default_kwargs
    # Update expected arguments to match test case
    expected_kwargs.update(kwargs)

    simulation_variables = rectangle_compression.mesh_convergence(**kwargs)
    assert simulation_variables == expected
