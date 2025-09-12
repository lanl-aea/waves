"""Parameter sets and schemas for the rectangle compression simulation."""

import types
import typing

default_width = types.MappingProxyType({"distribution": "uniform", "loc": 0.9, "scale": 0.2})
default_height = types.MappingProxyType({"distribution": "uniform", "loc": 0.9, "scale": 0.2})


def parameter_schema(
    num_simulations: int = 4,
    width: dict[str, typing.Any] | types.MappingProxyType = default_width,
    height: dict[str, typing.Any] | types.MappingProxyType = default_height,
) -> dict[str, typing.Any]:
    """Return WAVES SciPy Sobol parameter schema.

    :param num_simulations: Number of samples to generate
    :param width: The rectangle width SciPy distribution definition
    :param height: The rectangle height SciPy distribution definition

    :returns: WAVES SciPy Sobol parameter schema
    """
    schema = {
        "num_simulations": num_simulations,
        "width": dict(width),
        "height": dict(height),
    }
    return schema
