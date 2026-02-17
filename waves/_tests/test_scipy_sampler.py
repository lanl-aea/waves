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
                        [4.31],
                        coords={_set_coordinate_key: xarray.DataArray(["parameter_set0"], dims=_set_coordinate_key)},
                    ),
                    "parameter_2": xarray.DataArray(
                        [4.443],
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
            None,
        ),
    }

    @pytest.mark.parametrize(
        ("sampler", "parameter_schema", "kwargs", "expected_dataset"),
        generate_input.values(),
        ids=generate_input.keys(),
    )
    def test_generate(self, sampler: str, parameter_schema: dict, kwargs: dict, expected_dataset: xarray.Dataset) -> None:
        parameter_names = [key for key in parameter_schema if key != "num_simulations"]
        test_generate = ScipySampler(sampler, parameter_schema, **kwargs)
        if expected_dataset is not None:
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
