def positive_float(argument):
    """Type function for argparse - positive floats

    Both Abaqus Python 2 and Python 3 compatible

    :param str argument: string argument from argparse

    :returns: argument
    :rtype: float
    """
    MINIMUM_VALUE = 0.0
    try:
        argument = float(argument)
    except ValueError:
        raise argparse.ArgumentTypeError("invalid float value: '{}'".format(argument))
    if argument < MINIMUM_VALUE:
        raise argparse.ArgumentTypeError("invalid positive float: '{}'".format(argument))
    return argument
