"""Test LatinHypercube Class."""

import typing
from unittest.mock import patch

import numpy
import pytest
import xarray

from waves._settings import _hash_coordinate_key, _set_coordinate_key
from waves._tests.common import merge_samplers
from waves.parameter_generators import LatinHypercube, ScipySampler


class TestLatinHypercube:
    """Class for testing LatinHypercube parameter study generator class."""

    generate_input = {
        "good schema 5x2": (
            {
                "num_simulations": 5,
                "parameter_1": {"distribution": "norm", "loc": 50, "scale": 1},
                "parameter_2": {"distribution": "norm", "loc": -50, "scale": 1},
            },
            42,
            xarray.Dataset(
                {
                    "parameter_1": xarray.DataArray(
                        [51.01609863, 48.09331069, 50.37931242, 50.20487353, 49.67971797],
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
                        [-51.21478363, -49.58609982, -50.14390653, -49.140834, -50.49606915],
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
                            "10a53f8bbab9abcd9538087ed75a554c",
                            "39c2bf5b15394faeae3e93dcd0a6725e",
                            "8b77d886a6636ea41b45e7a61dd6c2f9",
                            "9abbd4182b58a04464f8e4a1377c9e51",
                            "e515d1a7e6e352140a1a7ae86c5425e8",
                        ],
                        dims=_set_coordinate_key,
                    ),
                }
            ).set_coords("set_hash"),
            [{"loc": 50, "scale": 1}, {"loc": -50, "scale": 1}],
        ),
        "good schema 2x1": (
            {"num_simulations": 2, "parameter_1": {"distribution": "norm", "loc": 50, "scale": 1}},
            42,
            xarray.Dataset(
                {
                    "parameter_1": xarray.DataArray(
                        [49.41882358, 50.2872041],
                        coords={
                            _set_coordinate_key: xarray.DataArray(
                                ["parameter_set0", "parameter_set1"],
                                dims=_set_coordinate_key,
                            )
                        },
                    ),
                    "set_hash": xarray.DataArray(
                        ["57e4c109b2e72ad106455e7976b1a07f", "ed32dfec2e7e74b8edb368cfb7a548ba"],
                        dims=_set_coordinate_key,
                    ),
                }
            ).set_coords("set_hash"),
            [{"loc": 50, "scale": 1}],
        ),
        "good schema 1x2": (
            {
                "num_simulations": 1,
                "parameter_1": {"distribution": "norm", "loc": 50, "scale": 1},
                "parameter_2": {"distribution": "norm", "loc": -50, "scale": 1},
            },
            42,
            xarray.Dataset(
                {
                    "parameter_1": xarray.DataArray(
                        [49.24806127],
                        coords={_set_coordinate_key: xarray.DataArray(["parameter_set0"], dims=_set_coordinate_key)},
                    ),
                    "parameter_2": xarray.DataArray(
                        [-49.84618661],
                        coords={_set_coordinate_key: xarray.DataArray(["parameter_set0"], dims=_set_coordinate_key)},
                    ),
                    "set_hash": xarray.DataArray(["dca1ee590a69d20d5fe79641f0c00e8e"], dims=_set_coordinate_key),
                }
            ).set_coords("set_hash"),
            [{"loc": 50, "scale": 1}, {"loc": -50, "scale": 1}],
        ),
        "all numpy typing": (
            {
                "num_simulations": 1,
                "parameter_1": {"distribution": "norm", "loc": numpy.float64(50), "scale": numpy.int64(1)},
                "parameter_2": {"distribution": "norm", "loc": numpy.float64(-50), "scale": numpy.int64(1)},
            },
            42,
            xarray.Dataset(
                {
                    "parameter_1": xarray.DataArray(
                        [49.24806127],
                        coords={_set_coordinate_key: xarray.DataArray(["parameter_set0"], dims=_set_coordinate_key)},
                    ),
                    "parameter_2": xarray.DataArray(
                        [-49.84618661],
                        coords={_set_coordinate_key: xarray.DataArray(["parameter_set0"], dims=_set_coordinate_key)},
                    ),
                    "set_hash": xarray.DataArray(["dca1ee590a69d20d5fe79641f0c00e8e"], dims=_set_coordinate_key),
                }
            ).set_coords("set_hash"),
            [{"loc": 50, "scale": 1}, {"loc": -50, "scale": 1}],
        ),
        "mixed numpy typing": (
            {
                "num_simulations": 1,
                "parameter_1": {"distribution": "norm", "loc": numpy.float64(50), "scale": 1},
                "parameter_2": {"distribution": "norm", "loc": -50, "scale": numpy.int64(1)},
            },
            42,
            xarray.Dataset(
                {
                    "parameter_1": xarray.DataArray(
                        [49.24806127],
                        coords={_set_coordinate_key: xarray.DataArray(["parameter_set0"], dims=_set_coordinate_key)},
                    ),
                    "parameter_2": xarray.DataArray(
                        [-49.84618661],
                        coords={_set_coordinate_key: xarray.DataArray(["parameter_set0"], dims=_set_coordinate_key)},
                    ),
                    "set_hash": xarray.DataArray(["dca1ee590a69d20d5fe79641f0c00e8e"], dims=_set_coordinate_key),
                }
            ).set_coords("set_hash"),
            [{"loc": 50, "scale": 1}, {"loc": -50, "scale": 1}],
        ),
        "all built-in typing": (
            {
                "num_simulations": 1,
                "parameter_1": {"distribution": "norm", "loc": 50, "scale": 1},
                "parameter_2": {"distribution": "norm", "loc": -50, "scale": 1},
            },
            42,
            xarray.Dataset(
                {
                    "parameter_1": xarray.DataArray(
                        [49.24806127],
                        coords={_set_coordinate_key: xarray.DataArray(["parameter_set0"], dims=_set_coordinate_key)},
                    ),
                    "parameter_2": xarray.DataArray(
                        [-49.84618661],
                        coords={_set_coordinate_key: xarray.DataArray(["parameter_set0"], dims=_set_coordinate_key)},
                    ),
                    "set_hash": xarray.DataArray(["dca1ee590a69d20d5fe79641f0c00e8e"], dims=_set_coordinate_key),
                }
            ).set_coords("set_hash"),
            [{"loc": 50, "scale": 1}, {"loc": -50, "scale": 1}],
        ),
    }

    @pytest.mark.parametrize(
        ("parameter_schema", "seed", "expected_dataset", "expected_scipy_kwds"),
        generate_input.values(),
        ids=generate_input.keys(),
    )
    def test_generate(
        self,
        parameter_schema: dict,
        seed: int,
        expected_dataset: xarray.Dataset,
        expected_scipy_kwds: list[dict[str, typing.Any]],
    ) -> None:
        """Test specific instances of LHC generator.

        Test specific instances of the generator to protect against any generator-specific behavior that could
        accidentally break the assumed behavior of the scipy base class.

        :param parameter_schema: dictionary schema defining number of simulations and the parameter distributions
        :param seed: integer randomization seed to ensure consistent test output
        :param expected_dataset: numpy array of the expected parameter study samples.
        :param expected_scipy_kwds: list containing dictionaries of each parameter, with keywords defining the
            statistical distribution of samples.
        """
        parameter_names = [key for key in parameter_schema if key != "num_simulations"]
        kwargs = {"seed": seed}
        generator_classes = (
            LatinHypercube(parameter_schema, **kwargs),
            ScipySampler("LatinHypercube", parameter_schema, **kwargs),
        )
        for test_generate in generator_classes:
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
            for parameter_name, expected_kwds in zip(parameter_names, expected_scipy_kwds, strict=True):
                assert test_generate.parameter_distributions[parameter_name].kwds == expected_kwds

    merge_test = {
        "increase simulations": (
            {
                "num_simulations": 1,
                "parameter_1": {"distribution": "norm", "loc": 50, "scale": 1},
                "parameter_2": {"distribution": "norm", "loc": -50, "scale": 1},
            },
            {
                "num_simulations": 2,
                "parameter_1": {"distribution": "norm", "loc": 50, "scale": 1},
                "parameter_2": {"distribution": "norm", "loc": -50, "scale": 1},
            },
            42,
            numpy.array(
                [
                    [49.24806127, -49.84618661],
                    [50.17815924, -49.61112421],
                    [48.7893875, -50.58117642],
                ],
            ),
        ),
    }

    @pytest.mark.parametrize(
        ("first_schema", "second_schema", "seed", "expected_samples"),
        merge_test.values(),
        ids=merge_test.keys(),
    )
    def test_merge(self, first_schema: dict, second_schema: dict, seed: int, expected_samples: numpy.ndarray) -> None:
        with patch("waves.parameter_generators._verify_parameter_study"):
            # LatinHypercube
            kwargs = {"seed": seed}
            test_merge1, test_merge2 = merge_samplers(LatinHypercube, first_schema, second_schema, kwargs)
            samples = test_merge2._samples.astype(float)
            # Sort flattens the array if no axis is provided.
            # We must preserve set contents (rows), so must sort on columns.
            # The unindexed set order doesn't matter, so sorting on columns doesn't impact these assertions
            assert numpy.allclose(numpy.sort(samples, axis=0), numpy.sort(expected_samples, axis=0))
            # Check for type preservation
            for key in test_merge2.parameter_study:
                assert test_merge2.parameter_study[key].dtype == numpy.float64
            # Check for consistent hash-parameter set relationships
            for set_name, parameters in test_merge1.parameter_study.groupby(_set_coordinate_key):
                assert parameters == test_merge2.parameter_study.sel({_set_coordinate_key: set_name})
            # Self-consistency checks
            assert (
                list(test_merge2._set_names.values())
                == test_merge2.parameter_study[_set_coordinate_key].values.tolist()
            )
            assert test_merge2._set_hashes == test_merge2.parameter_study[_hash_coordinate_key].values.tolist()

            # ScipySampler
            test_merge1, test_merge2 = merge_samplers(
                ScipySampler, first_schema, second_schema, kwargs, sampler="LatinHypercube"
            )
            samples = test_merge2._samples.astype(float)
            # Sort flattens the array if no axis is provided.
            # We must preserve set contents (rows), so must sort on columns.
            # The unindexed set order doesn't matter, so sorting on columns doesn't impact these assertions
            assert numpy.allclose(numpy.sort(samples, axis=0), numpy.sort(expected_samples, axis=0))
            # Check for consistent hash-parameter set relationships
            for set_name, parameters in test_merge1.parameter_study.groupby(_set_coordinate_key):
                assert parameters == test_merge2.parameter_study.sel(set_name=set_name)
            # Self-consistency checks
            assert (
                list(test_merge2._set_names.values())
                == test_merge2.parameter_study[_set_coordinate_key].values.tolist()
            )
            assert test_merge2._set_hashes == test_merge2.parameter_study[_hash_coordinate_key].values.tolist()
