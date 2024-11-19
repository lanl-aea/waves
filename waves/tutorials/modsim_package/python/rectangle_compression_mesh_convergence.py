"""Parameter sets and schemas for the rectangle compression simulation"""


def parameter_schema(
    global_seed=[1.0, 0.5, 0.25, 0.125],
):
    """Return mesh convergence WAVES CartesianProduct parameter schema

    :param float global_seed: The global mesh seed size

    :returns: WAVES CartesianProduct parameter schema
    :rtype: dict
    """
    schema = {
        "global_seed": global_seed,
    }
    return schema
