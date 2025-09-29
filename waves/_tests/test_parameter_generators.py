"""Test ParameterGenerator Abstract Base Class."""

import contextlib
import pathlib
import string
import typing
from unittest.mock import mock_open, patch

import numpy
import pytest
import xarray

from waves import _settings, _utilities, parameter_generators
from waves.exceptions import ChoicesError, MutuallyExclusiveError, SchemaValidationError

does_not_raise = contextlib.nullcontext()


set_hashes = {
    "set1": (
        ["name1", "name2", "name3"],
        numpy.array([[1, 10.1, "a"]], dtype=object),
        ["732411987fea3ae4a1e0bd7ea6a8841a"],
    ),
    "set1 different parameter order": (
        ["name3", "name2", "name1"],
        numpy.array([["a", 10.1, 1]], dtype=object),
        ["732411987fea3ae4a1e0bd7ea6a8841a"],
    ),
    "set1 different parameter names": (
        ["newname1", "newname2", "newname3"],
        numpy.array([[1, 10.1, "a"]], dtype=object),
        ["45458adbaeb9a55dcec2211383c9bd96"],
    ),
    "set2": (
        ["name1", "name2", "name3"],
        numpy.array([[1, 10.1, "a"], [2, 20.2, "b"], [3, 30.3, "c"]], dtype=object),
        [
            "732411987fea3ae4a1e0bd7ea6a8841a",
            "6dfcf74620c998f3ef7ab4cc9fb2d510",
            "57af5a35970eb8a1a93c1ed62ff3ff37",
        ],
    ),
    # Set3 hashes should all be different if types are preserved correctly
    "set3: ints": (
        ["number1", "number2"],
        numpy.array([[1, 2]], dtype=object),
        ["f1c28a9674481e365269ced217197221"],
    ),
    "set3: ints without dtype=object": (
        ["number1", "number2"],
        numpy.array([[1, 2]]),
        ["f1c28a9674481e365269ced217197221"],
    ),
    "set3: floats": (
        ["number1", "number2"],
        numpy.array([[1.0, 2.0]], dtype=object),
        ["f94ff85af046704aff100133c958ad1e"],
    ),
    "set3: floats without dtype=object": (
        ["number1", "number2"],
        numpy.array([[1.0, 2.0]]),
        ["f94ff85af046704aff100133c958ad1e"],
    ),
    "set3: mixed ints and floats": (
        ["number1", "number2"],
        numpy.array([[1, 2.0]], dtype=object),
        ["3d0f2e8a9a15239b28cee90d331e69e8"],
    ),
}


@pytest.mark.parametrize(
    ("parameter_names", "samples", "expected_hashes"),
    set_hashes.values(),
    ids=set_hashes.keys(),
)
def test_calculate_set_hash(parameter_names: list[str], samples: numpy.ndarray, expected_hashes: list[str]) -> None:
    for row, expected_hash in zip(samples, expected_hashes, strict=True):
        set_hash = parameter_generators._calculate_set_hash(parameter_names, row)
        assert set_hash == expected_hash
        with pytest.raises(RuntimeError):
            set_hash = parameter_generators._calculate_set_hash([], row)


@pytest.mark.parametrize(
    ("parameter_names", "samples", "expected_hashes"),
    set_hashes.values(),
    ids=set_hashes.keys(),
)
def test_calculate_set_hashes(parameter_names: list[str], samples: numpy.ndarray, expected_hashes: list[str]) -> None:
    set_hashes = parameter_generators._calculate_set_hashes(
        parameter_names,
        samples,
    )
    assert set_hashes == expected_hashes


@pytest.mark.parametrize(
    ("parameter_names", "samples", "expected_hashes"),
    set_hashes.values(),
    ids=set_hashes.keys(),
)
def test_verify_parameter_study(parameter_names: list[str], samples: numpy.ndarray, expected_hashes: list[str]) -> None:
    # Borrow setup from class test. See :meth:`test_create_set_hashes`
    hashes_parameter_generator = DummyGenerator({})
    hashes_parameter_generator._parameter_names = parameter_names
    hashes_parameter_generator._samples = samples
    hashes_parameter_generator._create_set_hashes()
    assert hashes_parameter_generator._set_hashes == expected_hashes
    parameter_study = hashes_parameter_generator.parameter_study

    with does_not_raise:
        parameter_generators._verify_parameter_study(parameter_study)

    # Delete necessary coordinates
    no_set_coordinate = parameter_study.drop_vars(_settings._set_coordinate_key)
    with pytest.raises(RuntimeError, match=f"coordinate '{_settings._set_coordinate_key}' missing"):
        parameter_generators._verify_parameter_study(no_set_coordinate)
    no_hash_coordinate = parameter_study.drop_vars(_settings._hash_coordinate_key)
    with pytest.raises(RuntimeError, match=f"coordinate '{_settings._hash_coordinate_key}' missing"):
        parameter_generators._verify_parameter_study(no_hash_coordinate)

    # Check dimension name
    wrong_coordinate_name = parameter_study.swap_dims(
        dims_dict={_settings._set_coordinate_key: _settings._hash_coordinate_key}
    )
    with pytest.raises(RuntimeError, match=f"Parameter study missing dimension '{_settings._set_coordinate_key}'"):
        parameter_generators._verify_parameter_study(wrong_coordinate_name)
    bad_data_dimension = parameter_study.copy(deep=True)
    bad_data_dimension["bad_data"] = xarray.DataArray([0], dims=["bad_dimension"], coords={"bad_dimension": [0.0]})
    with pytest.raises(RuntimeError, match=f"'bad_data' missing dimension '{_settings._set_coordinate_key}'"):
        parameter_generators._verify_parameter_study(bad_data_dimension)

    # Force set hashes to be incorrect. Expect to see a RuntimeError.
    bad_hashes = parameter_study.copy(deep=True)
    number_of_hashes = len(bad_hashes[_settings._hash_coordinate_key])
    bad_hashes[_settings._hash_coordinate_key] = xarray.DataArray(
        [""] * number_of_hashes, dims=[_settings._set_coordinate_key]
    )
    with pytest.raises(RuntimeError, match="set hashes not equal to calculated set hashes"):
        parameter_generators._verify_parameter_study(bad_hashes)


return_dataset_types_cases = {
    "CartesianProduct: identical datasets": (
        parameter_generators.CartesianProduct({"parameter_1": [1]}).parameter_study,
        parameter_generators.CartesianProduct({"parameter_1": [1]}).parameter_study,
        {"parameter_1": numpy.int64},
        does_not_raise,
    ),
    "CartesianProduct: different parameters": (
        parameter_generators.CartesianProduct({"parameter_1": [1]}).parameter_study,
        parameter_generators.CartesianProduct({"parameter_2": [10.0]}).parameter_study,
        {"parameter_1": numpy.int64, "parameter_2": numpy.float64},
        does_not_raise,
    ),
    "CartesianProduct: extra parameters in second dataset": (
        parameter_generators.CartesianProduct({"parameter_1": [1]}).parameter_study,
        parameter_generators.CartesianProduct({"parameter_1": [1], "parameter_2": [10.0]}).parameter_study,
        {"parameter_1": numpy.int64, "parameter_2": numpy.float64},
        does_not_raise,
    ),
    "CartesianProduct: extra parameters in both datasets": (
        parameter_generators.CartesianProduct({"parameter_1": [1], "parameter_3": ["a"]}).parameter_study,
        parameter_generators.CartesianProduct({"parameter_1": [1], "parameter_2": [10.0]}).parameter_study,
        {"parameter_1": numpy.int64, "parameter_2": numpy.float64, "parameter_3": numpy.dtype("U1")},
        does_not_raise,
    ),
    "CartesianProduct: extra parameters bools": (
        parameter_generators.CartesianProduct({"parameter_1": [1], "parameter_3": ["a"]}).parameter_study,
        parameter_generators.CartesianProduct({"parameter_1": [1], "parameter_2": [True]}).parameter_study,
        {"parameter_1": numpy.int64, "parameter_2": bool, "parameter_3": numpy.dtype("U1")},
        does_not_raise,
    ),
    "CartesianProduct: inconsistent types: int/float": (
        parameter_generators.CartesianProduct({"parameter_1": [1]}).parameter_study,
        parameter_generators.CartesianProduct({"parameter_1": [1.0]}).parameter_study,
        {"parameter_1": numpy.int64},
        pytest.raises(RuntimeError),
    ),
    "CartesianProduct: inconsistent types: int/str": (
        parameter_generators.CartesianProduct({"parameter_1": [1]}).parameter_study,
        parameter_generators.CartesianProduct({"parameter_1": ["a"]}).parameter_study,
        {"parameter_1": numpy.int64},
        pytest.raises(RuntimeError),
    ),
    "CartesianProduct: inconsistent types: int/bool": (
        parameter_generators.CartesianProduct({"parameter_1": [1]}).parameter_study,
        parameter_generators.CartesianProduct({"parameter_1": [True]}).parameter_study,
        {"parameter_1": numpy.int64},
        pytest.raises(RuntimeError),
    ),
    "OneAtATime: identical datasets": (
        parameter_generators.OneAtATime({"parameter_1": [1]}).parameter_study,
        parameter_generators.OneAtATime({"parameter_1": [1]}).parameter_study,
        {"parameter_1": numpy.int64},
        does_not_raise,
    ),
    "OneAtATime: different parameters": (
        parameter_generators.OneAtATime({"parameter_1": [1]}).parameter_study,
        parameter_generators.OneAtATime({"parameter_2": [10.0]}).parameter_study,
        {"parameter_1": numpy.int64, "parameter_2": numpy.float64},
        does_not_raise,
    ),
    "OneAtATime: extra parameters in second dataset": (
        parameter_generators.OneAtATime({"parameter_1": [1]}).parameter_study,
        parameter_generators.OneAtATime({"parameter_1": [1], "parameter_2": [10.0]}).parameter_study,
        {"parameter_1": numpy.int64, "parameter_2": numpy.float64},
        does_not_raise,
    ),
    "OneAtATime: extra parameters in both datasets": (
        parameter_generators.OneAtATime({"parameter_1": [1], "parameter_3": ["a"]}).parameter_study,
        parameter_generators.OneAtATime({"parameter_1": [1], "parameter_2": [10.0]}).parameter_study,
        {"parameter_1": numpy.int64, "parameter_2": numpy.float64, "parameter_3": numpy.dtype("U1")},
        does_not_raise,
    ),
    "OneAtATime: extra parameters bools": (
        parameter_generators.OneAtATime({"parameter_1": [1], "parameter_3": ["a"]}).parameter_study,
        parameter_generators.OneAtATime({"parameter_1": [1], "parameter_2": [True]}).parameter_study,
        {"parameter_1": numpy.int64, "parameter_2": bool, "parameter_3": numpy.dtype("U1")},
        does_not_raise,
    ),
    "OneAtATime: inconsistent types: int/float": (
        parameter_generators.OneAtATime({"parameter_1": [1]}).parameter_study,
        parameter_generators.OneAtATime({"parameter_1": [1.0]}).parameter_study,
        {"parameter_1": numpy.int64},
        pytest.raises(RuntimeError),
    ),
    "OneAtATime: inconsistent types: int/str": (
        parameter_generators.OneAtATime({"parameter_1": [1]}).parameter_study,
        parameter_generators.OneAtATime({"parameter_1": ["a"]}).parameter_study,
        {"parameter_1": numpy.int64},
        pytest.raises(RuntimeError),
    ),
    "OneAtATime: inconsistent types: int/bool": (
        parameter_generators.OneAtATime({"parameter_1": [1]}).parameter_study,
        parameter_generators.OneAtATime({"parameter_1": [True]}).parameter_study,
        {"parameter_1": numpy.int64},
        pytest.raises(RuntimeError),
    ),
}


@pytest.mark.parametrize(
    ("dataset_1", "dataset_2", "expected_types", "outcome"),
    return_dataset_types_cases.values(),
    ids=return_dataset_types_cases.keys(),
)
def test_return_dataset_types(
    dataset_1: xarray.Dataset,
    dataset_2: xarray.Dataset,
    expected_types: dict[str, type],
    outcome: contextlib.nullcontext | pytest.RaisesExc,
) -> None:
    with outcome:
        types = parameter_generators._return_dataset_types(dataset_1, dataset_2)
        assert types == expected_types


coerce_values_cases = {
    "no coercion int": (
        [1, 2],
        None,
        numpy.int64,
        False,
    ),
    "no coercion float": (
        [1.0, 2.0],
        None,
        numpy.float64,
        False,
    ),
    "no coercion str": (
        ["a", "b"],
        None,
        numpy.str_,
        False,
    ),
    "no coercion bool": (
        [True, False],
        None,
        numpy.bool_,
        False,
    ),
    "coerce int to float": (
        [1, 2.0],
        None,
        numpy.float64,
        True,
    ),
    "coerce all to string": (
        [1, 2.0, False, "a"],
        None,
        numpy.str_,
        True,
    ),
    "coerce all to float with parameter name": (
        [True, False, 3, 5.0, 7.0],
        "test_name",
        numpy.float64,
        True,
    ),
}


@pytest.mark.parametrize(
    ("values", "name", "expected_output_type", "should_warn"),
    coerce_values_cases.values(),
    ids=coerce_values_cases.keys(),
)
def test_coerce_values(
    values: list[typing.Any], name: str | None, expected_output_type: type, should_warn: bool
) -> None:
    with patch("warnings.warn") as mock_warn:
        values_coerced = parameter_generators._coerce_values(values, name)
        assert [type(item) for item in values_coerced] == [expected_output_type] * len(values_coerced)
        if should_warn:
            mock_warn.assert_called_once()
        else:
            mock_warn.assert_not_called()


assess_parameter_spaces_cases = {
    "duplicate studies": (
        [
            parameter_generators.OneAtATime({"parameter_1": [1]}).parameter_study,
            parameter_generators.OneAtATime({"parameter_1": [1]}).parameter_study,
        ],
        {
            "23c6b7bca2141bd8eee20b7f4960521b": [
                parameter_generators.OneAtATime({"parameter_1": [1]}).parameter_study,
                parameter_generators.OneAtATime({"parameter_1": [1]}).parameter_study,
            ],
        },
        does_not_raise,
    ),
    "single parameter space": (
        [
            parameter_generators.OneAtATime({"parameter_1": [1]}).parameter_study,
            parameter_generators.OneAtATime({"parameter_1": [2]}).parameter_study,
        ],
        {
            "23c6b7bca2141bd8eee20b7f4960521b": [
                parameter_generators.OneAtATime({"parameter_1": [1]}).parameter_study,
                parameter_generators.OneAtATime({"parameter_1": [2]}).parameter_study,
            ],
        },
        does_not_raise,
    ),
    "single parameter space reversed": (
        [
            parameter_generators.OneAtATime({"parameter_1": [2]}).parameter_study,
            parameter_generators.OneAtATime({"parameter_1": [1]}).parameter_study,
        ],
        {
            "23c6b7bca2141bd8eee20b7f4960521b": [
                parameter_generators.OneAtATime({"parameter_1": [2]}).parameter_study,
                parameter_generators.OneAtATime({"parameter_1": [1]}).parameter_study,
            ],
        },
        does_not_raise,
    ),
    "single parameter space, mixed data types": (
        [
            parameter_generators.CartesianProduct({"parameter_1": [1]}).parameter_study,
            parameter_generators.CartesianProduct({"parameter_1": [2.0]}).parameter_study,
            parameter_generators.CartesianProduct({"parameter_1": [True]}).parameter_study,
        ],
        {
            "23c6b7bca2141bd8eee20b7f4960521b": [
                parameter_generators.CartesianProduct({"parameter_1": [1]}).parameter_study,
                parameter_generators.CartesianProduct({"parameter_1": [2.0]}).parameter_study,
                parameter_generators.CartesianProduct({"parameter_1": [True]}).parameter_study,
            ],
        },
        does_not_raise,  # RuntimeError will occur in `_merge_parameter_space()`
    ),
    "two parameter spaces": (
        [
            parameter_generators.CartesianProduct({"parameter_1": [1, 2]}).parameter_study,
            parameter_generators.CartesianProduct({"parameter_1": [3, 4]}).parameter_study,
            parameter_generators.CartesianProduct({"parameter_2": [False]}).parameter_study,
        ],
        {
            "23c6b7bca2141bd8eee20b7f4960521b": [
                parameter_generators.CartesianProduct({"parameter_1": [1, 2]}).parameter_study,
                parameter_generators.CartesianProduct({"parameter_1": [3, 4]}).parameter_study,
            ],
            "8c3195f1068825253cd1714daa00ade7": [
                parameter_generators.CartesianProduct({"parameter_2": [False]}).parameter_study
            ],
        },
        does_not_raise,
    ),
    "three parameter spaces": (
        [
            parameter_generators.CartesianProduct({"parameter_1": [1, 2]}).parameter_study,
            parameter_generators.CartesianProduct({"parameter_2": [3.0, 4.0]}).parameter_study,
            parameter_generators.CartesianProduct({"parameter_3": ["a", "b"]}).parameter_study,
        ],
        {
            "23c6b7bca2141bd8eee20b7f4960521b": [
                parameter_generators.CartesianProduct({"parameter_1": [1, 2]}).parameter_study
            ],
            "8c3195f1068825253cd1714daa00ade7": [
                parameter_generators.CartesianProduct({"parameter_2": [3.0, 4.0]}).parameter_study
            ],
            "98fd033a1b70ea447495bec245e16669": [
                parameter_generators.CartesianProduct({"parameter_3": ["a", "b"]}).parameter_study
            ],
        },
        does_not_raise,
    ),
    "three parameter spaces, reversed parameter names": (
        [
            parameter_generators.CartesianProduct({"parameter_3": [1, 2]}).parameter_study,
            parameter_generators.CartesianProduct({"parameter_2": [3.0, 4.0]}).parameter_study,
            parameter_generators.CartesianProduct({"parameter_1": ["a", "b"]}).parameter_study,
        ],
        {
            "98fd033a1b70ea447495bec245e16669": [
                parameter_generators.CartesianProduct({"parameter_3": [1, 2]}).parameter_study
            ],
            "8c3195f1068825253cd1714daa00ade7": [
                parameter_generators.CartesianProduct({"parameter_2": [3.0, 4.0]}).parameter_study
            ],
            "23c6b7bca2141bd8eee20b7f4960521b": [
                parameter_generators.CartesianProduct({"parameter_1": ["a", "b"]}).parameter_study
            ],
        },
        does_not_raise,
    ),
    "partially overlapping spaces": (
        [
            parameter_generators.OneAtATime({"parameter_1": [1.0]}).parameter_study,
            parameter_generators.OneAtATime({"parameter_1": [2.0], "parameter_2": [3]}).parameter_study,
        ],
        None,
        pytest.raises(RuntimeError, match="Found study containing partially overlapping parameter space"),
    ),
}


@pytest.mark.parametrize(
    ("studies", "expected_dict", "outcome"),
    assess_parameter_spaces_cases.values(),
    ids=assess_parameter_spaces_cases.keys(),
)
def test_assess_parameter_spaces(
    studies: list[xarray.Dataset],
    expected_dict: dict[str, list[xarray.Dataset]] | None,
    outcome: contextlib.nullcontext | pytest.RaisesExc,
) -> None:
    """Check the sorting of parameter spaces.

    :param studies: list of N number of parameter study Xarray datasets, where the first study in the list is the base
        study
    :param expected_dict: dictionary of parameter name hashes with corresponding Xarray datasets with identical
        parameter space
    :param outcome: pytest expected error for the test case
    """
    with outcome:
        sorted_studies = parameter_generators._assess_parameter_spaces(studies)
        assert sorted_studies == expected_dict


propagate_parameter_space_cases = {
    "propagate one parameter: int": (
        [
            parameter_generators.OneAtATime({"parameter_1": [1]}).parameter_study,
            parameter_generators.OneAtATime({"parameter_2": [2]}).parameter_study,
        ],
        parameter_generators.OneAtATime({"parameter_1": [1], "parameter_2": [2]}).parameter_study,
        {"parameter_1": numpy.int64, "parameter_2": numpy.int64},
        True,
        does_not_raise,
    ),
    "propagate one parameter: bool": (
        [
            parameter_generators.CartesianProduct({"parameter_1": [True]}).parameter_study,
            parameter_generators.CartesianProduct({"parameter_2": [False]}).parameter_study,
        ],
        parameter_generators.CartesianProduct({"parameter_1": [True], "parameter_2": [False]}).parameter_study,
        {"parameter_1": numpy.bool_, "parameter_2": numpy.bool_},
        True,
        does_not_raise,
    ),
    "propagate one parameter: string": (
        [
            parameter_generators.OneAtATime({"parameter_1": ["a"]}).parameter_study,
            parameter_generators.OneAtATime({"parameter_2": ["a"]}).parameter_study,
        ],
        parameter_generators.OneAtATime({"parameter_1": ["a"], "parameter_2": ["a"]}).parameter_study,
        {"parameter_1": numpy.dtype("U1"), "parameter_2": numpy.dtype("U1")},
        True,
        does_not_raise,
    ),
    "propagate one parameter: float": (
        [
            parameter_generators.CartesianProduct({"parameter_1": [1.0, 2.0]}).parameter_study,
            parameter_generators.CartesianProduct({"parameter_2": [2.0, 3.0]}).parameter_study,
        ],
        parameter_generators.CartesianProduct({"parameter_1": [1.0, 2.0], "parameter_2": [2.0, 3.0]}).parameter_study,
        {"parameter_1": numpy.float64, "parameter_2": numpy.float64},
        True,
        does_not_raise,
    ),
    "propagate one parameter of mixed typing: int and bool": (
        [
            parameter_generators.CartesianProduct({"parameter_1": [1, 2]}).parameter_study,
            parameter_generators.CartesianProduct({"parameter_2": [False]}).parameter_study,
        ],
        parameter_generators.CartesianProduct({"parameter_1": [1, 2], "parameter_2": [False]}).parameter_study,
        {"parameter_1": numpy.int64, "parameter_2": numpy.bool_},
        True,
        does_not_raise,
    ),
    "propagate one parameter of mixed typing: int and float": (
        [
            parameter_generators.CartesianProduct({"parameter_1": [1, 2]}).parameter_study,
            parameter_generators.CartesianProduct({"parameter_2": [3.0, 4.0]}).parameter_study,
        ],
        parameter_generators.CartesianProduct({"parameter_1": [1, 2], "parameter_2": [3.0, 4.0]}).parameter_study,
        {"parameter_1": numpy.int64, "parameter_2": numpy.float64},
        True,
        does_not_raise,
    ),
    "propagate one parameter of mixed typing: float and str": (
        [
            parameter_generators.CartesianProduct({"parameter_1": [1.0]}).parameter_study,
            parameter_generators.CartesianProduct({"parameter_2": ["a", "b"]}).parameter_study,
        ],
        parameter_generators.CartesianProduct({"parameter_1": [1.0], "parameter_2": ["a", "b"]}).parameter_study,
        {"parameter_1": numpy.float64, "parameter_2": numpy.dtype("U1")},
        True,
        does_not_raise,
    ),
    "propagate one parameter with many values": (
        [
            parameter_generators.CartesianProduct({"parameter_1": [1.0, 2.0, 3.0]}).parameter_study,
            parameter_generators.CartesianProduct({"parameter_2": ["a", "b", "c"]}).parameter_study,
        ],
        parameter_generators.CartesianProduct(
            {"parameter_1": [1.0, 2.0, 3.0], "parameter_2": ["a", "b", "c"]}
        ).parameter_study,
        {"parameter_1": numpy.float64, "parameter_2": numpy.dtype("U1")},
        True,
        does_not_raise,
    ),
    "propagate one parameter with many values: reversed values": (
        [
            parameter_generators.CartesianProduct({"parameter_1": [3.0, 2.0, 1.0]}).parameter_study,
            parameter_generators.CartesianProduct({"parameter_2": ["c", "b", "a"]}).parameter_study,
        ],
        parameter_generators.CartesianProduct(
            {"parameter_1": [1.0, 2.0, 3.0], "parameter_2": ["a", "b", "c"]}
        ).parameter_study,
        {"parameter_1": numpy.float64, "parameter_2": numpy.dtype("U1")},
        True,
        does_not_raise,
    ),
    "propagate two parameters: cartesian product": (
        [
            parameter_generators.CartesianProduct({"parameter_1": [1.0, 2.0]}).parameter_study,
            parameter_generators.CartesianProduct({"parameter_2": ["a", "b"], "parameter_3": [5, 10]}).parameter_study,
        ],
        parameter_generators.CartesianProduct(
            {"parameter_1": [1.0, 2.0], "parameter_2": ["a", "b"], "parameter_3": [5, 10]}
        ).parameter_study,
        {"parameter_1": numpy.float64, "parameter_2": numpy.dtype("U1"), "parameter_3": numpy.int64},
        True,
        does_not_raise,
    ),
    "propagate two parameters: cartesian product shuffled values": (
        [
            parameter_generators.CartesianProduct({"parameter_1": [2.0, 1.0]}).parameter_study,
            parameter_generators.CartesianProduct({"parameter_2": ["b", "a"], "parameter_3": [5, 10]}).parameter_study,
        ],
        parameter_generators.CartesianProduct(
            {"parameter_1": [1.0, 2.0], "parameter_2": ["a", "b"], "parameter_3": [5, 10]}
        ).parameter_study,
        {"parameter_1": numpy.float64, "parameter_2": numpy.dtype("U1"), "parameter_3": numpy.int64},
        True,
        does_not_raise,
    ),
    "propagate two parameters: one-at-a-time": (
        [
            parameter_generators.OneAtATime({"parameter_1": [1.0, 2.0]}).parameter_study,
            parameter_generators.OneAtATime({"parameter_2": ["a"], "parameter_3": [5]}).parameter_study,
        ],
        parameter_generators.OneAtATime(
            {"parameter_1": [1.0, 2.0], "parameter_2": ["a"], "parameter_3": [5]}
        ).parameter_study,
        {"parameter_1": numpy.float64, "parameter_2": numpy.dtype("U1"), "parameter_3": numpy.int64},
        True,
        does_not_raise,
    ),
    "propagate one parameter into two: cartesian product": (
        [
            parameter_generators.CartesianProduct({"parameter_1": [1.0, 2.0], "parameter_3": [True]}).parameter_study,
            parameter_generators.CartesianProduct({"parameter_2": ["a", "b"]}).parameter_study,
        ],
        parameter_generators.CartesianProduct(
            {
                "parameter_1": [1.0, 2.0],
                "parameter_2": ["a", "b"],
                "parameter_3": [True],
            }
        ).parameter_study,
        {"parameter_1": numpy.float64, "parameter_2": numpy.dtype("U1"), "parameter_3": numpy.bool_},
        True,
        does_not_raise,
    ),
    "propagate two parameters into two: cartesian product": (
        [
            parameter_generators.CartesianProduct({"parameter_1": [1.0, 2.0], "parameter_4": [True]}).parameter_study,
            parameter_generators.CartesianProduct({"parameter_2": ["a", "b"], "parameter_3": [3, 4]}).parameter_study,
        ],
        parameter_generators.CartesianProduct(
            {
                "parameter_1": [1.0, 2.0],
                "parameter_2": ["a", "b"],
                "parameter_3": [3, 4],
                "parameter_4": [True],
            }
        ).parameter_study,
        {
            "parameter_1": numpy.float64,
            "parameter_2": numpy.dtype("U1"),
            "parameter_3": numpy.int64,
            "parameter_4": numpy.bool_,
        },
        True,
        does_not_raise,
    ),
    "propagate four parameter sets into three sets": (
        [
            parameter_generators.CartesianProduct({"parameter_1": [1.0, 2.0, 3.0]}).parameter_study,
            parameter_generators.CartesianProduct({"parameter_2": ["a", "b"], "parameter_3": [3, 4]}).parameter_study,
        ],
        parameter_generators.CartesianProduct(
            {
                "parameter_1": [1.0, 2.0, 3.0],
                "parameter_2": ["a", "b"],
                "parameter_3": [3, 4],
            }
        ).parameter_study,
        {
            "parameter_1": numpy.float64,
            "parameter_2": numpy.dtype("U1"),
            "parameter_3": numpy.int64,
        },
        True,
        does_not_raise,
    ),
    "propagate three parameter sets into four sets": (
        [
            parameter_generators.CartesianProduct({"parameter_2": ["a", "b"], "parameter_3": [3, 4]}).parameter_study,
            parameter_generators.CartesianProduct({"parameter_1": [1.0, 2.0, 3.0]}).parameter_study,
        ],
        parameter_generators.CartesianProduct(
            {
                "parameter_1": [1.0, 2.0, 3.0],
                "parameter_2": ["a", "b"],
                "parameter_3": [3, 4],
            }
        ).parameter_study,
        {
            "parameter_1": numpy.float64,
            "parameter_2": numpy.dtype("U1"),
            "parameter_3": numpy.int64,
        },
        True,
        does_not_raise,
    ),
}


@pytest.mark.parametrize(
    ("studies", "expected_study", "expected_types", "propagate_space", "outcome"),
    propagate_parameter_space_cases.values(),
    ids=propagate_parameter_space_cases.keys(),
)
def test_propagate_parameter_space(
    studies: list[xarray.Dataset],
    expected_study: xarray.Dataset,
    expected_types: dict[str, type],
    propagate_space: bool,  # noqa: ARG001, placeholder argument for test case compatibility with downstream functions
    outcome: contextlib.nullcontext | pytest.RaisesExc,
) -> None:
    """Check the propagation of parameter space between two studies.

    :param studies: list of N number of parameter study Xarray datasets to merge, where the first study in the list is
        the base study
    :param expected_study: Xarray dataset
    :param expected_types: dictionary with parameter names as the keys and numpy types as values
    :param propagate_space: boolean indicating if parameter space propagation is used to construct the output study
    :param outcome: pytest expected error for the test case
    """
    study_base, study_other = studies
    with outcome:
        try:
            propagated_study = parameter_generators._propagate_parameter_space(study_base, study_other)
            for key, parameter_type in expected_types.items():
                assert propagated_study[key].dtype == parameter_type
            xarray.testing.assert_identical(propagated_study, expected_study)
            parameter_generators._verify_parameter_study(propagated_study)
        finally:
            pass


merge_parameter_space_cases = {
    "concatenate along one parameter: unchanged": (
        [
            parameter_generators.OneAtATime({"parameter_1": [1]}).parameter_study,
            parameter_generators.OneAtATime({"parameter_1": [1]}).parameter_study,
        ],
        parameter_generators.OneAtATime({"parameter_1": [1]}).parameter_study,
        {"parameter_1": numpy.int64},
        False,
        does_not_raise,
    ),
    "concatenate along one parameter: int": (
        [
            parameter_generators.OneAtATime({"parameter_1": [1]}).parameter_study,
            parameter_generators.OneAtATime({"parameter_1": [2]}).parameter_study,
        ],
        xarray.Dataset(
            {
                "parameter_1": xarray.DataArray(
                    [1, 2], coords={_settings._set_coordinate_key: ["parameter_set0", "parameter_set1"]}
                ),
                _settings._hash_coordinate_key: xarray.DataArray(
                    [
                        "1661dcd0bf4761d25471c1cf5514ceae",
                        "0b588b6a82c1d3d3d19fda304f940342",
                    ],
                    coords={_settings._set_coordinate_key: ["parameter_set0", "parameter_set1"]},
                ),
            }
        )
        .set_coords(_settings._hash_coordinate_key)
        .sortby(_settings._hash_coordinate_key),
        {"parameter_1": numpy.int64},
        False,
        does_not_raise,
    ),
    "concatenate along one parameter: float": (
        [
            parameter_generators.CartesianProduct({"parameter_1": [1.0]}).parameter_study,
            parameter_generators.CartesianProduct({"parameter_1": [2.0]}).parameter_study,
        ],
        xarray.Dataset(
            {
                "parameter_1": xarray.DataArray(
                    [1.0, 2.0], coords={_settings._set_coordinate_key: ["parameter_set0", "parameter_set1"]}
                ),
                _settings._hash_coordinate_key: xarray.DataArray(
                    [
                        "7f9805b5c9946582ec1fb14b91dd144d",
                        "8f7d7ec854ffe07c4c976e2bccea0665",
                    ],
                    coords={_settings._set_coordinate_key: ["parameter_set0", "parameter_set1"]},
                ),
            }
        )
        .set_coords(_settings._hash_coordinate_key)
        .sortby(_settings._hash_coordinate_key),
        {"parameter_1": numpy.float64},
        False,
        does_not_raise,
    ),
    "concatenate along one parameter: bool": (
        [
            parameter_generators.OneAtATime({"parameter_1": [True]}).parameter_study,
            parameter_generators.OneAtATime({"parameter_1": [False]}).parameter_study,
        ],
        xarray.Dataset(
            {
                "parameter_1": xarray.DataArray(
                    [True, False], coords={_settings._set_coordinate_key: ["parameter_set0", "parameter_set1"]}
                ),
                _settings._hash_coordinate_key: xarray.DataArray(
                    [
                        "6c2fb5097da66f7bb3795420b802986e",
                        "3ded86c691cf9621651acb15d909139e",
                    ],
                    coords={_settings._set_coordinate_key: ["parameter_set0", "parameter_set1"]},
                ),
            }
        )
        .set_coords(_settings._hash_coordinate_key)
        .sortby(_settings._hash_coordinate_key),
        {"parameter_1": numpy.bool_},
        False,
        does_not_raise,
    ),
    "concatenate along one parameter: int/float": (
        [
            parameter_generators.CartesianProduct({"parameter_1": [1]}).parameter_study,
            parameter_generators.CartesianProduct({"parameter_1": [2.0]}).parameter_study,
        ],
        None,
        None,
        None,
        pytest.raises(RuntimeError, match="Different types for"),
    ),
    "concatenate along one parameter: int/bool": (
        [
            parameter_generators.CartesianProduct({"parameter_1": [1]}).parameter_study,
            parameter_generators.CartesianProduct({"parameter_1": [True]}).parameter_study,
        ],
        None,
        None,
        None,
        pytest.raises(RuntimeError, match="Different types for"),
    ),
    "concatenate along one parameter: float/bool": (
        [
            parameter_generators.OneAtATime({"parameter_1": [1.0]}).parameter_study,
            parameter_generators.OneAtATime({"parameter_1": [True]}).parameter_study,
        ],
        None,
        None,
        None,
        pytest.raises(RuntimeError, match="Different types for"),
    ),
    "concatenate along one parameter across multiple studies: float": (
        [
            parameter_generators.OneAtATime(
                {"parameter_1": [1, 2], "parameter_2": [3.0], "parameter_3": ["a"]}
            ).parameter_study,
            parameter_generators.OneAtATime(
                {"parameter_1": [1, 2], "parameter_2": [3.0, 4.0], "parameter_3": ["a"]}
            ).parameter_study,
            parameter_generators.OneAtATime(
                {"parameter_1": [1, 2], "parameter_2": [3.0, 5.0], "parameter_3": ["a"]}
            ).parameter_study,
        ],
        xarray.Dataset(
            {
                "parameter_1": xarray.DataArray(
                    [1, 1, 2, 1],
                    coords={
                        _settings._set_coordinate_key: [
                            "parameter_set0",
                            "parameter_set2",
                            "parameter_set1",
                            "parameter_set3",
                        ]
                    },
                ),
                "parameter_2": xarray.DataArray(
                    [3.0, 4.0, 3.0, 5.0],
                    coords={
                        _settings._set_coordinate_key: [
                            "parameter_set0",
                            "parameter_set2",
                            "parameter_set1",
                            "parameter_set3",
                        ]
                    },
                ),
                "parameter_3": xarray.DataArray(
                    ["a", "a", "a", "a"],
                    coords={
                        _settings._set_coordinate_key: [
                            "parameter_set0",
                            "parameter_set2",
                            "parameter_set1",
                            "parameter_set3",
                        ]
                    },
                ),
                _settings._hash_coordinate_key: xarray.DataArray(
                    [
                        "4d9644f3ff9205869b5c5aef11cb5235",
                        "8e213a62356cd1d4ce2b3b795fab6ef9",
                        "8eb85255b4d3888cbf413afc55cbbac3",
                        "d7dd3ecf2cebf5e89d3e211faf2f0526",
                    ],
                    coords={
                        _settings._set_coordinate_key: [
                            "parameter_set0",
                            "parameter_set2",
                            "parameter_set1",
                            "parameter_set3",
                        ]
                    },
                ),
            }
        )
        .set_coords(_settings._hash_coordinate_key)
        .sortby(_settings._hash_coordinate_key),
        {"parameter_1": numpy.int64, "parameter_2": numpy.float64, "parameter_3": numpy.dtype("U1")},
        False,
        does_not_raise,
    ),
    "concatenate along two parameters across multiple studies: int/bool": (
        [
            parameter_generators.CartesianProduct({"parameter_1": [1], "parameter_2": [True]}).parameter_study,
            parameter_generators.CartesianProduct({"parameter_1": [2], "parameter_2": [False]}).parameter_study,
        ],
        xarray.Dataset(
            {
                "parameter_1": xarray.DataArray(
                    [1, 2], coords={_settings._set_coordinate_key: ["parameter_set0", "parameter_set1"]}
                ),
                "parameter_2": xarray.DataArray(
                    [True, False], coords={_settings._set_coordinate_key: ["parameter_set0", "parameter_set1"]}
                ),
                _settings._hash_coordinate_key: xarray.DataArray(
                    [
                        "d65bccd02f05b0419dc634e643418e62",
                        "df1ac82da14f4f1fd9d73159bb64a717",
                    ],
                    coords={_settings._set_coordinate_key: ["parameter_set0", "parameter_set1"]},
                ),
            }
        )
        .set_coords(_settings._hash_coordinate_key)
        .sortby(_settings._hash_coordinate_key),
        {"parameter_1": numpy.int64, "parameter_2": numpy.bool_},
        False,
        does_not_raise,
    ),
    "concatenate along unchanged parameters across multiple studies": (
        [
            parameter_generators.CartesianProduct(
                {"parameter_1": [1, 2], "parameter_2": [3.0], "parameter_3": [True, False]}
            ).parameter_study,
            parameter_generators.CartesianProduct(
                {"parameter_1": [1, 2], "parameter_2": [3.0], "parameter_3": [True, False]}
            ).parameter_study,
            parameter_generators.CartesianProduct(
                {"parameter_1": [1, 2], "parameter_2": [3.0], "parameter_3": [True, False]}
            ).parameter_study,
        ],
        parameter_generators.CartesianProduct(
            {"parameter_1": [1, 2], "parameter_2": [3.0], "parameter_3": [True, False]}
        ).parameter_study,
        {"parameter_1": numpy.int64, "parameter_2": numpy.float64, "parameter_3": numpy.bool_},
        False,
        does_not_raise,
    ),
}


@pytest.mark.parametrize(
    ("studies", "expected_study", "expected_types", "propagate_space", "outcome"),
    merge_parameter_space_cases.values(),
    ids=merge_parameter_space_cases.keys(),
)
def test_merge_parameter_space(
    studies: list[xarray.Dataset],
    expected_study: xarray.Dataset,
    expected_types: dict[str, type],
    propagate_space: bool,
    outcome: contextlib.nullcontext | pytest.RaisesExc,
) -> None:
    """Check the propagation of parameter space between two studies.

    :param studies: list of N number of parameter study Xarray datasets to merge, where the first study in the list is
        the base study
    :param expected_study: Xarray dataset
    :param expected_types: dictionary with parameter names as the keys and numpy types as values
    :param propagate_space: boolean indicating if parameter space propagation is used to construct the output study.
    :param outcome: pytest expected error for the test case
    """
    with outcome:
        try:
            swap_to_hash_index = {_settings._set_coordinate_key: _settings._hash_coordinate_key}
            swap_to_set_index = {_settings._hash_coordinate_key: _settings._set_coordinate_key}
            studies = [study.swap_dims(swap_to_hash_index) for study in studies]
            merged_study = parameter_generators._merge_parameter_space(studies)
            merged_study = merged_study.swap_dims(swap_to_set_index)
            for key, parameter_type in expected_types.items():
                assert merged_study[key].dtype == parameter_type
            xarray.testing.assert_identical(merged_study, expected_study)
            parameter_generators._verify_parameter_study(merged_study)
            if not propagate_space:
                # Compare base study hash and set names to merged ones for uniform parameter space
                base_study = studies[0].swap_dims(swap_to_set_index)
                base_study_from_merged = merged_study.where(
                    merged_study[_settings._hash_coordinate_key] == base_study[_settings._hash_coordinate_key]
                )
                xarray.testing.assert_identical(base_study_from_merged, base_study)
        finally:
            pass


merge_parameter_studies_cases = propagate_parameter_space_cases | merge_parameter_space_cases
merge_parameter_studies_cases.update(
    {
        "too few parameter studies input": (
            [parameter_generators.OneAtATime({"parameter_1": [1]}).parameter_study],
            None,
            None,
            None,
            pytest.raises(RuntimeError, match="Not enough parameter studies provided for merge operation"),
        ),
        "concatenate with different numbers of parameters": (
            [
                parameter_generators.OneAtATime({"parameter_1": [1.0]}).parameter_study,
                parameter_generators.OneAtATime({"parameter_1": [2.0], "parameter_2": [3]}).parameter_study,
            ],
            None,
            None,
            None,
            pytest.raises(RuntimeError, match="Found study containing partially overlapping parameter space"),
        ),
        "merge and propagate: three studies, two parameter spaces - int/float": (
            [
                parameter_generators.CartesianProduct({"parameter_1": [1]}).parameter_study,
                parameter_generators.CartesianProduct({"parameter_1": [2]}).parameter_study,
                parameter_generators.CartesianProduct({"parameter_2": [3.0, 4.0]}).parameter_study,
            ],
            parameter_generators.CartesianProduct({"parameter_1": [1, 2], "parameter_2": [3.0, 4.0]}).parameter_study,
            {"parameter_1": numpy.int64, "parameter_2": numpy.float64},
            True,
            does_not_raise,
        ),
        "merge and propagate: four studies, two parameter spaces - string/bool": (
            [
                parameter_generators.CartesianProduct({"parameter_1": ["a"]}).parameter_study,
                parameter_generators.CartesianProduct({"parameter_2": [True]}).parameter_study,
                parameter_generators.CartesianProduct({"parameter_1": ["b"]}).parameter_study,
                parameter_generators.CartesianProduct({"parameter_2": [False]}).parameter_study,
            ],
            parameter_generators.CartesianProduct(
                {"parameter_1": ["a", "b"], "parameter_2": [True, False]}
            ).parameter_study,
            {"parameter_1": numpy.dtype("U1"), "parameter_2": numpy.bool_},
            True,
            does_not_raise,
        ),
        "merge and propagate: three studies, three parameter spaces": (
            [
                parameter_generators.CartesianProduct({"parameter_1": [1, 2]}).parameter_study,
                parameter_generators.CartesianProduct({"parameter_2": [True, False]}).parameter_study,
                parameter_generators.CartesianProduct({"parameter_3": [1.0, 2.0]}).parameter_study,
            ],
            parameter_generators.CartesianProduct(
                {"parameter_1": [1, 2], "parameter_2": [True, False], "parameter_3": [1.0, 2.0]}
            ).parameter_study,
            {"parameter_1": numpy.int64, "parameter_2": numpy.bool_, "parameter_3": numpy.float64},
            True,
            does_not_raise,
        ),
        "merge and propagate: One at a Time": (
            [
                parameter_generators.OneAtATime({"parameter_1": [1]}).parameter_study,
                parameter_generators.OneAtATime({"parameter_2": [2.0]}).parameter_study,
                parameter_generators.OneAtATime({"parameter_1": [2, 3]}).parameter_study,
            ],
            parameter_generators.CartesianProduct({"parameter_1": [1, 2, 3], "parameter_2": [2.0]}).parameter_study,
            {"parameter_1": numpy.int64, "parameter_2": numpy.float64},
            True,
            does_not_raise,
        ),
    }
)


@pytest.mark.parametrize(
    ("studies", "expected_study", "expected_types", "propagate_space", "outcome"),
    merge_parameter_studies_cases.values(),
    ids=merge_parameter_studies_cases.keys(),
)
def test_merge_parameter_studies(
    studies: list[xarray.Dataset],
    expected_study: xarray.Dataset,
    expected_types: dict[str, type],
    propagate_space: bool | None,
    outcome: contextlib.nullcontext | pytest.RaisesExc,
) -> None:
    """Check the merged parameter study contents and verify unchanged base study set_name-to-set_hash relationships.

    :param studies: list of N number of parameter study Xarray datasets to merge, where the first study in the list is
        the base study
    :param expected_study: Xarray dataset
    :param expected_types: dictionary with parameter names as the keys and numpy types as values
    :param propagate_space: boolean indicating if parameter space propagation is used to construct the output study
    :param outcome: pytest expected error for the test case
    """
    with outcome:
        try:
            merged_study = parameter_generators._merge_parameter_studies(studies)
            for key, parameter_type in expected_types.items():
                assert merged_study[key].dtype == parameter_type
            xarray.testing.assert_identical(merged_study, expected_study)
            parameter_generators._verify_parameter_study(merged_study)
            if not propagate_space:
                # Compare base study hash and set names to merged ones for uniform parameter space
                base_study = studies[0]
                base_study_from_merged = merged_study.where(
                    merged_study[_settings._hash_coordinate_key] == base_study[_settings._hash_coordinate_key]
                )
                xarray.testing.assert_identical(base_study_from_merged, base_study)
        finally:
            pass


test_create_set_names_cases = {
    "custom template": (
        ["0b588b6a82c1d3d3d19fda304f940342", "1661dcd0bf4761d25471c1cf5514ceae"],
        _utilities._AtSignTemplate(f"out{_settings._template_placeholder}"),
        {"0b588b6a82c1d3d3d19fda304f940342": "out0", "1661dcd0bf4761d25471c1cf5514ceae": "out1"},
    ),
    "default template": (
        ["0b588b6a82c1d3d3d19fda304f940342", "1661dcd0bf4761d25471c1cf5514ceae"],
        None,
        {"0b588b6a82c1d3d3d19fda304f940342": "parameter_set0", "1661dcd0bf4761d25471c1cf5514ceae": "parameter_set1"},
    ),
    "unordered hashes": (
        ["1661dcd0bf4761d25471c1cf5514ceae", "0b588b6a82c1d3d3d19fda304f940342", "f94ff85af046704aff100133c958ad1e"],
        None,
        {
            "0b588b6a82c1d3d3d19fda304f940342": "parameter_set0",
            "1661dcd0bf4761d25471c1cf5514ceae": "parameter_set1",
            "f94ff85af046704aff100133c958ad1e": "parameter_set2",
        },
    ),
}


@pytest.mark.parametrize(
    ("test_set_hashes", "template", "expected_set_names"),
    test_create_set_names_cases.values(),
    ids=test_create_set_names_cases.keys(),
)
def test_create_set_names(
    test_set_hashes: list[str], template: string.Template | None, expected_set_names: dict[str, str]
) -> None:
    """Test the parameter set name generation. Test that the same hashes get the same parameter set names.

    :param test_set_hashes: list of arbitrary hash strings for test purposes
    :param template: ``_AtSignTemplate`` typed string with substitution character
    :param expected_set_names: dictionary of set hash keys with corresponding expected set name as value
    """
    test_set_hashes_reversed = list(reversed(test_set_hashes))
    test_set_names = parameter_generators._create_set_names(test_set_hashes, template)
    test_set_names_reversed = parameter_generators._create_set_names(test_set_hashes_reversed, template)
    assert test_set_names == expected_set_names
    assert test_set_names_reversed == expected_set_names


test_update_set_names_cases = {
    # Unit test by direct parameter study dataset creation in expected format
    "filled dataset, no kwargs, should return as original": (
        xarray.Dataset(
            {
                "parameter_1": xarray.DataArray(
                    [2, 1],
                    coords={
                        _settings._hash_coordinate_key: [
                            "0b588b6a82c1d3d3d19fda304f940342",
                            "1661dcd0bf4761d25471c1cf5514ceae",
                        ],
                    },
                ),
                _settings._set_coordinate_key: xarray.DataArray(
                    ["parameter_set0", "parameter_set1"],
                    coords={
                        _settings._hash_coordinate_key: [
                            "0b588b6a82c1d3d3d19fda304f940342",
                            "1661dcd0bf4761d25471c1cf5514ceae",
                        ],
                    },
                ),
            }
        ).set_coords(_settings._set_coordinate_key),
        {},
        xarray.Dataset(
            {
                "parameter_1": xarray.DataArray(
                    [2, 1],
                    coords={
                        _settings._hash_coordinate_key: [
                            "0b588b6a82c1d3d3d19fda304f940342",
                            "1661dcd0bf4761d25471c1cf5514ceae",
                        ],
                    },
                ),
                _settings._set_coordinate_key: xarray.DataArray(
                    ["parameter_set0", "parameter_set1"],
                    coords={
                        _settings._hash_coordinate_key: [
                            "0b588b6a82c1d3d3d19fda304f940342",
                            "1661dcd0bf4761d25471c1cf5514ceae",
                        ],
                    },
                ),
            }
        ).set_coords(_settings._set_coordinate_key),
        does_not_raise,
    ),
    "filled dataset, non-default template, should return as original": (
        xarray.Dataset(
            {
                "parameter_1": xarray.DataArray(
                    [2, 1],
                    coords={
                        _settings._hash_coordinate_key: [
                            "0b588b6a82c1d3d3d19fda304f940342",
                            "1661dcd0bf4761d25471c1cf5514ceae",
                        ],
                    },
                ),
                _settings._set_coordinate_key: xarray.DataArray(
                    ["parameter_set0", "parameter_set1"],
                    coords={
                        _settings._hash_coordinate_key: [
                            "0b588b6a82c1d3d3d19fda304f940342",
                            "1661dcd0bf4761d25471c1cf5514ceae",
                        ],
                    },
                ),
            }
        ).set_coords(_settings._set_coordinate_key),
        {"template": _utilities._AtSignTemplate("out@{number}")},
        xarray.Dataset(
            {
                "parameter_1": xarray.DataArray(
                    [2, 1],
                    coords={
                        _settings._hash_coordinate_key: [
                            "0b588b6a82c1d3d3d19fda304f940342",
                            "1661dcd0bf4761d25471c1cf5514ceae",
                        ],
                    },
                ),
                _settings._set_coordinate_key: xarray.DataArray(
                    ["parameter_set0", "parameter_set1"],
                    coords={
                        _settings._hash_coordinate_key: [
                            "0b588b6a82c1d3d3d19fda304f940342",
                            "1661dcd0bf4761d25471c1cf5514ceae",
                        ],
                    },
                ),
            }
        ).set_coords(_settings._set_coordinate_key),
        does_not_raise,
    ),
    "empty dataset, default template": (
        xarray.Dataset(
            {
                "parameter_1": xarray.DataArray(
                    [2, 1],
                    coords={
                        _settings._hash_coordinate_key: [
                            "0b588b6a82c1d3d3d19fda304f940342",
                            "1661dcd0bf4761d25471c1cf5514ceae",
                        ],
                    },
                ),
                _settings._set_coordinate_key: xarray.DataArray(
                    numpy.array([numpy.nan, numpy.nan], dtype=object),
                    coords={
                        _settings._hash_coordinate_key: [
                            "0b588b6a82c1d3d3d19fda304f940342",
                            "1661dcd0bf4761d25471c1cf5514ceae",
                        ],
                    },
                ),
            }
        ).set_coords(_settings._set_coordinate_key),
        {},
        xarray.Dataset(
            {
                "parameter_1": xarray.DataArray(
                    [2, 1],
                    coords={
                        _settings._hash_coordinate_key: [
                            "0b588b6a82c1d3d3d19fda304f940342",
                            "1661dcd0bf4761d25471c1cf5514ceae",
                        ],
                    },
                ),
                _settings._set_coordinate_key: xarray.DataArray(
                    ["parameter_set0", "parameter_set1"],
                    coords={
                        _settings._hash_coordinate_key: [
                            "0b588b6a82c1d3d3d19fda304f940342",
                            "1661dcd0bf4761d25471c1cf5514ceae",
                        ],
                    },
                ),
            }
        ).set_coords(_settings._set_coordinate_key),
        does_not_raise,
    ),
    "empty dataset, non-default template": (
        xarray.Dataset(
            {
                "parameter_1": xarray.DataArray(
                    [2, 1],
                    coords={
                        _settings._hash_coordinate_key: [
                            "0b588b6a82c1d3d3d19fda304f940342",
                            "1661dcd0bf4761d25471c1cf5514ceae",
                        ],
                    },
                ),
                _settings._set_coordinate_key: xarray.DataArray(
                    numpy.array([numpy.nan, numpy.nan], dtype=object),
                    coords={
                        _settings._hash_coordinate_key: [
                            "0b588b6a82c1d3d3d19fda304f940342",
                            "1661dcd0bf4761d25471c1cf5514ceae",
                        ],
                    },
                ),
            }
        ).set_coords(_settings._set_coordinate_key),
        {"template": _utilities._AtSignTemplate("out@{number}")},
        xarray.Dataset(
            {
                "parameter_1": xarray.DataArray(
                    [2, 1],
                    coords={
                        _settings._hash_coordinate_key: [
                            "0b588b6a82c1d3d3d19fda304f940342",
                            "1661dcd0bf4761d25471c1cf5514ceae",
                        ],
                    },
                ),
                _settings._set_coordinate_key: xarray.DataArray(
                    ["out0", "out1"],
                    coords={
                        _settings._hash_coordinate_key: [
                            "0b588b6a82c1d3d3d19fda304f940342",
                            "1661dcd0bf4761d25471c1cf5514ceae",
                        ],
                    },
                ),
            }
        ).set_coords(_settings._set_coordinate_key),
        does_not_raise,
    ),
    "first set name filled dataset, default template": (
        xarray.Dataset(
            {
                "parameter_1": xarray.DataArray(
                    [2, 1],
                    coords={
                        _settings._hash_coordinate_key: [
                            "0b588b6a82c1d3d3d19fda304f940342",
                            "1661dcd0bf4761d25471c1cf5514ceae",
                        ],
                    },
                ),
                _settings._set_coordinate_key: xarray.DataArray(
                    numpy.array(["parameter_set0", numpy.nan], dtype=object),
                    coords={
                        _settings._hash_coordinate_key: [
                            "0b588b6a82c1d3d3d19fda304f940342",
                            "1661dcd0bf4761d25471c1cf5514ceae",
                        ],
                    },
                ),
            }
        ).set_coords(_settings._set_coordinate_key),
        {},
        xarray.Dataset(
            {
                "parameter_1": xarray.DataArray(
                    [2, 1],
                    coords={
                        _settings._hash_coordinate_key: [
                            "0b588b6a82c1d3d3d19fda304f940342",
                            "1661dcd0bf4761d25471c1cf5514ceae",
                        ],
                    },
                ),
                _settings._set_coordinate_key: xarray.DataArray(
                    ["parameter_set0", "parameter_set1"],
                    coords={
                        _settings._hash_coordinate_key: [
                            "0b588b6a82c1d3d3d19fda304f940342",
                            "1661dcd0bf4761d25471c1cf5514ceae",
                        ],
                    },
                ),
            }
        ).set_coords(_settings._set_coordinate_key),
        does_not_raise,
    ),
    "second set name filled dataset, default template": (
        xarray.Dataset(
            {
                "parameter_1": xarray.DataArray(
                    [2, 1],
                    coords={
                        _settings._hash_coordinate_key: [
                            "0b588b6a82c1d3d3d19fda304f940342",
                            "1661dcd0bf4761d25471c1cf5514ceae",
                        ],
                    },
                ),
                _settings._set_coordinate_key: xarray.DataArray(
                    numpy.array([numpy.nan, "parameter_set0"], dtype=object),
                    coords={
                        _settings._hash_coordinate_key: [
                            "0b588b6a82c1d3d3d19fda304f940342",
                            "1661dcd0bf4761d25471c1cf5514ceae",
                        ],
                    },
                ),
            }
        ).set_coords(_settings._set_coordinate_key),
        {},
        xarray.Dataset(
            {
                "parameter_1": xarray.DataArray(
                    [2, 1],
                    coords={
                        _settings._hash_coordinate_key: [
                            "0b588b6a82c1d3d3d19fda304f940342",
                            "1661dcd0bf4761d25471c1cf5514ceae",
                        ],
                    },
                ),
                _settings._set_coordinate_key: xarray.DataArray(
                    ["parameter_set1", "parameter_set0"],
                    coords={
                        _settings._hash_coordinate_key: [
                            "0b588b6a82c1d3d3d19fda304f940342",
                            "1661dcd0bf4761d25471c1cf5514ceae",
                        ],
                    },
                ),
            }
        ).set_coords(_settings._set_coordinate_key),
        does_not_raise,
    ),
    "first set name filled dataset, non-default template": (
        xarray.Dataset(
            {
                "parameter_1": xarray.DataArray(
                    [2, 1],
                    coords={
                        _settings._hash_coordinate_key: [
                            "0b588b6a82c1d3d3d19fda304f940342",
                            "1661dcd0bf4761d25471c1cf5514ceae",
                        ],
                    },
                ),
                _settings._set_coordinate_key: xarray.DataArray(
                    numpy.array(["out0", numpy.nan], dtype=object),
                    coords={
                        _settings._hash_coordinate_key: [
                            "0b588b6a82c1d3d3d19fda304f940342",
                            "1661dcd0bf4761d25471c1cf5514ceae",
                        ],
                    },
                ),
            }
        ).set_coords(_settings._set_coordinate_key),
        {"template": _utilities._AtSignTemplate("out@{number}")},
        xarray.Dataset(
            {
                "parameter_1": xarray.DataArray(
                    [2, 1],
                    coords={
                        _settings._hash_coordinate_key: [
                            "0b588b6a82c1d3d3d19fda304f940342",
                            "1661dcd0bf4761d25471c1cf5514ceae",
                        ],
                    },
                ),
                _settings._set_coordinate_key: xarray.DataArray(
                    ["out0", "out1"],
                    coords={
                        _settings._hash_coordinate_key: [
                            "0b588b6a82c1d3d3d19fda304f940342",
                            "1661dcd0bf4761d25471c1cf5514ceae",
                        ],
                    },
                ),
            }
        ).set_coords(_settings._set_coordinate_key),
        does_not_raise,
    ),
    "second set name filled dataset, non-default template": (
        xarray.Dataset(
            {
                "parameter_1": xarray.DataArray(
                    [2, 1],
                    coords={
                        _settings._hash_coordinate_key: [
                            "0b588b6a82c1d3d3d19fda304f940342",
                            "1661dcd0bf4761d25471c1cf5514ceae",
                        ],
                    },
                ),
                _settings._set_coordinate_key: xarray.DataArray(
                    numpy.array([numpy.nan, "out0"], dtype=object),
                    coords={
                        _settings._hash_coordinate_key: [
                            "0b588b6a82c1d3d3d19fda304f940342",
                            "1661dcd0bf4761d25471c1cf5514ceae",
                        ],
                    },
                ),
            }
        ).set_coords(_settings._set_coordinate_key),
        {"template": _utilities._AtSignTemplate("out@{number}")},
        xarray.Dataset(
            {
                "parameter_1": xarray.DataArray(
                    [2, 1],
                    coords={
                        _settings._hash_coordinate_key: [
                            "0b588b6a82c1d3d3d19fda304f940342",
                            "1661dcd0bf4761d25471c1cf5514ceae",
                        ],
                    },
                ),
                _settings._set_coordinate_key: xarray.DataArray(
                    ["out1", "out0"],
                    coords={
                        _settings._hash_coordinate_key: [
                            "0b588b6a82c1d3d3d19fda304f940342",
                            "1661dcd0bf4761d25471c1cf5514ceae",
                        ],
                    },
                ),
            }
        ).set_coords(_settings._set_coordinate_key),
        does_not_raise,
    ),
    "first set name filled dataset, non-default template, mismatching naming convention": (
        xarray.Dataset(
            {
                "parameter_1": xarray.DataArray(
                    [2, 1],
                    coords={
                        _settings._hash_coordinate_key: [
                            "0b588b6a82c1d3d3d19fda304f940342",
                            "1661dcd0bf4761d25471c1cf5514ceae",
                        ],
                    },
                ),
                _settings._set_coordinate_key: xarray.DataArray(
                    numpy.array(["parameter_set0", numpy.nan], dtype=object),
                    coords={
                        _settings._hash_coordinate_key: [
                            "0b588b6a82c1d3d3d19fda304f940342",
                            "1661dcd0bf4761d25471c1cf5514ceae",
                        ],
                    },
                ),
            }
        ).set_coords(_settings._set_coordinate_key),
        {"template": _utilities._AtSignTemplate("out@{number}")},
        None,
        pytest.raises(
            RuntimeError,
            match=r"Could not fill merged parameter set names. Does the parameter set naming convention match?",
        ),
    ),
    "filled dataset, no kwargs, should return as original, single parameter set": (
        xarray.Dataset(
            {
                "parameter_1": xarray.DataArray(
                    [1],
                    coords={_settings._hash_coordinate_key: ["1661dcd0bf4761d25471c1cf5514ceae"]},
                ),
                _settings._set_coordinate_key: xarray.DataArray(
                    ["parameter_set0"],
                    coords={_settings._hash_coordinate_key: ["1661dcd0bf4761d25471c1cf5514ceae"]},
                ),
            }
        ).set_coords(_settings._set_coordinate_key),
        {},
        xarray.Dataset(
            {
                "parameter_1": xarray.DataArray(
                    [1],
                    coords={_settings._hash_coordinate_key: ["1661dcd0bf4761d25471c1cf5514ceae"]},
                ),
                _settings._set_coordinate_key: xarray.DataArray(
                    ["parameter_set0"],
                    coords={_settings._hash_coordinate_key: ["1661dcd0bf4761d25471c1cf5514ceae"]},
                ),
            }
        ).set_coords(_settings._set_coordinate_key),
        does_not_raise,
    ),
    "empty dataset, no kwargs, should return as original, single parameter set": (
        xarray.Dataset(
            {
                "parameter_1": xarray.DataArray(
                    [1],
                    coords={_settings._hash_coordinate_key: ["1661dcd0bf4761d25471c1cf5514ceae"]},
                ),
                _settings._set_coordinate_key: xarray.DataArray(
                    numpy.array([numpy.nan], dtype=object),
                    coords={_settings._hash_coordinate_key: ["1661dcd0bf4761d25471c1cf5514ceae"]},
                ),
            }
        ).set_coords(_settings._set_coordinate_key),
        {},
        xarray.Dataset(
            {
                "parameter_1": xarray.DataArray(
                    [1],
                    coords={_settings._hash_coordinate_key: ["1661dcd0bf4761d25471c1cf5514ceae"]},
                ),
                _settings._set_coordinate_key: xarray.DataArray(
                    ["parameter_set0"],
                    coords={_settings._hash_coordinate_key: ["1661dcd0bf4761d25471c1cf5514ceae"]},
                ),
            }
        ).set_coords(_settings._set_coordinate_key),
        does_not_raise,
    ),
    # Integration test by parameter study dataset initialization by API
    "filled dataset, custom set name template": (
        parameter_generators.CartesianProduct(
            {"parameter_1": [1, 2]}, set_name_template=f"out{_settings._template_placeholder}"
        )
        .parameter_study.set_coords(_settings._hash_coordinate_key)
        .swap_dims({_settings._set_coordinate_key: _settings._hash_coordinate_key}),
        {"template": _utilities._AtSignTemplate("out@{number}")},
        xarray.Dataset(
            {
                "parameter_1": xarray.DataArray([2, 1], coords={_settings._set_coordinate_key: ["out0", "out1"]}),
                _settings._hash_coordinate_key: xarray.DataArray(
                    [
                        "0b588b6a82c1d3d3d19fda304f940342",
                        "1661dcd0bf4761d25471c1cf5514ceae",
                    ],
                    coords={_settings._set_coordinate_key: ["out0", "out1"]},
                ),
            }
        )
        .set_coords(_settings._hash_coordinate_key)
        .swap_dims({_settings._set_coordinate_key: _settings._hash_coordinate_key}),
        does_not_raise,
    ),
    "filled dataset, custom file name template": (
        parameter_generators.CartesianProduct(
            {"parameter_1": [1, 2]}, output_file_template=f"out{_settings._template_placeholder}"
        ).parameter_study.swap_dims({_settings._set_coordinate_key: _settings._hash_coordinate_key}),
        {"template": _utilities._AtSignTemplate("out@{number}")},
        xarray.Dataset(
            {
                "parameter_1": xarray.DataArray([2, 1], coords={_settings._set_coordinate_key: ["out0", "out1"]}),
                _settings._hash_coordinate_key: xarray.DataArray(
                    [
                        "0b588b6a82c1d3d3d19fda304f940342",
                        "1661dcd0bf4761d25471c1cf5514ceae",
                    ],
                    coords={_settings._set_coordinate_key: ["out0", "out1"]},
                ),
            }
        )
        .set_coords(_settings._hash_coordinate_key)
        .swap_dims({_settings._set_coordinate_key: _settings._hash_coordinate_key}),
        does_not_raise,
    ),
    "filled dataset, custom file name template override": (
        parameter_generators.CartesianProduct(
            {"parameter_1": [1, 2]},
            set_name_template=f"out{_settings._template_placeholder}",
            output_file_template=f"override{_settings._template_placeholder}",
        ).parameter_study.swap_dims({_settings._set_coordinate_key: _settings._hash_coordinate_key}),
        {"template": _utilities._AtSignTemplate("out@{number}")},
        xarray.Dataset(
            {
                "parameter_1": xarray.DataArray(
                    [2, 1], coords={_settings._set_coordinate_key: ["override0", "override1"]}
                ),
                _settings._hash_coordinate_key: xarray.DataArray(
                    [
                        "0b588b6a82c1d3d3d19fda304f940342",
                        "1661dcd0bf4761d25471c1cf5514ceae",
                    ],
                    coords={_settings._set_coordinate_key: ["override0", "override1"]},
                ),
            }
        )
        .set_coords(_settings._hash_coordinate_key)
        .swap_dims({_settings._set_coordinate_key: _settings._hash_coordinate_key}),
        does_not_raise,
    ),
    "filled dataset, single parameter set": (
        parameter_generators.CartesianProduct({"parameter_1": [1]}).parameter_study.swap_dims(
            {_settings._set_coordinate_key: _settings._hash_coordinate_key}
        ),
        {},
        xarray.Dataset(
            {
                "parameter_1": xarray.DataArray([1], coords={_settings._set_coordinate_key: ["parameter_set0"]}),
                _settings._hash_coordinate_key: xarray.DataArray(
                    [
                        "1661dcd0bf4761d25471c1cf5514ceae",
                    ],
                    coords={_settings._set_coordinate_key: ["parameter_set0"]},
                ),
            }
        )
        .set_coords(_settings._hash_coordinate_key)
        .swap_dims({_settings._set_coordinate_key: _settings._hash_coordinate_key}),
        does_not_raise,
    ),
}


@pytest.mark.parametrize(
    ("parameter_study", "kwargs", "expected", "outcome"),
    test_update_set_names_cases.values(),
    ids=test_update_set_names_cases.keys(),
)
def test_update_set_names(
    parameter_study: xarray.Dataset,
    kwargs: dict,
    expected: xarray.Dataset,
    outcome: contextlib.nullcontext | pytest.RaisesExc,
) -> None:
    """Check the generated and updated parameter set names against template arguments.

    :param parameter_study: parameter study Xarray dataset
    :param kwargs: optional keyword arguments dictionary to pass through to the function under test
    :param expected: expected output parameter study Xarray dataset
    """
    with outcome:
        try:
            parameter_study = parameter_generators._update_set_names(parameter_study, **kwargs)
            xarray.testing.assert_identical(parameter_study, expected)
        finally:
            pass


def test_open_parameter_study() -> None:
    mock_file = "dummy.h5"
    with (
        patch("pathlib.Path.is_file", return_value=True),
        patch("xarray.open_dataset") as mock_open_dataset,
        patch("waves.parameter_generators._verify_parameter_study"),
        does_not_raise,
    ):
        parameter_generators._open_parameter_study(mock_file)
        mock_open_dataset.assert_called_once_with(mock_file, engine="h5netcdf")

    # Test missing file failure
    with (
        patch("pathlib.Path.is_file", return_value=False),
        patch("xarray.open_dataset") as mock_open_dataset,
        patch("waves.parameter_generators._verify_parameter_study"),
        pytest.raises(RuntimeError),
    ):
        parameter_generators._open_parameter_study(mock_file)
    mock_open_dataset.assert_not_called()

    # Test verification failure
    with (
        patch("pathlib.Path.is_file", return_value=True),
        patch("xarray.open_dataset") as mock_open_dataset,
        patch("waves.parameter_generators._verify_parameter_study", side_effect=RuntimeError),
        pytest.raises(RuntimeError),
    ):
        parameter_generators._open_parameter_study(mock_file)
    mock_open_dataset.assert_called_once_with(mock_file, engine="h5netcdf")


class TestParameterGenerator:
    """Class for testing ABC ParameterGenerator."""

    def test_output_file_conflict(self) -> None:
        with pytest.raises(MutuallyExclusiveError):
            DummyGenerator({}, output_file_template="out@number", output_file="single_output_file")

    def test_output_file_type(self) -> None:
        with pytest.raises(ChoicesError):
            # Specifically testing bad argument type handling. Ignore static type check.
            DummyGenerator({}, output_file_type="notsupported")  # type: ignore[arg-type]

    def test_missing_previous_parameter_study_file(self) -> None:
        with (
            patch("pathlib.Path.is_file", return_value=False),
            patch("waves.parameter_generators.ParameterGenerator._merge_parameter_studies") as mock_merge,
            pytest.raises(RuntimeError),
        ):
            missing_previous_study = DummyGenerator(
                {}, previous_parameter_study="doesnotexist.h5", require_previous_parameter_study=True
            )
        mock_merge.assert_not_called()

        with (
            patch("pathlib.Path.is_file", return_value=False),
            patch("waves.parameter_generators.ParameterGenerator._merge_parameter_studies") as mock_merge,
            patch("warnings.warn") as mock_warn,
            does_not_raise,
        ):
            try:
                missing_previous_study = DummyGenerator(
                    {}, previous_parameter_study="doesnotexist.h5", require_previous_parameter_study=False
                )
                assert isinstance(missing_previous_study, parameter_generators.ParameterGenerator)
                mock_merge.assert_not_called()
                mock_warn.assert_called_once()
            finally:
                pass

    scons_write_cases = {
        "no kwargs": ({}, {}),
        "output file type": ({"output_file_type": "h5"}, {"output_file_type": "h5"}),
        "unused keyword argument": ({"unused": "should not show up in call"}, {}),
    }

    @pytest.mark.parametrize(
        ("env", "expected_kwargs"),
        scons_write_cases.values(),
        ids=scons_write_cases.keys(),
    )
    def test_scons_write(self, env: dict, expected_kwargs: dict) -> None:
        scons_write = DummyGenerator({})
        with patch("waves.parameter_generators.ParameterGenerator.write") as mock_write:
            # Fake an SCons environment with a dictionary. SCons environment object not required for unit testing
            scons_write._scons_write([], [], env)
        mock_write.assert_called_once_with(**expected_kwargs)

    templates: dict[str, tuple] = {
        "no template": ({}, None, None, ["parameter_set0"]),
        "file template": ({}, "out", None, ["out0"]),
        "set template": ({}, None, "out@number", ["out0"]),
        "set template, overridden": ({}, "out", "overridden", ["out0"]),
    }

    def test_merge_parameter_studies_with_missing_previous_parameter_study(self) -> None:
        # Test exception on missing previous parameter study attribute
        dummy_generator = DummyGenerator({})
        dummy_generator.previous_parameter_study = None
        with pytest.raises(RuntimeError):
            dummy_generator._merge_parameter_studies()

    @pytest.mark.parametrize("length", range(1, 20, 5))
    def test_parameter_study_to_dict(self, length: int) -> None:
        expected_by_hash = {
            parameter_generators._calculate_set_hash(["parameter_1"], [float(index)]): {"parameter_1": float(index)}
            for index in range(length)
        }
        expected = {
            f"parameter_set{index}": expected_by_hash[item]
            for index, item in enumerate(sorted(expected_by_hash.keys()))
        }
        scons_iterator = DummyGenerator({}, sets=length)
        set_samples = scons_iterator.parameter_study_to_dict()
        assert set_samples == expected
        assert all(isinstance(key, str) for key in set_samples)
        for set_name, set_value in expected.items():
            assert set_value == set_samples[set_name]
            for parameter in set_value:
                assert type(set_samples[set_name][parameter]) is type(set_value[parameter])

    @pytest.mark.parametrize(
        ("schema", "file_template", "set_template", "expected"),
        templates.values(),
        ids=templates.keys(),
    )
    def test_set_names(
        self, schema: dict, file_template: str | None, set_template: str | None, expected: list[str]
    ) -> None:
        """Check the generated parameter set names against template arguments.

        :param str schema: placeholder string standing in for the schema read from an input file
        :param str file_template: user supplied string to be used as a template for output file names
        :param str set_template: user supplied string to be used as a template for parameter names
        :param list expected: list of expected parameter name strings
        """
        if not set_template:
            template_generator = DummyGenerator(schema, output_file_template=file_template, sets=1)
        else:
            template_generator = DummyGenerator(
                schema, output_file_template=file_template, set_name_template=set_template, sets=1
            )
        assert list(template_generator._set_names.values()) == expected
        assert list(template_generator.parameter_study[_settings._set_coordinate_key].values) == expected

    @pytest.mark.parametrize(
        ("schema", "file_template", "set_template", "expected"),
        templates.values(),
        ids=templates.keys(),
    )
    def test_merge_parameter_studies(
        self, schema: dict, file_template: str | None, set_template: str | None, expected: list[str]
    ) -> None:
        """Check the generated parameter set names against template arguments after a merge operation.

        :param str schema: placeholder string standing in for the schema read from an input file
        :param str file_template: user supplied string to be used as a template for output file names
        :param str set_template: user supplied string to be used as a template for parameter names
        :param list expected: list of expected parameter name strings
        """
        mock_previous_study_name = "dummy_study.h5"
        if not set_template:
            mock_previous_study = DummyGenerator(schema, output_file_template=file_template, sets=1).parameter_study
            template_generator = DummyGenerator(
                schema, output_file_template=file_template, previous_parameter_study=mock_previous_study_name, sets=1
            )
        else:
            mock_previous_study = DummyGenerator(
                schema, output_file_template=file_template, set_name_template=set_template, sets=1
            ).parameter_study
            template_generator = DummyGenerator(
                schema,
                output_file_template=file_template,
                set_name_template=set_template,
                previous_parameter_study=mock_previous_study_name,
                sets=1,
            )
        with patch("waves.parameter_generators._open_parameter_study", return_value=mock_previous_study):
            assert list(template_generator._set_names.values()) == expected
            assert list(template_generator.parameter_study[_settings._set_coordinate_key].values) == expected
            template_generator._merge_parameter_studies()
            assert list(template_generator._set_names.values()) == expected
            assert list(template_generator.parameter_study[_settings._set_coordinate_key].values) == expected

    init_write_stdout: dict[str, tuple] = {
        "no-template-1": ({}, None, False, False, [False], 1, 1),
        "no-template-2": ({}, None, True, False, [False], 1, 1),
        "no-template-3": ({}, None, False, True, [False, False], 2, 1),
        "no-template-4": ({}, None, False, False, [True, True], 2, 1),
        "dry_run-1": ({}, "out", False, True, [False], 1, 1),
        "dry_run-2": ({}, "out", True, True, [False], 1, 1),
        "dry_run-3": ({}, "out", True, True, [True, False], 2, 2),
        "dry_run-4": ({}, "out", False, True, [False, True], 1, 1),
    }

    @pytest.mark.parametrize(
        ("schema", "template", "overwrite", "dry_run", "is_file", "sets", "stdout_calls"),
        init_write_stdout.values(),
        ids=init_write_stdout.keys(),
    )
    def test_write_to_stdout(
        self,
        schema: dict,
        template: str | None,
        overwrite: bool,
        dry_run: bool,
        is_file: bool,
        sets: int,
        stdout_calls: int,
    ) -> None:
        """Check for conditions that should result in calls to stdout.

        :param str schema: placeholder string standing in for the schema read from an input file
        :param str template: user supplied string to be used as a template for output file names
        :param bool overwrite: overwrite existing files
        :param bool dry_run: skip file write, but show file name and associated contents that would ahve been written
        :param bool is_file: test specific argument mocks output for pathlib.Path().is_file()
        :param int sets: test specific argument for the number of sets to build for the test
        :param int stdout_calls: number of calls to stdout. Should only differ from set count when no template is
            provides. Should always be 1 when no template is provided.
        """
        for output_file_type in _settings._allowable_output_file_types:
            write_parameter_generator = DummyGenerator(
                schema,
                output_file_template=template,
                output_file_type=output_file_type,
                overwrite=overwrite,
                sets=sets,
            )
            with (
                patch("waves.parameter_generators.ParameterGenerator._write_meta"),
                patch("pathlib.Path.open", mock_open()) as mock_file,
                patch("sys.stdout.write") as stdout_write,
                patch("xarray.Dataset.to_netcdf") as xarray_to_netcdf,
                patch("pathlib.Path.is_file", side_effect=is_file),
                patch("pathlib.Path.mkdir"),
            ):
                write_parameter_generator.write(dry_run=dry_run)
                mock_file.assert_not_called()
                xarray_to_netcdf.assert_not_called()
                assert stdout_write.call_count == stdout_calls

    init_write_files: dict[str, tuple] = {
        "template-1": ({}, "out", False, [False], 1, 1),
        "template-2": ({}, "out", False, [False, False], 2, 2),
        "template-3": ({}, "out", False, [True, True], 2, 0),
        "template-4": ({}, "out", False, [True, False], 2, 1),
        "overwrite-2": ({}, "out", True, [False, False], 2, 2),
        "overwrite-3": ({}, "out", True, [True, True], 2, 2),
        "overwrite-4": ({}, "out", True, [True, False], 2, 2),
    }

    @pytest.mark.parametrize(
        ("schema", "template", "overwrite", "is_file", "sets", "files"),
        init_write_files.values(),
        ids=init_write_files.keys(),
    )
    def test_write_yaml(
        self, schema: dict, template: str, overwrite: bool, is_file: list[bool], sets: int, files: int
    ) -> None:
        """Check for conditions that should result in calls to builtins.open.

        :param str schema: placeholder string standing in for the schema read from an input file
        :param str template: user supplied string to be used as a template for output file names
        :param bool overwrite: overwrite existing files
        :param list is_file: test specific argument mocks changing output for pathlib.Path().is_file() repeat calls
        :param int sets: test specific argument for the number of sets to build for the test
        :param int files: integer number of files that should be written
        """
        write_parameter_generator = DummyGenerator(
            schema,
            output_file_template=template,
            output_file_type="yaml",
            overwrite=overwrite,
            sets=sets,
        )
        with (
            patch("waves.parameter_generators.ParameterGenerator._write_meta"),
            patch("waves.parameter_generators.ParameterGenerator._conditionally_write_yaml") as mock_write_yaml,
            patch("waves.parameter_generators.ParameterGenerator._conditionally_write_dataset") as mock_write_dataset,
            patch("sys.stdout.write") as stdout_write,
            patch("pathlib.Path.is_file", side_effect=is_file),
        ):
            write_parameter_generator.write()
            stdout_write.assert_not_called()
            mock_write_dataset.assert_not_called()
            assert mock_write_yaml.call_count == files

        mismatched_output_type = DummyGenerator(
            schema,
            output_file_template=template,
            output_file_type="h5",
            overwrite=overwrite,
            sets=sets,
        )
        with (
            patch("waves.parameter_generators.ParameterGenerator._write_meta"),
            patch("waves.parameter_generators.ParameterGenerator._conditionally_write_yaml") as mock_write_yaml,
            patch("waves.parameter_generators.ParameterGenerator._conditionally_write_dataset") as mock_write_dataset,
            patch("sys.stdout.write") as stdout_write,
            patch("pathlib.Path.is_file", side_effect=is_file),
        ):
            mismatched_output_type.write(output_file_type="yaml")
            stdout_write.assert_not_called()
            mock_write_dataset.assert_not_called()
            assert mock_write_yaml.call_count == files

    @pytest.mark.parametrize(
        ("schema", "template", "overwrite", "is_file", "sets", "files"),
        init_write_files.values(),
        ids=init_write_files.keys(),
    )
    def test_write_dataset(
        self, schema: dict, template: str, overwrite: bool, is_file: list[bool], sets: int, files: int
    ) -> None:
        """Check for conditions that should result in calls to ParameterGenerator._write_netcdf.

        :param str schema: placeholder string standing in for the schema read from an input file
        :param str template: user supplied string to be used as a template for output file names
        :param bool overwrite: overwrite existing files
        :param list is_file: test specific argument mocks changing output for pathlib.Path().is_file() repeat calls
        :param int sets: test specific argument for the number of sets to build for the test
        :param int files: integer number of files that should be written
        """
        write_parameter_generator = DummyGenerator(
            schema,
            output_file_template=template,
            output_file_type="h5",
            overwrite=overwrite,
            sets=sets,
        )
        with (
            patch("waves.parameter_generators.ParameterGenerator._write_meta"),
            patch("sys.stdout.write") as stdout_write,
            patch("waves.parameter_generators.ParameterGenerator._conditionally_write_yaml") as mock_write_yaml,
            patch("waves.parameter_generators.ParameterGenerator._conditionally_write_dataset") as mock_write_dataset,
            patch("pathlib.Path.is_file", side_effect=is_file),
            patch("pathlib.Path.mkdir"),
        ):
            write_parameter_generator.write()
            stdout_write.assert_not_called()
            mock_write_yaml.assert_not_called()
            assert mock_write_dataset.call_count == files

        mismatched_output_type = DummyGenerator(
            schema,
            output_file_template=template,
            output_file_type="yaml",
            overwrite=overwrite,
            sets=sets,
        )
        with (
            patch("waves.parameter_generators.ParameterGenerator._write_meta"),
            patch("sys.stdout.write") as stdout_write,
            patch("waves.parameter_generators.ParameterGenerator._conditionally_write_yaml") as mock_write_yaml,
            patch("waves.parameter_generators.ParameterGenerator._conditionally_write_dataset") as mock_write_dataset,
            patch("pathlib.Path.is_file", side_effect=is_file),
            patch("pathlib.Path.mkdir"),
        ):
            mismatched_output_type.write(output_file_type="h5")
            stdout_write.assert_not_called()
            mock_write_yaml.assert_not_called()
            assert mock_write_dataset.call_count == files

    init_write_dataset_files = {
        "equal-datasets": (True, [True], False, 0),
        "equal-overwrite": (True, [True], True, 1),
        "different-datasets": (False, [True], False, 1),
        "not-file-1": (True, [False], False, 1),
        "not-file-2": (False, [False], False, 1),
    }

    @pytest.mark.parametrize(
        ("equals", "is_file", "overwrite", "expected_call_count"),
        init_write_dataset_files.values(),
        ids=init_write_dataset_files.keys(),
    )
    def test_conditionally_write_dataset(
        self, equals: bool, is_file: list[bool], overwrite: bool, expected_call_count: int
    ) -> None:
        """Check for conditions that should result in calls to xarray.Dataset.to_netcdf.

        :param bool equals: parameter that identifies when the xarray.Dataset objects should be equal
        :param list is_file: test specific argument mocks changing output for pathlib.Path().is_file() repeat calls
        :param bool overwrite: parameter that identifies when the file should always be overwritten
        :param int expected_call_count: amount of times that the xarray.Dataset.to_netcdf function should be called
        """
        write_parameter_generator = DummyGenerator({}, overwrite=overwrite)

        with (
            patch("xarray.Dataset.to_netcdf") as xarray_to_netcdf,
            patch("xarray.open_dataset", mock_open()),
            patch("xarray.Dataset.equals", return_value=equals),
            patch("pathlib.Path.is_file", side_effect=is_file),
        ):
            write_parameter_generator._conditionally_write_dataset(pathlib.Path("dummy_string"), xarray.Dataset())
            assert xarray_to_netcdf.call_count == expected_call_count

    @pytest.mark.parametrize(
        ("equals", "is_file", "overwrite", "expected_call_count"),
        init_write_dataset_files.values(),
        ids=init_write_dataset_files.keys(),
    )
    def test_conditionally_write_yaml(
        self, equals: bool, is_file: list[bool], overwrite: bool, expected_call_count: int
    ) -> None:
        """Check for conditions that should result in writing out to file.

        :param bool equals: parameter that identifies when the dictionaries should be equal
        :param list is_file: test specific argument mocks changing output for pathlib.Path().is_file() repeat calls
        :param bool overwrite: parameter that identifies when the file should always be overwritten
        :param int expected_call_count: amount of times that the open.write function should be called
        """
        write_parameter_generator = DummyGenerator({}, overwrite=overwrite)
        existing_dict = {"dummy": "dict"} if equals else {"smart": "dict"}

        with (
            patch("pathlib.Path.open", mock_open()) as write_yaml_file,
            patch("yaml.safe_load", return_value=existing_dict),
            patch("pathlib.Path.is_file", side_effect=is_file),
        ):
            write_parameter_generator._conditionally_write_yaml("dummy_string", {"dummy": "dict"})
            assert write_yaml_file.return_value.write.call_count == expected_call_count

    def test_write_type_override(self) -> None:
        output_file_type_combinations: tuple[
            tuple[_settings._allowable_output_file_typing, _settings._allowable_output_file_typing], ...
        ] = (("yaml", "h5"), ("h5", "yaml"))
        for instantiated_type, override_type in output_file_type_combinations:
            write_parameter_generator = DummyGenerator({}, output_file_type=instantiated_type)
            private_write_arguments = {
                "yaml": (
                    write_parameter_generator.parameter_study_to_dict(),
                    write_parameter_generator.parameter_study_to_dict().items(),
                    write_parameter_generator._conditionally_write_yaml,
                ),
                "h5": (
                    write_parameter_generator.parameter_study,
                    write_parameter_generator.parameter_study.groupby(_settings._set_coordinate_key),
                    write_parameter_generator._conditionally_write_dataset,
                ),
            }
            instantiated_arguments = private_write_arguments[instantiated_type]
            override_arguments = private_write_arguments[override_type]

            # Bare call should try to write YAML.
            # TODO: assert called with the correct objects or continue refactoring _write
            with (
                patch("waves.parameter_generators.ParameterGenerator._write_meta"),
                patch("waves.parameter_generators.ParameterGenerator._write") as mock_private_write,
            ):
                write_parameter_generator.write()
                mock_private_write.assert_called_once()
                assert mock_private_write.call_args[0][0] == instantiated_arguments[0]
                # FIXME: Can't do boolean comparisons on xarray.Dataset.GroupBy objects.
                # Prefer to refactor _write interface over complicated test
                if isinstance(instantiated_arguments[0], dict):
                    assert mock_private_write.call_args[0][1] == instantiated_arguments[1]
                assert mock_private_write.call_args[0][2] == instantiated_arguments[2]

            # Override should try to write H5.
            # TODO: assert called with the correct objects or continue refactoring _write
            with (
                patch("waves.parameter_generators.ParameterGenerator._write_meta"),
                patch("waves.parameter_generators.ParameterGenerator._write") as mock_private_write,
            ):
                write_parameter_generator.write(output_file_type=override_type)
                mock_private_write.assert_called_once()
                assert mock_private_write.call_args[0][0] == override_arguments[0]
                # FIXME: Can't do boolean comparisons on xarray.Dataset.GroupBy objects.
                # Prefer to refactor _write interface over complicated test
                if isinstance(override_arguments[0], dict):
                    assert mock_private_write.call_args[0][1] == override_arguments[1]
                assert mock_private_write.call_args[0][2] == override_arguments[2]

    def test_write_exception(self) -> None:
        """Calling a non-supported format string should raise an exception."""
        write_parameter_generator = DummyGenerator({})
        with (
            patch("waves.parameter_generators.ParameterGenerator._write_meta"),
            patch("waves.parameter_generators.ParameterGenerator._write") as mock_private_write,
            pytest.raises(ChoicesError),
        ):
            # Specifically testing bad argument type handling. Ignore static type check.
            write_parameter_generator.write(output_file_type="unsupported")  # type: ignore[arg-type]
        mock_private_write.assert_not_called()

    def test_write_call_to_write_meta(self) -> None:
        write_parameter_generator = DummyGenerator({})
        write_parameter_generator.write_meta = True
        write_parameter_generator.provided_output_file_template = True
        with (
            patch("waves.parameter_generators.ParameterGenerator._write_meta") as mock_write_meta,
            patch("waves.parameter_generators.ParameterGenerator._write") as mock_private_write,
        ):
            write_parameter_generator.write()
            mock_write_meta.assert_called_once()
            mock_private_write.assert_called_once()

    def test_write_meta(self) -> None:
        write_meta_parameter_generator = DummyGenerator({})
        with (
            patch("pathlib.Path.open", mock_open()) as mock_file,
            patch("pathlib.Path.resolve", return_value=pathlib.Path("parameter_set1.h5")),
        ):
            write_meta_parameter_generator._write_meta()
            handle = mock_file()
            handle.write.assert_called_once_with("parameter_set1.h5\n")

        write_meta_parameter_generator.output_file = pathlib.Path("dummy.h5")
        with (
            patch("pathlib.Path.open", mock_open()) as mock_file,
            patch("pathlib.Path.resolve", return_value=pathlib.Path("dummy.h5")),
        ):
            write_meta_parameter_generator._write_meta()
            handle = mock_file()
            handle.write.assert_called_once_with("dummy.h5\n")

    @pytest.mark.parametrize(
        ("parameter_names", "samples", "expected_hashes"),
        set_hashes.values(),
        ids=set_hashes.keys(),
    )
    def test_create_set_hashes(
        self, parameter_names: list[str], samples: numpy.ndarray, expected_hashes: list[str]
    ) -> None:
        hashes_parameter_generator = DummyGenerator({})
        hashes_parameter_generator._parameter_names = parameter_names
        hashes_parameter_generator._samples = samples
        del hashes_parameter_generator._set_hashes
        assert not hasattr(hashes_parameter_generator, "_set_hashes")
        # Check the function setting the set hashes attribute.
        hashes_parameter_generator._create_set_hashes()
        assert hashes_parameter_generator._set_hashes == expected_hashes

    def test_create_set_names(self) -> None:
        """Test the parameter set name generation."""
        set_names_parameter_generator = DummyGenerator({}, output_file_template="out")
        set_names_parameter_generator._samples = numpy.array([[1], [2]])
        set_names_parameter_generator._create_set_hashes()
        set_names_parameter_generator._create_set_names()
        assert list(set_names_parameter_generator._set_names.values()) == ["out0", "out1"]

    def test_parameter_study_to_numpy(self) -> None:
        """Test the self-consistency of the parameter study dataset construction and deconstruction."""
        # Setup
        data_parameter_generator = DummyGenerator({})
        data_parameter_generator._parameter_names = ["ints", "floats", "strings", "bools"]
        data_parameter_generator._samples = numpy.array([[1, 10.1, "a", True], [2, 20.2, "b", False]], dtype=object)
        data_parameter_generator._create_set_hashes()
        data_parameter_generator._create_set_names()
        data_parameter_generator._create_parameter_study()
        # Test class method
        returned_samples = data_parameter_generator._parameter_study_to_numpy()
        assert numpy.all(returned_samples == data_parameter_generator._samples)
        # Test module function
        returned_samples = parameter_generators._parameter_study_to_numpy(data_parameter_generator.parameter_study)


class TestParameterDistributions:
    """Class for testing _ScipyGenerator ABC class common methods."""

    def test_sampler_class_handling(self) -> None:
        class MissingRequiredAttribute(parameter_generators._ScipyGenerator):
            def __init__(self, *args, **kwargs) -> None:
                super().__init__(*args, **kwargs)

        class HasRequiredAttribute(parameter_generators._ScipyGenerator):
            sampler_class = "dummy"

            def _validate(self) -> None:
                pass

            def _generate(self, **kwargs) -> None:
                pass

        with pytest.raises(
            ValueError, match="_ScipyGenerator subclasses must set ``sampler_class`` to a non-empty string"
        ):
            MissingRequiredAttribute({})

        with does_not_raise:
            HasRequiredAttribute({})

    validate_input = {
        "good schema": (
            {"num_simulations": 1, "parameter_1": {"distribution": "norm", "kwarg1": 1}},
            does_not_raise,
        ),
        "not a dict": (
            "not a dict",
            pytest.raises(SchemaValidationError),
        ),
        "missing num_simulation": (
            {},
            pytest.raises(SchemaValidationError),
        ),
        "num_simulation non-integer": (
            {"num_simulations": "not_a_number"},
            pytest.raises(SchemaValidationError),
        ),
        "missing distribution": (
            {"num_simulations": 1, "parameter_1": {}},
            pytest.raises(SchemaValidationError),
        ),
        "distribution non-string": (
            {"num_simulations": 1, "parameter_1": {"distribution": 1}},
            pytest.raises(SchemaValidationError),
        ),
        "distribution bad identifier": (
            {"num_simulations": 1, "parameter_1": {"distribution": "my norm"}},
            pytest.raises(SchemaValidationError),
        ),
        "kwarg bad identifier": (
            {"num_simulations": 1, "parameter_1": {"distribution": "norm", "kwarg 1": 1}},
            pytest.raises(SchemaValidationError),
        ),
    }

    @pytest.mark.parametrize(
        ("parameter_schema", "outcome"),
        validate_input.values(),
        ids=validate_input.keys(),
    )
    def test_validate(self, parameter_schema: dict, outcome: contextlib.nullcontext | pytest.RaisesExc) -> None:
        with (
            patch("waves.parameter_generators._ScipyGenerator._generate_parameter_distributions") as mock_distros,
            outcome,
        ):
            try:
                # Validate is called in __init__. Do not need to call explicitly.
                test_validate = ParameterDistributions(parameter_schema)
                assert isinstance(test_validate, parameter_generators.ParameterGenerator)
                mock_distros.assert_called_once()
            finally:
                pass

    generate_input = {
        "good schema 5x2": (
            {
                "num_simulations": 5,
                "parameter_1": {"distribution": "norm", "loc": 50, "scale": 1},
                "parameter_2": {"distribution": "norm", "loc": -50, "scale": 1},
            },
            [{"loc": 50, "scale": 1}, {"loc": -50, "scale": 1}],
        ),
        "good schema 2x1": (
            {
                "num_simulations": 2,
                "parameter_1": {"distribution": "norm", "loc": 50, "scale": 1},
            },
            [{"loc": 50, "scale": 1}],
        ),
        "good schema 1x2": (
            {
                "num_simulations": 1,
                "parameter_1": {"distribution": "norm", "loc": 50, "scale": 1},
                "parameter_2": {"distribution": "norm", "loc": -50, "scale": 1},
            },
            [{"loc": 50, "scale": 1}, {"loc": -50, "scale": 1}],
        ),
    }

    @pytest.mark.parametrize(
        ("parameter_schema", "expected_scipy_kwds"),
        generate_input.values(),
        ids=generate_input.keys(),
    )
    def test_generate_parameter_distributions(
        self, parameter_schema: dict, expected_scipy_kwds: list[dict[str, typing.Any]]
    ) -> None:
        test_distributions = ParameterDistributions(parameter_schema)
        assert test_distributions._parameter_names == list(test_distributions.parameter_distributions.keys())
        for parameter_name, expected_kwds in zip(test_distributions._parameter_names, expected_scipy_kwds, strict=True):
            assert test_distributions.parameter_distributions[parameter_name].kwds == expected_kwds


class DummyGenerator(parameter_generators.ParameterGenerator):
    def _validate(self) -> None:
        self._parameter_names = ["parameter_1"]

    def _generate(self, sets: int = 1, **kwargs) -> None:
        """Generate float samples for all parameters. Value matches parameter set index."""
        parameter_count = len(self._parameter_names)
        self._samples = numpy.ones((sets, parameter_count))
        for row in range(sets):
            self._samples[row, :] = self._samples[row, :] * row
        super()._generate(**kwargs)


class ParameterDistributions(parameter_generators._ScipyGenerator):
    sampler_class = "dummy"

    def _generate(self, **kwargs) -> None:
        pass
