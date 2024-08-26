import pathlib
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


name_output_file = {
    "no output file": (pathlib.Path("input.yaml"), None, pathlib.Path("input.out")),
    "no output file, relative input path": (
        pathlib.Path("relative/input.yaml"), None, pathlib.Path("relative/input.out")
    ),
    "output file": (pathlib.Path("input.yaml"), pathlib.Path("output_file.out"), pathlib.Path("output_file.out")),
    "output file, mismatched relative paths": (
        pathlib.Path("relative/input.yaml"),
        pathlib.Path("different/output_file.out"),
        pathlib.Path("different/output_file.out")
    ),
    "output file, wrong extension": (
        pathlib.Path("input.yaml"), pathlib.Path("output_file.wrong"), pathlib.Path("output_file.out")
    )
}


@pytest.mark.parametrize("input_file, output_file, expected", name_output_file.values(), ids=name_output_file.keys())
def test_name_output_file(input_file, output_file, expected):
    returned_output_file = solver.name_output_file(input_file, output_file)
    assert returned_output_file == expected


name_log_file = {
    "no log file exists": (pathlib.Path("solver.log"), 10, [False], pathlib.Path("solver.log")),
}


@pytest.mark.parametrize("log_file, max_iterations, exists_side_effect, expected",
                         name_log_file.values(), ids=name_log_file.keys())
def test_name_log_file(log_file, max_iterations, exists_side_effect, expected):
    with patch("pathlib.Path.exists", side_effect=exists_side_effect):
        returned_log_file = solver.name_log_file(log_file, max_iterations=max_iterations)
        assert returned_log_file == expected


positive_nonzero_int = {
    "positive int": ("1", 1, does_not_raise()),
    "larger positive int": ("100", 100, does_not_raise()),
    "zero": ("0", None, pytest.raises(argparse.ArgumentTypeError)),
    "negative int": ("-1", None, pytest.raises(argparse.ArgumentTypeError)),
    "string": ("not an int", None, pytest.raises(argparse.ArgumentTypeError))
}


@pytest.mark.parametrize("argument, expected, outcome", positive_nonzero_int.values(), ids=positive_nonzero_int.keys())
def test_positive_nonzero_int(argument, expected, outcome):
    with outcome:
        try:
            answer = solver.positive_nonzero_int(argument)
            assert answer == expected
        finally:
            pass
