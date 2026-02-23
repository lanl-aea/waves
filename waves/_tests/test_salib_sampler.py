"""Test SALibSampler Class."""

import contextlib
import typing
from unittest.mock import patch

import numpy
import pytest
import xarray

from waves._settings import _set_coordinate_key, _supported_salib_samplers
from waves._tests.common import consistent_hash_parameter_check, merge_samplers, self_consistency_checks
from waves.exceptions import SchemaValidationError
from waves.parameter_generators import SALibSampler

does_not_raise = contextlib.nullcontext()


class TestSALibSampler:
    """Class for testing SALib Sampler parameter study generator class."""

    sampler_overrides = {
        "sobol: two parameter": (
            "sobol",
            {
                "N": 4,
                "problem": {
                    "num_vars": 2,
                    "names": ["parameter_1", "parameter_2"],
                    "bounds": [[-1, 1], [-2, 2]],
                },
            },
            {},
            {"calc_second_order": False},
        ),
        "sobol: two parameter: override kwargs": (
            "sobol",
            {
                "N": 4,
                "problem": {
                    "num_vars": 2,
                    "names": ["parameter_1", "parameter_2"],
                    "bounds": [[-1, 1], [-2, 2]],
                },
            },
            {"override_kwargs": {"dummy key": "dummy value"}},
            {"calc_second_order": False, "dummy key": "dummy value"},
        ),
    }

    @pytest.mark.parametrize(
        ("sampler_class", "parameter_schema", "kwargs", "expected"),
        sampler_overrides.values(),
        ids=sampler_overrides.keys(),
    )
    def test_sampler_overrides(
        self, sampler_class: str, parameter_schema: dict, kwargs: dict, expected: dict[str, typing.Any]
    ) -> None:
        test_validate = SALibSampler(sampler_class, parameter_schema)
        override_kwargs = test_validate._sampler_overrides(**kwargs)
        assert override_kwargs == expected

    validate_input = {
        "sobol: good schema": (
            "sobol",
            {
                "N": 4,
                "problem": {
                    "num_vars": 3,
                    "names": ["parameter_1", "parameter_2", "parameter_3"],
                    "bounds": [[-1, 1], [-2, 2], [-3, 3]],
                },
            },
            does_not_raise,
        ),
        "latin: good schema": (
            "latin",
            {
                "N": 4,
                "problem": {
                    "num_vars": 3,
                    "names": ["parameter_1", "parameter_2", "parameter_3"],
                    "bounds": [[-1, 1], [-2, 2], [-3, 3]],
                },
            },
            does_not_raise,
        ),
        "sobol: one parameter": (
            "sobol",
            {
                "N": 4,
                "problem": {
                    "num_vars": 1,
                    "names": ["parameter_1"],
                    "bounds": [[-1, 1]],
                },
            },
            pytest.raises(SchemaValidationError),
        ),
        "morris: one parameter": (
            "morris",
            {
                "N": 4,
                "problem": {
                    "num_vars": 1,
                    "names": ["parameter_1"],
                    "bounds": [[-1, 1]],
                },
            },
            pytest.raises(SchemaValidationError),
        ),
        "missing N": (
            "latin",
            {"problem": {"num_vars": 4, "names": ["p1"], "bounds": [[-1, 1]]}},
            pytest.raises(SchemaValidationError),
        ),
        "missing problem": (
            "latin",
            {"N": 4},
            pytest.raises(SchemaValidationError),
        ),
        "missing names": (
            "latin",
            {"N": 4, "problem": {"num_vars": 4, "bounds": [[-1, 1]]}},
            pytest.raises(SchemaValidationError),
        ),
        "schema not a dict": (
            "latin",
            "not a dict",
            pytest.raises(SchemaValidationError),
        ),
        "N not an int": (
            "latin",
            {"N": "not an int", "problem": {"num_vars": 4, "names": ["p1"], "bounds": [[-1, 1]]}},
            pytest.raises(SchemaValidationError),
        ),
        "problem not a dict": (
            "latin",
            {"N": 4, "problem": "not a dict"},
            pytest.raises(SchemaValidationError),
        ),
        "names not a list": (
            "latin",
            {"N": 4, "problem": {"num_vars": 4, "names": "not a list", "bounds": [[-1, 1]]}},
            pytest.raises(SchemaValidationError),
        ),
    }

    @pytest.mark.parametrize(
        ("sampler_class", "parameter_schema", "outcome"), validate_input.values(), ids=validate_input.keys()
    )
    def test_validate(
        self, sampler_class: str, parameter_schema: dict, outcome: contextlib.nullcontext | pytest.RaisesExc
    ) -> None:
        with outcome:
            # Validate is called in __init__. Do not need to call explicitly.
            test_validate = SALibSampler(sampler_class, parameter_schema)
            assert isinstance(test_validate, SALibSampler)

    generate_shapes_input = {
        "good schema 5x2": (
            {
                "N": 5,
                "problem": {
                    "num_vars": 2,
                    "names": ["parameter_1", "parameter_2"],
                    "bounds": [[-1, 1], [-2, 2]],
                },
            },
            {"seed": 42},
        ),
        "good schema 2x1": (
            {
                "N": 2,
                "problem": {
                    "num_vars": 1,
                    "names": ["parameter_1"],
                    "bounds": [[-1, 1]],
                },
            },
            {"seed": 42},
        ),
        "good schema 1x2": (
            {
                "N": 1,
                "problem": {
                    "num_vars": 2,
                    "names": ["parameter_1", "parameter_2"],
                    "bounds": [[-1, 1], [-2, 2]],
                },
            },
            {"seed": 42},
        ),
        "good schema 1x3": (
            {
                "N": 1,
                "problem": {
                    "num_vars": 3,
                    "names": ["parameter_1", "parameter_2", "parameter_3"],
                    "bounds": [[-1, 1], [-2, 2], [-3, 3]],
                },
            },
            {"seed": 42},
        ),
        "good schema 65x3": (
            {
                "N": 65,
                "problem": {
                    "num_vars": 3,
                    "names": ["parameter_1", "parameter_2", "parameter_3"],
                    "bounds": [[-1, 1], [-2, 2], [-3, 3]],
                },
            },
            {"seed": 42},
        ),
    }

    def _expected_set_names(self, sampler: str, N: int, num_vars: int) -> list[str]:  # noqa: N803
        number_of_simulations = N
        if sampler == "sobol" and num_vars <= 2:
            number_of_simulations = N * (num_vars + 2)
        elif sampler == "sobol":
            number_of_simulations = N * (2 * num_vars + 2)
        elif sampler == "fast_sampler":
            number_of_simulations = N * num_vars
        elif sampler == "finite_diff":
            number_of_simulations = N * (num_vars + 1)
        elif sampler == "morris":
            # Default interface settings
            number_of_simulations = int((num_vars + 1) * N)
        return [f"parameter_set{num}" for num in range(number_of_simulations)]

    def _big_enough(self, sampler: str, N: int, num_vars: int) -> bool:  # noqa: N803
        if (  # noqa: SIM103
            (sampler == "sobol" and num_vars < 2)
            or (sampler == "fast_sampler" and N < 64)
            or (sampler == "morris" and num_vars < 2)
        ):
            return False
        return True

    @pytest.mark.parametrize(
        ("parameter_schema", "kwargs"),
        generate_shapes_input.values(),
        ids=generate_shapes_input.keys(),
    )
    def test_generate_shapes(self, parameter_schema: dict, kwargs: dict) -> None:
        for sampler in _supported_salib_samplers:
            # TODO: find a better way to separate the sampler types and their test parameterization
            if not self._big_enough(sampler, parameter_schema["N"], parameter_schema["problem"]["num_vars"]):
                return
            # Unit tests
            test_generate = SALibSampler(sampler, parameter_schema, **kwargs)
            samples_array = test_generate._samples
            assert samples_array.shape[1] == parameter_schema["problem"]["num_vars"]
            # Verify that the parameter set name creation method was called
            # Morris produces inconsistent set counts depending on seed. Rely on the variable count shape check above.
            if sampler != "morris":
                expected_set_names = self._expected_set_names(
                    sampler, parameter_schema["N"], parameter_schema["problem"]["num_vars"]
                )
                assert samples_array.shape[0] == len(expected_set_names)
                assert list(test_generate._set_names.values()) == expected_set_names
                # Check that the parameter set names are correctly populated in the parameter study Xarray Dataset
                set_names = list(test_generate.parameter_study[_set_coordinate_key])
                assert numpy.all(set_names == expected_set_names)

    generate_input = {
        "morris: good schema 5x2": (
            "morris",
            {
                "N": 5,
                "problem": {
                    "num_vars": 2,
                    "names": ["parameter_1", "parameter_2"],
                    "bounds": [[-1, 1], [-2, 2]],
                },
            },
            {"seed": 42},
            xarray.Dataset(
                {
                    "parameter_1": xarray.DataArray(
                        [
                            -0.33333333,
                            0.33333333,
                            -0.33333333,
                            0.33333333,
                            -1.0,
                            -1.0,
                            1.0,
                            -1.0,
                            -0.33333333,
                            0.33333333,
                            -0.33333333,
                            -1.0,
                            1.0,
                        ],
                        coords={
                            _set_coordinate_key: xarray.DataArray(
                                [
                                    "parameter_set0",
                                    "parameter_set1",
                                    "parameter_set2",
                                    "parameter_set3",
                                    "parameter_set4",
                                    "parameter_set5",
                                    "parameter_set6",
                                    "parameter_set7",
                                    "parameter_set8",
                                    "parameter_set9",
                                    "parameter_set10",
                                    "parameter_set11",
                                    "parameter_set12",
                                ],
                                dims=_set_coordinate_key,
                            )
                        },
                    ),
                    "parameter_2": xarray.DataArray(
                        [
                            -0.66666667,
                            -0.66666667,
                            2.0,
                            -2.0,
                            2.0,
                            -0.66666667,
                            0.66666667,
                            -2.0,
                            0.66666667,
                            2.0,
                            -2.0,
                            0.66666667,
                            -0.66666667,
                        ],
                        coords={
                            _set_coordinate_key: xarray.DataArray(
                                [
                                    "parameter_set0",
                                    "parameter_set1",
                                    "parameter_set2",
                                    "parameter_set3",
                                    "parameter_set4",
                                    "parameter_set5",
                                    "parameter_set6",
                                    "parameter_set7",
                                    "parameter_set8",
                                    "parameter_set9",
                                    "parameter_set10",
                                    "parameter_set11",
                                    "parameter_set12",
                                ],
                                dims=_set_coordinate_key,
                            )
                        },
                    ),
                    "set_hash": xarray.DataArray(
                        [
                            "057a406025af9bc9831729c9770bfba4",
                            "0d7b252cb2bc8df82d671dd7b8be1d4a",
                            "4a34fe7bccad4fef1c82d4ceda72766c",
                            "52736bd353e11f6a22570350ebb868b6",
                            "528dc49f949ab0e5dd6a1b1b4c4a7d9a",
                            "6274803b3383cc6a9099bfc69398ae00",
                            "658601aa8b10b092a99d7e4f9d3c0358",
                            "94a32bb5e68d117276ffc4f138677803",
                            "bbca8f41f728353583e788e5dad118e9",
                            "c2b2f0ebc2552032a441f25fd2a45a88",
                            "c374b0c67fe8df32001f1e6e804f210b",
                            "da268cacb7badc54f7d2fe8b8a0a2db4",
                            "f80330e774ab37fa5e7876fe607a8f23",
                        ],
                        dims=_set_coordinate_key,
                    ),
                }
            ).set_coords("set_hash"),
        ),
        "latin: good schema 2x1": (
            "latin",
            {
                "N": 2,
                "problem": {
                    "num_vars": 1,
                    "names": ["parameter_1"],
                    "bounds": [[-1, 1]],
                },
            },
            {"seed": 42},
            xarray.Dataset(
                {
                    "parameter_1": xarray.DataArray(
                        [0.95071431, -0.62545988],
                        coords={
                            _set_coordinate_key: xarray.DataArray(
                                ["parameter_set0", "parameter_set1"],
                                dims=_set_coordinate_key,
                            )
                        },
                    ),
                    "set_hash": xarray.DataArray(
                        ["7bcbee46082cbee42254293bdea27d03", "a1c625990dc5944ad828c4da9ad5b7ec"],
                        dims=_set_coordinate_key,
                    ),
                }
            ).set_coords("set_hash"),
        ),
        "sobol: good schema 1x2": (
            "sobol",
            {
                "N": 1,
                "problem": {
                    "num_vars": 2,
                    "names": ["parameter_1", "parameter_2"],
                    "bounds": [[-1, 1], [-2, 2]],
                },
            },
            {"seed": 42},
            xarray.Dataset(
                {
                    "parameter_1": xarray.DataArray(
                        [-0.13794105, 0.61282553, 0.61282553, -0.13794105],
                        coords={
                            _set_coordinate_key: xarray.DataArray(
                                ["parameter_set0", "parameter_set1", "parameter_set2", "parameter_set3"],
                                dims=_set_coordinate_key,
                            )
                        },
                    ),
                    "parameter_2": xarray.DataArray(
                        [-1.78617326, 1.25747189, -1.78617326, 1.25747189],
                        coords={
                            _set_coordinate_key: xarray.DataArray(
                                ["parameter_set0", "parameter_set1", "parameter_set2", "parameter_set3"],
                                dims=_set_coordinate_key,
                            )
                        },
                    ),
                    "set_hash": xarray.DataArray(
                        [
                            "588a0fe5d064f8c972922a341fc32bf8",
                            "682c5b5176eda1cb47b736b6c98330c2",
                            "cfac62f65b2e8a2eafc97eb2d9a5e25e",
                            "ed806bda1ad84b54f933af0f792002fb",
                        ],
                        dims=_set_coordinate_key,
                    ),
                }
            ).set_coords("set_hash"),
        ),
        "finite diff: good schema 1x3": (
            "finite_diff",
            {
                "N": 1,
                "problem": {
                    "num_vars": 3,
                    "names": ["parameter_1", "parameter_2", "parameter_3"],
                    "bounds": [[-1, 1], [-2, 2], [-3, 3]],
                },
            },
            {"seed": 42},
            xarray.Dataset(
                {
                    "parameter_1": xarray.DataArray(
                        [-1.0, -0.99707031, -0.99707031, -0.99707031],
                        coords={
                            _set_coordinate_key: xarray.DataArray(
                                ["parameter_set0", "parameter_set1", "parameter_set2", "parameter_set3"],
                                dims=_set_coordinate_key,
                            )
                        },
                    ),
                    "parameter_2": xarray.DataArray(
                        [-0.49414062, -0.49414062, -0.49908203, -0.49414062],
                        coords={
                            _set_coordinate_key: xarray.DataArray(
                                ["parameter_set0", "parameter_set1", "parameter_set2", "parameter_set3"],
                                dims=_set_coordinate_key,
                            )
                        },
                    ),
                    "parameter_3": xarray.DataArray(
                        [-0.31347656, -0.31347656, -0.31347656, -0.31661133],
                        coords={
                            _set_coordinate_key: xarray.DataArray(
                                ["parameter_set0", "parameter_set1", "parameter_set2", "parameter_set3"],
                                dims=_set_coordinate_key,
                            )
                        },
                    ),
                    "set_hash": xarray.DataArray(
                        [
                            "1fdc4976fafdea84bdc8bbe4e14491ee",
                            "61bac0b1bae84a5f18f47fd6255285e4",
                            "dec5fa1decc5b82df746e8264ace22ab",
                            "faf3dc89be7811c84e5ec61da31752e2",
                        ],
                        dims=_set_coordinate_key,
                    ),
                }
            ).set_coords("set_hash"),
        ),
        "fast sampler: good schema 65x1": (
            "fast_sampler",
            {
                "N": 65,
                "problem": {
                    "num_vars": 1,
                    "names": ["parameter_1"],
                    "bounds": [[-1, 1]],
                },
            },
            {"seed": 42},
            xarray.Dataset(
                {
                    "parameter_1": xarray.DataArray(
                        [
                            -0.60585278,
                            -0.29816048,
                            -0.65568568,
                            0.3787626,
                            -0.10183952,
                            0.44030106,
                            0.25568568,
                            -0.11354509,
                            0.69816048,
                            0.20585278,
                            -0.40953183,
                            0.51354509,
                            -0.84030106,
                            0.0212374,
                            0.39046817,
                            0.68645491,
                            -0.22491645,
                            0.07107029,
                            0.88277586,
                            -0.48277586,
                            -0.97508355,
                            0.94431432,
                            -0.23662201,
                            0.45200663,
                            0.26739124,
                            -0.28645491,
                            -0.96337799,
                            0.8212374,
                            -0.71722414,
                            -0.7787626,
                            -0.72892971,
                            -0.34799337,
                            0.31722414,
                            0.57508355,
                            -0.47107029,
                            -0.17508355,
                            -0.79046817,
                            -0.85200663,
                            0.08277586,
                            0.19414722,
                            0.00953183,
                            0.50183952,
                            -0.54431432,
                            0.75969894,
                            0.56337799,
                            -0.35969894,
                            0.99414722,
                            -0.91354509,
                            -0.90183952,
                            0.74799337,
                            -0.16337799,
                            0.87107029,
                            0.13260876,
                            -0.05200663,
                            0.80953183,
                            0.14431432,
                            -0.59414722,
                            0.93260876,
                            -0.04030106,
                            -0.53260876,
                            0.32892971,
                            0.63662201,
                            0.62491645,
                            -0.4212374,
                            -0.66739124,
                        ],
                        coords={
                            _set_coordinate_key: xarray.DataArray(
                                [
                                    "parameter_set0",
                                    "parameter_set1",
                                    "parameter_set2",
                                    "parameter_set3",
                                    "parameter_set4",
                                    "parameter_set5",
                                    "parameter_set6",
                                    "parameter_set7",
                                    "parameter_set8",
                                    "parameter_set9",
                                    "parameter_set10",
                                    "parameter_set11",
                                    "parameter_set12",
                                    "parameter_set13",
                                    "parameter_set14",
                                    "parameter_set15",
                                    "parameter_set16",
                                    "parameter_set17",
                                    "parameter_set18",
                                    "parameter_set19",
                                    "parameter_set20",
                                    "parameter_set21",
                                    "parameter_set22",
                                    "parameter_set23",
                                    "parameter_set24",
                                    "parameter_set25",
                                    "parameter_set26",
                                    "parameter_set27",
                                    "parameter_set28",
                                    "parameter_set29",
                                    "parameter_set30",
                                    "parameter_set31",
                                    "parameter_set32",
                                    "parameter_set33",
                                    "parameter_set34",
                                    "parameter_set35",
                                    "parameter_set36",
                                    "parameter_set37",
                                    "parameter_set38",
                                    "parameter_set39",
                                    "parameter_set40",
                                    "parameter_set41",
                                    "parameter_set42",
                                    "parameter_set43",
                                    "parameter_set44",
                                    "parameter_set45",
                                    "parameter_set46",
                                    "parameter_set47",
                                    "parameter_set48",
                                    "parameter_set49",
                                    "parameter_set50",
                                    "parameter_set51",
                                    "parameter_set52",
                                    "parameter_set53",
                                    "parameter_set54",
                                    "parameter_set55",
                                    "parameter_set56",
                                    "parameter_set57",
                                    "parameter_set58",
                                    "parameter_set59",
                                    "parameter_set60",
                                    "parameter_set61",
                                    "parameter_set62",
                                    "parameter_set63",
                                    "parameter_set64",
                                ],
                                dims=_set_coordinate_key,
                            )
                        },
                    ),
                    "set_hash": xarray.DataArray(
                        [
                            "0a7a6ac9f289b70069f258d7d8d1e602",
                            "14ee687ea201228eb03c05469e539ce1",
                            "1566380f61a3200f188cb9757269be73",
                            "1f3a57882bf3c9d98c23b6f72686f7df",
                            "1f6cfcd3aa62cac5975b649b59ca6547",
                            "225709f8b986e01699397f76a6c7abc2",
                            "242f8e521b5ff8217df114704c938b5d",
                            "25fefee008bb5e6f3c656e0e5a029b50",
                            "2c1ca5b891415510113410708b5d6ade",
                            "2d2482717d3a8f01bcaf35ab4d522b28",
                            "319746710b451d65c6d06b01360eaf75",
                            "326b72f1878d6832dfcd220581abdda5",
                            "36aa5c8bc91d3f4bc5d0d63d580d8668",
                            "39bbe4b43c88536e87fc2b5aa24884ce",
                            "3b6bb6ce774e91a9699533ae5f973187",
                            "3daa33f11ef641b297ce2886fc566b6e",
                            "3df7e1832b090411cfb875a4ed9f97b4",
                            "3eb66e2e8005d6363d04d0904589afe3",
                            "4bbba3f777344d90b1d24925916c89e6",
                            "52be6d99d5211a0b6c4e2fdb8205f26e",
                            "5652c7a75748a2d1442f2a065e2cf3da",
                            "5b62fe3123929312a77dd645724b2205",
                            "5e94d857c3281c8b6ee9c6fb24b17906",
                            "5fe6cadb28019eaf4d38fdf30a5d36a7",
                            "659a69120181a1cdf3eef69df7ee9149",
                            "65c46f184bdc81b78d4697a6106acca3",
                            "69fa52afe33bd5416d91fa686e6fac17",
                            "6b1ee3ae1bb1d30b7020613fb1ca08a5",
                            "6e0de3ee0832677ca3bd8ad9ab606df6",
                            "7286eb32281f606d3be621ece9745ad5",
                            "743e126a1f0fc5c6dd7541c429ad05de",
                            "7901ae5c0fc26c0e929c693e0f7279c2",
                            "81221f2edf00ef5b10266c8a3eaa3511",
                            "87a2c03113dcd86fd858d36f5fa81711",
                            "8eb97803cf4e0f6ffd0da793927e36cc",
                            "8f61b48274530b64785d3cfd24be0d85",
                            "92a1c26333172decd12ea48f30542f46",
                            "953d2041587cbfb371075df40b6e1769",
                            "98c3ac944a8ef39d76e61fda2c284afe",
                            "98c3c68299f2bbbd47c9682063851f03",
                            "a52c064595ae66760b577767330d033c",
                            "a6ede81abeb19b4e1a8780a9f61f6e39",
                            "b05ebf5d7457f1fec93dcf02a59586c1",
                            "b0b0822c59998c189ae7d5948b465371",
                            "b2d46d246ba1659b64de522e3067ddc3",
                            "b77edc7e713fb1a31ac5f00dc50aebe1",
                            "be67a5abb1c7dccf50bb1d2193d46985",
                            "bfe963e45bb1945e66029be554e68786",
                            "c0b7b275d4f5aa6ec81a4a74b49d769b",
                            "c6ed331d379378e0b58fbb0e83e0e6cb",
                            "d165e9cd275f045e55cbbc05d81fe2b0",
                            "d2086e38ee64caa97612451b45269c6e",
                            "d853ccf28308d00f06e9524e8faed0a4",
                            "dc881143ee1cb8305cfb9be3ca5337fd",
                            "de7912ae54d562900d50a4968b3f755f",
                            "e142c5204a1c6eec65e0a8405b9def47",
                            "ea5e315491966996ec165656899108a8",
                            "f4e97db542d42272c0c5ea439f301174",
                            "f6c7c6a77acbf49e5ed4ae1993c3aa9c",
                            "fa79326c561814216ea4e42567b2ef79",
                            "fc50a7ed902b81e1bf2e96a653b44355",
                            "fcbbb861e911254641ebb283d7daa5dc",
                            "fe85ca4dbc177af3bbf4e40e2f9c6105",
                            "fef564bd102707ada8c388f8b705bc2c",
                            "ff1ffbe8a5f075b96e7b3b6ad4d28125",
                        ],
                        dims=_set_coordinate_key,
                    ),
                }
            ).set_coords("set_hash"),
        ),
    }

    @pytest.mark.parametrize(
        ("sampler", "parameter_schema", "kwargs", "expected_dataset"),
        generate_input.values(),
        ids=generate_input.keys(),
    )
    def test_generate(
        self, sampler: str, parameter_schema: dict, kwargs: dict, expected_dataset: xarray.Dataset
    ) -> None:
        test_generate = SALibSampler(sampler, parameter_schema, **kwargs)
        xarray.testing.assert_allclose(test_generate.parameter_study, expected_dataset)
        # Check for type preservation
        for key in test_generate.parameter_study:
            assert test_generate.parameter_study[key].dtype == numpy.float64
        # Verify that the parameter set name creation method was called
        # TODO: _set_names is an ordered object (dictionary). Fix test to compare dictionary-to-dictionary instead
        # of implied consistency according to value order.
        assert list(test_generate._set_names.values()) == list(expected_dataset[_set_coordinate_key].to_numpy())

    merge_test = {
        "new sets, 5(8)x2": (
            {
                "N": 5,
                "problem": {
                    "num_vars": 2,
                    "names": ["parameter_1", "parameter_2"],
                    "bounds": [[-1, 1], [-2, 2]],
                },
            },
            {
                "N": 8,
                "problem": {
                    "num_vars": 2,
                    "names": ["parameter_1", "parameter_2"],
                    "bounds": [[-1, 1], [-2, 2]],
                },
            },
            {"seed": 42},
        ),
        "new sets, 5(8)x3": (
            {
                "N": 5,
                "problem": {
                    "num_vars": 3,
                    "names": ["parameter_1", "parameter_2", "parameter_3"],
                    "bounds": [[-1, 1], [-2, 2], [-3, 3]],
                },
            },
            {
                "N": 8,
                "problem": {
                    "num_vars": 3,
                    "names": ["parameter_1", "parameter_2", "parameter_3"],
                    "bounds": [[-1, 1], [-2, 2], [-3, 3]],
                },
            },
            {"seed": 42},
        ),
        "unchanged sets, 5x2": (
            {
                "N": 5,
                "problem": {
                    "num_vars": 2,
                    "names": ["parameter_1", "parameter_2"],
                    "bounds": [[-1, 1], [-2, 2]],
                },
            },
            {
                "N": 5,
                "problem": {
                    "num_vars": 2,
                    "names": ["parameter_1", "parameter_2"],
                    "bounds": [[-1, 1], [-2, 2]],
                },
            },
            {"seed": 42},
        ),
        "unchanged sets, 5x3": (
            {
                "N": 5,
                "problem": {
                    "num_vars": 3,
                    "names": ["parameter_1", "parameter_2", "parameter_3"],
                    "bounds": [[-1, 1], [-2, 2], [-3, 3]],
                },
            },
            {
                "N": 5,
                "problem": {
                    "num_vars": 3,
                    "names": ["parameter_1", "parameter_2", "parameter_3"],
                    "bounds": [[-1, 1], [-2, 2], [-3, 3]],
                },
            },
            {"seed": 42},
        ),
        "changed sets, 65(70)x3": (
            {
                "N": 65,
                "problem": {
                    "num_vars": 3,
                    "names": ["parameter_1", "parameter_2", "parameter_3"],
                    "bounds": [[-1, 1], [-2, 2], [-3, 3]],
                },
            },
            {
                "N": 70,
                "problem": {
                    "num_vars": 3,
                    "names": ["parameter_1", "parameter_2", "parameter_3"],
                    "bounds": [[-1, 1], [-2, 2], [-3, 3]],
                },
            },
            {"seed": 42},
        ),
        "unchanged sets, 65x3": (
            {
                "N": 65,
                "problem": {
                    "num_vars": 3,
                    "names": ["parameter_1", "parameter_2", "parameter_3"],
                    "bounds": [[-1, 1], [-2, 2], [-3, 3]],
                },
            },
            {
                "N": 65,
                "problem": {
                    "num_vars": 3,
                    "names": ["parameter_1", "parameter_2", "parameter_3"],
                    "bounds": [[-1, 1], [-2, 2], [-3, 3]],
                },
            },
            {"seed": 42},
        ),
    }

    @pytest.mark.parametrize(
        ("first_schema", "second_schema", "kwargs"),
        merge_test.values(),
        ids=merge_test.keys(),
    )
    def test_merge(self, first_schema: dict, second_schema: dict, kwargs: dict) -> None:
        with patch("waves.parameter_generators._verify_parameter_study"):
            for sampler in _supported_salib_samplers:
                # TODO: find a better way to separate the sampler types and their test parameterization
                if not self._big_enough(sampler, first_schema["N"], first_schema["problem"]["num_vars"]):
                    return
                original_study, merged_study = merge_samplers(
                    SALibSampler, first_schema, second_schema, kwargs, sampler
                )
                merged_study._samples.astype(float)
                consistent_hash_parameter_check(original_study, merged_study)
                self_consistency_checks(merged_study)
