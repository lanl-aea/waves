"""Parameter sets and schemas for the rectangle compression simulation"""


def parameter_schema(
    width=[1.0, 1.1],
    height=[1.0, 1.1],
    global_seed=[1.0],
    displacement=[-0.01],
):
    """Return WAVES CartesianProduct parameter schema

    :param list width: The rectangle width
    :param list height: The rectangle height
    :param list global_seed: The global mesh seed size
    :param list displacement: The rectangle top surface displacement

    :returns: WAVES CartesianProduct parameter schema
    :rtype: dict
    """
    schema = {
        "width": width,
        "height": height,
        "global_seed": global_seed,
        "displacement": displacement,
    }
    return schema
