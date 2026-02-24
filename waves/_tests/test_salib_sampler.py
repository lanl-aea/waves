"""Test SALibSampler Class."""

import contextlib
import typing
from unittest.mock import patch

import numpy
import pytest
import xarray

from waves._settings import _set_coordinate_key, _supported_salib_samplers
from waves._tests.common import consistent_hash_parameter_check, merge_samplers, platform_check, self_consistency_checks
from waves.exceptions import SchemaValidationError
from waves.parameter_generators import SALibSampler

does_not_raise = contextlib.nullcontext()
testing_windows, root_fs, testing_macos = platform_check()


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
                        [-0.33333333, 1.0, 1.0, -0.33333333, 0.33333333, 1.0, -1.0, -0.33333333, -1.0, 0.33333333],
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
                                ],
                                dims=_set_coordinate_key,
                            )
                        },
                    ),
                    "parameter_2": xarray.DataArray(
                        [-0.66666667, -2.0, 2.0, 2.0, -2.0, 0.66666667, -2.0, 0.66666667, 0.66666667, 0.66666667],
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
                                ],
                                dims=_set_coordinate_key,
                            )
                        },
                    ),
                    "set_hash": xarray.DataArray(
                        [
                            "057a406025af9bc9831729c9770bfba4",
                            "2b18a719c7945d3296dd1debe2350c0d",
                            "30b1b83a463b6ec2a285675a02b6c303",
                            "4a34fe7bccad4fef1c82d4ceda72766c",
                            "52736bd353e11f6a22570350ebb868b6",
                            "658601aa8b10b092a99d7e4f9d3c0358",
                            "94a32bb5e68d117276ffc4f138677803",
                            "bbca8f41f728353583e788e5dad118e9",
                            "da268cacb7badc54f7d2fe8b8a0a2db4",
                            "eddac337f9c9c79d03e0ae0278076dc9",
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
                        [-0.22604395, 0.43887844],
                        coords={
                            _set_coordinate_key: xarray.DataArray(
                                ["parameter_set0", "parameter_set1"],
                                dims=_set_coordinate_key,
                            )
                        },
                    ),
                    "set_hash": xarray.DataArray(
                        ["6400508900158a61b0ec622281662fd8", "9730dec062211dbebb12f90bd45bf7ce"],
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
        "fast sampler: good schema 65x1 (linux)": pytest.param(
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
                            -0.350329651929995,
                            0.8734065750069187,
                            0.011868113468455732,
                            -0.8496703480700056,
                            -0.4118681134684544,
                            -0.3573626557623143,
                            -0.22725272885307113,
                            0.5041758057761472,
                            0.3265934249930822,
                            -0.2958241942238524,
                            -0.8426373442376888,
                            0.20351650191615844,
                            0.0734065750069175,
                            0.44967034807000594,
                            0.2650549634546224,
                            0.1419780403776989,
                            -0.9657142673146084,
                            0.8118681134684587,
                            0.8189011173007761,
                            -0.11120880960846447,
                            0.13494503654537948,
                            0.5112088096084677,
                            -0.9112088096084677,
                            -0.4804395788392357,
                            -0.9727472711469295,
                            -0.6650549634546179,
                            0.38109888269922454,
                            0.6887911903915305,
                            0.319560421160765,
                            -0.9041758057761471,
                            0.6342857326853881,
                            -0.10417580577614738,
                            -0.7881318865315415,
                            -0.5419780403776987,
                            -0.7265934249930819,
                            0.8804395788392354,
                            -0.6580219596223029,
                            -0.2887911903915352,
                            0.4426373442376854,
                            0.7573626557623119,
                            -0.16571426731460925,
                            0.9419780403776996,
                            0.01890111730077626,
                            -0.7195604211607649,
                            -0.042637344237685504,
                            0.08043957883923758,
                            -0.41890111730077606,
                            -0.4734065750069163,
                            0.258021959622301,
                            0.5727472711469297,
                            0.6272527288530712,
                            0.19648349808384125,
                            -0.7810988826992243,
                            -0.5964834980838412,
                            0.9349450365453782,
                            0.6958241942238521,
                            -0.534945036545377,
                            0.7503296519299947,
                            0.5657142673146089,
                            0.9964834980838442,
                            -0.17274727114692856,
                            -0.04967034807000614,
                            -0.6035165019161581,
                            0.38813188653154396,
                            -0.23428573268538821,
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
                            "06fef79b88be7d9698d3f310307a31ad",
                            "072986c01debd6f0d8d2596e0ced3bae",
                            "08f6d8b600b38201ec9cb39aeb06d6fb",
                            "134cc2e649cd3cbf582baf8ba3a9a763",
                            "18f13cff07746b69705fb381d06c52a3",
                            "27ecadc5090af0dc48a017f5504d428c",
                            "2821483395ace54382c415b394a00859",
                            "285f99341a817b6649b4916a52e37762",
                            "288a842a0f58e3c04b388daa6079fdf7",
                            "295af31ae559ae8f71c1d175ee7b46a8",
                            "298d77ff25b85cf7c25b252c1a95b25a",
                            "2ac6a38cadf9f64ab5c53af0b5cf864b",
                            "326344747cad9ba92bb846b829179a4d",
                            "349b0d0cb89f7adc5f81fd6b171372a4",
                            "362eda574f2fe41361a1e7b80ed7440c",
                            "3940ef1ef26d8692544ed9b9bc458a19",
                            "42c75970995f0d4bc4e5646192a657f2",
                            "46f286289977ac497aaf28cf4a793f0a",
                            "4745aa4e9448460b877b4a459a7a1f2f",
                            "476ca493d9eed4e81eb6c36555415448",
                            "504e94700fd75e65f3787659a6a6de52",
                            "57ea3ea7f1f97a2830d6d5fe64ce1d18",
                            "57ef2a497b431a9d551f83245d7f5f5d",
                            "5dd6b49107f89e93e2291b29e98f3d8b",
                            "60afcda90ba20c51450ab488dbaa5421",
                            "61efb702db70071290a361a3209f2bb1",
                            "6a9b93286fcf31170e7ab0138cd27cb7",
                            "7270b415afbb3f716c349b4435819037",
                            "72a6cc8a668a68d5b560da8323783d26",
                            "7612d06d508069164109d9ccf9478b3e",
                            "8482c2dc5b531b02a76c1cdc6bcba964",
                            "88492a15372b7f67e73cdfb9980795e0",
                            "89a7b151d76c778fc5cddba591443f12",
                            "8d386a31a92e88297e139516b12a262f",
                            "8e3a160362a7fa4f3ba7b1810823dccf",
                            "9d48b3d40c0bd1d352feb8b84c7b35f1",
                            "a151e8b530402e6bd887d54da5bc9d8c",
                            "a494c59d77733634c14d086ecc8a97db",
                            "a499f180bc51afe98e57ed5c007c21de",
                            "a62fbaf0d7418751cdc77625b8d47e69",
                            "a8deaf8d70eb7d29b6fe0bcd2ca63863",
                            "af6dcd2c4968d84ff16c33581cd4c2e3",
                            "b09a7329c3f5b86343127de475f99121",
                            "b598d21c2d52a8146657483a6550c27b",
                            "b7e9ded2f729d1967001013081e98d52",
                            "bc00c93faf614543dc5bca2ba26e5b9a",
                            "bd32e7d1f0e0ec63a235b7457f54cda3",
                            "bd57b6e543f52ac0dc9c55bdac0ef2d4",
                            "bdd962687e4e9ab321ac2903a3438d1c",
                            "c45d545546db87c187808f416185c7f2",
                            "c75c372f3bd37bec6d45600def2d71ff",
                            "c8b2d32d6290f7376e2b93b89fe6e5be",
                            "ca40d3e9e5bd3987b74897afe6a751eb",
                            "cdc5ccfc61107a29997c76c8225b8f5d",
                            "ce38b79251b7256e31e51fe119b79056",
                            "cfa134730f3924a0d4c9468a57cb3d6f",
                            "d0cbd66f59cb309b4e2a9f1c20e0c793",
                            "de32cdd33352a8ea97240e0039ffe20c",
                            "e1ceaf9c60a9aba4a91ce4381c176d43",
                            "eb07f839fede536cc93dbe6aa1dc92e1",
                            "edcc73d00aabdb7de229e6795e2e8ff2",
                            "f62dfb7548b3bbe8a32ae82867e15d08",
                            "f82f55b1b65e9b9eaeb6f2af3a387d7f",
                            "fdc5ae91af19820fa3cc9d351309eb19",
                            "fdd9f648153eb6e10a7a233817f1f945",
                        ],
                        dims=_set_coordinate_key,
                    ),
                }
            ).set_coords("set_hash"),
            marks=[
                pytest.mark.skipif(
                    testing_windows or testing_macos,
                    reason="Machine precision result known to differ on macOS and windows CI servers",
                )
            ],
        ),
        "fast sampler: good schema 65x1 (windows)": pytest.param(
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
                            -0.35032965,
                            0.87340658,
                            0.01186811,
                            0.88043958,
                            -0.84967035,
                            -0.41186811,
                            -0.22725273,
                            0.50417581,
                            0.32659342,
                            -0.29582419,
                            -0.84263734,
                            0.2035165,
                            0.07340658,
                            0.44967035,
                            0.26505496,
                            0.14197804,
                            -0.96571427,
                            0.81186811,
                            0.81890112,
                            -0.11120881,
                            0.13494504,
                            -0.91120881,
                            -0.28879119,
                            0.51120881,
                            -0.48043958,
                            -0.97274727,
                            -0.66505496,
                            0.38109888,
                            0.68879119,
                            0.31956042,
                            -0.90417581,
                            0.63428573,
                            -0.10417581,
                            -0.78813189,
                            -0.54197804,
                            -0.72659342,
                            -0.35736266,
                            -0.17274727,
                            -0.65802196,
                            0.62725273,
                            0.44263734,
                            0.75736266,
                            -0.16571427,
                            0.94197804,
                            0.01890112,
                            -0.71956042,
                            -0.04263734,
                            0.08043958,
                            -0.41890112,
                            -0.47340658,
                            0.25802196,
                            -0.78109888,
                            0.57274727,
                            0.1964835,
                            -0.5964835,
                            0.93494504,
                            0.69582419,
                            -0.53494504,
                            0.75032965,
                            0.56571427,
                            0.9964835,
                            -0.04967035,
                            -0.6035165,
                            0.38813189,
                            -0.23428573,
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
                            "06fef79b88be7d9698d3f310307a31ad",
                            "072986c01debd6f0d8d2596e0ced3bae",
                            "08f6d8b600b38201ec9cb39aeb06d6fb",
                            "0cb22629b8d5a45f77dbcc1f73a573ab",
                            "134cc2e649cd3cbf582baf8ba3a9a763",
                            "18f13cff07746b69705fb381d06c52a3",
                            "2821483395ace54382c415b394a00859",
                            "285f99341a817b6649b4916a52e37762",
                            "288a842a0f58e3c04b388daa6079fdf7",
                            "295af31ae559ae8f71c1d175ee7b46a8",
                            "298d77ff25b85cf7c25b252c1a95b25a",
                            "2ac6a38cadf9f64ab5c53af0b5cf864b",
                            "326344747cad9ba92bb846b829179a4d",
                            "349b0d0cb89f7adc5f81fd6b171372a4",
                            "362eda574f2fe41361a1e7b80ed7440c",
                            "3940ef1ef26d8692544ed9b9bc458a19",
                            "42c75970995f0d4bc4e5646192a657f2",
                            "46f286289977ac497aaf28cf4a793f0a",
                            "4745aa4e9448460b877b4a459a7a1f2f",
                            "476ca493d9eed4e81eb6c36555415448",
                            "504e94700fd75e65f3787659a6a6de52",
                            "52ca4282a2ba55962a6d60b8b2554b20",
                            "56ce58b1e56c29cdb26aaf154d94b8b6",
                            "57ea3ea7f1f97a2830d6d5fe64ce1d18",
                            "5dd6b49107f89e93e2291b29e98f3d8b",
                            "60afcda90ba20c51450ab488dbaa5421",
                            "61efb702db70071290a361a3209f2bb1",
                            "6a9b93286fcf31170e7ab0138cd27cb7",
                            "7270b415afbb3f716c349b4435819037",
                            "72a6cc8a668a68d5b560da8323783d26",
                            "7612d06d508069164109d9ccf9478b3e",
                            "8482c2dc5b531b02a76c1cdc6bcba964",
                            "88492a15372b7f67e73cdfb9980795e0",
                            "89a7b151d76c778fc5cddba591443f12",
                            "8d386a31a92e88297e139516b12a262f",
                            "8e3a160362a7fa4f3ba7b1810823dccf",
                            "9357e261cd71d74c2e190ecc6a7b18a9",
                            "9595498e3dff3435bd4cd70a1ec4688c",
                            "a151e8b530402e6bd887d54da5bc9d8c",
                            "a2c1d21713bd22b7f27e99579f42bca4",
                            "a499f180bc51afe98e57ed5c007c21de",
                            "a62fbaf0d7418751cdc77625b8d47e69",
                            "a8deaf8d70eb7d29b6fe0bcd2ca63863",
                            "af6dcd2c4968d84ff16c33581cd4c2e3",
                            "b09a7329c3f5b86343127de475f99121",
                            "b598d21c2d52a8146657483a6550c27b",
                            "b7e9ded2f729d1967001013081e98d52",
                            "bc00c93faf614543dc5bca2ba26e5b9a",
                            "bd32e7d1f0e0ec63a235b7457f54cda3",
                            "bd57b6e543f52ac0dc9c55bdac0ef2d4",
                            "bdd962687e4e9ab321ac2903a3438d1c",
                            "c13b84f816676b912d9702a197ca165e",
                            "c45d545546db87c187808f416185c7f2",
                            "c8b2d32d6290f7376e2b93b89fe6e5be",
                            "cdc5ccfc61107a29997c76c8225b8f5d",
                            "ce38b79251b7256e31e51fe119b79056",
                            "cfa134730f3924a0d4c9468a57cb3d6f",
                            "d0cbd66f59cb309b4e2a9f1c20e0c793",
                            "de32cdd33352a8ea97240e0039ffe20c",
                            "e1ceaf9c60a9aba4a91ce4381c176d43",
                            "eb07f839fede536cc93dbe6aa1dc92e1",
                            "f62dfb7548b3bbe8a32ae82867e15d08",
                            "f82f55b1b65e9b9eaeb6f2af3a387d7f",
                            "fdc5ae91af19820fa3cc9d351309eb19",
                            "fdd9f648153eb6e10a7a233817f1f945",
                        ],
                        dims=_set_coordinate_key,
                    ),
                }
            ).set_coords("set_hash"),
            marks=[
                pytest.mark.skipif(
                    not testing_windows,
                    reason="Machine precision result known to differ on Windows CI servers",
                )
            ],
        ),
        "fast sampler: good schema 65x1 (macos)": pytest.param(
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
                            0.87340658,
                            0.01186811,
                            -0.35032965,
                            -0.84967035,
                            -0.41186811,
                            -0.22725273,
                            0.50417581,
                            0.32659342,
                            -0.29582419,
                            -0.84263734,
                            0.2035165,
                            0.07340658,
                            0.44967035,
                            0.26505496,
                            0.14197804,
                            -0.96571427,
                            0.81186811,
                            0.81890112,
                            -0.11120881,
                            0.13494504,
                            -0.41890112,
                            0.51120881,
                            -0.91120881,
                            -0.48043958,
                            -0.97274727,
                            -0.66505496,
                            0.38109888,
                            0.68879119,
                            0.31956042,
                            -0.90417581,
                            0.63428573,
                            -0.10417581,
                            -0.78813189,
                            -0.54197804,
                            -0.72659342,
                            -0.35736266,
                            -0.17274727,
                            0.88043958,
                            -0.65802196,
                            -0.28879119,
                            0.44263734,
                            0.75736266,
                            -0.16571427,
                            0.94197804,
                            0.01890112,
                            -0.71956042,
                            -0.04263734,
                            0.08043958,
                            -0.47340658,
                            0.25802196,
                            0.57274727,
                            0.1964835,
                            -0.78109888,
                            -0.5964835,
                            0.93494504,
                            0.69582419,
                            -0.53494504,
                            0.75032965,
                            0.56571427,
                            0.9964835,
                            0.62725273,
                            -0.04967035,
                            -0.6035165,
                            0.38813189,
                            -0.23428573,
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
                            "072986c01debd6f0d8d2596e0ced3bae",
                            "08f6d8b600b38201ec9cb39aeb06d6fb",
                            "121ca46fc45248c5c027e9510787b8b3",
                            "134cc2e649cd3cbf582baf8ba3a9a763",
                            "18f13cff07746b69705fb381d06c52a3",
                            "2821483395ace54382c415b394a00859",
                            "285f99341a817b6649b4916a52e37762",
                            "288a842a0f58e3c04b388daa6079fdf7",
                            "295af31ae559ae8f71c1d175ee7b46a8",
                            "298d77ff25b85cf7c25b252c1a95b25a",
                            "2ac6a38cadf9f64ab5c53af0b5cf864b",
                            "326344747cad9ba92bb846b829179a4d",
                            "349b0d0cb89f7adc5f81fd6b171372a4",
                            "362eda574f2fe41361a1e7b80ed7440c",
                            "3940ef1ef26d8692544ed9b9bc458a19",
                            "42c75970995f0d4bc4e5646192a657f2",
                            "46f286289977ac497aaf28cf4a793f0a",
                            "4745aa4e9448460b877b4a459a7a1f2f",
                            "476ca493d9eed4e81eb6c36555415448",
                            "504e94700fd75e65f3787659a6a6de52",
                            "57dd9dcde701b4be1bdec9203636032b",
                            "57ea3ea7f1f97a2830d6d5fe64ce1d18",
                            "57ef2a497b431a9d551f83245d7f5f5d",
                            "5dd6b49107f89e93e2291b29e98f3d8b",
                            "60afcda90ba20c51450ab488dbaa5421",
                            "61efb702db70071290a361a3209f2bb1",
                            "6a9b93286fcf31170e7ab0138cd27cb7",
                            "7270b415afbb3f716c349b4435819037",
                            "72a6cc8a668a68d5b560da8323783d26",
                            "7612d06d508069164109d9ccf9478b3e",
                            "8482c2dc5b531b02a76c1cdc6bcba964",
                            "88492a15372b7f67e73cdfb9980795e0",
                            "89a7b151d76c778fc5cddba591443f12",
                            "8d386a31a92e88297e139516b12a262f",
                            "8e3a160362a7fa4f3ba7b1810823dccf",
                            "9357e261cd71d74c2e190ecc6a7b18a9",
                            "9595498e3dff3435bd4cd70a1ec4688c",
                            "9d48b3d40c0bd1d352feb8b84c7b35f1",
                            "a151e8b530402e6bd887d54da5bc9d8c",
                            "a494c59d77733634c14d086ecc8a97db",
                            "a499f180bc51afe98e57ed5c007c21de",
                            "a62fbaf0d7418751cdc77625b8d47e69",
                            "a8deaf8d70eb7d29b6fe0bcd2ca63863",
                            "af6dcd2c4968d84ff16c33581cd4c2e3",
                            "b09a7329c3f5b86343127de475f99121",
                            "b598d21c2d52a8146657483a6550c27b",
                            "b7e9ded2f729d1967001013081e98d52",
                            "bc00c93faf614543dc5bca2ba26e5b9a",
                            "bd57b6e543f52ac0dc9c55bdac0ef2d4",
                            "bdd962687e4e9ab321ac2903a3438d1c",
                            "c45d545546db87c187808f416185c7f2",
                            "c8b2d32d6290f7376e2b93b89fe6e5be",
                            "ca40d3e9e5bd3987b74897afe6a751eb",
                            "cdc5ccfc61107a29997c76c8225b8f5d",
                            "ce38b79251b7256e31e51fe119b79056",
                            "cfa134730f3924a0d4c9468a57cb3d6f",
                            "d0cbd66f59cb309b4e2a9f1c20e0c793",
                            "de32cdd33352a8ea97240e0039ffe20c",
                            "e1ceaf9c60a9aba4a91ce4381c176d43",
                            "eb07f839fede536cc93dbe6aa1dc92e1",
                            "f12d00b8f48e557bb2a977fcbcde1c85",
                            "f62dfb7548b3bbe8a32ae82867e15d08",
                            "f82f55b1b65e9b9eaeb6f2af3a387d7f",
                            "fdc5ae91af19820fa3cc9d351309eb19",
                            "fdd9f648153eb6e10a7a233817f1f945",
                        ],
                        dims=_set_coordinate_key,
                    ),
                }
            ).set_coords("set_hash"),
            marks=[
                pytest.mark.skipif(
                    not testing_macos,
                    reason="Machine precision result known to be specific to macOS Apple Silicon CI server",
                )
            ],
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
