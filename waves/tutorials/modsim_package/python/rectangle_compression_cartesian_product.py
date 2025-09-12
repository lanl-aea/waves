"""Parameter sets and schemas for the rectangle compression simulation"""


def parameter_schema(
    width: list[float] | tuple[float, ...] = (1.0, 1.1),
    height: list[float] | tuple[float, ...] = (1.0, 1.1),
    global_seed: list[float] | tuple[float, ...] = (1.0,),
    displacement: list[float] | tuple[float, ...] = (-0.01,),
) -> dict[str, list[float]]:
    """Return WAVES CartesianProduct parameter schema

    :param list width: The rectangle width
    :param list height: The rectangle height
    :param list global_seed: The global mesh seed size
    :param list displacement: The rectangle top surface displacement

    :returns: WAVES CartesianProduct parameter schema
    :rtype: dict
    """
    schema = {
        "width": list(width),
        "height": list(height),
        "global_seed": list(global_seed),
        "displacement": list(displacement),
    }
    return schema
