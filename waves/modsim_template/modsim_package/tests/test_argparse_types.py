import argparse
from contextlib import nullcontext as does_not_raise

import pytest

from modsim_package import argparse_types


positive_float = {
    "positive float": ("1", 1.0, does_not_raise()),
    "negative float": ("-1", None, pytest.raises(argparse.ArgumentTypeError)),
    "string": ("not a float", None, pytest.raises(argparse.ArgumentTypeError)),
}


@pytest.mark.parametrize(
    "argument, expected, outcome",
    positive_float.values(),
    ids=positive_float.keys(),
)
def test_positive_float(argument, expected, outcome):
    with outcome:
        try:
            answer = argparse_types.positive_float(argument)
            assert answer == expected
        finally:
            pass
