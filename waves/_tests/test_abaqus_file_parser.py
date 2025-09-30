import unittest.mock

from waves._abaqus import abaqus_file_parser


class ConcreteAbaqusFileParser(abaqus_file_parser.AbaqusFileParser):
    def parse(self, *args, **kwargs) -> None:
        pass


def test_abaqus_file_parser_init() -> None:
    with unittest.mock.patch("waves._tests.test_abaqus_file_parser.ConcreteAbaqusFileParser.parse") as mock_parse:
        test_instance = ConcreteAbaqusFileParser("dummy_file.input")
        assert test_instance.input_file == "dummy_file.input"
        assert test_instance.parsed == {}
        assert test_instance.output_file == "dummy_file.input.parsed"
        assert test_instance.verbose is False
        mock_parse.assert_called_once_with()
