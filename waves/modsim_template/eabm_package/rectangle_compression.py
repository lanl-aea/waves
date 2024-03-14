"""Parameter sets and schemas for the rectangle compression simulation"""


def nominal(width=1.0, height=1.0, global_seed=1.0, displacement=-0.01):
    """Return nominal simulation variables dictionary

    :param float width: The rectangle width
    :param float height: The rectangle height
    :param float global_seed: The global mesh seed size
    :param float displacement: The rectangle top surface displacement

    :returns: nominal simulation variables
    :rtype: dict
    """
    simulation_variables = {
        'width': width,
        'height': height,
        'global_seed': global_seed,
        'displacement': displacement
    }
    return simulation_variables


def mesh_convergence(global_seed=[1.0, 0.5, 0.25, 0.125]):
    """Return mesh convergence WAVES CartesianProduct schema dictionary
    :param float global_seed: The global mesh seed size

    :returns: WAVES CartesianProduct schema
    :rtype: dict
    """
    schema = {
        'global_seed': global_seed,
    }
    return schema
