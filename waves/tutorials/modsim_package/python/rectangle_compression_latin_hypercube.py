"""Parameter sets and schemas for the rectangle compression simulation"""


def parameter_schema(
    num_simulations=4,
    width={"distribution": "norm", "loc": 1, "scale": 0.1},
    height={"distribution": "norm", "loc": 1, "scale": 0.1},
):
    """Return WAVES Scipy LatinHypercube parameter schema

    :param int num_simulations: Number of samples to generate
    :param dict width: The rectangle width Scipy distribution definition
    :param dict height: The rectangle height Scipy distribution definition

    :returns: WAVES Scipy LatinHypercube parameter schema
    :rtype: dict
    """
    schema = {
        "num_simulations": num_simulations,
        "width": width,
        "height": height,
    }
    return schema
