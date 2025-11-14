"""Test CatenationStudy Class."""

import contextlib
import typing
import unittest
from unittest.mock import call, mock_open, patch

import numpy
import pytest
import xarray

from waves._settings import _allowable_output_file_typing, _set_coordinate_key
from waves.exceptions import SchemaValidationError
from waves.parameter_generators import CartesianProduct, CatenationStudy, CustomStudy, OneAtATime

does_not_raise = contextlib.nullcontext()


class TestCatenationStudy:
    """Class for testing CatenationStudy parameter study generator class."""

    validate_input = {
        "good schema": (
            {
                "1": (CartesianProduct, {"parameter_1": [1, 2], "parameter_2": ["a", "b"]}),
                "2": (OneAtATime, {"parameter_1": [5, 7], "parameter_2": ["x", "y"]}),
            },
            does_not_raise,
        ),
        "not a dictionary": (
            "not a dictionary",
            pytest.raises(SchemaValidationError),
        ),
        "bad schema: not a tuple": (
            {"1": "not a tuple"},
            pytest.raises(SchemaValidationError),
        ),
        "bad schema: too few entries": (
            {"1": (CartesianProduct, {"parameter_1": [1]})},
            pytest.raises(SchemaValidationError),
        ),
        "bad value entry: too few items": (
            {"1": ({"parameter_1": [1]}), "2": (CartesianProduct, {"parameter_1": [2]})},
            pytest.raises(SchemaValidationError),
        ),
        "bad generator: not a parameter generator": (
            {"1": ("not a generator", {"parameter_1": [2]}), "2": (CartesianProduct, {"parameter_1": [2]})},
            pytest.raises(SchemaValidationError),
        ),
        "bad sub-schema: not a dictionary": (
            {"1": (CartesianProduct, [[2]]), "2": (CartesianProduct, {"parameter_1": [2]})},
            pytest.raises(SchemaValidationError),
        ),
    }

    @pytest.mark.parametrize(
        ("parameter_schema", "outcome"),
        validate_input.values(),
        ids=validate_input.keys(),
    )
    def test_validate(
        self, parameter_schema: dict[str, tuple], outcome: contextlib.nullcontext | pytest.RaisesExc
    ) -> None:
        with outcome:
            # Validate is called in __init__. Do not need to call explicitly.
            test_validate = CatenationStudy(parameter_schema)
            assert isinstance(test_validate, CatenationStudy)

    generate_io = {
        "one parameter": (
            {"1": (CartesianProduct, {"parameter_1": [1]}), "2": (CartesianProduct, {"parameter_1": [2]})},
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
        "one parameter random keys": (
            {
                "study 1": (CartesianProduct, {"parameter_1": [1]}),
                "another study": (CartesianProduct, {"parameter_1": [2]}),
            },
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
        "one parameter custom template": (
            {"1": (CartesianProduct, {"parameter_1": [1]}), "2": (CartesianProduct, {"parameter_1": [2]})},
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
        "two parameter merge": (
            {
                "1": (OneAtATime, {"parameter_1": [1], "parameter_2": ["a"]}),
                "2": (OneAtATime, {"parameter_1": [2], "parameter_2": ["b"]}),
            },
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
                    "parameter_2": xarray.DataArray(
                        ["a", "b"],
                        coords={
                            _set_coordinate_key: xarray.DataArray(
                                ["parameter_set0", "parameter_set1"], dims=_set_coordinate_key
                            )
                        },
                    ),
                    "set_hash": xarray.DataArray(
                        [
                            "3b86be0b68c8a5a2a7dca07213846681",
                            "e90b9780b64cf43849b31dd6c5582015",
                        ],
                        dims=_set_coordinate_key,
                    ),
                }
            ).set_coords("set_hash"),
            {"parameter_1": numpy.int64, "parameter_2": numpy.dtype("U1")},
        ),
        "two parameter propagate": (
            {"1": (CartesianProduct, {"parameter_1": [1, 2]}), "2": (CartesianProduct, {"parameter_2": ["a", "b"]})},
            {},
            xarray.Dataset(
                {
                    "parameter_1": xarray.DataArray(
                        [1, 1, 2, 2],
                        coords={
                            _set_coordinate_key: xarray.DataArray(
                                ["parameter_set0", "parameter_set1", "parameter_set2", "parameter_set3"],
                                dims=_set_coordinate_key,
                            )
                        },
                    ),
                    "parameter_2": xarray.DataArray(
                        ["a", "b", "b", "a"],
                        coords={
                            _set_coordinate_key: xarray.DataArray(
                                ["parameter_set0", "parameter_set1", "parameter_set2", "parameter_set3"],
                                dims=_set_coordinate_key,
                            )
                        },
                    ),
                    "set_hash": xarray.DataArray(
                        [
                            "3b86be0b68c8a5a2a7dca07213846681",
                            "dd8d813de1f1b82671b694817bf10c3f",
                            "e90b9780b64cf43849b31dd6c5582015",
                            "f4f5a25089f52a0d069c83f34ce6b68b",
                        ],
                        dims=_set_coordinate_key,
                    ),
                }
            ).set_coords("set_hash"),
            {"parameter_1": numpy.int64, "parameter_2": numpy.dtype("U1")},
        ),
        "mixed generators ints and floats": (
            {"1": (CartesianProduct, {"parameter_1": [1, 2]}), "2": (OneAtATime, {"parameter_2": [3.0, 4.0]})},
            {},
            xarray.Dataset(
                {
                    "parameter_1": xarray.DataArray(
                        [1, 1, 2, 2],
                        coords={
                            _set_coordinate_key: xarray.DataArray(
                                ["parameter_set0", "parameter_set1", "parameter_set2", "parameter_set3"],
                                dims=_set_coordinate_key,
                            )
                        },
                    ),
                    "parameter_2": xarray.DataArray(
                        [4.0, 3.0, 4.0, 3.0],
                        coords={
                            _set_coordinate_key: xarray.DataArray(
                                ["parameter_set0", "parameter_set1", "parameter_set2", "parameter_set3"],
                                dims=_set_coordinate_key,
                            )
                        },
                    ),
                    "set_hash": xarray.DataArray(
                        [
                            "6a184a4ff7991572e4c8f2d096656b6b",
                            "ad4d9f0b45ec964db8f313a2b64636de",
                            "bdaabe6f836f8be5f34e39f328fa6c9d",
                            "e12bff8429a0bc549e4f029ffcb14e6b",
                        ],
                        dims=_set_coordinate_key,
                    ),
                }
            ).set_coords("set_hash"),
            {"parameter_1": numpy.int64, "parameter_2": numpy.float64},
        ),
        "mixed generators mixed parameters": (
            {
                "1": (OneAtATime, {"parameter_1": [1], "parameter_2": [3.0, 5.0]}),
                "2": (CartesianProduct, {"parameter_1": [2], "parameter_2": [4.0]}),
            },
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
                        [3.0, 5.0, 4.0],
                        coords={
                            _set_coordinate_key: xarray.DataArray(
                                ["parameter_set0", "parameter_set1", "parameter_set2"], dims=_set_coordinate_key
                            )
                        },
                    ),
                    "set_hash": xarray.DataArray(
                        [
                            "ad4d9f0b45ec964db8f313a2b64636de",
                            "7c5486efab196f73e863d2718e93e50f",
                            "bdaabe6f836f8be5f34e39f328fa6c9d",
                        ],
                        dims=_set_coordinate_key,
                    ),
                }
            ).set_coords("set_hash"),
            {"parameter_1": numpy.int64, "parameter_2": numpy.float64},
        ),
        "mixed generators three generators": (
            {
                "1": (OneAtATime, {"parameter_1": [1], "parameter_2": [3.0, 5.0]}),
                "2": (CartesianProduct, {"parameter_1": [2], "parameter_2": [4.0]}),
                "3": (OneAtATime, {"parameter_3": ["a"]}),
            },
            {},
            xarray.Dataset(
                {
                    "parameter_1": xarray.DataArray(
                        [2, 1, 1],
                        coords={
                            _set_coordinate_key: xarray.DataArray(
                                ["parameter_set0", "parameter_set1", "parameter_set2"], dims=_set_coordinate_key
                            )
                        },
                    ),
                    "parameter_2": xarray.DataArray(
                        [4.0, 3.0, 5.0],
                        coords={
                            _set_coordinate_key: xarray.DataArray(
                                ["parameter_set0", "parameter_set1", "parameter_set2"], dims=_set_coordinate_key
                            )
                        },
                    ),
                    "parameter_3": xarray.DataArray(
                        ["a", "a", "a"],
                        coords={
                            _set_coordinate_key: xarray.DataArray(
                                ["parameter_set0", "parameter_set1", "parameter_set2"], dims=_set_coordinate_key
                            )
                        },
                    ),
                    "set_hash": xarray.DataArray(
                        [
                            "1f3657a47619a055d857c49e1f48859d",
                            "4d9644f3ff9205869b5c5aef11cb5235",
                            "d7dd3ecf2cebf5e89d3e211faf2f0526",
                        ],
                        dims=_set_coordinate_key,
                    ),
                }
            ).set_coords("set_hash"),
            {"parameter_1": numpy.int64, "parameter_2": numpy.float64, "parameter_3": numpy.dtype("U1")},
        ),
        "custom studies": (
            {
                "1": (
                    CustomStudy,
                    {
                        "parameter_samples": numpy.array([[5, 1.0], [6, 2.0]], dtype=object),
                        "parameter_names": numpy.array(["parameter_1", "parameter_2"]),
                    },
                ),
                "2": (
                    CustomStudy,
                    {
                        "parameter_samples": numpy.array([[1, 3.0], [2, 4.0]], dtype=object),
                        "parameter_names": numpy.array(["parameter_1", "parameter_2"]),
                    },
                ),
            },
            {},
            xarray.Dataset(
                {
                    "parameter_1": xarray.DataArray(
                        [5, 6, 1, 2],
                        coords={
                            _set_coordinate_key: xarray.DataArray(
                                ["parameter_set0", "parameter_set1", "parameter_set2", "parameter_set3"],
                                dims=_set_coordinate_key,
                            )
                        },
                    ),
                    "parameter_2": xarray.DataArray(
                        [1.0, 2.0, 3.0, 4.0],
                        coords={
                            _set_coordinate_key: xarray.DataArray(
                                ["parameter_set0", "parameter_set1", "parameter_set2", "parameter_set3"],
                                dims=_set_coordinate_key,
                            )
                        },
                    ),
                    "set_hash": xarray.DataArray(
                        [
                            "4d31ac950f9f831fd30ce740aa877e7f",
                            "832567258fbc8675fe1c2c07e0061f42",
                            "ad4d9f0b45ec964db8f313a2b64636de",
                            "bdaabe6f836f8be5f34e39f328fa6c9d",
                        ],
                        dims=_set_coordinate_key,
                    ),
                }
            ).set_coords("set_hash"),
            {"parameter_1": numpy.int64, "parameter_2": numpy.float64},
        ),
    }

    @pytest.mark.parametrize(
        ("parameter_schema", "kwargs", "expected_dataset", "expected_types"),
        generate_io.values(),
        ids=generate_io.keys(),
    )
    def test_generate(
        self,
        parameter_schema: dict[str, tuple],
        kwargs: dict[str, typing.Any],
        expected_dataset: xarray.Dataset,
        expected_types: dict[str, type],
    ) -> None:
        test_generate = CatenationStudy(parameter_schema, **kwargs)
        xarray.testing.assert_identical(test_generate.parameter_study, expected_dataset)
        for key in test_generate.parameter_study:
            assert test_generate.parameter_study[key].dtype == expected_types[str(key)]
        # Verify that the parameter set name creation method was called
        # TODO: _set_names is an ordered object (dictionary). Fix test to compare dictionary-to-dictionary instead of
        # implied consistency according to value order.
        assert list(test_generate._set_names.values()) == list(expected_dataset[_set_coordinate_key].to_numpy())

    write_yaml = {
        "one parameter yaml": (
            {"1": (CartesianProduct, {"parameter_1": [1]}), "2": (CartesianProduct, {"parameter_1": [2]})},
            "out",
            None,
            "yaml",
            2,
            [call("parameter_1: 1\n"), call("parameter_1: 2\n")],
        ),
        "two parameter propagate yaml": (
            {"1": (CartesianProduct, {"parameter_1": [1, 2]}), "2": (CartesianProduct, {"parameter_2": ["a", "b"]})},
            "out",
            None,
            "yaml",
            4,
            [
                call("parameter_1: 1\nparameter_2: a\n"),
                call("parameter_1: 1\nparameter_2: b\n"),
                call("parameter_1: 2\nparameter_2: b\n"),
                call("parameter_1: 2\nparameter_2: a\n"),
            ],
        ),
        "mixed generators ints and floats yaml": (
            {"1": (CartesianProduct, {"parameter_1": [1, 2]}), "2": (OneAtATime, {"parameter_2": [3.0, 4.0]})},
            "out",
            None,
            "yaml",
            4,
            [
                call("parameter_1: 1\nparameter_2: 4.0\n"),
                call("parameter_1: 1\nparameter_2: 3.0\n"),
                call("parameter_1: 2\nparameter_2: 4.0\n"),
                call("parameter_1: 2\nparameter_2: 3.0\n"),
            ],
        ),
        "two parameter propagate yaml: bools and ints": (
            {"1": (CartesianProduct, {"parameter_1": [1, 2]}), "2": (CartesianProduct, {"parameter_2": [True, False]})},
            "out",
            None,
            "yaml",
            4,
            [
                call("parameter_1: 2\nparameter_2: true\n"),
                call("parameter_1: 1\nparameter_2: true\n"),
                call("parameter_1: 2\nparameter_2: false\n"),
                call("parameter_1: 1\nparameter_2: false\n"),
            ],
        ),
        "one parameter one file yaml": (
            {"1": (CartesianProduct, {"parameter_1": [1]}), "2": (CartesianProduct, {"parameter_1": [2]})},
            None,
            "parameter_study.yaml",
            "yaml",
            1,
            [call("parameter_set0:\n  parameter_1: 1\nparameter_set1:\n  parameter_1: 2\n")],
        ),
        "two parameter propagate one file yaml": (
            {"1": (CartesianProduct, {"parameter_1": [1, 2]}), "2": (CartesianProduct, {"parameter_2": ["a", "b"]})},
            None,
            "parameter_study.yaml",
            "yaml",
            1,
            [
                call(
                    "parameter_set0:\n  parameter_1: 1\n  parameter_2: a\n"
                    "parameter_set1:\n  parameter_1: 1\n  parameter_2: b\n"
                    "parameter_set2:\n  parameter_1: 2\n  parameter_2: b\n"
                    "parameter_set3:\n  parameter_1: 2\n  parameter_2: a\n"
                )
            ],
        ),
        "two parameter one file yaml: bools and ints": (
            {"1": (CartesianProduct, {"parameter_1": [1, 2]}), "2": (CartesianProduct, {"parameter_2": [True, False]})},
            None,
            "parameter_study.yaml",
            "yaml",
            1,
            [
                call(
                    "parameter_set0:\n  parameter_1: 2\n  parameter_2: true\n"
                    "parameter_set1:\n  parameter_1: 1\n  parameter_2: true\n"
                    "parameter_set2:\n  parameter_1: 2\n  parameter_2: false\n"
                    "parameter_set3:\n  parameter_1: 1\n  parameter_2: false\n"
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
        parameter_schema: dict[str, tuple],
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
            test_write_yaml = CatenationStudy(
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
            {"1": (CartesianProduct, {"ints": [1]}), "2": (CartesianProduct, {"ints": [2]})},
            {"parameter_set0": {"ints": 1}, "parameter_set1": {"ints": 2}},
        ),
        "floats": (
            {"1": (OneAtATime, {"floats": [10.0]}), "2": (OneAtATime, {"floats": [20.0]})},
            {"parameter_set0": {"floats": 10.0}, "parameter_set1": {"floats": 20.0}},
        ),
        "strings": (
            {"1": (CartesianProduct, {"strings": ["a"]}), "2": (CartesianProduct, {"strings": ["b"]})},
            {"parameter_set0": {"strings": "a"}, "parameter_set1": {"strings": "b"}},
        ),
        "bools": (
            {"1": (CartesianProduct, {"bools": [False]}), "2": (CartesianProduct, {"bools": [True]})},
            {"parameter_set0": {"bools": False}, "parameter_set1": {"bools": True}},
        ),
        "mixed ints, float": (
            {"1": (OneAtATime, {"ints": [1]}), "2": (CartesianProduct, {"floats": [10.0]})},
            {"parameter_set0": {"ints": 1, "floats": 10.0}},
        ),
    }

    previous_parameter_study_inputs = {
        "one parameter cartesian product": (
            CartesianProduct({"parameter_1": [1, 2]}).parameter_study,
            {"1": (CartesianProduct, {"parameter_1": [3]}), "2": (CartesianProduct, {"parameter_1": [4]})},
            CartesianProduct({"parameter_1": [1, 2, 3, 4]}).parameter_study,
        ),
        "two shared parameters cartesian product": (
            CartesianProduct({"parameter_1": [1], "parameter_2": [3.0]}).parameter_study,
            {"1": (CartesianProduct, {"parameter_1": [5]}), "2": (CartesianProduct, {"parameter_2": [7.0]})},
            xarray.Dataset(
                {
                    "parameter_1": xarray.DataArray(
                        [1, 5],
                        coords={
                            _set_coordinate_key: xarray.DataArray(
                                ["parameter_set0", "parameter_set1"], dims=_set_coordinate_key
                            )
                        },
                    ),
                    "parameter_2": xarray.DataArray(
                        [3.0, 7.0],
                        coords={
                            _set_coordinate_key: xarray.DataArray(
                                ["parameter_set0", "parameter_set1"], dims=_set_coordinate_key
                            )
                        },
                    ),
                    "set_hash": xarray.DataArray(
                        ["ad4d9f0b45ec964db8f313a2b64636de", "50055f40b5328726c8261ad0dbc1e644"],
                        dims=_set_coordinate_key,
                    ),
                }
            ).set_coords("set_hash").sortby("set_hash")
        ),
    }

    @pytest.mark.parametrize(
        (
            "mock_previous_study",
            "new_parameter_schema",
            "expected_dataset",
        ),
        previous_parameter_study_inputs.values(),
        ids=previous_parameter_study_inputs.keys(),
    )
    def test_previous_parameter_study(
        self,
        mock_previous_study: xarray.Dataset,
        new_parameter_schema: dict[str, tuple],
        expected_dataset: xarray.Dataset,
    ) -> None:
        with (
            patch("waves.parameter_generators._open_parameter_study", return_value=mock_previous_study),
            patch("pathlib.Path.is_file", return_value=True),
        ):
            returned_dataset = CatenationStudy(new_parameter_schema, previous_parameter_study="mock").parameter_study
            xarray.testing.assert_identical(expected_dataset, returned_dataset)

    @pytest.mark.parametrize(
        ("parameter_schema", "expected_dictionary"),
        parameter_study_to_dict.values(),
        ids=parameter_study_to_dict.keys(),
    )
    def test_parameter_study_to_dict(self, parameter_schema: dict[str, tuple], expected_dictionary: dict) -> None:
        """Test parameter study dictionary conversion."""
        test_parameter_study_dict = CatenationStudy(parameter_schema)
        returned_dictionary = test_parameter_study_dict.parameter_study_to_dict()
        assert expected_dictionary.keys() == returned_dictionary.keys()
        assert all(isinstance(key, str) for key in returned_dictionary)
        for set_name, set_contents in expected_dictionary.items():
            assert set_contents == returned_dictionary[set_name]
            for parameter in set_contents:
                assert type(set_contents[parameter]) is type(returned_dictionary[set_name][parameter])
