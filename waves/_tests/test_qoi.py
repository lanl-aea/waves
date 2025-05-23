"""Test QOI module"""

import pathlib
from unittest.mock import patch, mock_open, Mock
from contextlib import nullcontext as does_not_raise

import pytest
import numpy
import xarray

from waves import qoi


test_create_qoi_cases = {
    "minimum input": (
        {"name": "qoi1"},
        xarray.DataArray(
            [numpy.nan, numpy.nan, numpy.nan, numpy.nan],
            coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
            name="qoi1",
            attrs={},
        ),
        does_not_raise(),
    ),
    "calculated": (
        {"name": "qoi1", "calculated": 5.0},
        xarray.DataArray(
            [5.0, numpy.nan, numpy.nan, numpy.nan],
            coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
            name="qoi1",
            attrs={},
        ),
        does_not_raise(),
    ),
    "expected": (
        {"name": "qoi1", "expected": 5.0},
        xarray.DataArray(
            [numpy.nan, 5.0, numpy.nan, numpy.nan],
            coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
            name="qoi1",
            attrs={},
        ),
        does_not_raise(),
    ),
    "full": (
        {"name": "qoi1", "calculated": 5.1, "expected": 5.0, "lower_limit": 4.0, "upper_limit": 6.0},
        xarray.DataArray(
            [5.1, 5.0, 4.0, 6.0],
            coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
            name="qoi1",
            attrs={},
        ),
        does_not_raise(),
    ),
    "relative tolerance determines lower limit": (
        {"name": "qoi1", "expected": 1.0, "lower_rtol": 0.1, "lower_atol": 0.2, "lower_limit": 0.5},
        xarray.DataArray(
            [numpy.nan, 1.0, 0.9, numpy.nan],
            coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
            name="qoi1",
            attrs={},
        ),
        does_not_raise(),
    ),
    "direct limit determines lower limit": (
        {"name": "qoi1", "expected": 1.0, "lower_rtol": 0.1, "lower_atol": 0.2, "lower_limit": 0.95},
        xarray.DataArray(
            [numpy.nan, 1.0, 0.95, numpy.nan],
            coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
            name="qoi1",
            attrs={},
        ),
        does_not_raise(),
    ),
    "absolute tolerance determines lower limit": (
        {"name": "qoi1", "expected": 1.0, "lower_rtol": 0.3, "lower_atol": 0.2, "lower_limit": 0.5},
        xarray.DataArray(
            [numpy.nan, 1.0, 0.8, numpy.nan],
            coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
            name="qoi1",
            attrs={},
        ),
        does_not_raise(),
    ),
    "lower_rtol, missing expected: should raise ValueError": (
        {"name": "qoi1", "lower_rtol": 1.0e-2},
        None,
        pytest.raises(ValueError),
    ),
    "upper_rtol, missing expected: should raise ValueError": (
        {"name": "qoi1", "upper_rtol": 1.0e-2},
        None,
        pytest.raises(ValueError),
    ),
    "lower_atol, missing expected: should raise ValueError": (
        {"name": "qoi1", "lower_atol": 1.0e-2},
        None,
        pytest.raises(ValueError),
    ),
    "upper_atol, missing expected: should raise ValueError": (
        {"name": "qoi1", "upper_atol": 1.0e-2},
        None,
        pytest.raises(ValueError),
    ),
    "lower > upper: should raise ValueError": (
        {"name": "qoi1", "lower_limit": 1.0, "upper_limit": -1.0},
        None,
        pytest.raises(ValueError),
    ),
}


@pytest.mark.parametrize(
    "kwargs, expected, outcome",
    test_create_qoi_cases.values(),
    ids=test_create_qoi_cases.keys(),
)
def test_create_qoi(kwargs, expected, outcome):
    with outcome:
        try:
            output = qoi.create_qoi(**kwargs)
            assert expected.identical(output)
        finally:
            pass


def test_create_qoi_set():
    pass


def test__create_qoi_study():
    pass


def test__qoi_group():
    pass


def test__create_qoi_archive():
    pass


def test__merge_qoi_archives():
    pass


def test__read_qoi_set():
    pass


def test__add_tolerance_attribute():
    pass


def test_write_qoi_set_to_csv():
    pass


def test__plot_qoi_tolerance_check():
    pass


def test__plot_scalar_tolerance_check():
    pass


def test__write_qoi_report():
    pass


def test__get_plotting_name():
    pass


def test__plot_scalar_qoi_history():
    pass


def test__qoi_history_report():
    pass


def test__get_commit_date():
    pass


def test__add_commit_date():
    pass


def test__sort_by_date():
    pass


def test__accept():
    pass


def test__check():
    pass


def test__diff():
    pass


def test__aggregate():
    pass


def test__report():
    pass


def test__plot_archive():
    pass


def test__archive():
    pass
