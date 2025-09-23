"""Test LatinHypercube Class."""

import typing
from unittest.mock import patch

import numpy
import pytest

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
            numpy.array(
                [
                    [51.01609863, -51.21478363],
                    [48.09331069, -49.58609982],
                    [50.20487353, -49.140834],
                    [50.37931242, -50.14390653],
                    [49.67971797, -50.49606915],
                ]
            ),
            [{"loc": 50, "scale": 1}, {"loc": -50, "scale": 1}],
        ),
        "good schema 2x1": (
            {
                "num_simulations": 2,
                "parameter_1": {"distribution": "norm", "loc": 50, "scale": 1},
            },
            42,
            numpy.array([[50.2872041], [49.41882358]]),
            [{"loc": 50, "scale": 1}],
        ),
        "good schema 1x2": (
            {
                "num_simulations": 1,
                "parameter_1": {"distribution": "norm", "loc": 50, "scale": 1},
                "parameter_2": {"distribution": "norm", "loc": -50, "scale": 1},
            },
            42,
            numpy.array([[49.24806127, -49.84618661]]),
            [{"loc": 50, "scale": 1}, {"loc": -50, "scale": 1}],
        ),
    }

    @pytest.mark.parametrize(
        ("parameter_schema", "seed", "expected_samples", "expected_scipy_kwds"),
        generate_input.values(),
        ids=generate_input.keys(),
    )
    def test_generate(
        self,
        parameter_schema: dict,
        seed: int,
        expected_samples: numpy.ndarray,
        # FIXME: trace the original use of the ``expected_scipy_kwds`` variable and either use in tests or remove.
        # Remove ``noqa: ARG002`` after fixing.
        # https://re-git.lanl.gov/aea/python-projects/waves/-/issues/960
        expected_scipy_kwds: list[dict[str, typing.Any]],  # noqa: ARG002
    ) -> None:
        parameter_names = [key for key in parameter_schema if key != "num_simulations"]
        kwargs = {"seed": seed}
        generator_classes = (
            LatinHypercube(parameter_schema, **kwargs),
            ScipySampler("LatinHypercube", parameter_schema, **kwargs),
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
