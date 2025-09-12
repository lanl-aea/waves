"""Parameter sets and schemas for the rectangle compression simulation"""


def parameter_schema(
    N: int = 5,  # noqa: N803
    width_distribution: str = "norm",
    width_bounds: list[float] | tuple[float, ...] = (1.0, 0.1),
    height_distribution: str = "norm",
    height_bounds: list[float] | tuple[float, ...] = (1.0, 0.1),
):
    """Return WAVES SALibSampler Sobol schema

    :param int N: Number of samples to generate
    :param str width_distribution: SALib distribution name
    :param list width_bounds: Distribution characteristics. Meaning varies depending on distribution type.
    :param str height_distribution: SALib distribution name
    :param list height_bounds: Distribution characteristics. Meaning varies depending on distribution type.

    :returns: WAVES SALibSampler Sobol schema
    :rtype: dict
    """
    schema = {
        "N": N,
        "problem": {
            "num_vars": 2,
            "names": ["width", "height"],
            "bounds": [list(width_bounds), list(height_bounds)],
            "dists": [list(width_distribution), list(height_distribution)],
        },
    }
    return schema
