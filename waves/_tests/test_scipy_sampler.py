"""Test ScipySampler Class."""

from unittest.mock import patch

import numpy
import pytest
import xarray

from waves._settings import _set_coordinate_key, _supported_scipy_samplers
from waves._tests.common import consistent_hash_parameter_check, merge_samplers, self_consistency_checks
from waves.parameter_generators import ScipySampler


class TestScipySampler:
    """Class for testing Scipy Sequence parameter study generator class."""

    generate_input = {
        "sobol: good schema 5x2": (
            "Sobol",
            {
                "num_simulations": 5,
                "parameter_1": {"distribution": "uniform", "loc": 0, "scale": 10},
                "parameter_2": {"distribution": "uniform", "loc": 2, "scale": 3},
            },
            {"seed": 42},
            xarray.Dataset(
                {
                    "parameter_1": xarray.DataArray(
                        [4.31029474, 9.61578793, 0.35047322, 5.6453192, 2.38067276],
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
                        [4.44310392, 2.93422983, 2.07952781, 3.79350291, 3.91909283],
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
                            "0f9510490d521d7fa85154245288622e",
                            "2f71fbb34825f6fc651a9cdddce1adc8",
                            "4444a85f48a564a2c2e3ba3666b9967b",
                            "4c861fec1563e21bf1598d06dbe97dc7",
                            "658dfb19c773f5b3db9cf61a1d301668",
                        ],
                        dims=_set_coordinate_key,
                    ),
                }
            ).set_coords("set_hash"),
        ),
        "sobol: good schema 2x1": (
            "Sobol",
            {
                "num_simulations": 2,
                "parameter_1": {"distribution": "uniform", "loc": 0, "scale": 10},
            },
            {"seed": 42},
            xarray.Dataset(
                {
                    "parameter_1": xarray.DataArray(
                        [4.31029474, 6.3441517],
                        coords={
                            _set_coordinate_key: xarray.DataArray(
                                ["parameter_set0", "parameter_set1"],
                                dims=_set_coordinate_key,
                            )
                        },
                    ),
                    "set_hash": xarray.DataArray(
                        ["710d5b8c4c251c3847f09d923c1fef13", "f515960e20568d073440635e97fcde64"],
                        dims=_set_coordinate_key,
                    ),
                }
            ).set_coords("set_hash"),
        ),
        "sobol: good schema 1x2": (
            "Sobol",
            {
                "num_simulations": 1,
                "parameter_1": {"distribution": "uniform", "loc": 0, "scale": 10},
                "parameter_2": {"distribution": "uniform", "loc": 2, "scale": 3},
            },
            {"seed": 42},
            xarray.Dataset(
                {
                    "parameter_1": xarray.DataArray(
                        [4.31029474],
                        coords={_set_coordinate_key: xarray.DataArray(["parameter_set0"], dims=_set_coordinate_key)},
                    ),
                    "parameter_2": xarray.DataArray(
                        [4.44310392],
                        coords={_set_coordinate_key: xarray.DataArray(["parameter_set0"], dims=_set_coordinate_key)},
                    ),
                    "set_hash": xarray.DataArray(["0f9510490d521d7fa85154245288622e"], dims=_set_coordinate_key),
                }
            ).set_coords("set_hash"),
        ),
        "sobol: good schema 1x2, no seed": (
            "Sobol",
            {
                "num_simulations": 1,
                "parameter_1": {"distribution": "uniform", "loc": 0, "scale": 10},
                "parameter_2": {"distribution": "uniform", "loc": 2, "scale": 3},
            },
            {},
            # Values will be different due to random seed, but parameter names and sets should be aligned
            xarray.Dataset(
                {
                    "parameter_1": xarray.DataArray(
                        [4.31029474],
                        coords={_set_coordinate_key: xarray.DataArray(["parameter_set0"], dims=_set_coordinate_key)},
                    ),
                    "parameter_2": xarray.DataArray(
                        [4.44310392],
                        coords={_set_coordinate_key: xarray.DataArray(["parameter_set0"], dims=_set_coordinate_key)},
                    ),
                    "set_hash": xarray.DataArray(["0f9510490d521d7fa85154245288622e"], dims=_set_coordinate_key),
                }
            ).set_coords("set_hash"),
        ),
        "halton: good schema 5x2": (
            "Halton",
            {
                "num_simulations": 5,
                "parameter_1": {"distribution": "uniform", "loc": 0, "scale": 10},
                "parameter_2": {"distribution": "uniform", "loc": 2, "scale": 3},
            },
            {"seed": 42},
            xarray.Dataset(
                {
                    "parameter_1": xarray.DataArray(
                        [8.01305869, 3.01305869, 0.51305869, 6.76305869, 5.51305869],
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
                        [3.45530394, 2.78863727, 4.45530394, 4.78863727, 2.45530394],
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
                            "19dae7d5facf1ec27c799d50780b2844",
                            "2aa029475addd33b53330e5a8db7eb0a",
                            "31012af62d9968adb1030f7c8a9faa79",
                            "4a70f8ac568aa17b4d04ea2ab4a1493d",
                            "5b395830351e94db34bee7cd75364a96",
                        ],
                        dims=_set_coordinate_key,
                    ),
                }
            ).set_coords("set_hash"),
        ),
        "halton: good schema 2x1": (
            "Halton",
            {
                "num_simulations": 2,
                "parameter_1": {"distribution": "uniform", "loc": 0, "scale": 10},
            },
            {"seed": 42},
            xarray.Dataset(
                {
                    "parameter_1": xarray.DataArray(
                        [0.51305869, 5.51305869],
                        coords={
                            _set_coordinate_key: xarray.DataArray(
                                ["parameter_set0", "parameter_set1"],
                                dims=_set_coordinate_key,
                            )
                        },
                    ),
                    "set_hash": xarray.DataArray(
                        ["26c15fcb00e527f8acfdf5ea7eb4135f", "fe36599598fe4e8b7369dbe91df418a7"],
                        dims=_set_coordinate_key,
                    ),
                }
            ).set_coords("set_hash"),
        ),
        "halton: good schema 1x2": (
            "Halton",
            {
                "num_simulations": 1,
                "parameter_1": {"distribution": "uniform", "loc": 0, "scale": 10},
                "parameter_2": {"distribution": "uniform", "loc": 2, "scale": 3},
            },
            {"seed": 42},
            xarray.Dataset(
                {
                    "parameter_1": xarray.DataArray(
                        [5.51305869],
                        coords={_set_coordinate_key: xarray.DataArray(["parameter_set0"], dims=_set_coordinate_key)},
                    ),
                    "parameter_2": xarray.DataArray(
                        [2.45530394],
                        coords={_set_coordinate_key: xarray.DataArray(["parameter_set0"], dims=_set_coordinate_key)},
                    ),
                    "set_hash": xarray.DataArray(["5b395830351e94db34bee7cd75364a96"], dims=_set_coordinate_key),
                }
            ).set_coords("set_hash"),
        ),
        "halton: good schema 1x2, no seed": (
            "Halton",
            {
                "num_simulations": 1,
                "parameter_1": {"distribution": "uniform", "loc": 0, "scale": 10},
                "parameter_2": {"distribution": "uniform", "loc": 2, "scale": 3},
            },
            {},
            # Values will be different due to random seed, but parameter names and sets should be aligned
            xarray.Dataset(
                {
                    "parameter_1": xarray.DataArray(
                        [4.31029474],
                        coords={_set_coordinate_key: xarray.DataArray(["parameter_set0"], dims=_set_coordinate_key)},
                    ),
                    "parameter_2": xarray.DataArray(
                        [4.44310392],
                        coords={_set_coordinate_key: xarray.DataArray(["parameter_set0"], dims=_set_coordinate_key)},
                    ),
                    "set_hash": xarray.DataArray(["0f9510490d521d7fa85154245288622e"], dims=_set_coordinate_key),
                }
            ).set_coords("set_hash"),
        ),
        "latin hypercube: good schema 5x2": (
            "LatinHypercube",
            {
                "num_simulations": 5,
                "parameter_1": {"distribution": "uniform", "loc": 0, "scale": 10},
                "parameter_2": {"distribution": "uniform", "loc": 2, "scale": 3},
            },
            {"seed": 42},
            xarray.Dataset(
                {
                    "parameter_1": xarray.DataArray(
                        [6.4777206, 5.8116453, 8.4520879, 3.74377273, 0.28280416],
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
                        [3.32836142, 4.41462659, 2.33667294, 2.92976844, 3.98157918],
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
                            "013636ea8865a13c2b86d8043bbcd2d6",
                            "7c225945863abc12f0c92dcc49d90669",
                            "aa3844e906957716d05ecfffd8db471c",
                            "ee32d86b63d4984b497dc6099a9eda42",
                            "f742eef431ee0dbc138ca8df720fca21",
                        ],
                        dims=_set_coordinate_key,
                    ),
                }
            ).set_coords("set_hash"),
        ),
        "latin hypercube: good schema 2x1": (
            "LatinHypercube",
            {
                "num_simulations": 2,
                "parameter_1": {"distribution": "uniform", "loc": 0, "scale": 10},
            },
            {"seed": 42},
            xarray.Dataset(
                {
                    "parameter_1": xarray.DataArray(
                        [6.13021976, 2.8056078],
                        coords={
                            _set_coordinate_key: xarray.DataArray(
                                ["parameter_set0", "parameter_set1"],
                                dims=_set_coordinate_key,
                            )
                        },
                    ),
                    "set_hash": xarray.DataArray(
                        ["e846f8f7cc614e036a39b60b22d0d6f9", "fd8da5001063283e8b665e59bab3a5e5"],
                        dims=_set_coordinate_key,
                    ),
                }
            ).set_coords("set_hash"),
        ),
        "latin hypercube: good schema 1x2": (
            "LatinHypercube",
            {
                "num_simulations": 1,
                "parameter_1": {"distribution": "uniform", "loc": 0, "scale": 10},
                "parameter_2": {"distribution": "uniform", "loc": 2, "scale": 3},
            },
            {"seed": 42},
            xarray.Dataset(
                {
                    "parameter_1": xarray.DataArray(
                        [2.26043951],
                        coords={_set_coordinate_key: xarray.DataArray(["parameter_set0"], dims=_set_coordinate_key)},
                    ),
                    "parameter_2": xarray.DataArray(
                        [3.68336468],
                        coords={_set_coordinate_key: xarray.DataArray(["parameter_set0"], dims=_set_coordinate_key)},
                    ),
                    "set_hash": xarray.DataArray(["742f13896220c59851df3072477f4a0c"], dims=_set_coordinate_key),
                }
            ).set_coords("set_hash"),
        ),
        "latin hypercube: good schema 1x2, no seed": (
            "LatinHypercube",
            {
                "num_simulations": 1,
                "parameter_1": {"distribution": "uniform", "loc": 0, "scale": 10},
                "parameter_2": {"distribution": "uniform", "loc": 2, "scale": 3},
            },
            {},
            # Values will be different due to random seed, but parameter names and sets should be aligned
            xarray.Dataset(
                {
                    "parameter_1": xarray.DataArray(
                        [4.31029474],
                        coords={_set_coordinate_key: xarray.DataArray(["parameter_set0"], dims=_set_coordinate_key)},
                    ),
                    "parameter_2": xarray.DataArray(
                        [4.44310392],
                        coords={_set_coordinate_key: xarray.DataArray(["parameter_set0"], dims=_set_coordinate_key)},
                    ),
                    "set_hash": xarray.DataArray(["0f9510490d521d7fa85154245288622e"], dims=_set_coordinate_key),
                }
            ).set_coords("set_hash"),
        ),
        "poisson disk: good schema 5x2": (
            "PoissonDisk",
            {
                "num_simulations": 5,
                "parameter_1": {"distribution": "uniform", "loc": 0, "scale": 10},
                "parameter_2": {"distribution": "uniform", "loc": 2, "scale": 3},
            },
            {"seed": 42},
            xarray.Dataset(
                {
                    "parameter_1": xarray.DataArray(
                        [8.30518613, 6.93479829, 7.73956049, 7.72868365, 8.18720158],
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
                        [3.30699128, 3.15549858, 3.31663532, 3.15096067, 3.48494823],
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
                            "23bc90dfa61704980a7a944f12457ea7",
                            "50ccf1d6e5c8395a17e9773a7a33ec27",
                            "a90d1ba8aa6786907bb5f8ef488b666f",
                            "d4322096540bf143c5a7cffbca0f7173",
                            "fe9fb0c1a4661724d0f8790ef92d69dc",
                        ],
                        dims=_set_coordinate_key,
                    ),
                }
            ).set_coords("set_hash"),
        ),
        "poisson disk: good schema 2x1": (
            "PoissonDisk",
            {
                "num_simulations": 2,
                "parameter_1": {"distribution": "uniform", "loc": 0, "scale": 10},
            },
            {"seed": 42},
            xarray.Dataset(
                {
                    "parameter_1": xarray.DataArray(
                        [7.03790777, 7.73956049],
                        coords={
                            _set_coordinate_key: xarray.DataArray(
                                ["parameter_set0", "parameter_set1"],
                                dims=_set_coordinate_key,
                            )
                        },
                    ),
                    "set_hash": xarray.DataArray(
                        ["34e54a4fdffe134ecabe83f59f31be7f", "7827973d24662c3952157d9e3dd7aabc"],
                        dims=_set_coordinate_key,
                    ),
                }
            ).set_coords("set_hash"),
        ),
        "poisson disk: good schema 1x2": (
            "PoissonDisk",
            {
                "num_simulations": 1,
                "parameter_1": {"distribution": "uniform", "loc": 0, "scale": 10},
                "parameter_2": {"distribution": "uniform", "loc": 2, "scale": 3},
            },
            {"seed": 42},
            xarray.Dataset(
                {
                    "parameter_1": xarray.DataArray(
                        [7.73956049],
                        coords={_set_coordinate_key: xarray.DataArray(["parameter_set0"], dims=_set_coordinate_key)},
                    ),
                    "parameter_2": xarray.DataArray(
                        [3.31663532],
                        coords={_set_coordinate_key: xarray.DataArray(["parameter_set0"], dims=_set_coordinate_key)},
                    ),
                    "set_hash": xarray.DataArray(["a90d1ba8aa6786907bb5f8ef488b666f"], dims=_set_coordinate_key),
                }
            ).set_coords("set_hash"),
        ),
        "poisson disk: good schema 1x2, no seed": (
            "PoissonDisk",
            {
                "num_simulations": 1,
                "parameter_1": {"distribution": "uniform", "loc": 0, "scale": 10},
                "parameter_2": {"distribution": "uniform", "loc": 2, "scale": 3},
            },
            {},
            # Values will be different due to random seed, but parameter names and sets should be aligned
            xarray.Dataset(
                {
                    "parameter_1": xarray.DataArray(
                        [4.31029474],
                        coords={_set_coordinate_key: xarray.DataArray(["parameter_set0"], dims=_set_coordinate_key)},
                    ),
                    "parameter_2": xarray.DataArray(
                        [4.44310392],
                        coords={_set_coordinate_key: xarray.DataArray(["parameter_set0"], dims=_set_coordinate_key)},
                    ),
                    "set_hash": xarray.DataArray(["0f9510490d521d7fa85154245288622e"], dims=_set_coordinate_key),
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
        parameter_names = [key for key in parameter_schema if key != "num_simulations"]
        dtype_variants = [float, int, numpy.float32, numpy.float64, numpy.int64, numpy.int32, numpy.int16, numpy.int8]
        parameter_schema_dtype_variants = [
            {
                **parameter_schema,
                **{
                    key: {**val, "loc": dtype(val["loc"]), "scale": dtype(val["scale"])}
                    for key, val in parameter_schema.items()
                    if "parameter" in key
                },
            }
            for dtype in dtype_variants
        ]
        for schema in parameter_schema_dtype_variants:
            test_generate = ScipySampler(sampler, schema, **kwargs)
            if kwargs:
                xarray.testing.assert_allclose(test_generate.parameter_study, expected_dataset)
            # Check for type preservation
            for key in test_generate.parameter_study:
                assert test_generate.parameter_study[key].dtype == numpy.float64
            # Verify that the parameter set name creation method was called
            # TODO: _set_names is an ordered object (dictionary). Fix test to compare dictionary-to-dictionary instead
            # of implied consistency according to value order.
            assert list(test_generate._set_names.values()) == list(expected_dataset[_set_coordinate_key].to_numpy())
            # Check that the parameter names are correct
            assert parameter_names == test_generate._parameter_names
            assert parameter_names == list(test_generate.parameter_study.keys())

    merge_test = {
        "new sets": (
            {
                "num_simulations": 5,
                "parameter_1": {"distribution": "uniform", "loc": 0, "scale": 10},
                "parameter_2": {"distribution": "uniform", "loc": 2, "scale": 3},
            },
            {
                "num_simulations": 8,
                "parameter_1": {"distribution": "uniform", "loc": 0, "scale": 10},
                "parameter_2": {"distribution": "uniform", "loc": 2, "scale": 3},
            },
            {"seed": 42},
        ),
        "unchanged sets": (
            {
                "num_simulations": 5,
                "parameter_1": {"distribution": "uniform", "loc": 0, "scale": 10},
                "parameter_2": {"distribution": "uniform", "loc": 2, "scale": 3},
            },
            {
                "num_simulations": 5,
                "parameter_1": {"distribution": "uniform", "loc": 0, "scale": 10},
                "parameter_2": {"distribution": "uniform", "loc": 2, "scale": 3},
            },
            {"seed": 42},
        ),
    }

    @pytest.mark.parametrize(("first_schema", "second_schema", "kwargs"), merge_test.values(), ids=merge_test.keys())
    def test_merge(self, first_schema: dict, second_schema: dict, kwargs: dict) -> None:
        with patch("waves.parameter_generators._verify_parameter_study"):
            for sampler in _supported_scipy_samplers:
                original_study, merged_study = merge_samplers(
                    ScipySampler,
                    first_schema,
                    second_schema,
                    kwargs,
                    sampler,
                )
                merged_study._samples.astype(float)
                consistent_hash_parameter_check(original_study, merged_study)
                self_consistency_checks(merged_study)

    parameter_study_to_dict = {
        "good schema 1x2": (
            "LatinHypercube",
            {
                "num_simulations": 1,
                "parameter_1": {"distribution": "uniform", "loc": 0, "scale": 10},
                "parameter_2": {"distribution": "uniform", "loc": 2, "scale": 3},
            },
            {"seed": 42},
            {"parameter_set0": {"parameter_1": 2.2604395144403666, "parameter_2": 3.683364680743843}},
        )
    }

    @pytest.mark.parametrize(
        ("sampler", "parameter_schema", "kwargs", "expected_dictionary"),
        parameter_study_to_dict.values(),
        ids=parameter_study_to_dict.keys(),
    )
    def test_parameter_study_to_dict(
        self, sampler: str, parameter_schema: dict, kwargs: dict, expected_dictionary: dict
    ) -> None:
        """Test parameter study dictionary conversion."""
        test_parameter_study_dict = ScipySampler(sampler, parameter_schema, **kwargs)
        returned_dictionary = test_parameter_study_dict.parameter_study_to_dict()
        assert expected_dictionary.keys() == returned_dictionary.keys()
        assert all(isinstance(key, str) for key in returned_dictionary)
        for set_name, set_contents in expected_dictionary.items():
            assert set_contents == returned_dictionary[set_name]
            for parameter in set_contents:
                assert type(set_contents[parameter]) == type(  # noqa: E721
                    returned_dictionary[set_name][parameter]
                )
