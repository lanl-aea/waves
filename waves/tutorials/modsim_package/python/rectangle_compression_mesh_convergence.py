"""Parameter sets and schemas for the rectangle compression simulation."""


def parameter_schema(
    global_seed: list[float] | tuple[float, ...] = (1.0, 0.5, 0.25, 0.125),
) -> dict[str, list[float]]:
    """Return mesh convergence WAVES CartesianProduct parameter schema.

    :param global_seed: The global mesh seed size

    :returns: WAVES CartesianProduct parameter schema
    """
    schema = {
        "global_seed": list(global_seed),
    }
    return schema
