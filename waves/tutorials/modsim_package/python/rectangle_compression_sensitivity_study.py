"""Parameter sets and schemas for the rectangle compression simulation."""

import typing


def parameter_schema(
    N: int = 5,  # noqa: N803
    width_distribution: str = "norm",
    width_bounds: list[float] | tuple[float, ...] = (1.0, 0.1),
    height_distribution: str = "norm",
    height_bounds: list[float] | tuple[float, ...] = (1.0, 0.1),
) -> dict[str, typing.Any]:
    """Return WAVES SALibSampler Sobol schema.

    :param N: Number of samples to generate
    :param width_distribution: SALib distribution name
    :param width_bounds: Distribution characteristics. Meaning varies depending on distribution type.
    :param height_distribution: SALib distribution name
    :param height_bounds: Distribution characteristics. Meaning varies depending on distribution type.

    :returns: WAVES SALibSampler Sobol schema
    """
    schema = {
        "N": N,
        "problem": {
            "num_vars": 2,
            "names": ["width", "height"],
            "bounds": [list(width_bounds), list(height_bounds)],
            "dists": [width_distribution, height_distribution],
        },
    }
    return schema
