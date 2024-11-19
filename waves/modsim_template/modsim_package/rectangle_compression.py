"""Parameter sets and schemas for the rectangle compression simulation"""


def nominal(
    width=1.0,
    height=1.0,
    global_seed=1.0,
    displacement=-0.01,
):
    """Return nominal simulation variables dictionary

    :param float width: The rectangle width
    :param float height: The rectangle height
    :param float global_seed: The global mesh seed size
    :param float displacement: The rectangle top surface displacement

    :returns: nominal simulation variables
    :rtype: dict
    """
    parameters = {
        "width": width,
        "height": height,
        "global_seed": global_seed,
        "displacement": displacement,
    }
    return parameters


def mesh_convergence(
    width=[1.0],
    height=[1.0],
    global_seed=[1.0, 0.5, 0.25, 0.125],
    displacement=[-0.01],
):
    """Return mesh convergence WAVES CartesianProduct schema dictionary

    :param float global_seed: The global mesh seed size

    :returns: WAVES CartesianProduct schema
    :rtype: dict
    """
    schema = {
        "width": width,
        "height": height,
        "global_seed": global_seed,
        "displacement": displacement,
    }
    return schema
