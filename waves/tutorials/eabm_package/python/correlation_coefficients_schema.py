"""Parameter sets and schemas for the rectangle compression simulation"""


def schema(N=5,
           width_distribution="norm", width_bounds=[1., 0.1],
           height_distribution="norm", height_bounds[1., 0.1]):
    """Return WAVES SALibSampler Sobol schema dictionary

    :param int N: Number of parameter sets to sample
    :param str width_distribution: SALib distribution name
    :param list width_bounds: Distribution characteristics. Meaning varies depending on distribution type.
    :param str height_distribution: SALib distribution name
    :param list height_bounds: Distribution characteristics. Meaning varies depending on distribution type.

    :returns: WAVES SALibSampler Sobol schema
    :rtype: dict
    """
    schema = {
        'N': 5,
        'problem': {
            'num_vars': 2,
            'names': ['width', 'height'],
            'bounds': [width_bounds, heigh_bounds],
            'dists': [width_distribution, height_distribution]
        }
    }
    return schema
