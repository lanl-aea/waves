"""Test command line utility and associated functions"""

import pathlib
from unittest.mock import Mock, patch, mock_open
from contextlib import nullcontext as does_not_raise

import pytest

from waves import _main
from waves import _settings
from waves import exceptions


def test_main():
    # docs subcommand
    with (
        patch("sys.argv", ["waves.py", "docs"]),
        patch("waves._docs.main") as mock_docs,
    ):
        _main.main()
        mock_docs.assert_called_once()

    # docs subcommand, any subcommand that raises a RuntimeError
    with (
        patch("sys.argv", ["waves.py", "docs"]),
        patch("waves._docs.main", side_effect=RuntimeError) as mock_docs,
        patch("sys.exit") as mock_exit,
    ):
        _main.main()
        mock_docs.assert_called_once()
        mock_exit.assert_called_once()

    # docs subcommand, any subcommand that raises a WAVESError
    with (
        patch("sys.argv", ["waves.py", "docs"]),
        patch("waves._docs.main", side_effect=exceptions.WAVESError) as mock_docs,
        patch("sys.exit") as mock_exit,
    ):
        _main.main()
        mock_docs.assert_called_once()
        mock_exit.assert_called_once()

    # fetch subcommand
    requested_paths = ["dummy.file1", "dummy.file2"]
    requested_paths_args = [pathlib.Path(path) for path in requested_paths]
    with (
        patch("sys.argv", ["waves.py", "fetch"] + requested_paths),
        patch("waves._fetch.recursive_copy") as mock_recursive_copy,
    ):
        _main.main()
        mock_recursive_copy.assert_called_once()
        assert mock_recursive_copy.call_args[1]["requested_paths"] == requested_paths_args

    tutorial_number = 7
    with (
        patch("sys.argv", ["waves.py", "fetch", "--tutorial", str(tutorial_number)]),
        patch("waves._fetch.recursive_copy") as mock_recursive_copy,
    ):
        _main.main()
        mock_recursive_copy.assert_called_once()
        assert mock_recursive_copy.call_args[1]["tutorial"] == tutorial_number

    # visualize subcommand
    target_string = "dummy.target"
    with (
        patch("sys.argv", ["waves.py", "visualize", target_string]),
        patch("waves._visualize.main") as mock_visualize,
    ):
        _main.main()
        mock_visualize.assert_called_once()
        assert mock_visualize.call_args[0][0] == [target_string]

    # build subcommand
    target_string = "dummy.target"
    with (
        patch("sys.argv", ["waves.py", "build", target_string]),
        patch("waves._build.main") as mock_build,
    ):
        _main.main()
        mock_build.assert_called_once()
        assert mock_build.call_args[0][0] == [target_string]

    # print_study subcommand
    parameter_study_file = "dummy.h5"
    with (
        patch("sys.argv", ["waves.py", "print_study", parameter_study_file]),
        patch("waves._print_study.main") as mock_print_study,
    ):
        _main.main()
        mock_print_study.assert_called_once()
        assert mock_print_study.call_args[0][0] == pathlib.Path(parameter_study_file)

    # help
    with (
        patch("sys.argv", ["waves.py", "notasubcommand"]),
        pytest.raises(SystemExit),
    ):
        _main.main()

    with (
        patch("sys.argv", ["_main.py"]),
        patch("argparse.ArgumentParser.print_help") as mock_print_help,
    ):
        _main.main()
        mock_print_help.assert_called_once()


# fmt: off
parameter_study_args = {  #               subcommand,         class_name,                   argument,         option, argument_value  # noqa: E262,E501
    'cartesian product':        ('cartesian_product', 'CartesianProduct',                       None,           None,             None),  # noqa E241,E501
    'custom study':             (     'custom_study',      'CustomStudy',                       None,           None,             None),  # noqa E241,E501
    'latin hypercube':          (  'latin_hypercube',   'LatinHypercube',                       None,           None,             None),  # noqa E241,E501
    'sobol sequence':           (   'sobol_sequence',    'SobolSequence',                       None,           None,             None),  # noqa E241,E501
    'one at a time':            (    'one_at_a_time',       'OneAtATime',                       None,           None,             None),  # noqa E241,E501
    'output file template':     ('cartesian_product', 'CartesianProduct',     'output_file_template',           '-o', 'dummy_template'),  # noqa E241,E501
    'output file':              (     'custom_study',      'CustomStudy',              'output_file',           '-f', 'dummy_file.txt'),  # noqa E241,E501
    'output file type':         (  'latin_hypercube',   'LatinHypercube',         'output_file_type',           '-t',             'h5'),  # noqa E241,E501
    'set name template':        (   'sobol_sequence',    'SobolSequence',        'set_name_template',           '-s',        '@number'),  # noqa E241,E501
    'previous parameter study': ('cartesian_product', 'CartesianProduct', 'previous_parameter_study',           '-p', 'dummy_file.txt'),  # noqa E241,E501
    'overwrite':                (     'custom_study',      'CustomStudy',                'overwrite',  '--overwrite',             True),  # noqa E241,E501
    'dry run':                  (  'latin_hypercube',   'LatinHypercube',                  'dry_run',    '--dry-run',             True),  # noqa E241,E501
    'write meta':               (   'sobol_sequence',    'SobolSequence',               'write_meta', '--write-meta',             True),  # noqa E241,E501
}
# fmt: on


@pytest.mark.parametrize(
    "subcommand, class_name, argument, option, argument_value",
    parameter_study_args.values(),
    ids=list(parameter_study_args.keys()),
)
def test_parameter_study(subcommand, class_name, argument, option, argument_value):
    # Help/usage. Should not raise
    with (
        patch("sys.argv", ["_main.py", subcommand, "-h"]),
        pytest.raises(SystemExit) as err,
    ):
        _main.main()
    assert err.value.code == 0

    # Run main code. No SystemExit expected.
    arg_list = ["_main.py", subcommand, "dummy.file"]
    if option:
        arg_list.append(option)
    if argument_value:
        # Don't pass boolean values
        if not isinstance(argument_value, bool):
            arg_list.append(argument_value)
    mock_instantiation = Mock()
    with (
        patch("sys.argv", arg_list),
        patch("builtins.open", mock_open()),
        patch("yaml.safe_load"),
        patch(f"waves.parameter_generators.{class_name}", return_value=mock_instantiation) as mock_generator,
        patch("pathlib.Path.is_file", return_value=True),
        does_not_raise(),
    ):
        _main.main()
        mock_generator.assert_called_once()
        if argument and argument != "dry_run":
            assert mock_generator.call_args.kwargs[argument] == argument_value
            mock_instantiation.write.assert_called_once_with(dry_run=_settings._default_dry_run)
        elif argument and argument == "dry_run":
            mock_instantiation.write.assert_called_once_with(dry_run=argument_value)
