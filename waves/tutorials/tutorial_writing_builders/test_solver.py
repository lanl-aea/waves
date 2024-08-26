import argparse
from contextlib import nullcontext as does_not_raise

import pytest

import solver 


positive_float = {
    "positive int": ("1", 1, does_not_raise()),
    "larger positive int": ("100", 100, does_not_raise()),
    "zero": ("0", None, pytest.raises(argparse.ArgumentTypeError)),
    "negative int": ("-1", None, pytest.raises(argparse.ArgumentTypeError)),
    "string": ("not an int", None, pytest.raises(argparse.ArgumentTypeError))
}


@pytest.mark.parametrize("argument, expected, outcome", positive_float.values(), ids=positive_float.keys())
def test_positive_nonzero_int(argument, expected, outcome):
    with outcome:
        try:
            answer = solver.positive_nonzero_int(argument)
            assert answer == expected
        finally:
            pass
