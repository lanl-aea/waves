import typing
import unittest.mock

import pytest

from waves._abaqus import abaqus_file_parser


class ConcreteAbaqusFileParser(abaqus_file_parser.AbaqusFileParser):
    def parse(self, *args, **kwargs) -> None:
        pass


test_abaqus_file_parser_init_cases: dict[str, tuple] = {
    "only init arguments": (("dummy_file.input",), {}, "dummy_file.input", "dummy_file.input.parsed", False),
    "non-default kwargs": (
        ("dummy_file.input",),
        {"verbose": True},
        "dummy_file.input",
        "dummy_file.input.parsed",
        True,
    ),
    "init and parse arguments": (
        ("dummy_file.input", "thing1"),
        {"keyword1": "value1"},
        "dummy_file.input",
        "dummy_file.input.parsed",
        False,
    ),
}


@pytest.mark.parametrize(
    ("init_args", "init_kwargs", "input_file", "output_file", "verbose"),
    test_abaqus_file_parser_init_cases.values(),
    ids=test_abaqus_file_parser_init_cases.keys(),
)
def test_abaqus_file_parser_init(
    init_args: tuple,
    init_kwargs: dict[str, typing.Any],
    input_file: str,
    output_file: str,
    verbose: bool,
) -> None:
    """Test :class:`waves._abaqus.abaqus_file_parser.AbaqusFileParser`.

    :param init_args: the class initialization positional arguments
    :param init_kwargs: the class initialization keyword arguments
    :param input_file: the expected class input file attribute
    :param output_file: the expected class output file attribute
    :param verbose: the expected class verbose attribute
    """
    expected_parse_args = init_args[1:]
    expected_parse_kwargs = {key: value for key, value in init_kwargs.items() if key != "verbose"}
    with unittest.mock.patch("waves._tests.test_abaqus_file_parser.ConcreteAbaqusFileParser.parse") as mock_parse:
        test_instance = ConcreteAbaqusFileParser(*init_args, **init_kwargs)
        assert test_instance.input_file == input_file
        assert test_instance.parsed == {}
        assert test_instance.output_file == output_file
        assert test_instance.verbose is verbose
        mock_parse.assert_called_once_with(*expected_parse_args, **expected_parse_kwargs)


@pytest.mark.parametrize(
    ("init_args", "init_kwargs", "input_file", "output_file", "verbose"),
    test_abaqus_file_parser_init_cases.values(),
    ids=test_abaqus_file_parser_init_cases.keys(),
)
def test_odb_report_file_parser_init(
    init_args: tuple,
    init_kwargs: dict[str, typing.Any],
    input_file: str,
    output_file: str,
    verbose: bool,
) -> None:
    """Test :class:`waves._abaqus.abaqus_file_parser.OdbReportFileParser`.

    :param init_args: the class initialization positional arguments
    :param init_kwargs: the class initialization keyword arguments
    :param input_file: the expected class input file attribute
    :param output_file: the expected class output file attribute
    :param verbose: the expected class verbose attribute
    """
    expected_parse_args = init_args[1:]
    expected_parse_kwargs = {key: value for key, value in init_kwargs.items() if key != "verbose"}
    with unittest.mock.patch("waves._abaqus.abaqus_file_parser.OdbReportFileParser.parse") as mock_parse:
        test_instance = abaqus_file_parser.OdbReportFileParser(*init_args, **init_kwargs)
        assert test_instance.input_file == input_file
        assert test_instance.parsed == {}
        assert test_instance.output_file == output_file
        assert test_instance.verbose is verbose
        mock_parse.assert_called_once_with(*expected_parse_args, **expected_parse_kwargs)
