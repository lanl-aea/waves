"""Parameter sets and schemas for the rectangle compression simulation."""


def nominal(
    width: float = 1.0,
    height: float = 1.0,
    global_seed: float = 1.0,
    displacement: float = -0.01,
) -> dict[str, float]:
    """Return nominal simulation variables dictionary.

    :param width: The rectangle width
    :param height: The rectangle height
    :param global_seed: The global mesh seed size
    :param displacement: The rectangle top surface displacement

    :returns: nominal simulation variables
    """
    parameters = {
        "width": width,
        "height": height,
        "global_seed": global_seed,
        "displacement": displacement,
    }
    return parameters


def mesh_convergence(
    width: list[float] | tuple[float, ...] = (1.0,),
    height: list[float] | tuple[float, ...] = (1.0,),
    global_seed: list[float] | tuple[float, ...] = (1.0, 0.5, 0.25, 0.125),
    displacement: list[float] | tuple[float, ...] = (-0.01,),
) -> dict[str, list[float]]:
    """Return mesh convergence WAVES CartesianProduct schema dictionary.

    :param width: The rectangle width
    :param height: The rectangle height
    :param global_seed: The global mesh seed size
    :param displacement: The rectangle top surface displacement

    :returns: WAVES CartesianProduct schema
    """
    schema = {
        "width": list(width),
        "height": list(height),
        "global_seed": list(global_seed),
        "displacement": list(displacement),
    }
    return schema
