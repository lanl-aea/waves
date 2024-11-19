import pathlib
import argparse
from unittest.mock import patch, mock_open
from contextlib import nullcontext as does_not_raise

import pytest

import solver


def test_main():
    # Check print help
    with (
        patch("sys.argv", ["solver.py"]),
        patch("argparse.ArgumentParser.print_help") as mock_help,
        patch("solver.implicit") as mock_implicit,
        patch("solver.explicit") as mock_explicit,
    ):
        solver.main()
        mock_help.assert_called_once()
        mock_implicit.assert_not_called()
        mock_explicit.assert_not_called()

    # Check call implicit
    with (
        patch("sys.argv", ["solver.py", "implicit", "-i", "dummy_input.yaml"]),
        patch("argparse.ArgumentParser.print_help") as mock_help,
        patch("solver.implicit") as mock_implicit,
        patch("solver.explicit") as mock_explicit,
    ):
        solver.main()
        mock_help.assert_not_called()
        mock_implicit.assert_called_once()
        mock_explicit.assert_not_called()

    # Check call explicit
    with (
        patch("sys.argv", ["solver.py", "explicit", "-i", "dummy_input.yaml"]),
        patch("argparse.ArgumentParser.print_help") as mock_help,
        patch("solver.implicit") as mock_implicit,
        patch("solver.explicit") as mock_explicit,
    ):
        solver.main()
        mock_help.assert_not_called()
        mock_implicit.assert_not_called()
        mock_explicit.assert_called_once()

    # Check RuntimeError converted to SystemExit
    with (
        patch("sys.argv", ["solver.py", "explicit", "-i", "dummy_input.yaml"]),
        patch("solver.explicit", side_effect=RuntimeError("message")),
        pytest.raises(SystemExit) as err,
    ):
        solver.main()
        assert str(err) == message


name_output_file = {
    "no output file": (pathlib.Path("input.yaml"), None, pathlib.Path("input.out")),
    "no output file, relative input path": (
        pathlib.Path("relative/input.yaml"),
        None,
        pathlib.Path("relative/input.out"),
    ),
    "output file": (pathlib.Path("input.yaml"), pathlib.Path("output_file.out"), pathlib.Path("output_file.out")),
    "output file, mismatched relative paths": (
        pathlib.Path("relative/input.yaml"),
        pathlib.Path("different/output_file.out"),
        pathlib.Path("different/output_file.out"),
    ),
    "output file, wrong extension": (
        pathlib.Path("input.yaml"),
        pathlib.Path("output_file.wrong"),
        pathlib.Path("output_file.out"),
    ),
}


@pytest.mark.parametrize(
    "input_file, output_file, expected",
    name_output_file.values(),
    ids=name_output_file.keys(),
)
def test_name_output_file(input_file, output_file, expected):
    returned_output_file = solver.name_output_file(input_file, output_file)
    assert returned_output_file == expected


name_log_file = {
    "no log file exists": (
        pathlib.Path("solver.log"),
        10,
        [False],
        pathlib.Path("solver.log"),
        does_not_raise(),
    ),
    "last iteration file": (
        pathlib.Path("solver.log"),
        2,
        [True, True, False],
        pathlib.Path("solver.log2"),
        does_not_raise(),
    ),
    "default log file exists": (
        pathlib.Path("solver.log"),
        10,
        [True, False],
        pathlib.Path("solver.log1"),
        does_not_raise(),
    ),
    "too many iterations": (
        pathlib.Path("solver.log"),
        0,
        [True],
        None,
        pytest.raises(RuntimeError),
    ),
}


@pytest.mark.parametrize(
    "log_file, max_iterations, exists_side_effect, expected, outcome",
    name_log_file.values(),
    ids=name_log_file.keys(),
)
def test_name_log_file(log_file, max_iterations, exists_side_effect, expected, outcome):
    with (
        patch("pathlib.Path.exists", side_effect=exists_side_effect),
        outcome,
    ):
        try:
            returned_log_file = solver.name_log_file(log_file, max_iterations=max_iterations)
            assert returned_log_file == expected
        finally:
            pass


read_input = {
    "good yaml": (pathlib.Path("dummy.yaml"), True, "routine: implicit", {"routine": "implicit"}, does_not_raise()),
    "bad yaml": (pathlib.Path("dummy.yaml"), True, "\tnotvalidyaml", None, pytest.raises(RuntimeError)),
    "file does not exist": (pathlib.Path("dummy.yaml"), False, None, None, pytest.raises(RuntimeError)),
}


@pytest.mark.parametrize(
    "input_file, is_file_result, mock_data, expected, outcome",
    read_input.values(),
    ids=read_input.keys(),
)
def test_read_input(input_file, is_file_result, mock_data, expected, outcome):
    with (
        patch("pathlib.Path.is_file", side_effect=[is_file_result]),
        patch("builtins.open", mock_open(read_data=mock_data)),
        outcome,
    ):
        try:
            configuration = solver.read_input(input_file)
            assert configuration == expected
        finally:
            pass


configure = {
    "implicit input": (
        argparse.Namespace(
            subcommand="implicit", input_file="implicit.yaml", output_file=None, solve_cpus=1, overwrite=False
        ),
        {"key1": "value1"},
        {"key1": "value1", "routine": "implicit", "output_file": "implicit.out", "solve_cpus": 1, "overwrite": False},
        does_not_raise(),
    ),
    "explicit input": (
        argparse.Namespace(
            subcommand="explicit", input_file="explicit.yaml", output_file=None, solve_cpus=1, overwrite=False
        ),
        {"key1": "value1"},
        {"key1": "value1", "routine": "explicit", "output_file": "explicit.out", "solve_cpus": 1, "overwrite": False},
        does_not_raise(),
    ),
    "mismatch routine": (
        argparse.Namespace(
            subcommand="implicit", input_file="implicit.yaml", output_file=None, solve_cpus=1, overwrite=False
        ),
        {"key1": "value1", "routine": "nonimplicit"},
        {"output_file": "mismatch.out"},
        pytest.raises(RuntimeError),
    ),
    "no cli defaults": (
        argparse.Namespace(
            subcommand="implicit",
            input_file=pathlib.Path("different.yaml"),
            output_file=pathlib.Path("different.out"),
            solve_cpus=2,
            overwrite=True,
        ),
        {"key1": "value1"},
        {"key1": "value1", "routine": "implicit", "output_file": "different.out", "solve_cpus": 2, "overwrite": True},
        does_not_raise(),
    ),
}


@pytest.mark.parametrize(
    "args, read_input, expected, outcome",
    configure.values(),
    ids=configure.keys(),
)
def test_configure(args, read_input, expected, outcome):
    log_file = pathlib.Path("solver.log")
    output_file = pathlib.Path(expected["output_file"])
    mocked_configuration = {
        "version": solver._project_name_version,
        "log_file": str(log_file),
    }
    expected.update(**mocked_configuration)
    with (
        patch("solver.read_input", return_value=read_input),
        patch("solver.name_log_file", return_value=log_file),
        patch("solver.name_output_file", return_value=output_file),
        patch("builtins.open", mock_open()),
        outcome,
    ):
        try:
            returned_configuration = solver.configure(args)
            assert returned_configuration == expected
        finally:
            pass


solve_output_files = {
    "one": (pathlib.Path("output.out"), 1, [pathlib.Path("output.out")]),
    "two": (pathlib.Path("output.out"), 2, [pathlib.Path("output.out0"), pathlib.Path("output.out1")]),
}


@pytest.mark.parametrize(
    "output_file, solve_cpus, expected",
    solve_output_files.values(),
    ids=solve_output_files.keys(),
)
def test_solve_output_files(output_file, solve_cpus, expected):
    output_files = solver.solve_output_files(output_file, solve_cpus)
    assert output_files == expected


solve = {
    "no output files exist": (
        {"log_file": "solver.log", "output_file": "output.out", "solve_cpus": 1, "overwrite": False},
        False,
        does_not_raise(),
    ),
    "output files exist: overwrite": (
        {"log_file": "solver.log", "output_file": "output.out", "solve_cpus": 1, "overwrite": True},
        True,
        does_not_raise(),
    ),
    "output files exist: no overwrite": (
        {"log_file": "solver.log", "output_file": "output.out", "solve_cpus": 1, "overwrite": False},
        True,
        pytest.raises(RuntimeError),
    ),
}


@pytest.mark.parametrize(
    "configuration, exists, outcome",
    solve.values(),
    ids=solve.keys(),
)
def test_solve(configuration, exists, outcome):
    with (
        patch("pathlib.Path.exists", return_value=exists),
        patch("builtins.open", mock_open()),
        outcome,
    ):
        try:
            solver.solve(configuration)
        finally:
            pass


def test_implicit():
    dummy_namespace = {"dummy": "namespace"}
    dummy_configuration = {"configuration": "value"}
    with (
        patch("solver.configure", side_effect=[dummy_configuration]) as mock_configure,
        patch("solver.solve") as mock_solve,
    ):
        solver.implicit(dummy_namespace)
        mock_configure.assert_called_once_with(dummy_namespace)
        mock_solve.assert_called_once_with(dummy_configuration)


def test_explicit():
    dummy_namespace = {"dummy": "namespace"}
    dummy_configuration = {"configuration": "value"}
    with (
        patch("solver.configure", side_effect=[dummy_configuration]) as mock_configure,
        patch("solver.solve") as mock_solve,
    ):
        solver.implicit(dummy_namespace)
        mock_configure.assert_called_once_with(dummy_namespace)
        mock_solve.assert_called_once_with(dummy_configuration)


positive_nonzero_int = {
    "positive int": ("1", 1, does_not_raise()),
    "larger positive int": ("100", 100, does_not_raise()),
    "zero": ("0", None, pytest.raises(argparse.ArgumentTypeError)),
    "negative int": ("-1", None, pytest.raises(argparse.ArgumentTypeError)),
    "string": ("not an int", None, pytest.raises(argparse.ArgumentTypeError)),
}


@pytest.mark.parametrize(
    "argument, expected, outcome",
    positive_nonzero_int.values(),
    ids=positive_nonzero_int.keys(),
)
def test_positive_nonzero_int(argument, expected, outcome):
    with outcome:
        try:
            answer = solver.positive_nonzero_int(argument)
            assert answer == expected
        finally:
            pass


def test_get_parser():
    pass
