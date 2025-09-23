"""Test ScipySampler Class."""

from unittest.mock import patch

import numpy
import pytest

from waves._settings import _set_coordinate_key, _supported_scipy_samplers
from waves._tests.common import consistent_hash_parameter_check, merge_samplers, self_consistency_checks
from waves.parameter_generators import ScipySampler


class TestScipySampler:
    """Class for testing Scipy Sequence parameter study generator class."""

    generate_input = {
        "good schema 5x2": (
            {
                "num_simulations": 5,
                "parameter_1": {"distribution": "uniform", "loc": 0, "scale": 10},
                "parameter_2": {"distribution": "uniform", "loc": 2, "scale": 3},
            },
            {"seed": 42},
        ),
        "good schema 2x1": (
            {
                "num_simulations": 2,
                "parameter_1": {"distribution": "uniform", "loc": 0, "scale": 10},
            },
            {"seed": 42},
        ),
        "good schema 1x2": (
            {
                "num_simulations": 1,
                "parameter_1": {"distribution": "uniform", "loc": 0, "scale": 10},
                "parameter_2": {"distribution": "uniform", "loc": 2, "scale": 3},
            },
            {"seed": 42},
        ),
        "good schema 1x2, no seed": (
            {
                "num_simulations": 1,
                "parameter_1": {"distribution": "uniform", "loc": 0, "scale": 10},
                "parameter_2": {"distribution": "uniform", "loc": 2, "scale": 3},
            },
            {},
        ),
    }

    @pytest.mark.parametrize(
        ("parameter_schema", "kwargs"),
        generate_input.values(),
        ids=generate_input.keys(),
    )
    def test_generate(self, parameter_schema: dict, kwargs: dict) -> None:
        parameter_names = [key for key in parameter_schema if key != "num_simulations"]
        for sampler in _supported_scipy_samplers:
            # NOTE: we cannot test the samples array while simulateously iterating over available samplers because each
            # sampler will produce different samples arrays. To test expected sample arrays we must separate the test
            # expectations with hardcoded duplicate tests, one per sampler.
            test_generate = ScipySampler(sampler, parameter_schema, **kwargs)
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
