"""Test QOI module"""

import io
import os
import pathlib
import datetime
from unittest.mock import patch, Mock
from contextlib import nullcontext as does_not_raise

import numpy
import pandas
import pytest
import xarray

from waves import qoi
from waves import parameter_generators


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
    "recommended attrs": (
        {
            "name": "qoi1",
            "calculated": 5.1,
            "expected": 5.0,
            "lower_limit": 4.0,
            "upper_limit": 6.0,
            "group": "group1",
            "units": "units1",
            "description": "description1",
            "long_name": "long_name1",
            "version": "version1",
        },
        xarray.DataArray(
            [5.1, 5.0, 4.0, 6.0],
            coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
            name="qoi1",
            attrs={
                "group": "group1",
                "units": "units1",
                "description": "description1",
                "long_name": "long_name1",
                "version": "version1",
            },
        ),
        does_not_raise(),
    ),
    "custom attrs": (
        {"name": "qoi1", "someotherattr": "someotherattrvalue"},
        xarray.DataArray(
            [numpy.nan, numpy.nan, numpy.nan, numpy.nan],
            coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
            name="qoi1",
            attrs={"someotherattr": "someotherattrvalue"},
        ),
        does_not_raise(),
    ),
    "date attrs": (
        {"name": "qoi1", "date": "2025-05-23"},
        xarray.DataArray(
            [numpy.nan, numpy.nan, numpy.nan, numpy.nan],
            coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
            name="qoi1",
            attrs={"date": "2025-05-23"},
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
    "relative tolerance determines upper limit": (
        {"name": "qoi1", "expected": 1.0, "upper_rtol": 0.1, "upper_atol": 0.2, "upper_limit": 1.5},
        xarray.DataArray(
            [numpy.nan, 1.0, numpy.nan, 1.1],
            coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
            name="qoi1",
            attrs={},
        ),
        does_not_raise(),
    ),
    "absolute tolerance determines upper limit": (
        {"name": "qoi1", "expected": 1.0, "upper_rtol": 0.3, "upper_atol": 0.2, "upper_limit": 1.5},
        xarray.DataArray(
            [numpy.nan, 1.0, numpy.nan, 1.2],
            coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
            name="qoi1",
            attrs={},
        ),
        does_not_raise(),
    ),
    "direct limit determines upper limit": (
        {"name": "qoi1", "expected": 1.0, "upper_rtol": 0.1, "upper_atol": 0.2, "upper_limit": 1.05},
        xarray.DataArray(
            [numpy.nan, 1.0, numpy.nan, 1.05],
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


test_create_qoi_set_cases = {
    "one qoi": (
        [
            xarray.DataArray(
                [numpy.nan, numpy.nan, numpy.nan, numpy.nan],
                coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
                name="qoi1",
                attrs={"attr1": "value1"},
            ),
        ],
        xarray.Dataset(
            {
                "qoi1": xarray.DataArray(
                    [numpy.nan, numpy.nan, numpy.nan, numpy.nan],
                    coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
                    attrs={"attr1": "value1"},
                ),
            },
            coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
            attrs={},
        ),
    ),
    "one qoi: using ``create_qoi``": (
        [qoi.create_qoi(name="qoi1", attr1="value1")],
        xarray.Dataset(
            {
                "qoi1": xarray.DataArray(
                    [numpy.nan, numpy.nan, numpy.nan, numpy.nan],
                    coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
                    attrs={"attr1": "value1"},
                ),
            },
            coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
            attrs={},
        ),
    ),
    "two qoi": (
        [
            xarray.DataArray(
                [numpy.nan, numpy.nan, numpy.nan, numpy.nan],
                coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
                name="qoi1",
                attrs={"attr1": "value1"},
            ),
            xarray.DataArray(
                [numpy.nan, numpy.nan, numpy.nan, numpy.nan],
                coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
                name="qoi2",
                attrs={"attr1": "value2"},
            ),
        ],
        xarray.Dataset(
            {
                "qoi1": xarray.DataArray(
                    [numpy.nan, numpy.nan, numpy.nan, numpy.nan],
                    coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
                    attrs={"attr1": "value1"},
                ),
                "qoi2": xarray.DataArray(
                    [numpy.nan, numpy.nan, numpy.nan, numpy.nan],
                    coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
                    attrs={"attr1": "value2"},
                ),
            },
            coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
            attrs={},
        ),
    ),
    "two qoi: using ``create_qoi``": (
        [qoi.create_qoi(name="qoi1", attr1="value1"), qoi.create_qoi(name="qoi2", attr1="value2")],
        xarray.Dataset(
            {
                "qoi1": xarray.DataArray(
                    [numpy.nan, numpy.nan, numpy.nan, numpy.nan],
                    coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
                    attrs={"attr1": "value1"},
                ),
                "qoi2": xarray.DataArray(
                    [numpy.nan, numpy.nan, numpy.nan, numpy.nan],
                    coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
                    attrs={"attr1": "value2"},
                ),
            },
            coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
            attrs={},
        ),
    ),
    "propagate_identical": (
        [
            xarray.DataArray(
                [numpy.nan, numpy.nan, numpy.nan, numpy.nan],
                coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
                name="qoi1",
                attrs={"conflict": "value1", "noconflict": "shouldexist"},
            ),
            xarray.DataArray(
                [numpy.nan, numpy.nan, numpy.nan, numpy.nan],
                coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
                name="qoi1",
                attrs={"conflict": "value2"},
            ),
        ],
        xarray.Dataset(
            {
                "qoi1": xarray.DataArray(
                    [numpy.nan, numpy.nan, numpy.nan, numpy.nan],
                    coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
                    attrs={},
                ),
            },
            coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
            attrs={},
        ),
    ),
}


@pytest.mark.parametrize(
    "qoi_list, expected",
    test_create_qoi_set_cases.values(),
    ids=test_create_qoi_set_cases.keys(),
)
def test_create_qoi_set(qoi_list, expected):
    output = qoi.create_qoi_set(qoi_list)
    assert expected.identical(output)


test__create_qoi_study_cases = {
    "one qoi": (
        [
            xarray.DataArray(
                [numpy.nan, numpy.nan, numpy.nan, numpy.nan],
                coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
                name="qoi1",
                attrs={"set_name": "set_0", "attr1": "value1"},
            ),
        ],
        None,
        xarray.Dataset(
            {
                "qoi1": xarray.DataArray(
                    [[numpy.nan, numpy.nan, numpy.nan, numpy.nan]],
                    coords={
                        "set_name": ["set_0"],
                        "value_type": ["calculated", "expected", "lower_limit", "upper_limit"],
                    },
                    attrs={"set_name": "set_0", "attr1": "value1"},
                ),
            },
            coords={
                "value_type": ["calculated", "expected", "lower_limit", "upper_limit"],
            },
            attrs={},
        ),
        does_not_raise(),
    ),
    "one qoi: using ``create_qoi``": (
        [qoi.create_qoi(name="qoi1", attr1="value1", set_name="set_0")],
        None,
        xarray.Dataset(
            {
                "qoi1": xarray.DataArray(
                    [[numpy.nan, numpy.nan, numpy.nan, numpy.nan]],
                    coords={
                        "set_name": ["set_0"],
                        "value_type": ["calculated", "expected", "lower_limit", "upper_limit"],
                    },
                    attrs={"set_name": "set_0", "attr1": "value1"},
                ),
            },
            coords={
                "value_type": ["calculated", "expected", "lower_limit", "upper_limit"],
            },
            attrs={},
        ),
        does_not_raise(),
    ),
    "one qoi and a parameter study": (
        [qoi.create_qoi(name="qoi1", attr1="value1", set_name="set_0")],
        parameter_generators.CustomStudy(
            {"parameter_samples": [[1.0, 2.0]], "parameter_names": ["parameter_1", "parameter_2"]},
            set_name_template="set_@number",
        ).parameter_study,
        xarray.Dataset(
            {
                "qoi1": xarray.DataArray(
                    [[numpy.nan, numpy.nan, numpy.nan, numpy.nan]],
                    coords={
                        "set_name": ["set_0"],
                        "value_type": ["calculated", "expected", "lower_limit", "upper_limit"],
                    },
                    attrs={"set_name": "set_0", "attr1": "value1"},
                ),
                "set_hash": xarray.DataArray(["30b1b83a463b6ec2a285675a02b6c303"], coords={"set_name": ["set_0"]}),
                "parameter_1": xarray.DataArray([1.0], coords={"set_name": ["set_0"]}),
                "parameter_2": xarray.DataArray([2.0], coords={"set_name": ["set_0"]}),
            },
            coords={
                "set_name": ["set_0"],
                "value_type": ["calculated", "expected", "lower_limit", "upper_limit"],
            },
            attrs={},
        ).set_coords(["set_hash", "parameter_1", "parameter_2"]),
        does_not_raise(),
    ),
    "two qoi: different names, same set": (
        [
            xarray.DataArray(
                [numpy.nan, numpy.nan, numpy.nan, numpy.nan],
                coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
                name="qoi1",
                attrs={"set_name": "set_0", "attr1": "value1"},
            ),
            xarray.DataArray(
                [numpy.nan, numpy.nan, numpy.nan, numpy.nan],
                coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
                name="qoi2",
                attrs={"set_name": "set_0", "attr1": "value2"},
            ),
        ],
        None,
        xarray.Dataset(
            {
                "qoi1": xarray.DataArray(
                    [[numpy.nan, numpy.nan, numpy.nan, numpy.nan]],
                    coords={
                        "set_name": ["set_0"],
                        "value_type": ["calculated", "expected", "lower_limit", "upper_limit"],
                    },
                    attrs={"set_name": "set_0", "attr1": "value1"},
                ),
                "qoi2": xarray.DataArray(
                    [[numpy.nan, numpy.nan, numpy.nan, numpy.nan]],
                    coords={
                        "set_name": ["set_0"],
                        "value_type": ["calculated", "expected", "lower_limit", "upper_limit"],
                    },
                    attrs={"set_name": "set_0", "attr1": "value2"},
                ),
            },
            coords={
                "value_type": ["calculated", "expected", "lower_limit", "upper_limit"],
            },
            attrs={},
        ),
        does_not_raise(),
    ),
    "two qoi: different names, same set: using ``create_qoi``": (
        [
            qoi.create_qoi(name="qoi1", attr1="value1", set_name="set_0"),
            qoi.create_qoi(name="qoi2", attr1="value2", set_name="set_0"),
        ],
        None,
        xarray.Dataset(
            {
                "qoi1": xarray.DataArray(
                    [[numpy.nan, numpy.nan, numpy.nan, numpy.nan]],
                    coords={
                        "set_name": ["set_0"],
                        "value_type": ["calculated", "expected", "lower_limit", "upper_limit"],
                    },
                    attrs={"set_name": "set_0", "attr1": "value1"},
                ),
                "qoi2": xarray.DataArray(
                    [[numpy.nan, numpy.nan, numpy.nan, numpy.nan]],
                    coords={
                        "set_name": ["set_0"],
                        "value_type": ["calculated", "expected", "lower_limit", "upper_limit"],
                    },
                    attrs={"set_name": "set_0", "attr1": "value2"},
                ),
            },
            coords={
                "value_type": ["calculated", "expected", "lower_limit", "upper_limit"],
            },
            attrs={},
        ),
        does_not_raise(),
    ),
    "two qoi: same names, different sets": (
        [
            xarray.DataArray(
                [1.0, numpy.nan, numpy.nan, numpy.nan],
                coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
                name="qoi1",
                attrs={"set_name": "set_0", "attr1": "value1"},
            ),
            xarray.DataArray(
                [10.0, numpy.nan, numpy.nan, numpy.nan],
                coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
                name="qoi1",
                attrs={"set_name": "set_1", "attr1": "value2"},
            ),
        ],
        None,
        xarray.Dataset(
            {
                "qoi1": xarray.DataArray(
                    [
                        [1.0, numpy.nan, numpy.nan, numpy.nan],
                        [10.0, numpy.nan, numpy.nan, numpy.nan],
                    ],
                    coords={
                        "set_name": ["set_0", "set_1"],
                        "value_type": ["calculated", "expected", "lower_limit", "upper_limit"],
                    },
                    attrs={},
                ),
            },
            coords={
                "value_type": ["calculated", "expected", "lower_limit", "upper_limit"],
            },
            attrs={},
        ),
        does_not_raise(),
    ),
    "two qoi: same names, different sets: and a parameter study": (
        [
            xarray.DataArray(
                [1.0, numpy.nan, numpy.nan, numpy.nan],
                coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
                name="qoi1",
                attrs={"set_name": "set_0", "attr1": "value1"},
            ),
            xarray.DataArray(
                [10.0, numpy.nan, numpy.nan, numpy.nan],
                coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
                name="qoi1",
                attrs={"set_name": "set_1", "attr1": "value2"},
            ),
        ],
        parameter_generators.CustomStudy(
            {"parameter_samples": [[1.0, 2.0], [10.0, 20.0]], "parameter_names": ["parameter_1", "parameter_2"]},
            set_name_template="set_@number",
        ).parameter_study,
        xarray.Dataset(
            {
                "qoi1": xarray.DataArray(
                    [
                        [1.0, numpy.nan, numpy.nan, numpy.nan],
                        [10.0, numpy.nan, numpy.nan, numpy.nan],
                    ],
                    coords={
                        "set_name": ["set_0", "set_1"],
                        "value_type": ["calculated", "expected", "lower_limit", "upper_limit"],
                    },
                    attrs={},
                ),
                "set_hash": xarray.DataArray(
                    ["30b1b83a463b6ec2a285675a02b6c303", "5394e4ab1f5becd55700e840244214d5"],
                    coords={"set_name": ["set_0", "set_1"]},
                ),
                "parameter_1": xarray.DataArray([1.0, 10.0], coords={"set_name": ["set_0", "set_1"]}),
                "parameter_2": xarray.DataArray([2.0, 20.0], coords={"set_name": ["set_0", "set_1"]}),
            },
            coords={
                "value_type": ["calculated", "expected", "lower_limit", "upper_limit"],
            },
            attrs={},
        ).set_coords(["set_hash", "parameter_1", "parameter_2"]),
        does_not_raise(),
    ),
    "one qoi: missing ``set_name`` attribute should raise RuntimeError": (
        [
            xarray.DataArray(
                [numpy.nan, numpy.nan, numpy.nan, numpy.nan],
                coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
                name="qoi1",
                attrs={"attr1": "value1"},
            ),
        ],
        None,
        None,
        pytest.raises(RuntimeError),
    ),
    "two qoi: one is missing ``set_name`` attribute should raise RuntimeError": (
        [
            xarray.DataArray(
                [numpy.nan, numpy.nan, numpy.nan, numpy.nan],
                coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
                name="qoi1",
                attrs={"set_name": "set_0", "attr1": "value1"},
            ),
            xarray.DataArray(
                [numpy.nan, numpy.nan, numpy.nan, numpy.nan],
                coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
                name="qoi1",
                attrs={"attr1": "value1"},
            ),
        ],
        None,
        None,
        pytest.raises(RuntimeError),
    ),
}


@pytest.mark.parametrize(
    "qoi_list, parameter_study, expected, outcome",
    test__create_qoi_study_cases.values(),
    ids=test__create_qoi_study_cases.keys(),
)
def test__create_qoi_study(qoi_list, parameter_study, expected, outcome) -> None:
    with outcome:
        try:
            qoi_study = qoi._create_qoi_study(qoi_list, parameter_study)
            assert expected.identical(qoi_study)
        finally:
            pass


test__qoi_group_cases = {
    "expected use": (
        xarray.Dataset(
            {
                "qoi1": xarray.DataArray(
                    [numpy.nan, numpy.nan, numpy.nan, numpy.nan],
                    coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
                    attrs={"attr1": "value1"},
                ),
            },
            coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
            attrs={"group": "group1"},
        ),
        "group1",
        does_not_raise(),
    ),
    "missing dataset 'group' attr: should raise KeyError": (
        xarray.Dataset(
            {
                "qoi1": xarray.DataArray(
                    [numpy.nan, numpy.nan, numpy.nan, numpy.nan],
                    coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
                    attrs={"attr1": "value1", "group": "group1"},
                ),
            },
            coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
            attrs={},
        ),
        None,
        pytest.raises(KeyError),
    ),
}


@pytest.mark.parametrize(
    "qoi_set, expected, outcome",
    test__qoi_group_cases.values(),
    ids=test__qoi_group_cases.keys(),
)
def test__qoi_group(qoi_set, expected, outcome):
    with outcome:
        try:
            group = qoi._qoi_group(qoi_set)
            assert group == expected
        finally:
            pass


test__node_path_cases = {
    "expected use": (
        xarray.DataTree(children={"path1": xarray.DataTree()})["path1"],
        "/path1",
    ),
}


@pytest.mark.parametrize(
    "qoi_set, expected",
    test__node_path_cases.values(),
    ids=test__node_path_cases.keys(),
)
def test__node_path(qoi_set, expected):
    group = qoi._node_path(qoi_set)
    assert group == expected


test__propagate_identical_attrs_cases = {
    "no_common": (
        [{"a": 1, "b": 2}, {"a": 3, "c": 4}],
        {},
    ),
    "all_common": (
        [{"a": 1, "b": 2}, {"a": 1, "b": 2}, {"a": 1, "b": 2}],
        {"a": 1, "b": 2},
    ),
    "some_common": (
        [{"a": 1, "b": 2}, {"a": 1, "b": 2}, {"a": 3, "b": 2}],
        {"b": 2},
    ),
    "mixed_type": (
        [{"a": 1, "b": 2}, {"a": 1.0, "b": 2}],
        {"b": 2},
    ),
    "string": (
        [{"a": "text1", "b": "text2"}, {"a": "text1", "b": "text3"}],
        {"a": "text1"},
    ),
    "datetime": (
        [
            {"a": datetime.datetime(2025, 1, 1), "b": datetime.datetime(2025, 1, 1)},
            {"a": datetime.datetime(2025, 1, 1), "b": datetime.datetime(2024, 1, 1)},
        ],
        {"a": datetime.datetime(2025, 1, 1)},
    ),
    "single_dict": (
        [{"a": 1, "b": 2}],
        {"a": 1, "b": 2},
    ),
}


@pytest.mark.parametrize(
    "input_attrs, common_attrs",
    test__propagate_identical_attrs_cases.values(),
    ids=test__propagate_identical_attrs_cases.keys(),
)
def test__propagate_identical_attrs(input_attrs, common_attrs):
    output_attrs = qoi._propagate_identical_attrs(input_attrs, None)
    assert output_attrs == common_attrs


def test__create_qoi_archive():
    archive = qoi._create_qoi_archive(
        (
            qoi.create_qoi(
                name="load",
                calculated=5.3,
                expected=4.5,
                lower_limit=3.5,
                upper_limit=5.5,
                group="Assembly ABC Preload",
                version="ghijkl",
            ),
            qoi.create_qoi(
                name="gap",
                calculated=1.0,
                expected=0.95,
                lower_limit=0.85,
                upper_limit=1.05,
                group="Assembly ABC Preload",
                version="ghijkl",
            ),
            qoi.create_qoi(
                name="load",
                calculated=35.0,
                group="Assembly DEF Preload",
                version="ghijkl",
            ),
            qoi.create_qoi(
                name="stress",
                calculated=110.0,
                group="Assembly DEF Preload",
                version="ghijkl",
            ),
        )
    )
    expected = xarray.DataTree()
    expected["Assembly ABC Preload"] = xarray.Dataset(
        {
            "load": xarray.DataArray(
                [[5.3, 4.5, 3.5, 5.5]],
                coords={
                    "version": ["ghijkl"],
                    "value_type": ["calculated", "expected", "lower_limit", "upper_limit"],
                },
                attrs={"group": "Assembly ABC Preload", "version": "ghijkl"},
            ),
            "gap": xarray.DataArray(
                [[1.0, 0.95, 0.85, 1.05]],
                coords={
                    "version": ["ghijkl"],
                    "value_type": ["calculated", "expected", "lower_limit", "upper_limit"],
                },
                attrs={"group": "Assembly ABC Preload", "version": "ghijkl"},
            ),
        },
        coords={
            "version": ["ghijkl"],
            "value_type": ["calculated", "expected", "lower_limit", "upper_limit"],
        },
    )
    expected["Assembly DEF Preload"] = xarray.Dataset(
        {
            "load": xarray.DataArray(
                [[35.0, numpy.nan, numpy.nan, numpy.nan]],
                coords={
                    "version": ["ghijkl"],
                    "value_type": ["calculated", "expected", "lower_limit", "upper_limit"],
                },
                attrs={"group": "Assembly DEF Preload", "version": "ghijkl"},
            ),
            "stress": xarray.DataArray(
                [[110.0, numpy.nan, numpy.nan, numpy.nan]],
                coords={
                    "version": ["ghijkl"],
                    "value_type": ["calculated", "expected", "lower_limit", "upper_limit"],
                },
                attrs={"group": "Assembly DEF Preload", "version": "ghijkl"},
            ),
        },
        coords={
            "version": ["ghijkl"],
            "value_type": ["calculated", "expected", "lower_limit", "upper_limit"],
        },
    )
    assert expected.identical(archive)


def test__merge_qoi_archives():
    qoi_archives = [
        qoi._create_qoi_archive(
            (
                qoi.create_qoi(
                    name="load",
                    calculated=5.3,
                    expected=4.5,
                    lower_limit=3.5,
                    upper_limit=5.5,
                    group="Assembly ABC Preload",
                    version="ghijkl",
                ),
                qoi.create_qoi(
                    name="gap",
                    calculated=1.0,
                    expected=0.95,
                    lower_limit=0.85,
                    upper_limit=1.05,
                    group="Assembly ABC Preload",
                    version="ghijkl",
                ),
                qoi.create_qoi(
                    name="load",
                    calculated=35.0,
                    group="Assembly DEF Preload",
                    version="ghijkl",
                ),
                qoi.create_qoi(
                    name="stress",
                    calculated=110.0,
                    group="Assembly DEF Preload",
                    version="ghijkl",
                ),
            )
        ),
        qoi._create_qoi_archive(
            (
                qoi.create_qoi(
                    name="load",
                    calculated=5.4,
                    expected=4.6,
                    lower_limit=3.4,
                    upper_limit=5.6,
                    group="Assembly ABC Preload",
                    version="mnopqr",
                ),
                qoi.create_qoi(
                    name="gap",
                    calculated=1.05,
                    expected=1.0,
                    lower_limit=0.90,
                    upper_limit=1.1,
                    group="Assembly ABC Preload",
                    version="mnopqr",
                ),
                qoi.create_qoi(
                    name="load",
                    calculated=36.0,
                    group="Assembly DEF Preload",
                    version="mnopqr",
                ),
                qoi.create_qoi(
                    name="stress",
                    calculated=111.0,
                    group="Assembly DEF Preload",
                    version="mnopqr",
                ),
            )
        ),
    ]
    merged_archive = qoi._merge_qoi_archives(qoi_archives)
    expected = xarray.DataTree()
    expected["Assembly ABC Preload"] = xarray.Dataset(
        {
            "load": xarray.DataArray(
                [[5.3, 4.5, 3.5, 5.5], [5.4, 4.6, 3.4, 5.6]],
                coords={
                    "version": ["ghijkl", "mnopqr"],
                    "value_type": ["calculated", "expected", "lower_limit", "upper_limit"],
                },
                attrs={"group": "Assembly ABC Preload"},
            ),
            "gap": xarray.DataArray(
                [[1.0, 0.95, 0.85, 1.05], [1.05, 1.0, 0.9, 1.1]],
                coords={
                    "version": ["ghijkl", "mnopqr"],
                    "value_type": ["calculated", "expected", "lower_limit", "upper_limit"],
                },
                attrs={"group": "Assembly ABC Preload"},
            ),
        },
        coords={
            "version": ["ghijkl", "mnopqr"],
            "value_type": ["calculated", "expected", "lower_limit", "upper_limit"],
        },
    )
    expected["Assembly DEF Preload"] = xarray.Dataset(
        {
            "load": xarray.DataArray(
                [[35.0, numpy.nan, numpy.nan, numpy.nan], [36.0, numpy.nan, numpy.nan, numpy.nan]],
                coords={
                    "version": ["ghijkl", "mnopqr"],
                    "value_type": ["calculated", "expected", "lower_limit", "upper_limit"],
                },
                attrs={"group": "Assembly DEF Preload"},
            ),
            "stress": xarray.DataArray(
                [[110.0, numpy.nan, numpy.nan, numpy.nan], [111.0, numpy.nan, numpy.nan, numpy.nan]],
                coords={
                    "version": ["ghijkl", "mnopqr"],
                    "value_type": ["calculated", "expected", "lower_limit", "upper_limit"],
                },
                attrs={"group": "Assembly DEF Preload"},
            ),
        },
        coords={
            "version": ["ghijkl", "mnopqr"],
            "value_type": ["calculated", "expected", "lower_limit", "upper_limit"],
        },
    )
    assert expected.identical(merged_archive)


test__read_qoi_set_cases = {
    "one qoi: minimum api use": (
        xarray.Dataset(
            {
                "qoi1": xarray.DataArray(
                    [numpy.nan, numpy.nan, numpy.nan, numpy.nan],
                    coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
                    attrs={},
                ),
            },
            coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
            attrs={},
        ),
        f"name,calculated,expected,lower_limit,upper_limit{os.linesep}qoi1,,,,{os.linesep}",
    ),
    "one qoi: recommended attributes": (
        xarray.Dataset(
            {
                "qoi1": xarray.DataArray(
                    [5.1, 5.0, 4.0, 6.0],
                    coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
                    attrs={
                        "group": "group1",
                        "units": "units1",
                        "description": "description1",
                        "long_name": "long_name1",
                        "version": "version1",
                    },
                ),
            },
            coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
            attrs={},
        ),
        (
            f"name,calculated,expected,lower_limit,upper_limit,group,units,description,long_name,version{os.linesep}"
            f"qoi1,5.1,5.0,4.0,6.0,group1,units1,description1,long_name1,version1{os.linesep}"
        ),
    ),
    "two qoi: minimum api use": (
        xarray.Dataset(
            {
                "qoi1": xarray.DataArray(
                    [numpy.nan, numpy.nan, numpy.nan, numpy.nan],
                    coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
                    attrs={},
                ),
                "qoi2": xarray.DataArray(
                    [numpy.nan, numpy.nan, numpy.nan, numpy.nan],
                    coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
                    attrs={},
                ),
            },
            coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
            attrs={},
        ),
        (
            f"name,calculated,expected,lower_limit,upper_limit{os.linesep}"
            f"qoi1,,,,{os.linesep}"
            f"qoi2,,,,{os.linesep}"
        ),
    ),
    "two qoi: recommended attributes": (
        xarray.Dataset(
            {
                "qoi1": xarray.DataArray(
                    [5.1, 5.0, 4.0, 6.0],
                    coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
                    attrs={
                        "group": "group1",
                        "units": "units1",
                        "description": "description1",
                        "long_name": "long_name1",
                        "version": "version1",
                    },
                ),
                "qoi2": xarray.DataArray(
                    [0.8, 1.0, 0.9, 1.1],
                    coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
                    attrs={
                        "group": "group2",
                        "units": "units2",
                        "description": "description2",
                        "long_name": "long_name2",
                        "version": "version2",
                    },
                ),
            },
            coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
            attrs={},
        ),
        (
            f"name,calculated,expected,lower_limit,upper_limit,group,units,description,long_name,version{os.linesep}"
            f"qoi1,5.1,5.0,4.0,6.0,group1,units1,description1,long_name1,version1{os.linesep}"
            f"qoi2,0.8,1.0,0.9,1.1,group2,units2,description2,long_name2,version2{os.linesep}"
        ),
    ),
}


@pytest.mark.parametrize(
    "expected, mock_csv_data",
    test__read_qoi_set_cases.values(),
    ids=test__read_qoi_set_cases.keys(),
)
def test__read_qoi_set_csv(mock_csv_data, expected):
    # Test CSV read with mock CSV data
    from_file = pathlib.Path("test.csv")
    mock_dataframe = pandas.read_csv(io.StringIO(mock_csv_data))
    with (
        patch("pandas.read_csv", return_value=mock_dataframe) as mock_read_csv,
        patch("xarray.open_dataset") as mock_open_dataset,
    ):
        qoi_set = qoi._read_qoi_set(from_file)
        mock_read_csv.assert_called_once_with(from_file)
        mock_open_dataset.assert_not_called()
        assert expected.identical(qoi_set)


def test__read_qoi_set_h5():
    from_file = pathlib.Path("test.h5")
    with (
        patch("pandas.read_csv") as mock_read_csv,
        patch("xarray.open_dataset") as mock_open_dataset,
    ):
        qoi_set = qoi._read_qoi_set(from_file)
        mock_read_csv.assert_not_called()
        mock_open_dataset.assert_called_once_with(from_file, engine="h5netcdf")


def test__read_qoi_set_unknown():
    from_file = pathlib.Path("test.unknownsuffix")
    with (
        patch("pandas.read_csv") as mock_read_csv,
        patch("xarray.open_dataset") as mock_open_dataset,
        pytest.raises(RuntimeError),
    ):
        try:
            qoi_set = qoi._read_qoi_set(from_file)
        finally:
            mock_read_csv.assert_not_called()
            mock_open_dataset.assert_not_called()


test__add_tolerance_attribute_cases = {
    "one qoi: minimum api use: calculated NaN always out of tolerance": (
        xarray.Dataset(
            {
                "qoi1": xarray.DataArray(
                    [numpy.nan, numpy.nan, numpy.nan, numpy.nan],
                    coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
                    attrs={},
                ),
            },
            coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
            attrs={},
        ),
        xarray.Dataset(
            {
                "qoi1": xarray.DataArray(
                    [numpy.nan, numpy.nan, numpy.nan, numpy.nan],
                    coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
                    attrs={"within_tolerance": int(False)},
                ),
            },
            coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
            attrs={},
        ),
    ),
    "one qoi: in tolerance": (
        xarray.Dataset(
            {
                "qoi1": xarray.DataArray(
                    [1.0, numpy.nan, 0.9, 1.0],
                    coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
                    attrs={},
                ),
            },
            coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
            attrs={},
        ),
        xarray.Dataset(
            {
                "qoi1": xarray.DataArray(
                    [1.0, numpy.nan, 0.9, 1.0],
                    coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
                    attrs={"within_tolerance": int(True)},
                ),
            },
            coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
            attrs={},
        ),
    ),
    "one qoi: in tolerance: preserve attributes": (
        xarray.Dataset(
            {
                "qoi1": xarray.DataArray(
                    [1.0, numpy.nan, 0.9, 1.0],
                    coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
                    attrs={"custom_attr": "custom_attr1"},
                ),
            },
            coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
            attrs={},
        ),
        xarray.Dataset(
            {
                "qoi1": xarray.DataArray(
                    [1.0, numpy.nan, 0.9, 1.0],
                    coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
                    attrs={"custom_attr": "custom_attr1", "within_tolerance": int(True)},
                ),
            },
            coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
            attrs={},
        ),
    ),
    "one qoi: out of tolerance": (
        xarray.Dataset(
            {
                "qoi1": xarray.DataArray(
                    [0.8, numpy.nan, 0.9, 1.0],
                    coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
                    attrs={},
                ),
            },
            coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
            attrs={},
        ),
        xarray.Dataset(
            {
                "qoi1": xarray.DataArray(
                    [0.8, numpy.nan, 0.9, 1.0],
                    coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
                    attrs={"within_tolerance": int(False)},
                ),
            },
            coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
            attrs={},
        ),
    ),
    "one qoi: infinite upper bound": (
        xarray.Dataset(
            {
                "qoi1": xarray.DataArray(
                    [1.0e6, numpy.nan, 0.0, numpy.inf],
                    coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
                    attrs={},
                ),
            },
            coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
            attrs={},
        ),
        xarray.Dataset(
            {
                "qoi1": xarray.DataArray(
                    [1.0e6, numpy.nan, 0.0, numpy.inf],
                    coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
                    attrs={"within_tolerance": int(True)},
                ),
            },
            coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
            attrs={},
        ),
    ),
    "one qoi: NaN upper bound": (
        xarray.Dataset(
            {
                "qoi1": xarray.DataArray(
                    [1.0e6, numpy.nan, 0.0, numpy.nan],
                    coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
                    attrs={},
                ),
            },
            coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
            attrs={},
        ),
        xarray.Dataset(
            {
                "qoi1": xarray.DataArray(
                    [1.0e6, numpy.nan, 0.0, numpy.nan],
                    coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
                    attrs={"within_tolerance": int(True)},
                ),
            },
            coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
            attrs={},
        ),
    ),
    "one qoi: infinite lower bound": (
        xarray.Dataset(
            {
                "qoi1": xarray.DataArray(
                    [-1.0e6, numpy.nan, -numpy.inf, 0.0],
                    coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
                    attrs={},
                ),
            },
            coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
            attrs={},
        ),
        xarray.Dataset(
            {
                "qoi1": xarray.DataArray(
                    [-1.0e6, numpy.nan, -numpy.inf, 0.0],
                    coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
                    attrs={"within_tolerance": int(True)},
                ),
            },
            coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
            attrs={},
        ),
    ),
    "one qoi: NaN lower bound": (
        xarray.Dataset(
            {
                "qoi1": xarray.DataArray(
                    [-1.0e6, numpy.nan, numpy.nan, 0.0],
                    coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
                    attrs={},
                ),
            },
            coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
            attrs={},
        ),
        xarray.Dataset(
            {
                "qoi1": xarray.DataArray(
                    [-1.0e6, numpy.nan, numpy.nan, 0.0],
                    coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
                    attrs={"within_tolerance": int(True)},
                ),
            },
            coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
            attrs={},
        ),
    ),
    "two qoi: in tolerance": (
        xarray.Dataset(
            {
                "qoi1": xarray.DataArray(
                    [1.0, numpy.nan, 0.9, 1.0],
                    coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
                    attrs={},
                ),
                "qoi2": xarray.DataArray(
                    [5.0, numpy.nan, 4.5, 5.5],
                    coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
                    attrs={},
                ),
            },
            coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
            attrs={},
        ),
        xarray.Dataset(
            {
                "qoi1": xarray.DataArray(
                    [1.0, numpy.nan, 0.9, 1.0],
                    coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
                    attrs={"within_tolerance": int(True)},
                ),
                "qoi2": xarray.DataArray(
                    [5.0, numpy.nan, 4.5, 5.5],
                    coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
                    attrs={"within_tolerance": int(True)},
                ),
            },
            coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
            attrs={},
        ),
    ),
    "two qoi: qoi2 in tolerance": (
        xarray.Dataset(
            {
                "qoi1": xarray.DataArray(
                    [0.8, numpy.nan, 0.9, 1.0],
                    coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
                    attrs={},
                ),
                "qoi2": xarray.DataArray(
                    [5.0, numpy.nan, 4.5, 5.5],
                    coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
                    attrs={},
                ),
            },
            coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
            attrs={},
        ),
        xarray.Dataset(
            {
                "qoi1": xarray.DataArray(
                    [0.8, numpy.nan, 0.9, 1.0],
                    coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
                    attrs={"within_tolerance": int(False)},
                ),
                "qoi2": xarray.DataArray(
                    [5.0, numpy.nan, 4.5, 5.5],
                    coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
                    attrs={"within_tolerance": int(True)},
                ),
            },
            coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
            attrs={},
        ),
    ),
}


@pytest.mark.parametrize(
    "qoi_set, expected",
    test__add_tolerance_attribute_cases.values(),
    ids=test__add_tolerance_attribute_cases.keys(),
)
def test__add_tolerance_attribute(qoi_set, expected):
    qoi._add_tolerance_attribute(qoi_set)
    assert expected.identical(qoi_set)


test_write_qoi_set_to_csv_cases = test__read_qoi_set_cases


@pytest.mark.parametrize(
    "qoi_set, expected",
    test_write_qoi_set_to_csv_cases.values(),
    ids=test_write_qoi_set_to_csv_cases.keys(),
)
def test_write_qoi_set_to_csv(qoi_set, expected):
    buffer = io.StringIO()
    qoi.write_qoi_set_to_csv(qoi_set, buffer)
    csv_text = buffer.getvalue()
    assert csv_text == expected


def test__plot_qoi_tolerance_check():
    pass


def test__plot_scalar_tolerance_check():
    pass


def test__write_qoi_report():
    pass


test__get_plotting_name_cases = {
    "only name available": (
        xarray.DataArray(
            [numpy.nan, numpy.nan, numpy.nan, numpy.nan],
            coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
            name="qoi1",
            attrs={},
        ),
        "qoi1",
    ),
    "only name available units": (
        xarray.DataArray(
            [numpy.nan, numpy.nan, numpy.nan, numpy.nan],
            coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
            name="qoi1",
            attrs={"units": "units1"},
        ),
        "qoi1 [units1]",
    ),
    "standard_name available": (
        xarray.DataArray(
            [numpy.nan, numpy.nan, numpy.nan, numpy.nan],
            coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
            name="qoi1",
            attrs={"standard_name": "standard_name1"},
        ),
        "standard_name1",
    ),
    "standard_name units": (
        xarray.DataArray(
            [numpy.nan, numpy.nan, numpy.nan, numpy.nan],
            coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
            name="qoi1",
            attrs={"units": "units1", "standard_name": "standard_name1"},
        ),
        "standard_name1 [units1]",
    ),
    "long_name available": (
        xarray.DataArray(
            [numpy.nan, numpy.nan, numpy.nan, numpy.nan],
            coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
            name="qoi1",
            attrs={"long_name": "long_name1", "standard_name": "standard_name1"},
        ),
        "long_name1",
    ),
    "units available": (
        xarray.DataArray(
            [numpy.nan, numpy.nan, numpy.nan, numpy.nan],
            coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
            name="qoi1",
            attrs={"units": "units1", "long_name": "long_name1", "standard_name": "standard_name1"},
        ),
        "long_name1 [units1]",
    ),
}


@pytest.mark.parametrize(
    "qoi_array, expected",
    test__get_plotting_name_cases.values(),
    ids=test__get_plotting_name_cases.keys(),
)
def test__get_plotting_name(qoi_array, expected):
    output = qoi._get_plotting_name(qoi_array)
    assert output == expected


test__can_plot_scalar_qoi_history_cases = {
    "all_floats": (
        xarray.DataArray(
            [[1.0, 2.0, 3.0, 4.0], [1.1, 2.1, 3.1, 4.1]],
            coords={
                "version": ["abcdef", "ghijkl"],
                "value_type": ["calculated", "expected", "lower_limit", "upper_limit"],
            },
            name="qoi1",
            attrs={},
        ),
        True,
    ),
    "all_nan": (
        xarray.DataArray(
            [[numpy.nan, numpy.nan, numpy.nan, numpy.nan], [numpy.nan, numpy.nan, numpy.nan, numpy.nan]],
            coords={
                "version": ["abcdef", "ghijkl"],
                "value_type": ["calculated", "expected", "lower_limit", "upper_limit"],
            },
            name="qoi1",
            attrs={},
        ),
        False,
    ),
    "mostly_nan": (
        xarray.DataArray(
            [[1.0, numpy.nan, numpy.nan, numpy.nan], [numpy.nan, numpy.nan, numpy.nan, numpy.nan]],
            coords={
                "version": ["abcdef", "ghijkl"],
                "value_type": ["calculated", "expected", "lower_limit", "upper_limit"],
            },
            name="qoi1",
            attrs={},
        ),
        True,
    ),
    "no_version": (
        xarray.DataArray(
            [1.0, 2.0, 0.5, 3.0],
            coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
            name="qoi1",
            attrs={},
        ),
        False,
    ),
}


@pytest.mark.parametrize(
    "qoi_array, expected",
    test__can_plot_scalar_qoi_history_cases.values(),
    ids=test__can_plot_scalar_qoi_history_cases.keys(),
)
def test__can_plot_scalar_qoi_history(qoi_array, expected):
    output = qoi._can_plot_scalar_qoi_history(qoi_array)
    assert output == expected


test__can_plot_qoi_tolerance_check_cases = {
    "all_floats": (
        xarray.DataArray(
            [1.0, 2.0, 0.5, 3.0],
            coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
            name="qoi1",
            attrs={"within_tolerance": 1},
        ),
        True,
    ),
    "all_nan": (
        xarray.DataArray(
            [numpy.nan, numpy.nan, numpy.nan, numpy.nan],
            coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
            name="qoi1",
            attrs={"within_tolerance": 0},
        ),
        False,
    ),
    "no_within_tolerance_attribute": (
        xarray.DataArray(
            [1.0, 2.0, 0.5, 3.0],
            coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
            name="qoi1",
            attrs={},
        ),
        False,
    ),
    "some_nan": (
        xarray.DataArray(
            [1.0, numpy.nan, numpy.nan, numpy.nan],
            coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
            name="qoi1",
            attrs={"within_tolerance": 0},
        ),
        False,
    ),
    "non_scalar": (
        xarray.DataArray(
            [[1.0, 1.0], [1.0, 1.0], [1.0, 1.0], [1.0, 1.0]],
            coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"], "extra_dim": [0, 1]},
            name="qoi1",
            attrs={"within_tolerance": 0},
        ),
        False,
    ),
}


@pytest.mark.parametrize(
    "qoi_array, expected",
    test__can_plot_qoi_tolerance_check_cases.values(),
    ids=test__can_plot_qoi_tolerance_check_cases.keys(),
)
def test__can_plot_qoi_tolerance_check(qoi_array, expected):
    output = qoi._can_plot_qoi_tolerance_check(qoi_array)
    assert output == expected


def test__plot_scalar_qoi_history():
    pass


def test__qoi_history_report():
    pass


def test__pdf_report():
    pass


# https://re-git.lanl.gov/aea/python-projects/waves/-/issues/919
def test__accept():
    pass


# https://re-git.lanl.gov/aea/python-projects/waves/-/issues/920
def test__check():
    pass


# https://re-git.lanl.gov/aea/python-projects/waves/-/issues/921
def test__diff():
    pass


# https://re-git.lanl.gov/aea/python-projects/waves/-/issues/922
def test__aggregate():
    pass


# https://re-git.lanl.gov/aea/python-projects/waves/-/issues/923
def test__report():
    pass


# https://re-git.lanl.gov/aea/python-projects/waves/-/issues/924
def test__plot_archive():
    pass


# https://re-git.lanl.gov/aea/python-projects/waves/-/issues/925
def test__archive():
    pass
