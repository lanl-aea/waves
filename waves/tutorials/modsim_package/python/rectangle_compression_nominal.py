"""Parameter sets and schemas for the rectangle compression simulation."""


def parameter_schema(
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
    simulation_variables = {
        "width": width,
        "height": height,
        "global_seed": global_seed,
        "displacement": displacement,
    }
    return simulation_variables
