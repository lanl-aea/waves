"""Test OneAtATime Class."""

import contextlib
import typing
import unittest
from unittest.mock import call, mock_open, patch

import numpy
import pytest
import xarray

from waves._settings import _allowable_output_file_typing, _set_coordinate_key
from waves._tests.common import consistent_hash_parameter_check, merge_samplers, self_consistency_checks
from waves.exceptions import SchemaValidationError
from waves.parameter_generators import OneAtATime

does_not_raise = contextlib.nullcontext()


class TestOneAtATime:
    """Class for testing OneAtATime parameter study generator class."""

    validate_input = {
        "good schema": (
            {"parameter_1": [1], "parameter_2": (2,), "parameter_3": [3, 4]},
            does_not_raise,
        ),
        "not a dict": (
            "not a dict",
            pytest.raises(SchemaValidationError),
        ),
        "bad schema int": (
            {"parameter_1": 1},
            pytest.raises(SchemaValidationError),
        ),
        "bad schema dict": (
            {"parameter_1": {"thing1": 1}},
            pytest.raises(SchemaValidationError),
        ),
        "bad schema str": (
            {"parameter_1": "one"},
            pytest.raises(SchemaValidationError),
        ),
        "bad schema empty": (
            {"parameter_1": []},
            pytest.raises(SchemaValidationError),
        ),
        "bad schema set": (
            {"parameter_1": {1, 2}},
            pytest.raises(SchemaValidationError),
        ),
    }

    @pytest.mark.parametrize(
        ("parameter_schema", "outcome"),
        validate_input.values(),
        ids=validate_input.keys(),
    )
    def test_validate(self, parameter_schema: dict, outcome: contextlib.nullcontext | pytest.RaisesExc) -> None:
        with outcome:
            # Validate is called in __init__. Do not need to call explicitly.
            test_validate = OneAtATime(parameter_schema)
            assert isinstance(test_validate, OneAtATime)

    generate_io = {
        "one_parameter: 1, 2": (
            {"parameter_1": [1, 2]},
            {},
            xarray.Dataset(
                {
                    "parameter_1": xarray.DataArray(
                        [1, 2],
                        coords={
                            _set_coordinate_key: xarray.DataArray(
                                ["parameter_set0", "parameter_set1"], dims=_set_coordinate_key
                            )
                        },
                    ),
                    "set_hash": xarray.DataArray(
                        ["1661dcd0bf4761d25471c1cf5514ceae", "0b588b6a82c1d3d3d19fda304f940342"],
                        dims=_set_coordinate_key,
                    ),
                }
            ).set_coords("set_hash"),
            {"parameter_1": numpy.int64},
        ),
        "one_parameter: 1, 2, custom template": (
            {"parameter_1": [1, 2]},
            {"set_name_template": "set@number"},
            xarray.Dataset(
                {
                    "parameter_1": xarray.DataArray(
                        [1, 2],
                        coords={_set_coordinate_key: xarray.DataArray(["set0", "set1"], dims=_set_coordinate_key)},
                    ),
                    "set_hash": xarray.DataArray(
                        ["1661dcd0bf4761d25471c1cf5514ceae", "0b588b6a82c1d3d3d19fda304f940342"],
                        dims=_set_coordinate_key,
                    ),
                }
            ).set_coords("set_hash"),
            {"parameter_1": numpy.int64},
        ),
        "one_parameter: 2, 1": (
            {"parameter_1": [2, 1]},
            {},
            xarray.Dataset(
                {
                    "parameter_1": xarray.DataArray(
                        [2, 1],
                        coords={
                            _set_coordinate_key: xarray.DataArray(
                                ["parameter_set0", "parameter_set1"], dims=_set_coordinate_key
                            )
                        },
                    ),
                    "set_hash": xarray.DataArray(
                        ["0b588b6a82c1d3d3d19fda304f940342", "1661dcd0bf4761d25471c1cf5514ceae"],
                        dims=_set_coordinate_key,
                    ),
                }
            ).set_coords("set_hash"),
            {"parameter_1": numpy.int64},
        ),
        "two_parameter": (
            {"parameter_1": [1, 2], "parameter_2": ["a", "b"]},
            {},
            xarray.Dataset(
                {
                    "parameter_1": xarray.DataArray(
                        [1, 1, 2],
                        coords={
                            _set_coordinate_key: xarray.DataArray(
                                ["parameter_set0", "parameter_set1", "parameter_set2"], dims=_set_coordinate_key
                            )
                        },
                    ),
                    "parameter_2": xarray.DataArray(
                        ["a", "b", "a"],
                        coords={
                            _set_coordinate_key: xarray.DataArray(
                                ["parameter_set0", "parameter_set1", "parameter_set2"], dims=_set_coordinate_key
                            )
                        },
                    ),
                    "set_hash": xarray.DataArray(
                        [
                            "3b86be0b68c8a5a2a7dca07213846681",
                            "dd8d813de1f1b82671b694817bf10c3f",
                            "f4f5a25089f52a0d069c83f34ce6b68b",
                        ],
                        dims=_set_coordinate_key,
                    ),
                }
            ).set_coords("set_hash"),
            {"parameter_1": numpy.int64, "parameter_2": numpy.dtype("U1")},
        ),
        "ints and floats": (
            {"parameter_1": [1, 2], "parameter_2": [3.0, 4.0]},
            {},
            xarray.Dataset(
                {
                    "parameter_1": xarray.DataArray(
                        [1, 1, 2],
                        coords={
                            _set_coordinate_key: xarray.DataArray(
                                ["parameter_set0", "parameter_set1", "parameter_set2"], dims=_set_coordinate_key
                            )
                        },
                    ),
                    "parameter_2": xarray.DataArray(
                        [3.0, 4.0, 3.0],
                        coords={
                            _set_coordinate_key: xarray.DataArray(
                                ["parameter_set0", "parameter_set1", "parameter_set2"], dims=_set_coordinate_key
                            )
                        },
                    ),
                    "set_hash": xarray.DataArray(
                        [
                            "ad4d9f0b45ec964db8f313a2b64636de",
                            "6a184a4ff7991572e4c8f2d096656b6b",
                            "e12bff8429a0bc549e4f029ffcb14e6b",
                        ],
                        dims=_set_coordinate_key,
                    ),
                }
            ).set_coords("set_hash"),
            {"parameter_1": numpy.int64, "parameter_2": numpy.float64},
        ),
        "various parameter types, sizes, and orders": (
            {"parameter_1": [1, 2], "parameter_2": [3.0, -1.0, 4.0], "parameter_3": ("a", "b")},
            {},
            xarray.Dataset(
                {
                    "parameter_1": xarray.DataArray(
                        [1, 1, 1, 2, 1],
                        coords={
                            _set_coordinate_key: xarray.DataArray(
                                [
                                    "parameter_set0",
                                    "parameter_set1",
                                    "parameter_set2",
                                    "parameter_set3",
                                    "parameter_set4",
                                ],
                                dims=_set_coordinate_key,
                            )
                        },
                    ),
                    "parameter_2": xarray.DataArray(
                        [3.0, -1.0, 4.0, 3.0, 3.0],
                        coords={
                            _set_coordinate_key: xarray.DataArray(
                                [
                                    "parameter_set0",
                                    "parameter_set1",
                                    "parameter_set2",
                                    "parameter_set3",
                                    "parameter_set4",
                                ],
                                dims=_set_coordinate_key,
                            )
                        },
                    ),
                    "parameter_3": xarray.DataArray(
                        ["a", "a", "a", "a", "b"],
                        coords={
                            _set_coordinate_key: xarray.DataArray(
                                [
                                    "parameter_set0",
                                    "parameter_set1",
                                    "parameter_set2",
                                    "parameter_set3",
                                    "parameter_set4",
                                ],
                                dims=_set_coordinate_key,
                            )
                        },
                    ),
                    "set_hash": xarray.DataArray(
                        [
                            "4d9644f3ff9205869b5c5aef11cb5235",
                            "52c0adc106690f2ab51d40f4e810a005",
                            "8e213a62356cd1d4ce2b3b795fab6ef9",
                            "8eb85255b4d3888cbf413afc55cbbac3",
                            "e12e11343c63ebc9b329cf90c9a2b07e",
                        ],
                        dims=_set_coordinate_key,
                    ),
                }
            ).set_coords("set_hash"),
            {"parameter_1": numpy.int64, "parameter_2": numpy.float64, "parameter_3": numpy.dtype("U1")},
        ),
    }

    @pytest.mark.parametrize(
        ("parameter_schema", "kwargs", "expected_dataset", "expected_types"),
        generate_io.values(),
        ids=generate_io.keys(),
    )
    def test_generate(
        self,
        parameter_schema: dict,
        kwargs: dict[str, typing.Any],
        expected_dataset: xarray.Dataset,
        expected_types: dict[str, type],
    ) -> None:
        test_generate = OneAtATime(parameter_schema, **kwargs)
        xarray.testing.assert_identical(test_generate.parameter_study, expected_dataset)
        for key in test_generate.parameter_study:
            assert test_generate.parameter_study[key].dtype == expected_types[str(key)]
        # Verify that the parameter set name creation method was called
        # TODO: _set_names is an ordered object (dictionary). Fix test to compare dictionary-to-dictionary instead of
        # implied consistency according to value order.
        assert list(test_generate._set_names.values()) == list(expected_dataset[_set_coordinate_key].to_numpy())

    merge_test = {
        "single set unchanged": (
            {"parameter_1": [1]},
            {"parameter_1": [1]},
            # Ordered by md5 hash during Xarray merge operation. New tests must verify hash ordering.
            numpy.array([[1]], dtype=object),
            {"parameter_1": numpy.int64},
        ),
        "single set and new set": (
            {"parameter_1": [1]},
            {"parameter_1": [2]},
            # Ordered by md5 hash during Xarray merge operation. New tests must verify hash ordering.
            numpy.array([[2], [1]], dtype=object),
            {"parameter_1": numpy.int64},
        ),
        "new set": (
            {"parameter_1": [1, 2], "parameter_2": [3.0], "parameter_3": ["a"]},
            {"parameter_1": [1, 2], "parameter_2": [3.0, 4.0], "parameter_3": ["a"]},
            # Ordered by md5 hash during Xarray merge operation. New tests must verify hash ordering.
            numpy.array(
                [
                    [1, 3.0, "a"],
                    [1, 4.0, "a"],
                    [2, 3.0, "a"],
                ],
                dtype=object,
            ),
            {"parameter_1": numpy.int64, "parameter_2": numpy.float64, "parameter_3": numpy.dtype("U1")},
        ),
        "new set: bools": (
            {"parameter_1": [1, 2], "parameter_2": [True], "parameter_3": ["a"]},
            {"parameter_1": [1, 2], "parameter_2": [True, False], "parameter_3": ["a"]},
            # Ordered by md5 hash during Xarray merge operation. New tests must verify hash ordering.
            numpy.array(
                [
                    [2, True, "a"],
                    [1, False, "a"],
                    [1, True, "a"],
                ],
                dtype=object,
            ),
            {"parameter_1": numpy.int64, "parameter_2": bool, "parameter_3": numpy.dtype("U1")},
        ),
        "unchanged sets": (
            {"parameter_1": [1, 2], "parameter_2": [3.0], "parameter_3": ["a"]},
            {"parameter_1": [1, 2], "parameter_2": [3.0], "parameter_3": ["a"]},
            # Ordered by md5 hash during Xarray merge operation. New tests must verify hash ordering.
            numpy.array(
                [
                    [1, 3.0, "a"],
                    [2, 3.0, "a"],
                ],
                dtype=object,
            ),
            {"parameter_1": numpy.int64, "parameter_2": numpy.float64, "parameter_3": numpy.dtype("U1")},
        ),
        "unchanged sets: bools": (
            {"parameter_1": [1, 2], "parameter_2": [True], "parameter_3": ["a"]},
            {"parameter_1": [1, 2], "parameter_2": [True], "parameter_3": ["a"]},
            # Ordered by md5 hash during Xarray merge operation. New tests must verify hash ordering.
            numpy.array(
                [
                    [2, True, "a"],
                    [1, True, "a"],
                ],
                dtype=object,
            ),
            {"parameter_1": numpy.int64, "parameter_2": bool, "parameter_3": numpy.dtype("U1")},
        ),
    }

    @pytest.mark.parametrize(
        ("first_schema", "second_schema", "expected_array", "expected_types"),
        merge_test.values(),
        ids=merge_test.keys(),
    )
    def test_merge(
        self, first_schema: dict, second_schema: dict, expected_array: numpy.ndarray, expected_types: dict[str, type]
    ) -> None:
        with patch("waves.parameter_generators._verify_parameter_study"):
            original_study, merged_study = merge_samplers(OneAtATime, first_schema, second_schema, {})
            generate_array = merged_study._samples
            assert numpy.all(generate_array == expected_array)
            for key in merged_study.parameter_study:
                assert merged_study.parameter_study[key].dtype == expected_types[str(key)]
            consistent_hash_parameter_check(original_study, merged_study)
            self_consistency_checks(merged_study)

    write_yaml = {
        "one parameter yaml": (
            {"parameter_1": [1, 2]},
            "out",
            None,
            "yaml",
            2,
            [call("parameter_1: 1\n"), call("parameter_1: 2\n")],
        ),
        "two parameter yaml": (
            {"parameter_1": [1, 2], "parameter_2": ["a", "b"]},
            "out",
            None,
            "yaml",
            3,
            [
                call("parameter_1: 1\nparameter_2: a\n"),
                call("parameter_1: 1\nparameter_2: b\n"),
                call("parameter_1: 2\nparameter_2: a\n"),
            ],
        ),
        "two parameter yaml: floats and ints": (
            {"parameter_1": [1, 2], "parameter_2": [3.0, 4.0]},
            "out",
            None,
            "yaml",
            3,
            [
                call("parameter_1: 1\nparameter_2: 3.0\n"),
                call("parameter_1: 1\nparameter_2: 4.0\n"),
                call("parameter_1: 2\nparameter_2: 3.0\n"),
            ],
        ),
        "two parameter yaml: bools and ints": (
            {"parameter_1": [1, 2], "parameter_2": [True, False]},
            "out",
            None,
            "yaml",
            3,
            [
                call("parameter_1: 1\nparameter_2: true\n"),
                call("parameter_1: 2\nparameter_2: true\n"),
                call("parameter_1: 1\nparameter_2: false\n"),
            ],
        ),
        "one parameter one file yaml": (
            {"parameter_1": [1, 2]},
            None,
            "parameter_study.yaml",
            "yaml",
            1,
            [call("parameter_set0:\n  parameter_1: 1\nparameter_set1:\n  parameter_1: 2\n")],
        ),
        "two parameter one file yaml": (
            {"parameter_1": [1, 2], "parameter_2": ["a", "b"]},
            None,
            "parameter_study.yaml",
            "yaml",
            1,
            [
                call(
                    "parameter_set0:\n  parameter_1: 1\n  parameter_2: a\n"
                    "parameter_set1:\n  parameter_1: 1\n  parameter_2: b\n"
                    "parameter_set2:\n  parameter_1: 2\n  parameter_2: a\n"
                )
            ],
        ),
        "two parameter one file yaml: bools": (
            {"parameter_1": [1, 2], "parameter_2": [True, False]},
            None,
            "parameter_study.yaml",
            "yaml",
            1,
            [
                call(
                    "parameter_set0:\n  parameter_1: 1\n  parameter_2: true\n"
                    "parameter_set1:\n  parameter_1: 2\n  parameter_2: true\n"
                    "parameter_set2:\n  parameter_1: 1\n  parameter_2: false\n"
                )
            ],
        ),
    }

    @pytest.mark.parametrize(
        ("parameter_schema", "output_file_template", "output_file", "output_type", "file_count", "expected_calls"),
        write_yaml.values(),
        ids=write_yaml.keys(),
    )
    def test_write_yaml(
        self,
        parameter_schema: dict,
        output_file_template: str | None,
        output_file: str | None,
        output_type: _allowable_output_file_typing,
        file_count: int,
        expected_calls: list[unittest.mock._Call],
    ) -> None:
        with (
            patch("waves.parameter_generators.ParameterGenerator._write_meta"),
            patch("pathlib.Path.open", mock_open()) as mock_file,
            patch("xarray.Dataset.to_netcdf") as xarray_to_netcdf,
            patch("sys.stdout.write") as stdout_write,
            patch("pathlib.Path.is_file", return_value=False),
        ):
            test_write_yaml = OneAtATime(
                parameter_schema,
                output_file_template=output_file_template,
                output_file=output_file,
                output_file_type=output_type,
            )
            test_write_yaml.write()
            stdout_write.assert_not_called()
            xarray_to_netcdf.assert_not_called()
            assert mock_file.call_count == file_count
            mock_file().write.assert_has_calls(expected_calls, any_order=False)

    parameter_study_to_dict = {
        "ints": (
            {"ints": [1, 2]},
            {"parameter_set0": {"ints": 1}, "parameter_set1": {"ints": 2}},
        ),
        "floats": (
            {"floats": [10.0, 20.0]},
            {"parameter_set0": {"floats": 10.0}, "parameter_set1": {"floats": 20.0}},
        ),
        "strings": (
            {"strings": ["a", "b"]},
            {"parameter_set0": {"strings": "a"}, "parameter_set1": {"strings": "b"}},
        ),
        "bools": (
            {"bools": [False, True]},
            {"parameter_set0": {"bools": False}, "parameter_set1": {"bools": True}},
        ),
        "mixed ints, float": (
            {"ints": [1], "floats": [10.0]},
            {"parameter_set0": {"ints": 1, "floats": 10.0}},
        ),
    }

    @pytest.mark.parametrize(
        ("parameter_schema", "expected_dictionary"),
        parameter_study_to_dict.values(),
        ids=parameter_study_to_dict.keys(),
    )
    def test_parameter_study_to_dict(self, parameter_schema: dict, expected_dictionary: dict) -> None:
        """Test parameter study dictionary conversion."""
        test_parameter_study_dict = OneAtATime(parameter_schema)
        returned_dictionary = test_parameter_study_dict.parameter_study_to_dict()
        assert expected_dictionary.keys() == returned_dictionary.keys()
        assert all(isinstance(key, str) for key in returned_dictionary)
        for set_name, set_contents in expected_dictionary.items():
            assert set_contents == returned_dictionary[set_name]
            for parameter in set_contents:
                assert type(set_contents[parameter]) is type(returned_dictionary[set_name][parameter])
