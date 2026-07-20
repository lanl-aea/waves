"""Test CustomStudy Class."""

import contextlib
from unittest.mock import call, mock_open, patch

import numpy
import pytest
import xarray

from waves._settings import _allowable_output_file_typing, _hash_coordinate_key, _set_coordinate_key
from waves._tests.common import merge_samplers
from waves.exceptions import SchemaValidationError
from waves.parameter_generators import CustomStudy

does_not_raise = contextlib.nullcontext()


class TestCustomStudy:
    """Class for testing CustomStudy parameter study generator class."""

    validate_input = {
        "good schema list of lists": (
            {"parameter_names": ["a", "b"], "parameter_samples": [[1, 2.0], [3, 4.5]]},
            does_not_raise,
        ),
        "good schema numpy array": (
            {"parameter_names": ["a", "b"], "parameter_samples": numpy.array([[1, 2.0], [3, 4.5]])},
            does_not_raise,
        ),
        "mixed length strings": (
            {
                "parameter_names": ["parameter_1"],
                "parameter_samples": numpy.array([["one"], ["two"], ["many"]], dtype=object),
            },
            does_not_raise,
        ),
        "not a dict": (
            "not a dict",
            pytest.raises(SchemaValidationError),
        ),
        "bad schema no names": (
            {"parameter_samples": numpy.array([[1, 2.0], [3, 4.5]], dtype=object)},
            pytest.raises(SchemaValidationError),
        ),
        "bad schema no values": (
            {"parameter_names": ["a", "b"]},
            pytest.raises(SchemaValidationError),
        ),
        "bad schema dimension": (
            {"parameter_names": ["a", "b"], "parameter_samples": numpy.array([1, 2.0], dtype=object)},
            pytest.raises(SchemaValidationError),
        ),
        "bad schema shape": (
            {"parameter_names": ["a", "b", "c"], "parameter_samples": numpy.array([[1, 2.0], [3, 4.5]], dtype=object)},
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
            test_validate = CustomStudy(parameter_schema)
            assert isinstance(test_validate, CustomStudy)

    test_generate_cases = {
        "mixed length strings": (
            {
                "parameter_names": ["parameter_1"],
                "parameter_samples": numpy.array([["one"], ["two"], ["many"]], dtype=object),
            },
            xarray.Dataset(
                {
                    "parameter_1": xarray.DataArray(
                        ["many", "one", "two"],
                        coords={
                            _set_coordinate_key: xarray.DataArray(
                                ["parameter_set0", "parameter_set1", "parameter_set2"], dims=_set_coordinate_key
                            )
                        },
                    ),
                    "set_hash": xarray.DataArray(
                        [
                            "1780094887590cdd640fcd69c04fc323",
                            "489dc5ad052f9d061c2b85fcf217072d",
                            "5a1506e07dcd8f7126021ee5aec04afc",
                        ],
                        dims=_set_coordinate_key,
                    ),
                }
            ).set_coords("set_hash"),
            {"parameter_1": numpy.dtype("U4")},
        ),
        "one_parameter": (
            {"parameter_names": ["parameter_1"], "parameter_samples": numpy.array([[1], [2]], dtype=object)},
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
            {
                "parameter_names": ["parameter_1", "parameter_2"],
                "parameter_samples": numpy.array([[1, 10.0], [2, 20.0]], dtype=object),
            },
            xarray.Dataset(
                {
                    "parameter_1": xarray.DataArray(
                        [1, 2],
                        coords={
                            _set_coordinate_key: xarray.DataArray(
                                ["parameter_set0", "parameter_set1"],
                                dims=_set_coordinate_key,
                            )
                        },
                    ),
                    "parameter_2": xarray.DataArray(
                        [10.0, 20.0],
                        coords={
                            _set_coordinate_key: xarray.DataArray(
                                ["parameter_set0", "parameter_set1"],
                                dims=_set_coordinate_key,
                            )
                        },
                    ),
                    "set_hash": xarray.DataArray(
                        [
                            "ad786a85fdef9bb1f2fc7a915e58446e",
                            "d3d9a8defeae15fd99bb31fbc4cbf2bf",
                        ],
                        dims=_set_coordinate_key,
                    ),
                }
            ).set_coords("set_hash"),
            {"parameter_1": numpy.int64, "parameter_2": numpy.float64},
        ),
        "all numpy typing": (
            {
                "parameter_names": [
                    "parameter_1",
                    "parameter_2",
                    "parameter_3",
                    "parameter_4",
                    "parameter_5",
                    "parameter_6",
                ],
                "parameter_samples": numpy.array(
                    [
                        [
                            numpy.int16(1),
                            numpy.int32(-1),
                            numpy.int64(-10),
                            numpy.float64(1.23),
                            numpy.bool_(True),
                            numpy.str_("zero"),
                        ],
                        [
                            numpy.int16(1),
                            numpy.int32(-1),
                            numpy.int64(-10),
                            numpy.float64(1.23),
                            numpy.bool_(True),
                            numpy.str_("one"),
                        ],
                    ],
                    dtype=object,
                ),
            },
            # Same expected output for numpy typing, mixed typing, and built-in typing
            xarray.Dataset(
                {
                    "parameter_1": xarray.DataArray(
                        [1, 1],
                        coords={
                            _set_coordinate_key: xarray.DataArray(
                                ["parameter_set0", "parameter_set1"],
                                dims=_set_coordinate_key,
                            )
                        },
                    ),
                    "parameter_2": xarray.DataArray(
                        [-1, -1],
                        coords={
                            _set_coordinate_key: xarray.DataArray(
                                ["parameter_set0", "parameter_set1"],
                                dims=_set_coordinate_key,
                            )
                        },
                    ),
                    "parameter_3": xarray.DataArray(
                        [-10, -10],
                        coords={
                            _set_coordinate_key: xarray.DataArray(
                                ["parameter_set0", "parameter_set1"],
                                dims=_set_coordinate_key,
                            )
                        },
                    ),
                    "parameter_4": xarray.DataArray(
                        [1.23, 1.23],
                        coords={
                            _set_coordinate_key: xarray.DataArray(
                                ["parameter_set0", "parameter_set1"],
                                dims=_set_coordinate_key,
                            )
                        },
                    ),
                    "parameter_5": xarray.DataArray(
                        [True, True],
                        coords={
                            _set_coordinate_key: xarray.DataArray(
                                ["parameter_set0", "parameter_set1"],
                                dims=_set_coordinate_key,
                            )
                        },
                    ),
                    "parameter_6": xarray.DataArray(
                        ["zero", "one"],
                        coords={
                            _set_coordinate_key: xarray.DataArray(
                                ["parameter_set0", "parameter_set1"],
                                dims=_set_coordinate_key,
                            )
                        },
                    ),
                    "set_hash": xarray.DataArray(
                        ["501f23f42f3aabd912e1b70072701434", "c88259b8113aeb6880829e4c092dd445"],
                        dims=_set_coordinate_key,
                    ),
                }
            ).set_coords("set_hash"),
            {
                "parameter_1": numpy.int64,
                "parameter_2": numpy.int64,
                "parameter_3": numpy.int64,
                "parameter_4": numpy.float64,
                "parameter_5": bool,
                "parameter_6": numpy.dtype("U4"),
            },
        ),
        "mixed numpy typing": (
            {
                "parameter_names": [
                    "parameter_1",
                    "parameter_2",
                    "parameter_3",
                    "parameter_4",
                    "parameter_5",
                    "parameter_6",
                ],
                "parameter_samples": numpy.array(
                    [
                        [1, numpy.int32(-1), -10, numpy.float64(1.23), numpy.bool_(True), "zero"],
                        [1, numpy.int32(-1), -10, numpy.float64(1.23), numpy.bool_(True), "one"],
                    ],
                    dtype=object,
                ),
            },
            xarray.Dataset(
                {
                    "parameter_1": xarray.DataArray(
                        [1, 1],
                        coords={
                            _set_coordinate_key: xarray.DataArray(
                                ["parameter_set0", "parameter_set1"],
                                dims=_set_coordinate_key,
                            )
                        },
                    ),
                    "parameter_2": xarray.DataArray(
                        [-1, -1],
                        coords={
                            _set_coordinate_key: xarray.DataArray(
                                ["parameter_set0", "parameter_set1"],
                                dims=_set_coordinate_key,
                            )
                        },
                    ),
                    "parameter_3": xarray.DataArray(
                        [-10, -10],
                        coords={
                            _set_coordinate_key: xarray.DataArray(
                                ["parameter_set0", "parameter_set1"],
                                dims=_set_coordinate_key,
                            )
                        },
                    ),
                    "parameter_4": xarray.DataArray(
                        [1.23, 1.23],
                        coords={
                            _set_coordinate_key: xarray.DataArray(
                                ["parameter_set0", "parameter_set1"],
                                dims=_set_coordinate_key,
                            )
                        },
                    ),
                    "parameter_5": xarray.DataArray(
                        [True, True],
                        coords={
                            _set_coordinate_key: xarray.DataArray(
                                ["parameter_set0", "parameter_set1"],
                                dims=_set_coordinate_key,
                            )
                        },
                    ),
                    "parameter_6": xarray.DataArray(
                        ["zero", "one"],
                        coords={
                            _set_coordinate_key: xarray.DataArray(
                                ["parameter_set0", "parameter_set1"],
                                dims=_set_coordinate_key,
                            )
                        },
                    ),
                    "set_hash": xarray.DataArray(
                        ["501f23f42f3aabd912e1b70072701434", "c88259b8113aeb6880829e4c092dd445"],
                        dims=_set_coordinate_key,
                    ),
                }
            ).set_coords("set_hash"),
            {
                "parameter_1": numpy.int64,
                "parameter_2": numpy.int64,
                "parameter_3": numpy.int64,
                "parameter_4": numpy.float64,
                "parameter_5": bool,
                "parameter_6": numpy.dtype("U4"),
            },
        ),
        "all built-in typing": (
            {
                "parameter_names": [
                    "parameter_1",
                    "parameter_2",
                    "parameter_3",
                    "parameter_4",
                    "parameter_5",
                    "parameter_6",
                ],
                "parameter_samples": numpy.array(
                    [
                        [1, -1, -10, 1.23, True, "zero"],
                        [1, -1, -10, 1.23, True, "one"],
                    ],
                    dtype=object,
                ),
            },
            xarray.Dataset(
                {
                    "parameter_1": xarray.DataArray(
                        [1, 1],
                        coords={
                            _set_coordinate_key: xarray.DataArray(
                                ["parameter_set0", "parameter_set1"],
                                dims=_set_coordinate_key,
                            )
                        },
                    ),
                    "parameter_2": xarray.DataArray(
                        [-1, -1],
                        coords={
                            _set_coordinate_key: xarray.DataArray(
                                ["parameter_set0", "parameter_set1"],
                                dims=_set_coordinate_key,
                            )
                        },
                    ),
                    "parameter_3": xarray.DataArray(
                        [-10, -10],
                        coords={
                            _set_coordinate_key: xarray.DataArray(
                                ["parameter_set0", "parameter_set1"],
                                dims=_set_coordinate_key,
                            )
                        },
                    ),
                    "parameter_4": xarray.DataArray(
                        [1.23, 1.23],
                        coords={
                            _set_coordinate_key: xarray.DataArray(
                                ["parameter_set0", "parameter_set1"],
                                dims=_set_coordinate_key,
                            )
                        },
                    ),
                    "parameter_5": xarray.DataArray(
                        [True, True],
                        coords={
                            _set_coordinate_key: xarray.DataArray(
                                ["parameter_set0", "parameter_set1"],
                                dims=_set_coordinate_key,
                            )
                        },
                    ),
                    "parameter_6": xarray.DataArray(
                        ["zero", "one"],
                        coords={
                            _set_coordinate_key: xarray.DataArray(
                                ["parameter_set0", "parameter_set1"],
                                dims=_set_coordinate_key,
                            )
                        },
                    ),
                    "set_hash": xarray.DataArray(
                        ["501f23f42f3aabd912e1b70072701434", "c88259b8113aeb6880829e4c092dd445"],
                        dims=_set_coordinate_key,
                    ),
                }
            ).set_coords("set_hash"),
            {
                "parameter_1": numpy.int64,
                "parameter_2": numpy.int64,
                "parameter_3": numpy.int64,
                "parameter_4": numpy.float64,
                "parameter_5": bool,
                "parameter_6": numpy.dtype("U4"),
            },
        ),
    }

    @pytest.mark.parametrize(
        ("parameter_schema", "expected_dataset", "expected_types"),
        test_generate_cases.values(),
        ids=test_generate_cases.keys(),
    )
    def test_generate(
        self, parameter_schema: dict, expected_dataset: xarray.Dataset, expected_types: dict[str, type]
    ) -> None:
        test_generate = CustomStudy(parameter_schema)
        xarray.testing.assert_identical(test_generate.parameter_study, expected_dataset)
        for key in test_generate.parameter_study:
            assert test_generate.parameter_study[key].dtype == expected_types[str(key)]
        # Verify that the parameter set name creation method was called
        # TODO: _set_names is an ordered object (dictionary). Fix test to compare dictionary-to-dictionary instead of
        # implied consistency according to value order.
        assert list(test_generate._set_names.values()) == list(expected_dataset[_set_coordinate_key].to_numpy())

    merge_test = {
        "mixed length strings": (
            {"parameter_names": ["parameter_1"], "parameter_samples": numpy.array([["one"]], dtype=object)},
            {"parameter_names": ["parameter_1"], "parameter_samples": numpy.array([["many"]], dtype=object)},
            numpy.array([["many"], ["one"]], dtype=object),
            {"parameter_1": numpy.dtype("U4")},
        ),
        "single set unchanged": (
            {"parameter_names": ["ints"], "parameter_samples": numpy.array([[1]], dtype=object)},
            {"parameter_names": ["ints"], "parameter_samples": numpy.array([[1]], dtype=object)},
            # Ordered by md5 hash during Xarray merge operation. New tests must verify hash ordering.
            numpy.array([[1]], dtype=object),
            {"ints": numpy.int64},
        ),
        "single set and new set": (
            {"parameter_names": ["ints"], "parameter_samples": numpy.array([[1]], dtype=object)},
            {"parameter_names": ["ints"], "parameter_samples": numpy.array([[2]], dtype=object)},
            # Ordered by md5 hash during Xarray merge operation. New tests must verify hash ordering.
            numpy.array([[1], [2]], dtype=object),
            {"ints": numpy.int64},
        ),
        "new set": (
            {
                "parameter_names": ["ints", "floats", "strings"],
                "parameter_samples": numpy.array([[1, 10.1, "a"], [2, 20.2, "b"]], dtype=object),
            },
            {
                "parameter_names": ["ints", "floats", "strings"],
                "parameter_samples": numpy.array([[1, 10.1, "a"], [3, 30.3, "c"], [2, 20.2, "b"]], dtype=object),
            },
            # Ordered by md5 hash during Xarray merge operation. New tests must verify hash ordering.
            numpy.array(
                [
                    [3, 30.3, "c"],
                    [1, 10.1, "a"],
                    [2, 20.2, "b"],
                ],
                dtype=object,
            ),
            {"ints": numpy.int64, "floats": numpy.float64, "strings": numpy.dtype("U1")},
        ),
        "unchanged sets": (
            {
                "parameter_names": ["ints", "floats", "strings"],
                "parameter_samples": numpy.array([[1, 10.1, "a"], [2, 20.2, "b"]], dtype=object),
            },
            {
                "parameter_names": ["ints", "floats", "strings"],
                "parameter_samples": numpy.array([[1, 10.1, "a"], [2, 20.2, "b"]], dtype=object),
            },
            # Ordered by md5 hash during Xarray merge operation. New tests must verify hash ordering.
            numpy.array(
                [[1, 10.1, "a"], [2, 20.2, "b"]],
                dtype=object,
            ),
            {"ints": numpy.int64, "floats": numpy.float64, "strings": numpy.dtype("U1")},
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
            test_merge1, test_merge2 = merge_samplers(CustomStudy, first_schema, second_schema, {})
            generate_array = test_merge2._samples
            assert numpy.all(generate_array == expected_array)
            # Check for type preservation
            for key in test_merge2.parameter_study:
                assert test_merge2.parameter_study[key].dtype == expected_types[str(key)]
            # Check for consistent hash-parameter set relationships
            for set_name, parameters in test_merge1.parameter_study.groupby(_set_coordinate_key):
                assert parameters == test_merge2.parameter_study.sel({_set_coordinate_key: set_name})
            # Self-consistency checks
            assert (
                list(test_merge2._set_names.values())
                == test_merge2.parameter_study[_set_coordinate_key].values.tolist()
            )
            assert test_merge2._set_hashes == test_merge2.parameter_study[_hash_coordinate_key].values.tolist()
