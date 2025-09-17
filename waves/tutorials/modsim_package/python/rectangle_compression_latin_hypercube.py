"""Parameter sets and schemas for the rectangle compression simulation."""

import types
import typing

default_width = types.MappingProxyType({"distribution": "norm", "loc": 1, "scale": 0.1})
default_height = types.MappingProxyType({"distribution": "norm", "loc": 1, "scale": 0.1})


def parameter_schema(
    num_simulations: int = 4,
    width: dict[str, typing.Any] | types.MappingProxyType = default_width,
    height: dict[str, typing.Any] | types.MappingProxyType = default_height,
) -> dict[str, typing.Any]:
    """Return WAVES Scipy LatinHypercube parameter schema.

    :param num_simulations: Number of samples to generate
    :param width: The rectangle width Scipy distribution definition
    :param height: The rectangle height Scipy distribution definition

    :returns: WAVES Scipy LatinHypercube parameter schema
    """
    schema = {
        "num_simulations": num_simulations,
        "width": dict(width),
        "height": dict(height),
    }
    return schema
