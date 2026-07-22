"""Test CartesianProduct Class."""

import contextlib
from unittest.mock import patch

import numpy
import pytest
import xarray

from waves import parameter_generators
from waves._settings import _set_coordinate_key
from waves._tests.common import consistent_hash_parameter_check, merge_samplers, self_consistency_checks
from waves.exceptions import SchemaValidationError
from waves.parameter_generators import CartesianProduct

does_not_raise = contextlib.nullcontext()


class TestCartesianProduct:
    """Class for testing CartesianProduct parameter study generator class."""

    validate_input = {
        "good schema": (
            {"parameter_1": [1], "parameter_2": (2,), "parameter_3": {3, 4}},
            does_not_raise,
        ),
        "mixed length strings": (
            {"parameter_1": ["one", "two", "many"]},
            does_not_raise,
        ),
        "scaler valued parameter int": (
            {"parameter_1": 1},
            does_not_raise,
        ),
        "scaler valued parameter str": (
            {"parameter_1": "one"},
            does_not_raise,
        ),
        "test all scalars valued parameters": (
            {"parameter_1": 1, "parameter_2": "two", "parameter_3": True},
            does_not_raise,
        ),
        "test mixed scalars and lists": (
            {"parameter_1": 1, "parameter_2": [1, 2]},
            does_not_raise,
        ),
        "numpy scalar type": (
            {"parameter_1": numpy.int64(42)},
            does_not_raise,
        ),
        "not a dict": (
            "not a dict",
            pytest.raises(SchemaValidationError, match=r"parameter_schema must be a dictionary"),
        ),
        "bad schema dict": (
            {"parameter_1": {"thing1": 1}},
            pytest.raises(
                SchemaValidationError,
                match=r"Parmeters must be a sequence of scalar values or a supported scalar value"
            ),
        ),
        "bad schema empty": (
            {"parameter_1": []},
            pytest.raises(
                SchemaValidationError,
                match=r"Parmeters must be a sequence of scalar values or a supported scalar value"
            ),
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
            test_validate = CartesianProduct(parameter_schema)
            assert isinstance(test_validate, CartesianProduct)

    generate_io = {
        "mixed length strings": (
            {"parameter_1": ["one", "two", "many"]},
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
            {"parameter_1": [1, 2]},
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
        "ints and floats": (
            {"parameter_1": [1, 2], "parameter_2": [3.0, 4.0]},
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
        "ints and bools": (
            {"parameter_1": [1, 2], "parameter_2": [True, False]},
            xarray.Dataset(
                {
                    "parameter_1": xarray.DataArray(
                        [2, 1, 2, 1],
                        coords={
                            _set_coordinate_key: xarray.DataArray(
                                ["parameter_set0", "parameter_set1", "parameter_set2", "parameter_set3"],
                                dims=_set_coordinate_key,
                            )
                        },
                    ),
                    "parameter_2": xarray.DataArray(
                        [True, True, False, False],
                        coords={
                            _set_coordinate_key: xarray.DataArray(
                                ["parameter_set0", "parameter_set1", "parameter_set2", "parameter_set3"],
                                dims=_set_coordinate_key,
                            )
                        },
                    ),
                    "set_hash": xarray.DataArray(
                        [
                            "6b483a95c061cff58194545c7d2b548c",
                            "d65bccd02f05b0419dc634e643418e62",
                            "df1ac82da14f4f1fd9d73159bb64a717",
                            "fad886b3a9a58a623ba80745c094f53f",
                        ],
                        dims=_set_coordinate_key,
                    ),
                }
            ).set_coords("set_hash"),
            {"parameter_1": numpy.int64, "parameter_2": bool},
        ),
        "float and bool": (
            {"parameter_1": [1.0, 2.0], "parameter_2": [True, False]},
            xarray.Dataset(
                {
                    "parameter_1": xarray.DataArray(
                        [1.0, 2.0, 1.0, 2.0],
                        coords={
                            _set_coordinate_key: xarray.DataArray(
                                ["parameter_set0", "parameter_set1", "parameter_set2", "parameter_set3"],
                                dims=_set_coordinate_key,
                            )
                        },
                    ),
                    "parameter_2": xarray.DataArray(
                        [False, True, True, False],
                        coords={
                            _set_coordinate_key: xarray.DataArray(
                                ["parameter_set0", "parameter_set1", "parameter_set2", "parameter_set3"],
                                dims=_set_coordinate_key,
                            )
                        },
                    ),
                    "set_hash": xarray.DataArray(
                        [
                            "7052493af57e86c7b9aa704f3056c8ad",
                            "8612daddcbbd616b8b426b39e9b47fef",
                            "92988d818731c8f420bfb0b14180c3b5",
                            "d269ea65e04db7050191b6ecfdb3bba7",
                        ],
                        dims=_set_coordinate_key,
                    ),
                }
            ).set_coords("set_hash"),
            {"parameter_1": numpy.float64, "parameter_2": bool},
        ),
        "all numpy typing": (
            {
                "parameter_1": [numpy.int16(1)],
                "parameter_2": [numpy.int32(-1)],
                "parameter_3": [numpy.int64(-10)],
                "parameter_4": [numpy.float64(1.23)],
                "parameter_5": [numpy.bool_(True)],
                "parameter_6": [numpy.str_("zero"), numpy.str_("one")],
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
                "parameter_1": [1],
                "parameter_2": [numpy.int32(-1)],
                "parameter_3": [-10],
                "parameter_4": [numpy.float64(1.23)],
                "parameter_5": [numpy.bool_(True)],
                "parameter_6": ["zero", "one"],
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
                "parameter_1": [1],
                "parameter_2": [-1],
                "parameter_3": [-10],
                "parameter_4": [1.23],
                "parameter_5": [True],
                "parameter_6": ["zero", "one"],
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
        "single scalar int": (
            {"parameter_1": 42},
            xarray.Dataset(
                {
                    "parameter_1": xarray.DataArray(
                        [42],
                        coords={
                            _set_coordinate_key: xarray.DataArray(
                                ["parameter_set0"],
                                dims=_set_coordinate_key,
                            )
                        },
                    ),
                    "set_hash": xarray.DataArray(
                        ["8661a78b1bbef2ce06c8f27f0030ae39"],
                        dims=_set_coordinate_key,
                    ),
                }
            ).set_coords("set_hash"),
            {"parameter_1": numpy.int64},
        ),
        "single scalar float": (
            {"parameter_1": 3.14},
            xarray.Dataset(
                {
                    "parameter_1": xarray.DataArray(
                        [3.14],
                        coords={
                            _set_coordinate_key: xarray.DataArray(
                                ["parameter_set0"],
                                dims=_set_coordinate_key,
                            )
                        },
                    ),
                    "set_hash": xarray.DataArray(
                        ["29ca606c0ab080d234d56bd01cda05ef"],
                        dims=_set_coordinate_key,
                    ),
                }
            ).set_coords("set_hash"),
            {"parameter_1": numpy.float64},
        ),
        "single scalar string": (
            {"parameter_1": "hello"},
            xarray.Dataset(
                {
                    "parameter_1": xarray.DataArray(
                        ["hello"],
                        coords={
                            _set_coordinate_key: xarray.DataArray(
                                ["parameter_set0"],
                                dims=_set_coordinate_key,
                            )
                        },
                    ),
                    "set_hash": xarray.DataArray(
                        ["f638f65386fd4b7d6558a27cd5b1654e"],
                        dims=_set_coordinate_key,
                    ),
                }
            ).set_coords("set_hash"),
            {"parameter_1": numpy.dtype("U5")},
        ),
        "single scalar bool": (
            {"parameter_1": True},
            xarray.Dataset(
                {
                    "parameter_1": xarray.DataArray(
                        [True],
                        coords={
                            _set_coordinate_key: xarray.DataArray(
                                ["parameter_set0"],
                                dims=_set_coordinate_key,
                            )
                        },
                    ),
                    "set_hash": xarray.DataArray(
                        ["6c2fb5097da66f7bb3795420b802986e"],
                        dims=_set_coordinate_key,
                    ),
                }
            ).set_coords("set_hash"),
            {"parameter_1": bool},
        ),
        "multiple scalar parameters": (
            {"parameter_1": 10, "parameter_2": 2.5, "parameter_3": "test"},
            xarray.Dataset(
                {
                    "parameter_1": xarray.DataArray(
                        [10],
                        coords={
                            _set_coordinate_key: xarray.DataArray(
                                ["parameter_set0"],
                                dims=_set_coordinate_key,
                            )
                        },
                    ),
                    "parameter_2": xarray.DataArray(
                        [2.5],
                        coords={
                            _set_coordinate_key: xarray.DataArray(
                                ["parameter_set0"],
                                dims=_set_coordinate_key,
                            )
                        },
                    ),
                    "parameter_3": xarray.DataArray(
                        ["test"],
                        coords={
                            _set_coordinate_key: xarray.DataArray(
                                ["parameter_set0"],
                                dims=_set_coordinate_key,
                            )
                        },
                    ),
                    "set_hash": xarray.DataArray(
                        ["48713683c8c26aa9b921b548ca56f201"],
                        dims=_set_coordinate_key,
                    ),
                }
            ).set_coords("set_hash"),
            {"parameter_1": numpy.int64, "parameter_2": numpy.float64, "parameter_3": numpy.dtype("U4")},
        ),
        "scalar int with list": (
            {"parameter_1": 5, "parameter_2": [1, 2]},
            xarray.Dataset(
                {
                    "parameter_1": xarray.DataArray(
                        [5, 5],
                        coords={
                            _set_coordinate_key: xarray.DataArray(
                                ["parameter_set0", "parameter_set1"],
                                dims=_set_coordinate_key,
                            )
                        },
                    ),
                    "parameter_2": xarray.DataArray(
                        [2, 1],
                        coords={
                            _set_coordinate_key: xarray.DataArray(
                                ["parameter_set0", "parameter_set1"],
                                dims=_set_coordinate_key,
                            )
                        },
                    ),
                    "set_hash": xarray.DataArray(
                        ["2fb2d42b512e7843c1aab96b2990ce6b", "bba66d84c35e92cd2dbd9a5cda168997"],
                        dims=_set_coordinate_key,
                    ),
                }
            ).set_coords("set_hash"),
            {"parameter_1": numpy.int64, "parameter_2": numpy.int64},
        ),
        "multiple scalars with list cartesian product": (
            {"parameter_1": 100, "parameter_2": "fixed", "parameter_3": [10.0, 20.0]},
            xarray.Dataset(
                {
                    "parameter_1": xarray.DataArray(
                        [100, 100],
                        coords={
                            _set_coordinate_key: xarray.DataArray(
                                ["parameter_set0", "parameter_set1"],
                                dims=_set_coordinate_key,
                            )
                        },
                    ),
                    "parameter_2": xarray.DataArray(
                        ["fixed", "fixed"],
                        coords={
                            _set_coordinate_key: xarray.DataArray(
                                ["parameter_set0", "parameter_set1"],
                                dims=_set_coordinate_key,
                            )
                        },
                    ),
                    "parameter_3": xarray.DataArray(
                        [10.0, 20.0],
                        coords={
                            _set_coordinate_key: xarray.DataArray(
                                ["parameter_set0", "parameter_set1"],
                                dims=_set_coordinate_key,
                            )
                        },
                    ),
                    "set_hash": xarray.DataArray(
                        ["3e0a4ecb94fcecc080b64a788205c45e", "58d6dfc2839ab3e7822d1cf461f90a90"],
                        dims=_set_coordinate_key,
                    ),
                }
            ).set_coords("set_hash"),
            {"parameter_1": numpy.int64, "parameter_2": numpy.dtype("U5"), "parameter_3": numpy.float64},
        ),
        "scalar with two lists cartesian product": (
            {"parameter_1": 7, "parameter_2": ["a", "b"], "parameter_3": [1.0, 2.0]},
            xarray.Dataset(
                {
                    "parameter_1": xarray.DataArray(
                        [7, 7, 7, 7],
                        coords={
                            _set_coordinate_key: xarray.DataArray(
                                ["parameter_set0", "parameter_set1", "parameter_set2", "parameter_set3"],
                                dims=_set_coordinate_key,
                            )
                        },
                    ),
                    "parameter_2": xarray.DataArray(
                        ["a", "a", "b", "b"],
                        coords={
                            _set_coordinate_key: xarray.DataArray(
                                ["parameter_set0", "parameter_set1", "parameter_set2", "parameter_set3"],
                                dims=_set_coordinate_key,
                            )
                        },
                    ),
                    "parameter_3": xarray.DataArray(
                        [2.0, 1.0, 1.0, 2.0],
                        coords={
                            _set_coordinate_key: xarray.DataArray(
                                ["parameter_set0", "parameter_set1", "parameter_set2", "parameter_set3"],
                                dims=_set_coordinate_key,
                            )
                        },
                    ),
                    "set_hash": xarray.DataArray(
                        [
                            "20cdbecd1293e56c55d5f8a0b9374f51",
                            "4ed5c5fece70ffd5c18b67974499addc",
                            "70989af2e36024e93ebe56125ea6b695",
                            "7b013ec31b0e2822e6a93e84251f4468",
                        ],
                        dims=_set_coordinate_key,
                    ),
                }
            ).set_coords("set_hash"),
            {"parameter_1": numpy.int64, "parameter_2": numpy.dtype("U1"), "parameter_3": numpy.float64},
        ),
    }

    @pytest.mark.parametrize(
        ("parameter_schema", "expected_dataset", "expected_types"),
        generate_io.values(),
        ids=generate_io.keys(),
    )
    def test_generate(
        self, parameter_schema: dict, expected_dataset: xarray.Dataset, expected_types: dict[str, type]
    ) -> None:
        test_generate = CartesianProduct(parameter_schema)
        xarray.testing.assert_identical(test_generate.parameter_study, expected_dataset)
        for key in test_generate.parameter_study:
            assert test_generate.parameter_study[key].dtype == expected_types[str(key)]
        # Verify that the parameter set name creation method was called
        # TODO: _set_names is an ordered object (dictionary). Fix test to compare dictionary-to-dictionary instead of
        # implied consistency according to value order.
        assert list(test_generate._set_names.values()) == list(expected_dataset[_set_coordinate_key].to_numpy())

    @pytest.mark.parametrize(
        ("parameter_schema", "expected_array", "expected_types"),
        generate_io.values(),
        ids=generate_io.keys(),
    )
    def test_verify_parameter_study(
        self,
        parameter_schema: dict,
        expected_array: numpy.ndarray,  # noqa: ARG002
        expected_types: dict[str, type],  # noqa: ARG002
    ) -> None:
        """Test that correctly built parameter studies do not raise an exception when verified.

        Test originates to catch a past bug where correctly built parameter study objects would fail the verification
        check. This is a proof-of-success function to protect against inconsistencies between the verification check
        function and the parameter study objects. The ``generate_io`` test cases should all produce correct parameter
        studies, so they should never generate an exception in the ``_verify_parameter_study`` method, either.

        :param parameter_schema: parameter schema that should result in a correct CartesianProduct parameter study
            definition.
        :param expected_array: the expected parameter study numpy data. Unused by this test function. Must be present
            to allow re-use of the ``test_generate`` test case dictionary.
        :param expected_types: the expected parameter study parameter data types. Unused by this test function. Must be
            present to allow re-use of the ``test_generate`` test case dictionary.
        """
        test_generate = CartesianProduct(parameter_schema)
        parameter_generators._verify_parameter_study(test_generate.parameter_study)

    merge_test = {
        "mixed length strings": (
            {"parameter_1": ["one"]},
            {"parameter_1": ["many"]},
            numpy.array([["many"], ["one"]], dtype=object),
            {"parameter_1": numpy.dtype("U4")},
        ),
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
                    [2, 4.0, "a"],
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
                    [2, False, "a"],
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
            original_study, merged_study = merge_samplers(CartesianProduct, first_schema, second_schema, {})
            generate_array = merged_study._samples
            assert numpy.all(generate_array == expected_array)
            for key in merged_study.parameter_study:
                assert merged_study.parameter_study[key].dtype == expected_types[str(key)]
            consistent_hash_parameter_check(original_study, merged_study)
            self_consistency_checks(merged_study)

    parameter_study_to_dict = {
        "ints": (
            {"ints": [1, 2]},
            {"parameter_set0": {"ints": 1}, "parameter_set1": {"ints": 2}},
        ),
        "floats": (
            {"floats": [10.0, 20.0]},
            {"parameter_set0": {"floats": 20.0}, "parameter_set1": {"floats": 10.0}},
        ),
        "strings": (
            {"strings": ["a", "b"]},
            {"parameter_set0": {"strings": "b"}, "parameter_set1": {"strings": "a"}},
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
        test_parameter_study_dict = CartesianProduct(parameter_schema)
        returned_dictionary = test_parameter_study_dict.parameter_study_to_dict()
        assert expected_dictionary.keys() == returned_dictionary.keys()
        assert all(isinstance(key, str) for key in returned_dictionary)
        for set_name, set_contents in expected_dictionary.items():
            assert set_contents == returned_dictionary[set_name]
            for parameter in set_contents:
                assert type(set_contents[parameter]) is type(returned_dictionary[set_name][parameter])
