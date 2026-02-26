"""Test Sobol Sequence Class."""

from unittest.mock import patch

import numpy
import pytest
import xarray

from waves._settings import _set_coordinate_key
from waves._tests.common import consistent_hash_parameter_check, merge_samplers, self_consistency_checks
from waves.parameter_generators import ScipySampler, SobolSequence


class TestSobolSequence:
    """Class for testing Sobol Sequence parameter study generator class."""

    generate_input = {
        "good schema 5x2": (
            {
                "num_simulations": 5,
                "parameter_1": {"distribution": "uniform", "loc": 0, "scale": 10},
                "parameter_2": {"distribution": "uniform", "loc": 2, "scale": 3},
            },
            {"scramble": False},
            xarray.Dataset(
                {
                    "parameter_1": xarray.DataArray(
                        [2.5, 5.0, 0.0, 7.5, 3.75],
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
                        [4.25, 3.5, 2.0, 2.75, 3.125],
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
                            "30c106960a1999a14008b4bac5b43a58",
                            "57a50989a94588be7fdd031cefc501bc",
                            "aa5e177c64820d6c5e66aacff18e8a6a",
                            "abaa63f291be5c1696ce61d66209170a",
                            "c85431f047d29a3b4afe859b42311a4f",
                        ],
                        dims=_set_coordinate_key,
                    ),
                }
            ).set_coords("set_hash"),
        ),
        "good schema 2x1": (
            {"num_simulations": 2, "parameter_1": {"distribution": "uniform", "loc": 0, "scale": 10}},
            {"scramble": False},
            xarray.Dataset(
                {
                    "parameter_1": xarray.DataArray(
                        [0.0, 5.0],
                        coords={
                            _set_coordinate_key: xarray.DataArray(
                                ["parameter_set0", "parameter_set1"],
                                dims=_set_coordinate_key,
                            )
                        },
                    ),
                    "set_hash": xarray.DataArray(
                        ["b08c7e57b1d886e1189831a70f4ad003", "dd47d104ad348384b03e863b221e9d05"],
                        dims=_set_coordinate_key,
                    ),
                }
            ).set_coords("set_hash"),
        ),
        "good schema 1x2": (
            {
                "num_simulations": 1,
                "parameter_1": {"distribution": "uniform", "loc": 0, "scale": 10},
                "parameter_2": {"distribution": "uniform", "loc": 2, "scale": 3},
            },
            {"scramble": False},
            xarray.Dataset(
                {
                    "parameter_1": xarray.DataArray(
                        [0.0],
                        coords={_set_coordinate_key: xarray.DataArray(["parameter_set0"], dims=_set_coordinate_key)},
                    ),
                    "parameter_2": xarray.DataArray(
                        [2.0],
                        coords={_set_coordinate_key: xarray.DataArray(["parameter_set0"], dims=_set_coordinate_key)},
                    ),
                    "set_hash": xarray.DataArray(["aa5e177c64820d6c5e66aacff18e8a6a"], dims=_set_coordinate_key),
                }
            ).set_coords("set_hash"),
        ),
    }

    @pytest.mark.parametrize(
        ("parameter_schema", "kwargs", "expected_dataset"),
        generate_input.values(),
        ids=generate_input.keys(),
    )
    def test_generate(self, parameter_schema: dict, kwargs: dict, expected_dataset: xarray.Dataset) -> None:
        parameter_names = [key for key in parameter_schema if key != "num_simulations"]
        generator_classes = (
            SobolSequence(parameter_schema, **kwargs),
            ScipySampler("Sobol", parameter_schema, **kwargs),
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
            {"scramble": False},
            # Ordered by md5 hash during Xarray merge operation. New tests must verify hash ordering.
            numpy.array(
                [
                    [1.25, 3.875],
                    [5.0, 3.5],
                    [2.5, 4.25],
                    [3.75, 3.125],
                    [8.75, 4.625],
                    [6.25, 2.375],
                    [7.5, 2.75],
                    [0.0, 2.0],
                ],
            ),
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
            {"scramble": False},
            # Ordered by md5 hash during Xarray merge operation. New tests must verify hash ordering.
            numpy.array(
                [
                    [5.0, 3.5],
                    [2.5, 4.25],
                    [3.75, 3.125],
                    [7.5, 2.75],
                    [0.0, 2.0],
                ],
            ),
        ),
    }

    @pytest.mark.parametrize(
        ("first_schema", "second_schema", "kwargs", "expected_samples"),
        merge_test.values(),
        ids=merge_test.keys(),
    )
    def test_merge(
        self, first_schema: dict, second_schema: dict, kwargs: dict, expected_samples: numpy.ndarray
    ) -> None:
        with patch("waves.parameter_generators._verify_parameter_study"):
            # Sobol
            original_study, merged_study = merge_samplers(SobolSequence, first_schema, second_schema, kwargs)
            samples_array = merged_study._samples.astype(float)
            # Sort flattens the array if no axis is provided.
            # We must preserve set contents (rows), so must sort on columns.
            # The unindexed set order doesn't matter, so sorting on columns doesn't impact these assertions
            assert numpy.allclose(numpy.sort(samples_array, axis=0), numpy.sort(expected_samples, axis=0))
            # Check for type preservation
            for key in merged_study.parameter_study:
                assert merged_study.parameter_study[key].dtype == numpy.float64
            consistent_hash_parameter_check(original_study, merged_study)
            self_consistency_checks(merged_study)

            # ScipySampler
            original_study, merged_study = merge_samplers(
                ScipySampler, first_schema, second_schema, kwargs, sampler="Sobol"
            )
            samples_array = merged_study._samples.astype(float)
            # Sort flattens the array if no axis is provided.
            # We must preserve set contents (rows), so must sort on columns.
            # The unindexed set order doesn't matter, so sorting on columns doesn't impact these assertions
            assert numpy.allclose(numpy.sort(samples_array, axis=0), numpy.sort(expected_samples, axis=0))
            # Check for type preservation
            for key in merged_study.parameter_study:
                assert merged_study.parameter_study[key].dtype == numpy.float64
            consistent_hash_parameter_check(original_study, merged_study)
            self_consistency_checks(merged_study)
