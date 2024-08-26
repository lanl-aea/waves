import argparse
from unittest.mock import patch, mock_open
from contextlib import nullcontext as does_not_raise

import pytest

import solver


def test_main():
    # Check print help
    with patch('sys.argv', ['solver.py']), \
         patch('argparse.ArgumentParser.print_help') as mock_help, \
         patch('solver.implicit') as mock_implicit, \
         patch('solver.explicit') as mock_explicit:
        solver.main()
        mock_help.assert_called_once()
        mock_implicit.assert_not_called()
        mock_explicit.assert_not_called()

    # Check call implicit
    with patch('sys.argv', ['solver.py', 'implicit', '-i', 'dummy_input.yaml']), \
         patch('argparse.ArgumentParser.print_help') as mock_help, \
         patch('solver.implicit') as mock_implicit, \
         patch('solver.explicit') as mock_explicit:
        solver.main()
        mock_help.assert_not_called()
        mock_implicit.assert_called_once()
        mock_explicit.assert_not_called()

    # Check call explicit
    with patch('sys.argv', ['solver.py', 'explicit', '-i', 'dummy_input.yaml']), \
         patch('argparse.ArgumentParser.print_help') as mock_help, \
         patch('solver.implicit') as mock_implicit, \
         patch('solver.explicit') as mock_explicit:
        solver.main()
        mock_help.assert_not_called()
        mock_implicit.assert_not_called()
        mock_explicit.assert_called_once()


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
