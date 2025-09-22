"""Test Sobol Sequence Class."""

from unittest.mock import patch

import numpy
import pytest

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
            numpy.array(
                [
                    [0.0, 2.0],
                    [5.0, 3.5],
                    [7.5, 2.75],
                    [2.5, 4.25],
                    [3.75, 3.125],
                ],
            ),
        ),
        "good schema 2x1": (
            {
                "num_simulations": 2,
                "parameter_1": {"distribution": "uniform", "loc": 0, "scale": 10},
            },
            {"scramble": False},
            numpy.array([[0.0], [5.0]]),
        ),
        "good schema 1x2": (
            {
                "num_simulations": 1,
                "parameter_1": {"distribution": "uniform", "loc": 0, "scale": 10},
                "parameter_2": {"distribution": "uniform", "loc": 2, "scale": 3},
            },
            {"scramble": False},
            numpy.array([[0.0, 2.0]]),
        ),
    }

    @pytest.mark.parametrize(
        ("parameter_schema", "kwargs", "expected_samples"),
        generate_input.values(),
        ids=generate_input.keys(),
    )
    def test_generate(self, parameter_schema: dict, kwargs: dict, expected_samples: numpy.array) -> None:
        parameter_names = [key for key in parameter_schema if key != "num_simulations"]
        generator_classes = (
            SobolSequence(parameter_schema, **kwargs),
            ScipySampler("Sobol", parameter_schema, **kwargs),
        )
        for test_generate in generator_classes:
            samples_array = test_generate._samples
            assert numpy.allclose(samples_array, expected_samples)
            # Check for type preservation
            for key in test_generate.parameter_study:
                assert test_generate.parameter_study[key].dtype == numpy.float64
            # Verify that the parameter set name creation method was called
            expected_set_names = [f"parameter_set{num}" for num in range(parameter_schema["num_simulations"])]
            assert list(test_generate._set_names.values()) == expected_set_names
            # Check that the parameter set names are correctly populated in the parameter study Xarray Dataset
            expected_set_names = [f"parameter_set{num}" for num in range(parameter_schema["num_simulations"])]
            set_names = list(test_generate.parameter_study[_set_coordinate_key])
            assert numpy.all(set_names == expected_set_names)
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
    def test_merge(self, first_schema: dict, second_schema: dict, kwargs: dict, expected_samples: numpy.array) -> None:
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
