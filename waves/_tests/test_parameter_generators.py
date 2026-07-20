"""Test ParameterGenerator Abstract Base Class."""

import contextlib
import copy
import pathlib
import string
import typing
from unittest.mock import call, mock_open, patch

import numpy
import pytest
import xarray

from waves import _settings, _utilities, parameter_generators
from waves.exceptions import APIError, ChoicesError, MutuallyExclusiveError, SchemaValidationError

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
    "CartesianProduct: mixed length strings": (
        parameter_generators.CartesianProduct({"parameter_1": ["one", "two", "many"]}).parameter_study,
        parameter_generators.CartesianProduct({"parameter_1": ["one", "two", "many"]}).parameter_study,
        {"parameter_1": numpy.dtype("U")},
        does_not_raise,
    ),
    "CartesianProduct: increasing length strings": (
        parameter_generators.CartesianProduct({"parameter_1": ["one", "two"]}).parameter_study,
        parameter_generators.CartesianProduct({"parameter_1": ["one", "two", "many"]}).parameter_study,
        {"parameter_1": numpy.dtype("U")},
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
        {"parameter_1": numpy.int64, "parameter_2": numpy.float64, "parameter_3": numpy.dtype("U")},
        does_not_raise,
    ),
    "CartesianProduct: extra parameters bools": (
        parameter_generators.CartesianProduct({"parameter_1": [1], "parameter_3": ["a"]}).parameter_study,
        parameter_generators.CartesianProduct({"parameter_1": [1], "parameter_2": [True]}).parameter_study,
        {"parameter_1": numpy.int64, "parameter_2": bool, "parameter_3": numpy.dtype("U")},
        does_not_raise,
    ),
    "CartesianProduct: inconsistent types: int/float": (
        parameter_generators.CartesianProduct({"parameter_1": [1]}).parameter_study,
        parameter_generators.CartesianProduct({"parameter_1": [1.0]}).parameter_study,
        None,
        pytest.raises(RuntimeError),
    ),
    "CartesianProduct: inconsistent types: int/str": (
        parameter_generators.CartesianProduct({"parameter_1": [1]}).parameter_study,
        parameter_generators.CartesianProduct({"parameter_1": ["a"]}).parameter_study,
        None,
        pytest.raises(RuntimeError),
    ),
    "CartesianProduct: inconsistent types: int/bool": (
        parameter_generators.CartesianProduct({"parameter_1": [1]}).parameter_study,
        parameter_generators.CartesianProduct({"parameter_1": [True]}).parameter_study,
        None,
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
        {"parameter_1": numpy.int64, "parameter_2": numpy.float64, "parameter_3": numpy.dtype("U")},
        does_not_raise,
    ),
    "OneAtATime: extra parameters bools": (
        parameter_generators.OneAtATime({"parameter_1": [1], "parameter_3": ["a"]}).parameter_study,
        parameter_generators.OneAtATime({"parameter_1": [1], "parameter_2": [True]}).parameter_study,
        {"parameter_1": numpy.int64, "parameter_2": bool, "parameter_3": numpy.dtype("U")},
        does_not_raise,
    ),
    "OneAtATime: inconsistent types: int/float": (
        parameter_generators.OneAtATime({"parameter_1": [1]}).parameter_study,
        parameter_generators.OneAtATime({"parameter_1": [1.0]}).parameter_study,
        None,
        pytest.raises(RuntimeError),
    ),
    "OneAtATime: inconsistent types: int/str": (
        parameter_generators.OneAtATime({"parameter_1": [1]}).parameter_study,
        parameter_generators.OneAtATime({"parameter_1": ["a"]}).parameter_study,
        None,
        pytest.raises(RuntimeError),
    ),
    "OneAtATime: inconsistent types: int/bool": (
        parameter_generators.OneAtATime({"parameter_1": [1]}).parameter_study,
        parameter_generators.OneAtATime({"parameter_1": [True]}).parameter_study,
        None,
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
        {},
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
        {},
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
        {},
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
        {},
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
        {},
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
        {},
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
        {},
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
        {},
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
        {},
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
        {},
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
        {},
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
        {},
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
        {},
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
        {},
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
        {},
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
    "propagate four parameter sets into three sets, set name template": (
        [
            parameter_generators.CartesianProduct({"parameter_1": [1.0, 2.0, 3.0]}).parameter_study,
            parameter_generators.CartesianProduct({"parameter_2": ["a", "b"], "parameter_3": [3, 4]}).parameter_study,
        ],
        {"template": _utilities._AtSignTemplate("set@number")},
        parameter_generators.CartesianProduct(
            {
                "parameter_1": [1.0, 2.0, 3.0],
                "parameter_2": ["a", "b"],
                "parameter_3": [3, 4],
            },
            set_name_template="set@number",
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
        {},
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
    "propagate three parameter sets into four sets, set name template": (
        [
            parameter_generators.CartesianProduct({"parameter_2": ["a", "b"], "parameter_3": [3, 4]}).parameter_study,
            parameter_generators.CartesianProduct({"parameter_1": [1.0, 2.0, 3.0]}).parameter_study,
        ],
        {"template": _utilities._AtSignTemplate("set@number")},
        parameter_generators.CartesianProduct(
            {
                "parameter_1": [1.0, 2.0, 3.0],
                "parameter_2": ["a", "b"],
                "parameter_3": [3, 4],
            },
            set_name_template="set@number",
        ).parameter_study,
        {
            "parameter_1": numpy.float64,
            "parameter_2": numpy.dtype("U1"),
            "parameter_3": numpy.int64,
        },
        True,
        does_not_raise,
    ),
    "propagate one parameter: int, set name template": (
        [
            parameter_generators.OneAtATime({"parameter_1": [1]}).parameter_study,
            parameter_generators.OneAtATime({"parameter_2": [2]}).parameter_study,
        ],
        {"template": _utilities._AtSignTemplate("set@number")},
        parameter_generators.OneAtATime(
            {"parameter_1": [1], "parameter_2": [2]}, set_name_template="set@number"
        ).parameter_study,
        {"parameter_1": numpy.int64, "parameter_2": numpy.int64},
        True,
        does_not_raise,
    ),
    "propagate one parameter: int, set name template, mixed original set names": (
        [
            parameter_generators.OneAtATime({"parameter_1": [1]}, set_name_template="first@number").parameter_study,
            parameter_generators.OneAtATime({"parameter_2": [2]}, set_name_template="second@number").parameter_study,
        ],
        {"template": _utilities._AtSignTemplate("set@number")},
        parameter_generators.OneAtATime(
            {"parameter_1": [1], "parameter_2": [2]}, set_name_template="set@number"
        ).parameter_study,
        {"parameter_1": numpy.int64, "parameter_2": numpy.int64},
        True,
        does_not_raise,
    ),
}


@pytest.mark.parametrize(
    ("studies", "kwargs", "expected_study", "expected_types", "propagate_space", "outcome"),
    propagate_parameter_space_cases.values(),
    ids=propagate_parameter_space_cases.keys(),
)
def test_propagate_parameter_space(
    studies: list[xarray.Dataset],
    kwargs: dict,
    expected_study: xarray.Dataset,
    expected_types: dict[str, type],
    propagate_space: bool,  # noqa: ARG001, placeholder argument for test case compatibility with downstream functions
    outcome: contextlib.nullcontext | pytest.RaisesExc,
) -> None:
    """Check the propagation of parameter space between two studies.

    :param studies: list of N number of parameter study Xarray datasets to merge, where the first study in the list is
        the base study
    :param kwargs: the function keyword arguments
    :param expected_study: Xarray dataset
    :param expected_types: dictionary with parameter names as the keys and numpy types as values
    :param propagate_space: boolean indicating if parameter space propagation is used to construct the output study
    :param outcome: pytest expected error for the test case
    """
    study_base, study_other = studies
    with outcome:
        try:
            propagated_study = parameter_generators._propagate_parameter_space(study_base, study_other, **kwargs)
            for key, parameter_type in expected_types.items():
                assert propagated_study[key].dtype == parameter_type
            xarray.testing.assert_identical(propagated_study, expected_study)
            parameter_generators._verify_parameter_study(propagated_study)
        finally:
            pass


merge_parameter_space_cases: dict = {
    "concatenate along one parameter: unchanged": (
        [
            parameter_generators.OneAtATime({"parameter_1": [1]}).parameter_study,
            parameter_generators.OneAtATime({"parameter_1": [1]}).parameter_study,
        ],
        {},
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
        {},
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
        {},
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
        {},
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
        {},
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
        {},
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
        {},
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
        {},
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
        {},
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
        {},
        parameter_generators.CartesianProduct(
            {"parameter_1": [1, 2], "parameter_2": [3.0], "parameter_3": [True, False]}
        ).parameter_study,
        {"parameter_1": numpy.int64, "parameter_2": numpy.float64, "parameter_3": numpy.bool_},
        False,
        does_not_raise,
    ),
}


@pytest.mark.parametrize(
    ("studies", "kwargs", "expected_study", "expected_types", "propagate_space", "outcome"),
    merge_parameter_space_cases.values(),
    ids=merge_parameter_space_cases.keys(),
)
def test_merge_parameter_space(
    studies: list[xarray.Dataset],
    kwargs: dict,
    expected_study: xarray.Dataset,
    expected_types: dict[str, type],
    propagate_space: bool,
    outcome: contextlib.nullcontext | pytest.RaisesExc,
) -> None:
    """Check the propagation of parameter space between two studies.

    :param studies: list of N number of parameter study Xarray datasets to merge, where the first study in the list is
        the base study
    :param kwargs: the function keyword arguments
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
            merged_study = parameter_generators._merge_parameter_space(studies, **kwargs)
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
            {},
            None,
            None,
            None,
            pytest.raises(RuntimeError, match="Not enough parameter studies provided for merge operation"),
        ),
        "concatenate original_index should raise": (
            [
                parameter_generators.SALibSampler(
                    "latin",
                    {
                        "N": 2,
                        "problem": {
                            "num_vars": 1,
                            "names": ["parameter_1"],
                            "bounds": [[-1, 1]],
                        },
                    },
                    seed=42,
                    original_index=True,
                ).parameter_study,
                parameter_generators.SALibSampler(
                    "latin",
                    {
                        "N": 2,
                        "problem": {
                            "num_vars": 1,
                            "names": ["parameter_1"],
                            "bounds": [[-1, 1]],
                        },
                    },
                    seed=42,
                    original_index=True,
                ).parameter_study,
            ],
            {},
            None,
            None,
            None,
            pytest.raises(
                RuntimeError, match="The 'original_index' coordinate is incompatible with merging parameter studies"
            ),
        ),
        "concatenate with different numbers of parameters": (
            [
                parameter_generators.OneAtATime({"parameter_1": [1.0]}).parameter_study,
                parameter_generators.OneAtATime({"parameter_1": [2.0], "parameter_2": [3]}).parameter_study,
            ],
            {},
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
            {},
            parameter_generators.CartesianProduct({"parameter_1": [1, 2], "parameter_2": [3.0, 4.0]}).parameter_study,
            {"parameter_1": numpy.int64, "parameter_2": numpy.float64},
            True,
            does_not_raise,
        ),
        "merge and propagate: three studies, two parameter spaces - int/float, mismatched template request": (
            [
                parameter_generators.CartesianProduct({"parameter_1": [1]}).parameter_study,
                parameter_generators.CartesianProduct({"parameter_1": [2]}).parameter_study,
                parameter_generators.CartesianProduct({"parameter_2": [3.0, 4.0]}).parameter_study,
            ],
            {"template": _utilities._AtSignTemplate("set@number")},
            None,
            {"parameter_1": numpy.int64, "parameter_2": numpy.float64},
            True,
            pytest.raises(
                RuntimeError,
                match=r"Could not fill merged parameter set names. Does the parameter set naming convention match?",
            ),
        ),
        "merge and propagate: three studies, two parameter spaces - int/float, mismatched original set name template": (
            [
                parameter_generators.CartesianProduct(
                    {"parameter_1": [1]}, set_name_template="set@number"
                ).parameter_study,
                parameter_generators.CartesianProduct({"parameter_1": [2]}).parameter_study,
                parameter_generators.CartesianProduct({"parameter_2": [3.0, 4.0]}).parameter_study,
            ],
            {},
            None,
            {"parameter_1": numpy.int64, "parameter_2": numpy.float64},
            True,
            pytest.raises(
                RuntimeError,
                match=r"Could not fill merged parameter set names. Does the parameter set naming convention match?",
            ),
        ),
        "merge and propagate: four studies, two parameter spaces - string/bool": (
            [
                parameter_generators.CartesianProduct({"parameter_1": ["a"]}).parameter_study,
                parameter_generators.CartesianProduct({"parameter_2": [True]}).parameter_study,
                parameter_generators.CartesianProduct({"parameter_1": ["b"]}).parameter_study,
                parameter_generators.CartesianProduct({"parameter_2": [False]}).parameter_study,
            ],
            {},
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
            {},
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
            {},
            parameter_generators.CartesianProduct({"parameter_1": [1, 2, 3], "parameter_2": [2.0]}).parameter_study,
            {"parameter_1": numpy.int64, "parameter_2": numpy.float64},
            True,
            does_not_raise,
        ),
    }
)


@pytest.mark.parametrize(
    ("studies", "kwargs", "expected_study", "expected_types", "propagate_space", "outcome"),
    merge_parameter_studies_cases.values(),
    ids=merge_parameter_studies_cases.keys(),
)
def test_merge_parameter_studies(
    studies: list[xarray.Dataset],
    kwargs: dict,
    expected_study: xarray.Dataset,
    expected_types: dict[str, type],
    propagate_space: bool | None,
    outcome: contextlib.nullcontext | pytest.RaisesExc,
) -> None:
    """Check the merged parameter study contents and verify unchanged base study set_name-to-set_hash relationships.

    :param studies: list of N number of parameter study Xarray datasets to merge, where the first study in the list is
        the base study
    :param kwargs: the function keyword arguments
    :param expected_study: Xarray dataset
    :param expected_types: dictionary with parameter names as the keys and numpy types as values
    :param propagate_space: boolean indicating if parameter space propagation is used to construct the output study
    :param outcome: pytest expected error for the test case
    """
    with outcome:
        try:
            merged_study = parameter_generators._merge_parameter_studies(studies, **kwargs)
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


test_convert_numpy_to_builtin_cases = {
    "one parameter numpy typing - float 64": (
        numpy.array(
            [
                [1.0, numpy.float64(10.0)],
                [2.0, numpy.float64(20.0)],
            ],
            dtype=object,
        ),
        numpy.array(
            [
                [1.0, 10.0],
                [2.0, 20.0],
            ],
            dtype=object,
        ),
        1e-15,
        does_not_raise,
    ),
    "all parameters numpy typing - float 64": (
        numpy.array(
            [
                [numpy.float64(1.0), numpy.float64(10.0)],
                [numpy.float64(2.0), numpy.float64(20.0)],
            ],
            dtype=object,
        ),
        numpy.array(
            [
                [1.0, 10.0],
                [2.0, 20.0],
            ],
            dtype=object,
        ),
        1e-15,
        does_not_raise,
    ),
    "one parameter numpy typing - int 64": (
        numpy.array(
            [
                [numpy.int64(1), 10.0],
                [numpy.int64(2), 20.0],
            ],
            dtype=object,
        ),
        numpy.array(
            [
                [1, 10.0],
                [2, 20.0],
            ],
            dtype=object,
        ),
        1e-15,
        does_not_raise,
    ),
    "all parameters numpy typing - int/float 64": (
        numpy.array(
            [
                [numpy.int64(1), numpy.float64(10.0)],
                [numpy.int64(2), numpy.float64(20.0)],
            ],
            dtype=object,
        ),
        numpy.array(
            [
                [1, 10.0],
                [2, 20.0],
            ],
            dtype=object,
        ),
        1e-15,
        does_not_raise,
    ),
    "one parameter numpy typing - boolean": (
        numpy.array(
            [
                [numpy.bool_(True), 10.0],
                [numpy.bool_(False), 20.0],
            ],
            dtype=object,
        ),
        numpy.array(
            [
                [True, 10.0],
                [False, 20.0],
            ],
            dtype=object,
        ),
        1e-15,
        does_not_raise,
    ),
    "one parameter numpy typing - string": (
        numpy.array(
            [
                [numpy.str_("zero"), 10.0],
                [numpy.str_("one"), 20.0],
            ],
            dtype=object,
        ),
        numpy.array(
            [
                ["zero", 10.0],
                ["one", 20.0],
            ],
            dtype=object,
        ),
        1e-15,
        does_not_raise,
    ),
    "one parameter numpy typing - int 32": (
        numpy.array(
            [
                [numpy.int32(1), 10.0],
                [numpy.int32(2), 20.0],
            ],
            dtype=object,
        ),
        numpy.array(
            [
                [1, 10.0],
                [2, 20.0],
            ],
            dtype=object,
        ),
        1e-7,
        does_not_raise,
    ),
    "one parameter numpy typing - int 16": (
        numpy.array(
            [
                [numpy.int16(1), 10.0],
                [numpy.int16(2), 20.0],
            ],
            dtype=object,
        ),
        numpy.array(
            [
                [1, 10.0],
                [2, 20.0],
            ],
            dtype=object,
        ),
        1e-3,
        does_not_raise,
    ),
    "one parameter numpy typing - float 32": (
        numpy.array(
            [
                [1.0, numpy.float32(1.23)],
                [2.0, numpy.float32(4.56)],
            ],
            dtype=object,
        ),
        numpy.array(
            [
                [1.0, 1.23],
                [2.0, 4.56],
            ],
            dtype=object,
        ),
        1e-7,
        does_not_raise,
    ),
    "one parameter numpy typing - float 16": (
        numpy.array(
            [
                [1.0, numpy.float16(1.23)],
                [2.0, numpy.float16(4.56)],
            ],
            dtype=object,
        ),
        numpy.array(
            [
                [1.0, 1.23],
                [2.0, 4.56],
            ],
            dtype=object,
        ),
        1e-3,
        does_not_raise,
    ),
    "all parameters numpy typing - equivalent WAVES types": (
        # Python int bit size is variable, from ~16-64. Floats are always 64.
        numpy.array(
            [
                [
                    numpy.int16(1),
                    numpy.int32(-1),
                    numpy.int64(-10),
                    numpy.float64(1.23),
                    numpy.bool_(True),
                    numpy.str_("zero"),
                ],
                [
                    numpy.int16(2),
                    numpy.int32(-2),
                    numpy.int64(-20),
                    numpy.float64(4.56),
                    numpy.bool_(False),
                    numpy.str_("one"),
                ],
            ],
            dtype=object,
        ),
        numpy.array(
            [
                [1, -1, -10, 1.23, True, "zero"],
                [2, -2, -20, 4.56, False, "one"],
            ],
            dtype=object,
        ),
        1e-15,
        does_not_raise,
    ),
    "1D array - equivalent WAVES types": (
        numpy.array(
            [
                numpy.int16(1),
                numpy.int32(-1),
                numpy.int64(-10),
                numpy.float64(1.23),
                numpy.bool_(True),
                numpy.str_("zero"),
            ],
            dtype=object,
        ),
        numpy.array([1, -1, -10, 1.23, True, "zero"], dtype=object),
        1e-15,
        does_not_raise,
    ),
    "3D array - int 16": (
        numpy.array(
            [
                [[numpy.int16(1), 10.0], [3, 30.0]],
                [[numpy.int16(2), 20.0], [4, 40.0]],
            ],
            dtype=object,
        ),
        numpy.array(
            [
                [[1, 10.0], [3, 30.0]],
                [[2, 20.0], [4, 40.0]],
            ],
            dtype=object,
        ),
        1e-3,
        does_not_raise,
    ),
    "one parameter numpy typing - long double": (
        numpy.array(
            [
                [1.0, numpy.longdouble(1.23)],
                [2.0, numpy.longdouble(4.56)],
            ],
            dtype=object,
        ),
        None,
        None,
        pytest.raises(TypeError, match="could not be converted"),
    ),
    "item method check - float extended": (
        numpy.array(
            [
                [1.0, numpy.float64(1.23456789123456789)],
                [2.0, numpy.float64(4.56789123456789123)],
            ],
            dtype=object,
        ),
        numpy.array(
            [
                [1.0, numpy.float64(1.23456789123456789).item()],
                [2.0, numpy.float64(4.56789123456789123).item()],
            ],
            dtype=object,
        ),
        1e-15,
        does_not_raise,
    ),
    # Not a valid WAVES input, but reliably triggers TypeError from string mismatch
    "string cast mismatch - timedelta": (
        numpy.array(
            [[numpy.timedelta64(1, "D")]],
            dtype=object,
        ),
        None,
        None,
        pytest.raises(TypeError, match="could not be converted"),
    ),
}


@pytest.mark.parametrize(
    ("samples", "expected", "tolerance", "outcome"),
    test_convert_numpy_to_builtin_cases.values(),
    ids=test_convert_numpy_to_builtin_cases.keys(),
)
def test_convert_numpy_to_builtin(
    samples: numpy.ndarray,
    expected: numpy.ndarray,
    tolerance: float,
    outcome: contextlib.nullcontext | pytest.RaisesExc,
) -> None:
    """Check the function of converting NumPy datatypes to Python datatypes.

    :param samples: numpy.ndarray of samples
    :param expected: expected output numpy.ndarray
    :param tolerance: relative tolerance
    :param outcome: pytest outcome
    """
    with outcome:
        converted = parameter_generators._convert_numpy_to_builtin(samples)
        for converted_entry, expected_entry in zip(converted.flat, expected.flat, strict=True):
            assert type(converted_entry) is type(expected_entry)
            if isinstance(expected_entry, (numpy.inexact, float)):
                assert numpy.isclose(converted_entry, expected_entry, rtol=tolerance)
            else:
                assert converted_entry == expected_entry


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

    property_parameter_schema_cases = {"schema": ({"parameter_1": [1]}, {"parameter_1": [1]})}

    @pytest.mark.parametrize(
        ("input_value", "expected_value"),
        property_parameter_schema_cases.values(),
        ids=property_parameter_schema_cases.keys(),
    )
    def test_property_parameter_schema(self, input_value: dict, expected_value: dict) -> None:
        generator = DummyGenerator(input_value)
        assert generator.parameter_schema == expected_value

    property_output_file_template_cases = {
        "no arg": ({}, _utilities._AtSignTemplate(_settings._default_set_name_template)),
        "custom": (
            {"output_file_template": "custom"},
            _utilities._AtSignTemplate(f"custom{_settings._template_placeholder}"),
        ),
    }

    @pytest.mark.parametrize(
        ("kwargs", "expected_value"),
        property_output_file_template_cases.values(),
        ids=property_output_file_template_cases.keys(),
    )
    def test_property_output_file_template(self, kwargs: dict, expected_value: string.Template | None) -> None:
        generator = DummyGenerator({}, **kwargs)
        if generator.output_file_template is not None and expected_value is not None:
            assert generator.output_file_template.template == expected_value.template
        else:
            assert generator.output_file_template == expected_value

    property_output_file_cases = {
        "no arg": ({}, _settings._default_output_file),
        "custom": ({"output_file": "custom.h5"}, pathlib.Path("custom.h5")),
    }

    @pytest.mark.parametrize(
        ("kwargs", "expected_value"),
        property_output_file_cases.values(),
        ids=property_output_file_cases.keys(),
    )
    def test_property_output_file(self, kwargs: dict, expected_value: pathlib.Path | None) -> None:
        generator = DummyGenerator({}, **kwargs)
        assert generator.output_file == expected_value

    property_output_file_type_cases = {
        "no arg": ({}, "h5"),
        "yaml": ({"output_file_type": "yaml"}, "yaml"),
    }

    @pytest.mark.parametrize(
        ("kwargs", "expected_value"),
        property_output_file_type_cases.values(),
        ids=property_output_file_type_cases.keys(),
    )
    def test_property_output_file_type(self, kwargs: dict, expected_value: str) -> None:
        generator = DummyGenerator({}, **kwargs)
        assert generator.output_file_type == expected_value

    property_set_name_template_cases = {
        "no arg": ({}, _utilities._AtSignTemplate(_settings._default_set_name_template)),
        "custom": (
            {"set_name_template": "custom"},
            _utilities._AtSignTemplate(f"custom{_settings._template_placeholder}"),
        ),
    }

    @pytest.mark.parametrize(
        ("kwargs", "expected_value"),
        property_set_name_template_cases.values(),
        ids=property_set_name_template_cases.keys(),
    )
    def test_property_set_name_template(self, kwargs: dict, expected_value: string.Template) -> None:
        generator = DummyGenerator({}, **kwargs)
        assert generator.set_name_template.template == expected_value.template

    property_previous_parameter_study_cases = {
        "no arg": ({}, _settings._default_previous_parameter_study),
        "use previous": ({"previous_parameter_study": "dummy.h5"}, pathlib.Path("dummy.h5")),
    }

    @pytest.mark.parametrize(
        ("kwargs", "expected_value"),
        property_previous_parameter_study_cases.values(),
        ids=property_previous_parameter_study_cases.keys(),
    )
    def test_property_previous_parameter_study(self, kwargs: dict, expected_value: pathlib.Path | None) -> None:
        generator = DummyGenerator({}, **kwargs)
        assert generator.previous_parameter_study == expected_value

    property_require_previous_parameter_study_cases = {
        "no arg": ({}, _settings._default_require_previous_parameter_study),
        "use previous": ({"require_previous_parameter_study": True}, True),
    }

    @pytest.mark.parametrize(
        ("kwargs", "expected_value"),
        property_require_previous_parameter_study_cases.values(),
        ids=property_require_previous_parameter_study_cases.keys(),
    )
    def test_property_require_previous_parameter_study(self, kwargs: dict, expected_value: bool) -> None:
        generator = DummyGenerator({}, **kwargs)
        assert generator.require_previous_parameter_study == expected_value

    property_overwrite_cases = {
        "no arg": ({}, _settings._default_overwrite),
        "overwrite": ({"overwrite": True}, True),
    }

    @pytest.mark.parametrize(
        ("kwargs", "expected_value"),
        property_overwrite_cases.values(),
        ids=property_overwrite_cases.keys(),
    )
    def test_property_overwrite(self, kwargs: dict, expected_value: bool) -> None:
        generator = DummyGenerator({}, **kwargs)
        assert generator.overwrite == expected_value

    property_write_meta_cases = {
        "no arg": ({}, _settings._default_write_meta_flag),
        "write meta": ({"write_meta": True}, True),
    }

    @pytest.mark.parametrize(
        ("kwargs", "expected_value"),
        property_write_meta_cases.values(),
        ids=property_write_meta_cases.keys(),
    )
    def test_property_write_meta(self, kwargs: dict, expected_value: bool) -> None:
        generator = DummyGenerator({}, **kwargs)
        assert generator.write_meta == expected_value

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

    def test_verify_generated_parameter_study(self) -> None:
        dummy_generator = DummyGenerator({})
        with does_not_raise:
            dummy_generator._verify_generated_parameter_study()
        with (
            patch("waves.parameter_generators._verify_parameter_study", side_effect=RuntimeError),
            pytest.raises(RuntimeError, match="Encountered hash inconsistency during parameter study verification"),
        ):
            dummy_generator._verify_generated_parameter_study()

    def test_generate_verification(self) -> None:
        with (
            patch("waves.parameter_generators._verify_parameter_study", return_value=None) as mock_verify,
            does_not_raise,
        ):
            DummyGenerator({})
            mock_verify.assert_called_once()
        with (
            patch("waves.parameter_generators._verify_parameter_study", side_effect=RuntimeError),
            pytest.raises(RuntimeError, match="Encountered hash inconsistency during parameter study verification"),
        ):
            DummyGenerator({})

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

    def test_merge_parameter_studies_with_missing_previous_parameter_study(self) -> None:
        # Test exception on missing previous parameter study attribute
        dummy_generator = DummyGenerator({})
        dummy_generator._previous_parameter_study = None
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

    test_set_names_cases: dict[str, tuple] = {
        "no template": ({}, ["parameter_set0"]),
        "file template": ({"output_file_template": "out"}, ["out0"]),
        "set template": ({"set_name_template": "out@number"}, ["out0"]),
        "set template, no placeholder": ({"set_name_template": "out"}, ["out0"]),
        "set template, overridden": ({"output_file_template": "out", "set_name_template": "overridden"}, ["out0"]),
    }

    @pytest.mark.parametrize(
        ("kwargs", "expected"),
        test_set_names_cases.values(),
        ids=test_set_names_cases.keys(),
    )
    def test_set_names(self, kwargs: dict, expected: list[str]) -> None:
        """Check the generated parameter set names against template arguments.

        :param kwargs: the output_name_template and set_name_template keyword arguments
        :param list expected: list of expected parameter name strings
        """
        template_generator = DummyGenerator({}, **kwargs, sets=1)
        assert list(template_generator._set_names.values()) == expected
        assert list(template_generator.parameter_study[_settings._set_coordinate_key].values) == expected

    @pytest.mark.parametrize(
        ("kwargs", "expected"),
        test_set_names_cases.values(),
        ids=test_set_names_cases.keys(),
    )
    def test_merge_parameter_studies(self, kwargs: dict, expected: list[str]) -> None:
        """Check the generated parameter set names against template arguments after a merge operation.

        :param kwargs: the output_name_template and set_name_template keyword arguments
        :param list expected: list of expected parameter name strings
        """
        mock_previous_study_name = "dummy_study.h5"
        mock_previous_study = DummyGenerator({}, **kwargs, sets=1).parameter_study
        template_generator = DummyGenerator({}, **kwargs, previous_parameter_study=mock_previous_study_name, sets=1)
        with patch("waves.parameter_generators._open_parameter_study", return_value=mock_previous_study):
            assert list(template_generator._set_names.values()) == expected
            assert list(template_generator.parameter_study[_settings._set_coordinate_key].values) == expected
            template_generator._merge_parameter_studies()
            assert list(template_generator._set_names.values()) == expected
            assert list(template_generator.parameter_study[_settings._set_coordinate_key].values) == expected

    # Deprecate the ParameterGenerator write_meta API and method
    # https://re-git.lanl.gov/aea/python-projects/waves/-/work_items/1024
    def test_write_call_to_write_meta(self) -> None:
        write_parameter_generator = DummyGenerator({})
        write_parameter_generator._write_meta_flag = True
        with (
            patch("waves.parameter_generators.ParameterGenerator._write_meta") as mock_write_meta,
            patch("waves.parameter_generators._write") as mock_private_write,
        ):
            write_parameter_generator.write()
            mock_write_meta.assert_called_once()
            mock_private_write.assert_called_once()

    # Deprecate the ParameterGenerator write_meta API and method
    # https://re-git.lanl.gov/aea/python-projects/waves/-/work_items/1024
    def test_write_meta(self) -> None:
        write_meta_parameter_generator = DummyGenerator({})
        with (
            patch("pathlib.Path.open", mock_open()) as mock_file,
            patch("pathlib.Path.resolve", return_value=pathlib.Path("parameter_set1.h5")),
        ):
            write_meta_parameter_generator._write_meta()
            handle = mock_file()
            handle.write.assert_called_once_with("parameter_set1.h5\n")

        write_meta_parameter_generator = DummyGenerator({}, output_file="dummy.h5")
        with (
            patch("pathlib.Path.open", mock_open()) as mock_file,
            patch("pathlib.Path.resolve", return_value=pathlib.Path("dummy.h5")),
        ):
            write_meta_parameter_generator._write_meta()
            handle = mock_file()
            handle.write.assert_called_once_with("dummy.h5\n")

    test_original_index_cases = {
        "default": ({}, False, does_not_raise),
        "only original index": ({"original_index": True}, True, does_not_raise),
        "only previous parameter study": ({"previous_parameter_study": "dummy.h5"}, False, does_not_raise),
        "both original index and previous parameter study": (
            {"previous_parameter_study": "dummy.h5", "original_index": True},
            None,
            pytest.raises(
                MutuallyExclusiveError,
                match=r"The original index and previous parameter study features are mutually incompatible\.",
            ),
        ),
    }

    @pytest.mark.parametrize(
        ("generator_kwargs", "expected", "outcome"),
        test_original_index_cases.values(),
        ids=test_original_index_cases.keys(),
    )
    def test_original_index(
        self, generator_kwargs: dict, expected: bool, outcome: contextlib.nullcontext | pytest.RaisesExc
    ) -> None:
        with (
            outcome,
            patch("pathlib.Path.is_file", return_value=True),
            patch("waves.parameter_generators.ParameterGenerator._validate"),
            patch("waves.parameter_generators.ParameterGenerator._generate"),
        ):
            original_index_generator = DummyGenerator({}, **generator_kwargs)
            assert original_index_generator._original_index is expected

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

    def test_create_parameter_study(self) -> None:
        with does_not_raise:
            generator = DummyGenerator({})
            generator._create_parameter_study()
        with does_not_raise:
            generator = DummyGenerator({})
            generator._create_parameter_study(original_index=True)
        with (  # noqa: PT012
            pytest.raises(
                RuntimeError,
                match=r"The original index and previous parameter study features are mutually incompatible\.",
            ),
        ):
            generator = DummyGenerator({})
            generator._previous_parameter_study = pathlib.Path("dummy.h5")
            generator._create_parameter_study(original_index=True)

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
            _sampler_class = "dummy"

            def _validate(self) -> None:
                pass

            def _generate(self, **kwargs) -> None:
                pass

        with pytest.raises(
            ValueError, match="_ScipyGenerator subclasses must set ``_sampler_class`` to a non-empty string"
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
    _sampler_class = "dummy"

    def _generate(self, **kwargs) -> None:
        pass


test__return_parameter_study_files_cases = {
    "MutuallyExclusiveError": (
        parameter_generators.CartesianProduct({"parameter_1": [1, 2]}),
        {"output_file": "output.h5", "output_directory": "directory"},
        None,
        pytest.raises(
            MutuallyExclusiveError,
            match=(
                r"The options 'output_directory' and 'output_file' are mutually exclusive."
                r" Please specify one or the other."
            ),
        ),
    ),
    "no kwargs, APIError must have one of output directory/file": (
        parameter_generators.CartesianProduct({"parameter_1": [1, 2]}),
        {},
        None,
        pytest.raises(APIError, match=r"One of 'output_directory' or 'output_file' must be specified."),
    ),
    "APIError must have one of output directory/file": (
        parameter_generators.CartesianProduct({"parameter_1": [1, 2]}),
        {"output_file": None, "output_directory": None},
        None,
        pytest.raises(APIError, match=r"One of 'output_directory' or 'output_file' must be specified."),
    ),
    "unsupported output file type": (
        parameter_generators.CartesianProduct({"parameter_1": [1, 2]}),
        {"output_file": "output.h5", "output_file_type": "notsupported"},
        None,
        pytest.raises(
            ChoicesError,
            match=(
                r"Unsupported 'output_file_type': 'notsupported'."
                r" The 'output_file_type' must be one of \('h5', 'yaml'\)."
            ),
        ),
    ),
    "CartesianProduct, output file, default output file type": (
        parameter_generators.CartesianProduct({"parameter_1": [1, 2]}),
        {"output_file": "output.h5"},
        {
            "output.h5": xarray.Dataset(
                {
                    "parameter_1": xarray.DataArray(
                        [2, 1],
                        coords={"set_name": xarray.DataArray(["parameter_set0", "parameter_set1"], dims=["set_name"])},
                    ),
                    "set_hash": xarray.DataArray(
                        ["0b588b6a82c1d3d3d19fda304f940342", "1661dcd0bf4761d25471c1cf5514ceae"],
                        dims="set_name",
                    ),
                },
            ).set_coords("set_hash"),
        },
        does_not_raise,
    ),
    "CartesianProduct, output file, H5": (
        parameter_generators.CartesianProduct({"parameter_1": [1, 2]}),
        {"output_file": "output.h5", "output_file_type": "h5"},
        {
            "output.h5": xarray.Dataset(
                {
                    "parameter_1": xarray.DataArray(
                        [2, 1],
                        coords={"set_name": xarray.DataArray(["parameter_set0", "parameter_set1"], dims=["set_name"])},
                    ),
                    "set_hash": xarray.DataArray(
                        ["0b588b6a82c1d3d3d19fda304f940342", "1661dcd0bf4761d25471c1cf5514ceae"],
                        dims="set_name",
                    ),
                },
            ).set_coords("set_hash"),
        },
        does_not_raise,
    ),
    "CartesianProduct, output file, YAML": (
        parameter_generators.CartesianProduct({"parameter_1": [1, 2]}),
        {"output_file": "output.h5", "output_file_type": "yaml"},
        {"output.h5": {"parameter_set0": {"parameter_1": 2}, "parameter_set1": {"parameter_1": 1}}},
        does_not_raise,
    ),
    "CartesianProduct, output directory, default output file type": (
        parameter_generators.CartesianProduct({"parameter_1": [1, 2]}),
        {"output_directory": pathlib.Path("directory")},
        {
            pathlib.Path("directory") / "parameter_set0.h5": xarray.Dataset(
                {
                    "parameter_1": xarray.DataArray(
                        [2],
                        coords={"set_name": xarray.DataArray(["parameter_set0"], dims=["set_name"])},
                    ),
                    "set_hash": xarray.DataArray(["0b588b6a82c1d3d3d19fda304f940342"], dims="set_name"),
                },
            ).set_coords("set_hash"),
            pathlib.Path("directory") / "parameter_set1.h5": xarray.Dataset(
                {
                    "parameter_1": xarray.DataArray(
                        [1],
                        coords={"set_name": xarray.DataArray(["parameter_set1"], dims=["set_name"])},
                    ),
                    "set_hash": xarray.DataArray(["1661dcd0bf4761d25471c1cf5514ceae"], dims="set_name"),
                },
            ).set_coords("set_hash"),
        },
        does_not_raise,
    ),
    "CartesianProduct, output directory, H5": (
        parameter_generators.CartesianProduct({"parameter_1": [1, 2]}),
        {"output_directory": pathlib.Path("directory"), "output_file_type": "h5"},
        {
            pathlib.Path("directory") / "parameter_set0.h5": xarray.Dataset(
                {
                    "parameter_1": xarray.DataArray(
                        [2],
                        coords={"set_name": xarray.DataArray(["parameter_set0"], dims=["set_name"])},
                    ),
                    "set_hash": xarray.DataArray(["0b588b6a82c1d3d3d19fda304f940342"], dims="set_name"),
                },
            ).set_coords("set_hash"),
            pathlib.Path("directory") / "parameter_set1.h5": xarray.Dataset(
                {
                    "parameter_1": xarray.DataArray(
                        [1],
                        coords={"set_name": xarray.DataArray(["parameter_set1"], dims=["set_name"])},
                    ),
                    "set_hash": xarray.DataArray(["1661dcd0bf4761d25471c1cf5514ceae"], dims="set_name"),
                },
            ).set_coords("set_hash"),
        },
        does_not_raise,
    ),
    "CartesianProduct, output directory, YAML": (
        parameter_generators.CartesianProduct({"parameter_1": [1, 2]}),
        {"output_directory": pathlib.Path("directory"), "output_file_type": "yaml"},
        {
            pathlib.Path("directory") / "parameter_set0.yaml": {"parameter_1": 2},
            pathlib.Path("directory") / "parameter_set1.yaml": {"parameter_1": 1},
        },
        does_not_raise,
    ),
    "CartesianProduct, output file, YAML, set name template": (
        parameter_generators.CartesianProduct({"parameter_1": [1, 2]}, set_name_template="set@number"),
        {"output_directory": pathlib.Path("directory"), "output_file_type": "yaml"},
        {
            pathlib.Path("directory") / "set0.yaml": {"parameter_1": 2},
            pathlib.Path("directory") / "set1.yaml": {"parameter_1": 1},
        },
        does_not_raise,
    ),
    "CartesianProduct, output file, YAML, path-like set name template": (
        parameter_generators.CartesianProduct({"parameter_1": [1, 2]}, set_name_template="set@number/study"),
        {"output_directory": pathlib.Path("directory"), "output_file_type": "yaml"},
        {
            pathlib.Path("directory/set0/study.yaml"): {"parameter_1": 2},
            pathlib.Path("directory/set1/study.yaml"): {"parameter_1": 1},
        },
        does_not_raise,
    ),
}


@pytest.mark.parametrize(
    ("generator", "kwargs", "expected", "outcome"),
    test__return_parameter_study_files_cases.values(),
    ids=test__return_parameter_study_files_cases.keys(),
)
def test__return_parameter_study_files(
    generator: parameter_generators.ParameterGenerator,
    kwargs: dict,
    expected: dict[pathlib.Path, dict | xarray.Dataset],
    outcome: contextlib.nullcontext | pytest.RaisesExc,
) -> None:
    with outcome:
        parameter_study_files = parameter_generators._return_parameter_study_files(generator, **kwargs)
        assert expected.keys() == parameter_study_files.keys()
        for key, expected_value in expected.items():
            if isinstance(expected_value, xarray.Dataset):
                xarray.testing.assert_identical(expected_value, parameter_study_files[key])
            else:
                assert expected_value == parameter_study_files[key]


test__return_parameter_study_files_to_write_cases = {
    "ValueError not dictionary or xarray": (
        {pathlib.Path("output.h5"): ["parameter_1"]},
        [False],
        None,
        None,
        None,
        pytest.raises(
            ValueError,
            match=(
                r"Parameter study file content must be a dictionary or xarray Dataset."
                r" This is likely an internal bug. Please contact the developers."
            ),
        ),
    ),
    "no preexisting files, single file, dataset": (
        {
            pathlib.Path("output.h5"): xarray.Dataset(
                {"parameter_1": xarray.DataArray([1, 2], coords={"set_name": ["set0", "set1"]})}
            ),
        },
        [False],
        None,
        None,
        {
            pathlib.Path("output.h5"): xarray.Dataset(
                {"parameter_1": xarray.DataArray([1, 2], coords={"set_name": ["set0", "set1"]})}
            ),
        },
        does_not_raise,
    ),
    "preexisting files, single file, dataset, same content": (
        {
            pathlib.Path("output.h5"): xarray.Dataset(
                {"parameter_1": xarray.DataArray([1, 2], coords={"set_name": ["set0", "set1"]})}
            ),
        },
        [True],
        [
            xarray.Dataset({"parameter_1": xarray.DataArray([1, 2], coords={"set_name": ["set0", "set1"]})}),
        ],
        None,
        {},
        does_not_raise,
    ),
    "no preexisting files, two files, datasets": (
        {
            pathlib.Path("set0.h5"): xarray.Dataset(
                {"parameter_1": xarray.DataArray([1], coords={"set_name": ["set0"]})}
            ),
            pathlib.Path("set1.h5"): xarray.Dataset(
                {"parameter_1": xarray.DataArray([2], coords={"set_name": ["set1"]})}
            ),
        },
        [False, False],
        None,
        None,
        {
            pathlib.Path("set0.h5"): xarray.Dataset(
                {"parameter_1": xarray.DataArray([1], coords={"set_name": ["set0"]})}
            ),
            pathlib.Path("set1.h5"): xarray.Dataset(
                {"parameter_1": xarray.DataArray([2], coords={"set_name": ["set1"]})}
            ),
        },
        does_not_raise,
    ),
    "preexisting files, two files, datasets, same content": (
        {
            pathlib.Path("set0.h5"): xarray.Dataset(
                {"parameter_1": xarray.DataArray([1], coords={"set_name": ["set0"]})}
            ),
            pathlib.Path("set1.h5"): xarray.Dataset(
                {"parameter_1": xarray.DataArray([2], coords={"set_name": ["set1"]})}
            ),
        },
        [True, True],
        [
            xarray.Dataset({"parameter_1": xarray.DataArray([1], coords={"set_name": ["set0"]})}),
            xarray.Dataset({"parameter_1": xarray.DataArray([2], coords={"set_name": ["set1"]})}),
        ],
        None,
        {},
        does_not_raise,
    ),
    "preexisting files, two files, datasets, first content differs": (
        {
            pathlib.Path("set0.h5"): xarray.Dataset(
                {"parameter_1": xarray.DataArray([1], coords={"set_name": ["set0"]})}
            ),
            pathlib.Path("set1.h5"): xarray.Dataset(
                {"parameter_1": xarray.DataArray([2], coords={"set_name": ["set1"]})}
            ),
        },
        [True, True],
        [
            xarray.Dataset({"parameter_1": xarray.DataArray([1.1], coords={"set_name": ["set0"]})}),
            xarray.Dataset({"parameter_1": xarray.DataArray([2], coords={"set_name": ["set1"]})}),
        ],
        None,
        {
            pathlib.Path("set0.h5"): xarray.Dataset(
                {"parameter_1": xarray.DataArray([1], coords={"set_name": ["set0"]})}
            ),
        },
        does_not_raise,
    ),
    "preexisting files, two files, datasets, second content differs": (
        {
            pathlib.Path("set0.h5"): xarray.Dataset(
                {"parameter_1": xarray.DataArray([1], coords={"set_name": ["set0"]})}
            ),
            pathlib.Path("set1.h5"): xarray.Dataset(
                {"parameter_1": xarray.DataArray([2], coords={"set_name": ["set1"]})}
            ),
        },
        [True, True],
        [
            xarray.Dataset({"parameter_1": xarray.DataArray([1], coords={"set_name": ["set0"]})}),
            xarray.Dataset({"parameter_1": xarray.DataArray([2.2], coords={"set_name": ["set1"]})}),
        ],
        None,
        {
            pathlib.Path("set1.h5"): xarray.Dataset(
                {"parameter_1": xarray.DataArray([2], coords={"set_name": ["set1"]})}
            ),
        },
        does_not_raise,
    ),
    "no preexisting files, single file, dict": (
        {pathlib.Path("output.yaml"): {"parameter_set0": {"parameter_1": 1}, "parameter_set1": {"parameter_1": 2}}},
        [False],
        None,
        None,
        {
            pathlib.Path("output.yaml"): {"parameter_set0": {"parameter_1": 1}, "parameter_set1": {"parameter_1": 2}},
        },
        does_not_raise,
    ),
    "preexisting files, single file, dict, same content": (
        {pathlib.Path("output.yaml"): {"parameter_set0": {"parameter_1": 1}, "parameter_set1": {"parameter_1": 2}}},
        [True],
        None,
        [{"parameter_set0": {"parameter_1": 1}, "parameter_set1": {"parameter_1": 2}}],
        {},
        does_not_raise,
    ),
    "no preexisting files, two files, dict": (
        {
            pathlib.Path("set0.yaml"): {"parameter_1": 1},
            pathlib.Path("set1.yaml"): {"parameter_1": 2},
        },
        [False, False],
        None,
        None,
        {
            pathlib.Path("set0.yaml"): {"parameter_1": 1},
            pathlib.Path("set1.yaml"): {"parameter_1": 2},
        },
        does_not_raise,
    ),
    "preexisting files, two files, dict, same content": (
        {
            pathlib.Path("set0.yaml"): {"parameter_1": 1},
            pathlib.Path("set1.yaml"): {"parameter_1": 2},
        },
        [True, True],
        None,
        [
            {"parameter_1": 1},
            {"parameter_1": 2},
        ],
        {},
        does_not_raise,
    ),
    "preexisting files, two files, dict, first content differs": (
        {
            pathlib.Path("set0.yaml"): {"parameter_1": 1},
            pathlib.Path("set1.yaml"): {"parameter_1": 2},
        },
        [True, True],
        None,
        [
            {"parameter_1": 1.1},
            {"parameter_1": 2},
        ],
        {
            pathlib.Path("set0.yaml"): {"parameter_1": 1},
        },
        does_not_raise,
    ),
    "preexisting files, two files, dict, second content differs": (
        {
            pathlib.Path("set0.yaml"): {"parameter_1": 1},
            pathlib.Path("set1.yaml"): {"parameter_1": 2},
        },
        [True, True],
        None,
        [
            {"parameter_1": 1},
            {"parameter_1": 2.2},
        ],
        {
            pathlib.Path("set1.yaml"): {"parameter_1": 2},
        },
        does_not_raise,
    ),
}


@pytest.mark.parametrize(
    (
        "parameter_study_files",
        "is_file_side_effects",
        "open_dataset_side_effects",
        "safe_load_side_effects",
        "expected",
        "outcome",
    ),
    test__return_parameter_study_files_to_write_cases.values(),
    ids=test__return_parameter_study_files_to_write_cases.keys(),
)
def test__return_parameter_study_files_to_write(
    parameter_study_files: dict[pathlib.Path, dict | xarray.Dataset],
    is_file_side_effects: list[bool],
    open_dataset_side_effects: list[xarray.Dataset] | None,
    safe_load_side_effects: list[dict] | None,
    expected: dict[pathlib.Path, dict | xarray.Dataset],
    outcome: contextlib.nullcontext | pytest.RaisesExc,
) -> None:
    with (
        outcome,
        patch("pathlib.Path.is_file", side_effect=is_file_side_effects),
        patch("xarray.open_dataset", side_effect=open_dataset_side_effects),
        patch("pathlib.Path.open", mock_open()),
        patch("yaml.safe_load", side_effect=safe_load_side_effects),
    ):
        result = parameter_generators._return_parameter_study_files_to_write(parameter_study_files)
        assert result.keys() == expected.keys()
        for key, expected_value in expected.items():
            if isinstance(expected_value, xarray.Dataset):
                xarray.testing.assert_identical(expected_value, result[key])
            else:
                assert expected_value == result[key]


test__write_parameter_study_files_cases = {
    "ValueError not dictionary or xarray": (
        {pathlib.Path("output.h5"): ["parameter_1"]},
        {},
        None,
        None,
        None,
        pytest.raises(
            ValueError,
            match=(
                r"Parameter study file content must be a dictionary or xarray Dataset."
                r" This is likely an internal bug. Please contact the developers."
            ),
        ),
    ),
    "output file, dataset": (
        {
            pathlib.Path("output.h5"): xarray.Dataset(
                {"parameter_1": xarray.DataArray([1, 2], coords={"set_name": ["set0", "set1"]})}
            ),
        },
        {},
        None,
        [
            xarray.Dataset({"parameter_1": xarray.DataArray([1, 2], coords={"set_name": ["set0", "set1"]})}),
        ],
        None,
        does_not_raise,
    ),
    "output file, dataset, dry run": (
        {
            pathlib.Path("output.h5"): xarray.Dataset(
                {"parameter_1": xarray.DataArray([1, 2], coords={"set_name": ["set0", "set1"]})}
            ),
        },
        {"dry_run": True},
        [
            "output.h5\n"
            + str(xarray.Dataset({"parameter_1": xarray.DataArray([1, 2], coords={"set_name": ["set0", "set1"]})}))
            + "\n",
        ],
        None,
        None,
        does_not_raise,
    ),
    "output files, dataset": (
        {
            pathlib.Path("set0.h5"): xarray.Dataset(
                {"parameter_1": xarray.DataArray([1], coords={"set_name": ["set0"]})}
            ),
            pathlib.Path("set1.h5"): xarray.Dataset(
                {"parameter_1": xarray.DataArray([2], coords={"set_name": ["set1"]})}
            ),
        },
        {},
        None,
        [
            xarray.Dataset({"parameter_1": xarray.DataArray([1], coords={"set_name": ["set0"]})}),
            xarray.Dataset({"parameter_1": xarray.DataArray([2], coords={"set_name": ["set1"]})}),
        ],
        None,
        does_not_raise,
    ),
    "output files, dataset, dry run": (
        {
            pathlib.Path("set0.h5"): xarray.Dataset(
                {"parameter_1": xarray.DataArray([1], coords={"set_name": ["set0"]})}
            ),
            pathlib.Path("set1.h5"): xarray.Dataset(
                {"parameter_1": xarray.DataArray([2], coords={"set_name": ["set1"]})}
            ),
        },
        {"dry_run": True},
        [
            "set0.h5\n"
            + str(xarray.Dataset({"parameter_1": xarray.DataArray([1], coords={"set_name": ["set0"]})}))
            + "\n",
            "set1.h5\n"
            + str(xarray.Dataset({"parameter_1": xarray.DataArray([2], coords={"set_name": ["set1"]})}))
            + "\n",
        ],
        None,
        None,
        does_not_raise,
    ),
    "output file, dict": (
        {pathlib.Path("output.yaml"): {"parameter_set0": {"parameter_1": 2}, "parameter_set1": {"parameter_1": 1}}},
        {},
        None,
        None,
        ["parameter_set0:\n  parameter_1: 2\nparameter_set1:\n  parameter_1: 1\n"],
        does_not_raise,
    ),
    "output file, dict, dry-run": (
        {pathlib.Path("output.yaml"): {"parameter_set0": {"parameter_1": 2}, "parameter_set1": {"parameter_1": 1}}},
        {"dry_run": True},
        ["output.yaml\nparameter_set0:\n  parameter_1: 2\nparameter_set1:\n  parameter_1: 1\n"],
        None,
        None,
        does_not_raise,
    ),
    "output files, dict": (
        {
            pathlib.Path("directory") / "parameter_set0.yaml": {"parameter_1": 2},
            pathlib.Path("directory") / "parameter_set1.yaml": {"parameter_1": 1},
        },
        {},
        None,
        None,
        [
            "parameter_1: 2\n",
            "parameter_1: 1\n",
        ],
        does_not_raise,
    ),
    "output files, dict, dry-run": (
        {
            pathlib.Path("directory") / "parameter_set0.yaml": {"parameter_1": 2},
            pathlib.Path("directory") / "parameter_set1.yaml": {"parameter_1": 1},
        },
        {"dry_run": True},
        [
            f"{pathlib.Path('directory') / 'parameter_set0.yaml'}\nparameter_1: 2\n",
            f"{pathlib.Path('directory') / 'parameter_set1.yaml'}\nparameter_1: 1\n",
        ],
        None,
        None,
        does_not_raise,
    ),
}


@pytest.mark.parametrize(
    ("parameter_study_files", "kwargs", "expected_stdout", "expected_to_netcdf", "expected_write", "outcome"),
    test__write_parameter_study_files_cases.values(),
    ids=test__write_parameter_study_files_cases.keys(),
)
def test__write_parameter_study_files(
    parameter_study_files: dict[pathlib.Path, dict | xarray.Dataset],
    kwargs: dict,
    expected_stdout: list[str] | None,
    expected_to_netcdf: list[xarray.Dataset] | None,
    expected_write: list[str] | None,
    outcome: contextlib.nullcontext | pytest.RaisesExc,
) -> None:
    with (
        outcome,
        patch("sys.stdout.write") as mock_stdout,
        patch("xarray.Dataset.to_netcdf") as mock_to_netcdf,
        patch("pathlib.Path.open", mock_open()) as mock_file,
        patch("pathlib.Path.mkdir"),
    ):
        parameter_generators._write_parameter_study_files(parameter_study_files, **kwargs)
        if expected_stdout is None:
            mock_stdout.assert_not_called()
        else:
            assert mock_stdout.call_count == len(expected_stdout)
            mock_stdout.assert_has_calls([call(item) for item in expected_stdout])
        if expected_to_netcdf is None:
            mock_to_netcdf.assert_not_called()
        else:
            # TODO: figure out how to assert the dataset/output association
            assert mock_to_netcdf.call_count == len(expected_to_netcdf)
        if expected_write is None:
            mock_file().assert_not_called()
        else:
            assert mock_file().write.call_count == len(expected_write)
            mock_file().write.assert_has_calls([call(item) for item in expected_write])


test__write_parameter_study_meta_file_cases = {
    "file does not exist": (
        pathlib.Path("meta_file.txt"),
        "contents of meta file",
        {},
        False,
        None,
        "contents of meta file",
    ),
    "file does not exist, overwrite": (
        pathlib.Path("meta_file.txt"),
        "contents of meta file",
        {"overwrite": True},
        False,
        None,
        "contents of meta file",
    ),
    "file does exist, same contents": (
        pathlib.Path("meta_file.txt"),
        "contents of meta file",
        {},
        True,
        "contents of meta file",
        None,
    ),
    "file does exist, same contents, overwrite": (
        pathlib.Path("meta_file.txt"),
        "contents of meta file",
        {"overwrite": True},
        True,
        "contents of meta file",
        "contents of meta file",
    ),
    "file does exist, different contents": (
        pathlib.Path("meta_file.txt"),
        "contents of meta file",
        {},
        True,
        "different contents of meta file",
        "contents of meta file",
    ),
    "file does exist, different contents, overwrite": (
        pathlib.Path("meta_file.txt"),
        "contents of meta file",
        {"overwrite": True},
        True,
        "different contents of meta file",
        "contents of meta file",
    ),
}


@pytest.mark.parametrize(
    ("meta_file", "meta_file_contents", "kwargs", "mock_is_file", "mock_read", "expected_write"),
    test__write_parameter_study_meta_file_cases.values(),
    ids=test__write_parameter_study_meta_file_cases.keys(),
)
def test__write_parameter_study_meta_file(
    meta_file: pathlib.Path,
    meta_file_contents: str,
    kwargs: dict,
    mock_is_file: bool,
    mock_read: str,
    expected_write: str | None,
) -> None:
    with (
        patch("pathlib.Path.is_file", return_value=mock_is_file),
        patch("pathlib.Path.open", mock_open(read_data=mock_read)) as mock_file,
        patch("pathlib.Path.mkdir"),
    ):
        parameter_generators._write_parameter_study_meta_file(meta_file, meta_file_contents, **kwargs)
        if expected_write is None:
            mock_file().write.assert_not_called()
        else:
            mock_file().write.assert_called_once_with(meta_file_contents)


test__write_cases = {
    "MutuallyExclusiveError": (
        parameter_generators.CartesianProduct({"parameter_1": [1, 2]}),
        {"output_file": "output.h5", "output_directory": "directory"},
        None,
        None,
        None,
        None,
        pytest.raises(
            MutuallyExclusiveError,
            match=(
                r"The options 'output_directory' and 'output_file' are mutually exclusive."
                r" Please specify one or the other."
            ),
        ),
    ),
    "unsupported output file type": (
        parameter_generators.CartesianProduct({"parameter_1": [1, 2]}),
        {"output_file": "output.h5", "output_file_type": "notsupported"},
        None,
        None,
        None,
        None,
        pytest.raises(
            ChoicesError,
            match=(
                r"Unsupported 'output_file_type': 'notsupported'."
                r" The 'output_file_type' must be one of \('h5', 'yaml'\)."
            ),
        ),
    ),
    "meta file without output directory/file": (
        parameter_generators.CartesianProduct({"parameter_1": [1, 2]}),
        {"meta_file": "meta_file.txt"},
        None,
        None,
        None,
        None,
        pytest.raises(
            APIError,
            match=r"The option 'meta_file' requires one of 'output_directory' or 'output_file'.",
        ),
    ),
    "CartesianProduct: STDOUT": (
        parameter_generators.CartesianProduct({"parameter_1": [1, 2]}),
        {},
        ["parameter_set0:\n  parameter_1: 2\nparameter_set1:\n  parameter_1: 1\n"],
        None,
        None,
        None,
        does_not_raise,
    ),
    # Module function ignores class attributes
    "CartesianProduct (class init): output file, default type": (
        parameter_generators.CartesianProduct({"parameter_1": [1, 2]}, output_file=pathlib.Path("output.h5")),
        {},
        ["parameter_set0:\n  parameter_1: 2\nparameter_set1:\n  parameter_1: 1\n"],
        None,
        None,
        None,
        does_not_raise,
    ),
    "CartesianProduct: output file, default type": (
        parameter_generators.CartesianProduct({"parameter_1": [1, 2]}),
        {"output_file": pathlib.Path("output.h5")},
        None,
        [
            xarray.Dataset(
                {
                    "parameter_1": xarray.DataArray(
                        [2, 1],
                        coords={"set_name": xarray.DataArray(["parameter_set0", "parameter_set1"], dims=["set_name"])},
                    ),
                    "set_hash": xarray.DataArray(
                        ["0b588b6a82c1d3d3d19fda304f940342", "1661dcd0bf4761d25471c1cf5514ceae"],
                        dims="set_name",
                    ),
                },
            ).set_coords("set_hash"),
        ],
        None,
        None,
        does_not_raise,
    ),
    # Module function ignores class attributes
    "CartesianProduct (class init): output file, default type, overwrite": (
        parameter_generators.CartesianProduct(
            {"parameter_1": [1, 2]}, output_file=pathlib.Path("output.h5"), overwrite=True
        ),
        {},
        ["parameter_set0:\n  parameter_1: 2\nparameter_set1:\n  parameter_1: 1\n"],
        None,
        None,
        None,
        does_not_raise,
    ),
    "CartesianProduct: output file, default type, overwrite": (
        parameter_generators.CartesianProduct({"parameter_1": [1, 2]}),
        {"output_file": pathlib.Path("output.h5"), "overwrite": True},
        None,
        [
            xarray.Dataset(
                {
                    "parameter_1": xarray.DataArray(
                        [2, 1],
                        coords={"set_name": xarray.DataArray(["parameter_set0", "parameter_set1"], dims=["set_name"])},
                    ),
                    "set_hash": xarray.DataArray(
                        ["0b588b6a82c1d3d3d19fda304f940342", "1661dcd0bf4761d25471c1cf5514ceae"],
                        dims="set_name",
                    ),
                },
            ).set_coords("set_hash"),
        ],
        None,
        None,
        does_not_raise,
    ),
    "CartesianProduct: output file, default type, meta file": (
        parameter_generators.CartesianProduct({"parameter_1": [1, 2]}),
        {"output_file": pathlib.Path("/output.h5"), "meta_file": pathlib.Path("output.txt")},
        None,
        [
            xarray.Dataset(
                {
                    "parameter_1": xarray.DataArray(
                        [2, 1],
                        coords={"set_name": xarray.DataArray(["parameter_set0", "parameter_set1"], dims=["set_name"])},
                    ),
                    "set_hash": xarray.DataArray(
                        ["0b588b6a82c1d3d3d19fda304f940342", "1661dcd0bf4761d25471c1cf5514ceae"],
                        dims="set_name",
                    ),
                },
            ).set_coords("set_hash"),
        ],
        None,
        f"{pathlib.Path('/output.h5').resolve()}\n",
        does_not_raise,
    ),
    "CartesianProduct: output file, default type, dry run": (
        parameter_generators.CartesianProduct({"parameter_1": [1, 2]}),
        {"output_file": pathlib.Path("output.h5"), "dry_run": True},
        [
            "output.h5\n"
            + str(
                xarray.Dataset(
                    {
                        "parameter_1": xarray.DataArray(
                            [2, 1],
                            coords={
                                "set_name": xarray.DataArray(["parameter_set0", "parameter_set1"], dims=["set_name"])
                            },
                        ),
                        "set_hash": xarray.DataArray(
                            ["0b588b6a82c1d3d3d19fda304f940342", "1661dcd0bf4761d25471c1cf5514ceae"],
                            dims="set_name",
                        ),
                    },
                ).set_coords("set_hash")
            )
            + "\n",
        ],
        None,
        None,
        None,
        does_not_raise,
    ),
    "CartesianProduct: output file, default type, dry run, overwrite": (
        parameter_generators.CartesianProduct({"parameter_1": [1, 2]}),
        {"output_file": pathlib.Path("output.h5"), "dry_run": True, "overwrite": True},
        [
            "output.h5\n"
            + str(
                xarray.Dataset(
                    {
                        "parameter_1": xarray.DataArray(
                            [2, 1],
                            coords={
                                "set_name": xarray.DataArray(["parameter_set0", "parameter_set1"], dims=["set_name"])
                            },
                        ),
                        "set_hash": xarray.DataArray(
                            ["0b588b6a82c1d3d3d19fda304f940342", "1661dcd0bf4761d25471c1cf5514ceae"],
                            dims="set_name",
                        ),
                    },
                ).set_coords("set_hash")
            )
            + "\n",
        ],
        None,
        None,
        None,
        does_not_raise,
    ),
    "CartesianProduct: output directory, default type": (
        parameter_generators.CartesianProduct({"parameter_1": [1, 2]}),
        {"output_directory": pathlib.Path("directory")},
        None,
        [
            xarray.Dataset(
                {
                    "parameter_1": xarray.DataArray(
                        [2],
                        coords={
                            "set_name": xarray.DataArray(["parameter_set0"], dims=["set_name"]),
                        },
                    ),
                    "set_hash": xarray.DataArray(["0b588b6a82c1d3d3d19fda304f940342"], dims="set_name"),
                },
            ).set_coords("set_hash"),
            xarray.Dataset(
                {
                    "parameter_1": xarray.DataArray(
                        [1],
                        coords={
                            "set_name": xarray.DataArray(["parameter_set1"], dims=["set_name"]),
                        },
                    ),
                    "set_hash": xarray.DataArray(["1661dcd0bf4761d25471c1cf5514ceae"], dims="set_name"),
                },
            ).set_coords("set_hash"),
        ],
        None,
        None,
        does_not_raise,
    ),
    "CartesianProduct: output directory, default type, dry run": (
        parameter_generators.CartesianProduct({"parameter_1": [1, 2]}),
        {"output_directory": pathlib.Path("directory"), "dry_run": True},
        [
            f"{pathlib.Path('directory') / 'parameter_set0.h5'}\n"
            + str(
                xarray.Dataset(
                    {
                        "parameter_1": xarray.DataArray(
                            [2],
                            coords={
                                "set_name": xarray.DataArray(["parameter_set0"], dims=["set_name"]),
                            },
                        ),
                        "set_hash": xarray.DataArray(["0b588b6a82c1d3d3d19fda304f940342"], dims="set_name"),
                    },
                ).set_coords("set_hash")
            )
            + "\n",
            f"{pathlib.Path('directory') / 'parameter_set1.h5'}\n"
            + str(
                xarray.Dataset(
                    {
                        "parameter_1": xarray.DataArray(
                            [1],
                            coords={
                                "set_name": xarray.DataArray(["parameter_set1"], dims=["set_name"]),
                            },
                        ),
                        "set_hash": xarray.DataArray(["1661dcd0bf4761d25471c1cf5514ceae"], dims="set_name"),
                    },
                ).set_coords("set_hash")
            )
            + "\n",
        ],
        None,
        None,
        None,
        does_not_raise,
    ),
    "CartesianProduct: output directory, default type, meta file": (
        parameter_generators.CartesianProduct({"parameter_1": [1, 2]}),
        {"output_directory": pathlib.Path("/directory"), "meta_file": pathlib.Path("directory/output.txt")},
        None,
        [
            xarray.Dataset(
                {
                    "parameter_1": xarray.DataArray(
                        [2],
                        coords={
                            "set_name": xarray.DataArray(["parameter_set0"], dims=["set_name"]),
                        },
                    ),
                    "set_hash": xarray.DataArray(["0b588b6a82c1d3d3d19fda304f940342"], dims="set_name"),
                },
            ).set_coords("set_hash"),
            xarray.Dataset(
                {
                    "parameter_1": xarray.DataArray(
                        [1],
                        coords={
                            "set_name": xarray.DataArray(["parameter_set1"], dims=["set_name"]),
                        },
                    ),
                    "set_hash": xarray.DataArray(["1661dcd0bf4761d25471c1cf5514ceae"], dims="set_name"),
                },
            ).set_coords("set_hash"),
        ],
        None,
        f"{pathlib.Path('/directory/parameter_set0.h5').resolve()}\n{pathlib.Path('/directory/parameter_set1.h5').resolve()}\n",
        does_not_raise,
    ),
    # Module function ignores class attributes
    "CartesianProduct (class init): output file, H5": (
        parameter_generators.CartesianProduct(
            {"parameter_1": [1, 2]}, output_file=pathlib.Path("output.h5"), output_file_type="h5"
        ),
        {},
        ["parameter_set0:\n  parameter_1: 2\nparameter_set1:\n  parameter_1: 1\n"],
        None,
        None,
        None,
        does_not_raise,
    ),
    "CartesianProduct: output file, H5": (
        parameter_generators.CartesianProduct({"parameter_1": [1, 2]}),
        {"output_file": pathlib.Path("output.h5"), "output_file_type": "h5"},
        None,
        [
            xarray.Dataset(
                {
                    "parameter_1": xarray.DataArray(
                        [2, 1],
                        coords={
                            "set_name": xarray.DataArray(
                                ["parameter_set0", "parameter_set1"],
                                dims=["set_name"],
                            )
                        },
                    ),
                    "set_hash": xarray.DataArray(
                        ["0b588b6a82c1d3d3d19fda304f940342", "1661dcd0bf4761d25471c1cf5514ceae"],
                        dims="set_name",
                    ),
                },
            ).set_coords("set_hash"),
        ],
        None,
        None,
        does_not_raise,
    ),
    "CartesianProduct: output file, H5, dry run": (
        parameter_generators.CartesianProduct({"parameter_1": [1, 2]}),
        {"output_file": pathlib.Path("output.h5"), "output_file_type": "h5", "dry_run": True},
        [
            "output.h5\n"
            + str(
                xarray.Dataset(
                    {
                        "parameter_1": xarray.DataArray(
                            [2, 1],
                            coords={
                                "set_name": xarray.DataArray(["parameter_set0", "parameter_set1"], dims=["set_name"])
                            },
                        ),
                        "set_hash": xarray.DataArray(
                            ["0b588b6a82c1d3d3d19fda304f940342", "1661dcd0bf4761d25471c1cf5514ceae"],
                            dims="set_name",
                        ),
                    },
                ).set_coords("set_hash")
            )
            + "\n",
        ],
        None,
        None,
        None,
        does_not_raise,
    ),
    "CartesianProduct: output directory, H5": (
        parameter_generators.CartesianProduct({"parameter_1": [1, 2]}),
        {"output_directory": pathlib.Path("directory"), "output_file_type": "h5"},
        None,
        [
            xarray.Dataset(
                {
                    "parameter_1": xarray.DataArray(
                        [2],
                        coords={
                            "set_name": xarray.DataArray(["parameter_set0"], dims=["set_name"]),
                        },
                    ),
                    "set_hash": xarray.DataArray(["0b588b6a82c1d3d3d19fda304f940342"], dims="set_name"),
                },
            ).set_coords("set_hash"),
            xarray.Dataset(
                {
                    "parameter_1": xarray.DataArray(
                        [1],
                        coords={
                            "set_name": xarray.DataArray(["parameter_set1"], dims=["set_name"]),
                        },
                    ),
                    "set_hash": xarray.DataArray(["1661dcd0bf4761d25471c1cf5514ceae"], dims="set_name"),
                },
            ).set_coords("set_hash"),
        ],
        None,
        None,
        does_not_raise,
    ),
    "CartesianProduct: output directory, H5, dry run": (
        parameter_generators.CartesianProduct({"parameter_1": [1, 2]}),
        {"output_directory": pathlib.Path("directory"), "output_file_type": "h5", "dry_run": True},
        [
            f"{pathlib.Path('directory') / 'parameter_set0.h5'}\n"
            + str(
                xarray.Dataset(
                    {
                        "parameter_1": xarray.DataArray(
                            [2],
                            coords={
                                "set_name": xarray.DataArray(["parameter_set0"], dims=["set_name"]),
                            },
                        ),
                        "set_hash": xarray.DataArray(["0b588b6a82c1d3d3d19fda304f940342"], dims="set_name"),
                    },
                ).set_coords("set_hash")
            )
            + "\n",
            f"{pathlib.Path('directory') / 'parameter_set1.h5'}\n"
            + str(
                xarray.Dataset(
                    {
                        "parameter_1": xarray.DataArray(
                            [1],
                            coords={
                                "set_name": xarray.DataArray(["parameter_set1"], dims=["set_name"]),
                            },
                        ),
                        "set_hash": xarray.DataArray(["1661dcd0bf4761d25471c1cf5514ceae"], dims="set_name"),
                    },
                ).set_coords("set_hash")
            )
            + "\n",
        ],
        None,
        None,
        None,
        does_not_raise,
    ),
    # Module function ignores class attributes
    "CartesianProduct (class init): output file, YAML": (
        parameter_generators.CartesianProduct(
            {"parameter_1": [1, 2]}, output_file=pathlib.Path("output.yaml"), output_file_type="yaml"
        ),
        {},
        ["parameter_set0:\n  parameter_1: 2\nparameter_set1:\n  parameter_1: 1\n"],
        None,
        None,
        None,
        does_not_raise,
    ),
    "CartesianProduct: output file, YAML": (
        parameter_generators.CartesianProduct({"parameter_1": [1, 2]}),
        {"output_file": pathlib.Path("output.yaml"), "output_file_type": "yaml"},
        None,
        None,
        ["parameter_set0:\n  parameter_1: 2\nparameter_set1:\n  parameter_1: 1\n"],
        None,
        does_not_raise,
    ),
    "CartesianProduct: output file, YAML, dry run": (
        parameter_generators.CartesianProduct({"parameter_1": [1, 2]}),
        {"output_file": pathlib.Path("output.yaml"), "output_file_type": "yaml", "dry_run": True},
        ["output.yaml\nparameter_set0:\n  parameter_1: 2\nparameter_set1:\n  parameter_1: 1\n"],
        None,
        None,
        None,
        does_not_raise,
    ),
    "CartesianProduct: output directory, YAML": (
        parameter_generators.CartesianProduct({"parameter_1": [1, 2]}),
        {"output_directory": pathlib.Path("directory"), "output_file_type": "yaml"},
        None,
        None,
        ["parameter_1: 2\n", "parameter_1: 1\n"],
        None,
        does_not_raise,
    ),
    "CartesianProduct two parameters: output file, YAML, set name template": (
        parameter_generators.CartesianProduct(
            {"parameter_1": [1, 2], "parameter_2": ["a", "b"]}, set_name_template="out"
        ),
        {"output_file": pathlib.Path("output.yaml"), "output_file_type": "yaml"},
        None,
        None,
        [
            "out0:\n  parameter_1: 1\n  parameter_2: a\n"
            "out1:\n  parameter_1: 1\n  parameter_2: b\n"
            "out2:\n  parameter_1: 2\n  parameter_2: b\n"
            "out3:\n  parameter_1: 2\n  parameter_2: a\n"
        ],
        None,
        does_not_raise,
    ),
    "CartesianProduct two parameters: output file, YAML, set name template, dry run": (
        parameter_generators.CartesianProduct(
            {"parameter_1": [1, 2], "parameter_2": ["a", "b"]}, set_name_template="out"
        ),
        {"output_file": pathlib.Path("output.yaml"), "output_file_type": "yaml", "dry_run": True},
        [
            f"{pathlib.Path('output.yaml')}\n"
            "out0:\n  parameter_1: 1\n  parameter_2: a\n"
            "out1:\n  parameter_1: 1\n  parameter_2: b\n"
            "out2:\n  parameter_1: 2\n  parameter_2: b\n"
            "out3:\n  parameter_1: 2\n  parameter_2: a\n"
        ],
        None,
        None,
        None,
        does_not_raise,
    ),
    "CartesianProduct two parameters: output directory, YAML, set name template": (
        parameter_generators.CartesianProduct(
            {"parameter_1": [1, 2], "parameter_2": ["a", "b"]}, set_name_template="out"
        ),
        {"output_directory": pathlib.Path("/directory"), "output_file_type": "yaml"},
        None,
        None,
        [
            "parameter_1: 1\nparameter_2: a\n",
            "parameter_1: 1\nparameter_2: b\n",
            "parameter_1: 2\nparameter_2: b\n",
            "parameter_1: 2\nparameter_2: a\n",
        ],
        None,
        does_not_raise,
    ),
    "CartesianProduct two parameters: output directory, YAML, set name template, dry run": (
        parameter_generators.CartesianProduct(
            {"parameter_1": [1, 2], "parameter_2": ["a", "b"]}, set_name_template="out"
        ),
        {"output_directory": pathlib.Path("/directory"), "output_file_type": "yaml", "dry_run": True},
        [
            f"{pathlib.Path('/directory/out0.yaml')}\nparameter_1: 1\nparameter_2: a\n",
            f"{pathlib.Path('/directory/out1.yaml')}\nparameter_1: 1\nparameter_2: b\n",
            f"{pathlib.Path('/directory/out2.yaml')}\nparameter_1: 2\nparameter_2: b\n",
            f"{pathlib.Path('/directory/out3.yaml')}\nparameter_1: 2\nparameter_2: a\n",
        ],
        None,
        None,
        None,
        does_not_raise,
    ),
    # TODO: VVV Remove uses of output_file_template in favor of set_name_template and ``write(output_directory=)``
    # https://re-git.lanl.gov/aea/python-projects/waves/-/work_items/1023
    "CartesianProduct two parameters: output directory, YAML, output file template, dry run": (
        parameter_generators.CartesianProduct(
            {"parameter_1": [1, 2], "parameter_2": ["a", "b"]}, output_file_template="out"
        ),
        {"output_directory": pathlib.Path("/directory"), "output_file_type": "yaml", "dry_run": True},
        [
            f"{pathlib.Path('/directory/out0.yaml')}\nparameter_1: 1\nparameter_2: a\n",
            f"{pathlib.Path('/directory/out1.yaml')}\nparameter_1: 1\nparameter_2: b\n",
            f"{pathlib.Path('/directory/out2.yaml')}\nparameter_1: 2\nparameter_2: b\n",
            f"{pathlib.Path('/directory/out3.yaml')}\nparameter_1: 2\nparameter_2: a\n",
        ],
        None,
        None,
        None,
        does_not_raise,
    ),
    # https://re-git.lanl.gov/aea/python-projects/waves/-/work_items/1023
    # TODO: ^^^ Remove uses of output_file_template in favor of set_name_template and ``write(output_directory=)``
    "CartesianProduct two parameters floats/ints: output directory, YAML, set name template": (
        parameter_generators.CartesianProduct(
            {"parameter_1": [1, 2], "parameter_2": [3.0, 4.0]}, set_name_template="out"
        ),
        {"output_directory": pathlib.Path("/directory"), "output_file_type": "yaml"},
        None,
        None,
        [
            "parameter_1: 1\nparameter_2: 4.0\n",
            "parameter_1: 1\nparameter_2: 3.0\n",
            "parameter_1: 2\nparameter_2: 4.0\n",
            "parameter_1: 2\nparameter_2: 3.0\n",
        ],
        None,
        does_not_raise,
    ),
    "CartesianProduct two parameters floats/ints: output directory, YAML, set name template, dry run": (
        parameter_generators.CartesianProduct(
            {"parameter_1": [1, 2], "parameter_2": [3.0, 4.0]}, set_name_template="out"
        ),
        {"output_directory": pathlib.Path("/directory"), "output_file_type": "yaml", "dry_run": True},
        [
            f"{pathlib.Path('/directory/out0.yaml')}\nparameter_1: 1\nparameter_2: 4.0\n",
            f"{pathlib.Path('/directory/out1.yaml')}\nparameter_1: 1\nparameter_2: 3.0\n",
            f"{pathlib.Path('/directory/out2.yaml')}\nparameter_1: 2\nparameter_2: 4.0\n",
            f"{pathlib.Path('/directory/out3.yaml')}\nparameter_1: 2\nparameter_2: 3.0\n",
        ],
        None,
        None,
        None,
        does_not_raise,
    ),
    "CartesianProduct two parameters bools/ints: output file, YAML, set name template": (
        parameter_generators.CartesianProduct(
            {"parameter_1": [1, 2], "parameter_2": [True, False]}, set_name_template="out"
        ),
        {"output_file": pathlib.Path("output.yaml"), "output_file_type": "yaml"},
        None,
        None,
        [
            "out0:\n  parameter_1: 2\n  parameter_2: true\n"
            "out1:\n  parameter_1: 1\n  parameter_2: true\n"
            "out2:\n  parameter_1: 2\n  parameter_2: false\n"
            "out3:\n  parameter_1: 1\n  parameter_2: false\n"
        ],
        None,
        does_not_raise,
    ),
    "CartesianProduct two parameters bools/ints: output file, YAML, set name template, dry run": (
        parameter_generators.CartesianProduct(
            {"parameter_1": [1, 2], "parameter_2": [True, False]}, set_name_template="out"
        ),
        {"output_file": pathlib.Path("output.yaml"), "output_file_type": "yaml", "dry_run": True},
        [
            f"{pathlib.Path('output.yaml')}\n"
            "out0:\n  parameter_1: 2\n  parameter_2: true\n"
            "out1:\n  parameter_1: 1\n  parameter_2: true\n"
            "out2:\n  parameter_1: 2\n  parameter_2: false\n"
            "out3:\n  parameter_1: 1\n  parameter_2: false\n"
        ],
        None,
        None,
        None,
        does_not_raise,
    ),
    "CartesianProduct two parameters bools/ints: output directory, YAML, set name template": (
        parameter_generators.CartesianProduct(
            {"parameter_1": [1, 2], "parameter_2": [True, False]}, set_name_template="out"
        ),
        {"output_directory": pathlib.Path("/directory"), "output_file_type": "yaml"},
        None,
        None,
        [
            "parameter_1: 2\nparameter_2: true\n",
            "parameter_1: 1\nparameter_2: true\n",
            "parameter_1: 2\nparameter_2: false\n",
            "parameter_1: 1\nparameter_2: false\n",
        ],
        None,
        does_not_raise,
    ),
    "CartesianProduct two parameters bools/ints: output directory, YAML, set name template, dry run": (
        parameter_generators.CartesianProduct(
            {"parameter_1": [1, 2], "parameter_2": [True, False]}, set_name_template="out"
        ),
        {"output_directory": pathlib.Path("/directory"), "output_file_type": "yaml", "dry_run": True},
        [
            f"{pathlib.Path('/directory/out0.yaml')}\nparameter_1: 2\nparameter_2: true\n",
            f"{pathlib.Path('/directory/out1.yaml')}\nparameter_1: 1\nparameter_2: true\n",
            f"{pathlib.Path('/directory/out2.yaml')}\nparameter_1: 2\nparameter_2: false\n",
            f"{pathlib.Path('/directory/out3.yaml')}\nparameter_1: 1\nparameter_2: false\n",
        ],
        None,
        None,
        None,
        does_not_raise,
    ),
    "CartesianProduct: output directory, YAML, dry run": (
        parameter_generators.CartesianProduct({"parameter_1": [1, 2]}),
        {"output_directory": pathlib.Path("directory"), "output_file_type": "yaml", "dry_run": True},
        [
            f"{pathlib.Path('directory') / 'parameter_set0.yaml'}\nparameter_1: 2\n",
            f"{pathlib.Path('directory') / 'parameter_set1.yaml'}\nparameter_1: 1\n",
        ],
        None,
        None,
        None,
        does_not_raise,
    ),
    "CartesianProduct: output directory, YAML, pathlike set name template": (
        parameter_generators.CartesianProduct({"parameter_1": [1, 2]}, set_name_template="set@number/study"),
        {"output_directory": pathlib.Path("directory"), "output_file_type": "yaml"},
        None,
        None,
        ["parameter_1: 2\n", "parameter_1: 1\n"],
        None,
        does_not_raise,
    ),
    "CartesianProduct: output directory, YAML, dry run, pathlike set name template": (
        parameter_generators.CartesianProduct({"parameter_1": [1, 2]}, set_name_template="set@number/study"),
        {"output_directory": pathlib.Path("directory"), "output_file_type": "yaml", "dry_run": True},
        [
            f"{pathlib.Path('directory') / 'set0/study.yaml'}\nparameter_1: 2\n",
            f"{pathlib.Path('directory') / 'set1/study.yaml'}\nparameter_1: 1\n",
        ],
        None,
        None,
        None,
        does_not_raise,
    ),
    "CartesianProduct: output directory, YAML, meta file, pathlike set name template": (
        parameter_generators.CartesianProduct({"parameter_1": [1, 2]}, set_name_template="set@number/study"),
        {"output_directory": pathlib.Path("/directory"), "output_file_type": "yaml", "meta_file": "meta.txt"},
        None,
        None,
        ["parameter_1: 2\n", "parameter_1: 1\n"],
        (
            f"{pathlib.Path('/directory/set0/study.yaml').resolve()}\n"
            f"{pathlib.Path('/directory/set1/study.yaml').resolve()}\n"
        ),
        does_not_raise,
    ),
    "CustomStudy: output file, YAML": (
        parameter_generators.CustomStudy(
            {"parameter_names": ["a"], "parameter_samples": numpy.array([[1], [2]], dtype=object)},
        ),
        {"output_file": pathlib.Path("output.yaml"), "output_file_type": "yaml"},
        None,
        None,
        ["parameter_set0:\n  a: 2\nparameter_set1:\n  a: 1\n"],
        None,
        does_not_raise,
    ),
    "CustomStudy: output file, YAML, dry run": (
        parameter_generators.CustomStudy(
            {"parameter_names": ["a"], "parameter_samples": numpy.array([[1], [2]], dtype=object)},
        ),
        {"output_file": pathlib.Path("output.yaml"), "output_file_type": "yaml", "dry_run": True},
        [f"{pathlib.Path('output.yaml')}\nparameter_set0:\n  a: 2\nparameter_set1:\n  a: 1\n"],
        None,
        None,
        None,
        does_not_raise,
    ),
    "CustomStudy: output directory, YAML, set name template": (
        parameter_generators.CustomStudy(
            {"parameter_names": ["a"], "parameter_samples": numpy.array([[1], [2]], dtype=object)},
            set_name_template="out",
        ),
        {"output_directory": pathlib.Path("/directory"), "output_file_type": "yaml"},
        None,
        None,
        ["a: 2\n", "a: 1\n"],
        None,
        does_not_raise,
    ),
    "CustomStudy: output directory, YAML, set name template, dry run": (
        parameter_generators.CustomStudy(
            {"parameter_names": ["a"], "parameter_samples": numpy.array([[1], [2]], dtype=object)},
            set_name_template="out",
        ),
        {"output_directory": pathlib.Path("/directory"), "output_file_type": "yaml", "dry_run": True},
        [
            f"{pathlib.Path('/directory/out0.yaml')}\na: 2\n",
            f"{pathlib.Path('/directory/out1.yaml')}\na: 1\n",
        ],
        None,
        None,
        None,
        does_not_raise,
    ),
    "CustomStudy two parameters: output file, YAML, set name template": (
        parameter_generators.CustomStudy(
            {"parameter_names": ["a", "b"], "parameter_samples": numpy.array([[1, 3.0], [2, 4.5]], dtype=object)},
            set_name_template="out",
        ),
        {"output_file": pathlib.Path("output.yaml"), "output_file_type": "yaml"},
        None,
        None,
        [
            "out0:\n  a: 2\n  b: 4.5\nout1:\n  a: 1\n  b: 3.0\n",
        ],
        None,
        does_not_raise,
    ),
    "CustomStudy two parameters: output file, YAML, set name template, dry run": (
        parameter_generators.CustomStudy(
            {"parameter_names": ["a", "b"], "parameter_samples": numpy.array([[1, 3.0], [2, 4.5]], dtype=object)},
            set_name_template="out",
        ),
        {"output_file": pathlib.Path("output.yaml"), "output_file_type": "yaml", "dry_run": True},
        [
            f"{pathlib.Path('output.yaml')}\nout0:\n  a: 2\n  b: 4.5\nout1:\n  a: 1\n  b: 3.0\n",
        ],
        None,
        None,
        None,
        does_not_raise,
    ),
    "CustomStudy two parameters: output directory, YAML, set name template": (
        parameter_generators.CustomStudy(
            {"parameter_names": ["a", "b"], "parameter_samples": numpy.array([[1, 3.0], [2, 4.5]], dtype=object)},
            set_name_template="out",
        ),
        {"output_directory": pathlib.Path("/directory"), "output_file_type": "yaml"},
        None,
        None,
        ["a: 2\nb: 4.5\n", "a: 1\nb: 3.0\n"],
        None,
        does_not_raise,
    ),
    "CustomStudy two parameters: output directory, YAML, set name template, dry run": (
        parameter_generators.CustomStudy(
            {"parameter_names": ["a", "b"], "parameter_samples": numpy.array([[1, 3.0], [2, 4.5]], dtype=object)},
            set_name_template="out",
        ),
        {"output_directory": pathlib.Path("/directory"), "output_file_type": "yaml", "dry_run": True},
        [
            f"{pathlib.Path('/directory/out0.yaml')}\na: 2\nb: 4.5\n",
            f"{pathlib.Path('/directory/out1.yaml')}\na: 1\nb: 3.0\n",
        ],
        None,
        None,
        None,
        does_not_raise,
    ),
    "OneAtATime: output file, YAML, set name template": (
        parameter_generators.OneAtATime({"parameter_1": [1, 2]}, set_name_template="out"),
        {"output_file": pathlib.Path("output.yaml"), "output_file_type": "yaml"},
        None,
        None,
        ["out0:\n  parameter_1: 1\nout1:\n  parameter_1: 2\n"],
        None,
        does_not_raise,
    ),
    "OneAtATime: output file, YAML, set name template, dry run": (
        parameter_generators.OneAtATime({"parameter_1": [1, 2]}, set_name_template="out"),
        {"output_file": pathlib.Path("output.yaml"), "output_file_type": "yaml", "dry_run": True},
        [f"{pathlib.Path('output.yaml')}\nout0:\n  parameter_1: 1\nout1:\n  parameter_1: 2\n"],
        None,
        None,
        None,
        does_not_raise,
    ),
    "OneAtATime: output directory, YAML, set name template": (
        parameter_generators.OneAtATime({"parameter_1": [1, 2]}, set_name_template="out"),
        {"output_directory": pathlib.Path("/directory"), "output_file_type": "yaml"},
        None,
        None,
        [
            "parameter_1: 1\n",
            "parameter_1: 2\n",
        ],
        None,
        does_not_raise,
    ),
    "OneAtATime: output directory, YAML, set name template, dry run": (
        parameter_generators.OneAtATime({"parameter_1": [1, 2]}, set_name_template="out"),
        {"output_directory": pathlib.Path("/directory"), "output_file_type": "yaml", "dry_run": True},
        [
            f"{pathlib.Path('/directory/out0.yaml')}\nparameter_1: 1\n",
            f"{pathlib.Path('/directory/out1.yaml')}\nparameter_1: 2\n",
        ],
        None,
        None,
        None,
        does_not_raise,
    ),
    "OneAtATime two parameters int/str: output file, YAML, set name template": (
        parameter_generators.OneAtATime({"parameter_1": [1, 2], "parameter_2": ["a", "b"]}, set_name_template="out"),
        {"output_file": pathlib.Path("output.yaml"), "output_file_type": "yaml"},
        None,
        None,
        [
            "out0:\n  parameter_1: 1\n  parameter_2: a\n"
            "out1:\n  parameter_1: 1\n  parameter_2: b\n"
            "out2:\n  parameter_1: 2\n  parameter_2: a\n"
        ],
        None,
        does_not_raise,
    ),
    "OneAtATime two parameters int/str: output file, YAML, set name template, dry run": (
        parameter_generators.OneAtATime({"parameter_1": [1, 2], "parameter_2": ["a", "b"]}, set_name_template="out"),
        {"output_file": pathlib.Path("output.yaml"), "output_file_type": "yaml", "dry_run": True},
        [
            f"{pathlib.Path('output.yaml')}\n"
            "out0:\n  parameter_1: 1\n  parameter_2: a\n"
            "out1:\n  parameter_1: 1\n  parameter_2: b\n"
            "out2:\n  parameter_1: 2\n  parameter_2: a\n"
        ],
        None,
        None,
        None,
        does_not_raise,
    ),
    "OneAtATime two parameters int/str: output directory, YAML, set name template": (
        parameter_generators.OneAtATime({"parameter_1": [1, 2], "parameter_2": ["a", "b"]}, set_name_template="out"),
        {"output_directory": pathlib.Path("/directory"), "output_file_type": "yaml"},
        None,
        None,
        [
            "parameter_1: 1\nparameter_2: a\n",
            "parameter_1: 1\nparameter_2: b\n",
            "parameter_1: 2\nparameter_2: a\n",
        ],
        None,
        does_not_raise,
    ),
    "OneAtATime two parameters int/str: output directory, YAML, set name template, dry run": (
        parameter_generators.OneAtATime({"parameter_1": [1, 2], "parameter_2": ["a", "b"]}, set_name_template="out"),
        {"output_directory": pathlib.Path("/directory"), "output_file_type": "yaml", "dry_run": True},
        [
            f"{pathlib.Path('/directory/out0.yaml')}\nparameter_1: 1\nparameter_2: a\n",
            f"{pathlib.Path('/directory/out1.yaml')}\nparameter_1: 1\nparameter_2: b\n",
            f"{pathlib.Path('/directory/out2.yaml')}\nparameter_1: 2\nparameter_2: a\n",
        ],
        None,
        None,
        None,
        does_not_raise,
    ),
    "OneAtATime two parameters int/float: output directory, YAML, set name template": (
        parameter_generators.OneAtATime({"parameter_1": [1, 2], "parameter_2": [3.0, 4.0]}, set_name_template="out"),
        {"output_directory": pathlib.Path("/directory"), "output_file_type": "yaml"},
        None,
        None,
        [
            "parameter_1: 1\nparameter_2: 3.0\n",
            "parameter_1: 1\nparameter_2: 4.0\n",
            "parameter_1: 2\nparameter_2: 3.0\n",
        ],
        None,
        does_not_raise,
    ),
    "OneAtATime two parameters int/float: output directory, YAML, set name template, dry run": (
        parameter_generators.OneAtATime({"parameter_1": [1, 2], "parameter_2": [3.0, 4.0]}, set_name_template="out"),
        {"output_directory": pathlib.Path("/directory"), "output_file_type": "yaml", "dry_run": True},
        [
            f"{pathlib.Path('/directory/out0.yaml')}\nparameter_1: 1\nparameter_2: 3.0\n",
            f"{pathlib.Path('/directory/out1.yaml')}\nparameter_1: 1\nparameter_2: 4.0\n",
            f"{pathlib.Path('/directory/out2.yaml')}\nparameter_1: 2\nparameter_2: 3.0\n",
        ],
        None,
        None,
        None,
        does_not_raise,
    ),
    "OneAtATime two parameters int/bool: output file, YAML, set name template": (
        parameter_generators.OneAtATime({"parameter_1": [1, 2], "parameter_2": [True, False]}, set_name_template="out"),
        {"output_file": pathlib.Path("output.yaml"), "output_file_type": "yaml"},
        None,
        None,
        [
            "out0:\n  parameter_1: 1\n  parameter_2: true\n"
            "out1:\n  parameter_1: 2\n  parameter_2: true\n"
            "out2:\n  parameter_1: 1\n  parameter_2: false\n"
        ],
        None,
        does_not_raise,
    ),
    "OneAtATime two parameters int/bool: output file, YAML, set name template, dry run": (
        parameter_generators.OneAtATime({"parameter_1": [1, 2], "parameter_2": [True, False]}, set_name_template="out"),
        {"output_file": pathlib.Path("output.yaml"), "output_file_type": "yaml", "dry_run": True},
        [
            f"{pathlib.Path('output.yaml')}\n"
            "out0:\n  parameter_1: 1\n  parameter_2: true\n"
            "out1:\n  parameter_1: 2\n  parameter_2: true\n"
            "out2:\n  parameter_1: 1\n  parameter_2: false\n"
        ],
        None,
        None,
        None,
        does_not_raise,
    ),
    "OneAtATime two parameters int/bool: output directory, YAML, set name template": (
        parameter_generators.OneAtATime({"parameter_1": [1, 2], "parameter_2": [True, False]}, set_name_template="out"),
        {"output_directory": pathlib.Path("/directory"), "output_file_type": "yaml"},
        None,
        None,
        [
            "parameter_1: 1\nparameter_2: true\n",
            "parameter_1: 2\nparameter_2: true\n",
            "parameter_1: 1\nparameter_2: false\n",
        ],
        None,
        does_not_raise,
    ),
    "OneAtATime two parameters int/bool: output directory, YAML, set name template, dry run": (
        parameter_generators.OneAtATime({"parameter_1": [1, 2], "parameter_2": [True, False]}, set_name_template="out"),
        {"output_directory": pathlib.Path("/directory"), "output_file_type": "yaml", "dry_run": True},
        [
            f"{pathlib.Path('/directory/out0.yaml')}\nparameter_1: 1\nparameter_2: true\n",
            f"{pathlib.Path('/directory/out1.yaml')}\nparameter_1: 2\nparameter_2: true\n",
            f"{pathlib.Path('/directory/out2.yaml')}\nparameter_1: 1\nparameter_2: false\n",
        ],
        None,
        None,
        None,
        does_not_raise,
    ),
    "CatenationStudy: output file, YAML, set name template": (
        parameter_generators.CatenationStudy(
            {
                "1": parameter_generators.CartesianProduct({"parameter_1": [1]}, set_name_template="out"),
                "2": parameter_generators.CartesianProduct({"parameter_1": [2]}, set_name_template="out"),
            },
            set_name_template="out",
        ),
        {"output_file": pathlib.Path("output.yaml"), "output_file_type": "yaml"},
        None,
        None,
        ["out0:\n  parameter_1: 1\nout1:\n  parameter_1: 2\n"],
        None,
        does_not_raise,
    ),
    "CatenationStudy: output file, YAML, set name template, dry run": (
        parameter_generators.CatenationStudy(
            {
                "1": parameter_generators.CartesianProduct({"parameter_1": [1]}, set_name_template="out"),
                "2": parameter_generators.CartesianProduct({"parameter_1": [2]}, set_name_template="out"),
            },
            set_name_template="out",
        ),
        {"output_file": pathlib.Path("output.yaml"), "output_file_type": "yaml", "dry_run": True},
        [f"{pathlib.Path('output.yaml')}\nout0:\n  parameter_1: 1\nout1:\n  parameter_1: 2\n"],
        None,
        None,
        None,
        does_not_raise,
    ),
    "CatenationStudy: output directory, YAML, set name template": (
        parameter_generators.CatenationStudy(
            {
                "1": parameter_generators.CartesianProduct({"parameter_1": [1]}, set_name_template="out"),
                "2": parameter_generators.CartesianProduct({"parameter_1": [2]}, set_name_template="out"),
            },
            set_name_template="out",
        ),
        {"output_directory": pathlib.Path("/directory"), "output_file_type": "yaml"},
        None,
        None,
        [
            "parameter_1: 1\n",
            "parameter_1: 2\n",
        ],
        None,
        does_not_raise,
    ),
    "CatenationStudy: output directory, YAML, set name template, dry run": (
        parameter_generators.CatenationStudy(
            {
                "1": parameter_generators.CartesianProduct({"parameter_1": [1]}, set_name_template="out"),
                "2": parameter_generators.CartesianProduct({"parameter_1": [2]}, set_name_template="out"),
            },
            set_name_template="out",
        ),
        {"output_directory": pathlib.Path("/directory"), "output_file_type": "yaml", "dry_run": True},
        [
            f"{pathlib.Path('/directory/out0.yaml')}\nparameter_1: 1\n",
            f"{pathlib.Path('/directory/out1.yaml')}\nparameter_1: 2\n",
        ],
        None,
        None,
        None,
        does_not_raise,
    ),
    "CatenationStudy two parameters int/str: output file, YAML, set name template": (
        parameter_generators.CatenationStudy(
            {
                "1": parameter_generators.CartesianProduct({"parameter_1": [1, 2]}, set_name_template="out"),
                "2": parameter_generators.CartesianProduct({"parameter_2": ["a", "b"]}, set_name_template="out"),
            },
            set_name_template="out",
        ),
        {"output_file": pathlib.Path("output.yaml"), "output_file_type": "yaml"},
        None,
        None,
        [
            "out0:\n  parameter_1: 1\n  parameter_2: a\n"
            "out1:\n  parameter_1: 1\n  parameter_2: b\n"
            "out2:\n  parameter_1: 2\n  parameter_2: b\n"
            "out3:\n  parameter_1: 2\n  parameter_2: a\n"
        ],
        None,
        does_not_raise,
    ),
    "CatenationStudy two parameters int/str: output file, YAML, set name template, dry run": (
        parameter_generators.CatenationStudy(
            {
                "1": parameter_generators.CartesianProduct({"parameter_1": [1, 2]}, set_name_template="out"),
                "2": parameter_generators.CartesianProduct({"parameter_2": ["a", "b"]}, set_name_template="out"),
            },
            set_name_template="out",
        ),
        {"output_file": pathlib.Path("output.yaml"), "output_file_type": "yaml", "dry_run": True},
        [
            f"{pathlib.Path('output.yaml')}\n"
            "out0:\n  parameter_1: 1\n  parameter_2: a\n"
            "out1:\n  parameter_1: 1\n  parameter_2: b\n"
            "out2:\n  parameter_1: 2\n  parameter_2: b\n"
            "out3:\n  parameter_1: 2\n  parameter_2: a\n"
        ],
        None,
        None,
        None,
        does_not_raise,
    ),
    "CatenationStudy two parameters int/str: output directory, YAML, set name template": (
        parameter_generators.CatenationStudy(
            {
                "1": parameter_generators.CartesianProduct({"parameter_1": [1, 2]}, set_name_template="out"),
                "2": parameter_generators.CartesianProduct({"parameter_2": ["a", "b"]}, set_name_template="out"),
            },
            set_name_template="out",
        ),
        {"output_directory": pathlib.Path("/directory"), "output_file_type": "yaml"},
        None,
        None,
        [
            "parameter_1: 1\nparameter_2: a\n",
            "parameter_1: 1\nparameter_2: b\n",
            "parameter_1: 2\nparameter_2: b\n",
            "parameter_1: 2\nparameter_2: a\n",
        ],
        None,
        does_not_raise,
    ),
    "CatenationStudy two parameters int/str: output directory, YAML, set name template, dry run": (
        parameter_generators.CatenationStudy(
            {
                "1": parameter_generators.CartesianProduct({"parameter_1": [1, 2]}, set_name_template="out"),
                "2": parameter_generators.CartesianProduct({"parameter_2": ["a", "b"]}, set_name_template="out"),
            },
            set_name_template="out",
        ),
        {"output_directory": pathlib.Path("/directory"), "output_file_type": "yaml", "dry_run": True},
        [
            f"{pathlib.Path('/directory/out0.yaml')}\nparameter_1: 1\nparameter_2: a\n",
            f"{pathlib.Path('/directory/out1.yaml')}\nparameter_1: 1\nparameter_2: b\n",
            f"{pathlib.Path('/directory/out2.yaml')}\nparameter_1: 2\nparameter_2: b\n",
            f"{pathlib.Path('/directory/out3.yaml')}\nparameter_1: 2\nparameter_2: a\n",
        ],
        None,
        None,
        None,
        does_not_raise,
    ),
    "CatenationStudy two parameters int/float: output file, YAML, set name template": (
        parameter_generators.CatenationStudy(
            {
                "1": parameter_generators.CartesianProduct({"parameter_1": [1, 2]}, set_name_template="out"),
                "2": parameter_generators.OneAtATime({"parameter_2": [3.0, 4.0]}, set_name_template="out"),
            },
            set_name_template="out",
        ),
        {"output_file": pathlib.Path("output.yaml"), "output_file_type": "yaml"},
        None,
        None,
        [
            "out0:\n  parameter_1: 1\n  parameter_2: 4.0\n"
            "out1:\n  parameter_1: 1\n  parameter_2: 3.0\n"
            "out2:\n  parameter_1: 2\n  parameter_2: 4.0\n"
            "out3:\n  parameter_1: 2\n  parameter_2: 3.0\n"
        ],
        None,
        does_not_raise,
    ),
    "CatenationStudy two parameters int/float: output file, YAML, set name template, dry run": (
        parameter_generators.CatenationStudy(
            {
                "1": parameter_generators.CartesianProduct({"parameter_1": [1, 2]}, set_name_template="out"),
                "2": parameter_generators.OneAtATime({"parameter_2": [3.0, 4.0]}, set_name_template="out"),
            },
            set_name_template="out",
        ),
        {"output_file": pathlib.Path("output.yaml"), "output_file_type": "yaml", "dry_run": True},
        [
            f"{pathlib.Path('output.yaml')}\n"
            "out0:\n  parameter_1: 1\n  parameter_2: 4.0\n"
            "out1:\n  parameter_1: 1\n  parameter_2: 3.0\n"
            "out2:\n  parameter_1: 2\n  parameter_2: 4.0\n"
            "out3:\n  parameter_1: 2\n  parameter_2: 3.0\n"
        ],
        None,
        None,
        None,
        does_not_raise,
    ),
    "CatenationStudy two parameters int/float: output directory, YAML, set name template": (
        parameter_generators.CatenationStudy(
            {
                "1": parameter_generators.CartesianProduct({"parameter_1": [1, 2]}, set_name_template="out"),
                "2": parameter_generators.OneAtATime({"parameter_2": [3.0, 4.0]}, set_name_template="out"),
            },
            set_name_template="out",
        ),
        {"output_directory": pathlib.Path("/directory"), "output_file_type": "yaml"},
        None,
        None,
        [
            "parameter_1: 1\nparameter_2: 4.0\n",
            "parameter_1: 1\nparameter_2: 3.0\n",
            "parameter_1: 2\nparameter_2: 4.0\n",
            "parameter_1: 2\nparameter_2: 3.0\n",
        ],
        None,
        does_not_raise,
    ),
    "CatenationStudy two parameters int/float: output directory, YAML, set name template, dry run": (
        parameter_generators.CatenationStudy(
            {
                "1": parameter_generators.CartesianProduct({"parameter_1": [1, 2]}, set_name_template="out"),
                "2": parameter_generators.OneAtATime({"parameter_2": [3.0, 4.0]}, set_name_template="out"),
            },
            set_name_template="out",
        ),
        {"output_directory": pathlib.Path("/directory"), "output_file_type": "yaml", "dry_run": True},
        [
            f"{pathlib.Path('/directory/out0.yaml')}\nparameter_1: 1\nparameter_2: 4.0\n",
            f"{pathlib.Path('/directory/out1.yaml')}\nparameter_1: 1\nparameter_2: 3.0\n",
            f"{pathlib.Path('/directory/out2.yaml')}\nparameter_1: 2\nparameter_2: 4.0\n",
            f"{pathlib.Path('/directory/out3.yaml')}\nparameter_1: 2\nparameter_2: 3.0\n",
        ],
        None,
        None,
        None,
        does_not_raise,
    ),
    "CatenationStudy two parameters int/bool: output file, YAML, set name template": (
        parameter_generators.CatenationStudy(
            {
                "1": parameter_generators.CartesianProduct({"parameter_1": [1, 2]}, set_name_template="out"),
                "2": parameter_generators.CartesianProduct({"parameter_2": [True, False]}, set_name_template="out"),
            },
            set_name_template="out",
        ),
        {"output_file": pathlib.Path("output.yaml"), "output_file_type": "yaml"},
        None,
        None,
        [
            "out0:\n  parameter_1: 2\n  parameter_2: true\n"
            "out1:\n  parameter_1: 1\n  parameter_2: true\n"
            "out2:\n  parameter_1: 2\n  parameter_2: false\n"
            "out3:\n  parameter_1: 1\n  parameter_2: false\n"
        ],
        None,
        does_not_raise,
    ),
    "CatenationStudy two parameters int/bool: output file, YAML, set name template, dry run": (
        parameter_generators.CatenationStudy(
            {
                "1": parameter_generators.CartesianProduct({"parameter_1": [1, 2]}, set_name_template="out"),
                "2": parameter_generators.CartesianProduct({"parameter_2": [True, False]}, set_name_template="out"),
            },
            set_name_template="out",
        ),
        {"output_file": pathlib.Path("output.yaml"), "output_file_type": "yaml", "dry_run": True},
        [
            f"{pathlib.Path('output.yaml')}\n"
            "out0:\n  parameter_1: 2\n  parameter_2: true\n"
            "out1:\n  parameter_1: 1\n  parameter_2: true\n"
            "out2:\n  parameter_1: 2\n  parameter_2: false\n"
            "out3:\n  parameter_1: 1\n  parameter_2: false\n"
        ],
        None,
        None,
        None,
        does_not_raise,
    ),
    "CatenationStudy two parameters int/bool: output directory, YAML, set name template": (
        parameter_generators.CatenationStudy(
            {
                "1": parameter_generators.CartesianProduct({"parameter_1": [1, 2]}, set_name_template="out"),
                "2": parameter_generators.CartesianProduct({"parameter_2": [True, False]}, set_name_template="out"),
            },
            set_name_template="out",
        ),
        {"output_directory": pathlib.Path("/directory"), "output_file_type": "yaml"},
        None,
        None,
        [
            "parameter_1: 2\nparameter_2: true\n",
            "parameter_1: 1\nparameter_2: true\n",
            "parameter_1: 2\nparameter_2: false\n",
            "parameter_1: 1\nparameter_2: false\n",
        ],
        None,
        does_not_raise,
    ),
    "CatenationStudy two parameters int/bool: output directory, YAML, set name template, dry run": (
        parameter_generators.CatenationStudy(
            {
                "1": parameter_generators.CartesianProduct({"parameter_1": [1, 2]}, set_name_template="out"),
                "2": parameter_generators.CartesianProduct({"parameter_2": [True, False]}, set_name_template="out"),
            },
            set_name_template="out",
        ),
        {"output_directory": pathlib.Path("/directory"), "output_file_type": "yaml", "dry_run": True},
        [
            f"{pathlib.Path('/directory/out0.yaml')}\nparameter_1: 2\nparameter_2: true\n",
            f"{pathlib.Path('/directory/out1.yaml')}\nparameter_1: 1\nparameter_2: true\n",
            f"{pathlib.Path('/directory/out2.yaml')}\nparameter_1: 2\nparameter_2: false\n",
            f"{pathlib.Path('/directory/out3.yaml')}\nparameter_1: 1\nparameter_2: false\n",
        ],
        None,
        None,
        None,
        does_not_raise,
    ),
}


@pytest.mark.parametrize(
    (
        "generator",
        "kwargs",
        "expected_stdout",
        "expected_to_netcdf",
        "expected_write",
        "expected_write_meta_file_contents",
        "outcome",
    ),
    test__write_cases.values(),
    ids=test__write_cases.keys(),
)
def test__write(
    generator: parameter_generators.ParameterGenerator,
    kwargs: dict,
    expected_stdout: list[str] | None,
    expected_to_netcdf: list[xarray.Dataset] | None,
    expected_write: list[str] | None,
    expected_write_meta_file_contents: str | None,
    outcome: contextlib.nullcontext | pytest.RaisesExc,
) -> None:
    if sum([thing is not None for thing in (expected_stdout, expected_to_netcdf, expected_write)]) > 1:
        raise ValueError("Do not pass more than one expected output")
    with (
        outcome,
        patch("sys.stdout.write") as mock_stdout,
        patch("xarray.Dataset.to_netcdf") as mock_to_netcdf,
        patch("pathlib.Path.is_file", return_value=False),
        patch("pathlib.Path.open", mock_open()) as mock_file,
        patch("waves.parameter_generators._write_parameter_study_meta_file") as mock_write_meta_file,
        patch("pathlib.Path.mkdir"),
    ):
        parameter_generators._write(generator, **kwargs)
        if expected_stdout is None:
            mock_stdout.assert_not_called()
        else:
            assert mock_stdout.call_count == len(expected_stdout)
            mock_stdout.assert_has_calls([call(item) for item in expected_stdout])
        if expected_to_netcdf is None:
            mock_to_netcdf.assert_not_called()
        else:
            # TODO: figure out how to assert the dataset/output association
            assert mock_to_netcdf.call_count == len(expected_to_netcdf)
        if expected_write is None:
            mock_file().assert_not_called()
        else:
            assert mock_file().write.call_count == len(expected_write)
            mock_file().write.assert_has_calls([call(item) for item in expected_write])
        if expected_write_meta_file_contents is None:
            mock_write_meta_file.assert_not_called()
        else:
            mock_write_meta_file.assert_called_once()
            assert mock_write_meta_file.call_args[0][1] == expected_write_meta_file_contents


# In the class method, the generator attributes are not ignored. Override the ``(class init)`` test cases where the
# generator attributes are respected.
test_class_write_cases = copy.deepcopy(test__write_cases)
test_class_write_cases.update(
    {
        "CartesianProduct (class init): output file, default type": (
            parameter_generators.CartesianProduct({"parameter_1": [1, 2]}, output_file=pathlib.Path("output.h5")),
            {},
            None,
            [
                xarray.Dataset(
                    {
                        "parameter_1": xarray.DataArray(
                            [2, 1],
                            coords={
                                "set_name": xarray.DataArray(["parameter_set0", "parameter_set1"], dims=["set_name"])
                            },
                        ),
                        "set_hash": xarray.DataArray(
                            ["0b588b6a82c1d3d3d19fda304f940342", "1661dcd0bf4761d25471c1cf5514ceae"],
                            dims="set_name",
                        ),
                    },
                ).set_coords("set_hash"),
            ],
            None,
            None,
            does_not_raise,
        ),
        "CartesianProduct (class init): output file, default type (overridden)": (
            parameter_generators.CartesianProduct({"parameter_1": [1, 2]}, output_file=pathlib.Path("output.h5")),
            {"output_file_type": "yaml"},
            None,
            None,
            ["parameter_set0:\n  parameter_1: 2\nparameter_set1:\n  parameter_1: 1\n"],
            None,
            does_not_raise,
        ),
        "CartesianProduct (class init): output file, default type, overwrite": (
            parameter_generators.CartesianProduct(
                {"parameter_1": [1, 2]}, output_file=pathlib.Path("output.h5"), overwrite=True
            ),
            {},
            None,
            [
                xarray.Dataset(
                    {
                        "parameter_1": xarray.DataArray(
                            [2, 1],
                            coords={
                                "set_name": xarray.DataArray(["parameter_set0", "parameter_set1"], dims=["set_name"])
                            },
                        ),
                        "set_hash": xarray.DataArray(
                            ["0b588b6a82c1d3d3d19fda304f940342", "1661dcd0bf4761d25471c1cf5514ceae"],
                            dims="set_name",
                        ),
                    },
                ).set_coords("set_hash"),
            ],
            None,
            None,
            does_not_raise,
        ),
        "CartesianProduct (class init): output file, H5": (
            parameter_generators.CartesianProduct(
                {"parameter_1": [1, 2]}, output_file=pathlib.Path("output.h5"), output_file_type="h5"
            ),
            {},
            None,
            [
                xarray.Dataset(
                    {
                        "parameter_1": xarray.DataArray(
                            [2, 1],
                            coords={
                                "set_name": xarray.DataArray(
                                    ["parameter_set0", "parameter_set1"],
                                    dims=["set_name"],
                                )
                            },
                        ),
                        "set_hash": xarray.DataArray(
                            ["0b588b6a82c1d3d3d19fda304f940342", "1661dcd0bf4761d25471c1cf5514ceae"],
                            dims="set_name",
                        ),
                    },
                ).set_coords("set_hash"),
            ],
            None,
            None,
            does_not_raise,
        ),
        "CartesianProduct (class init): output file, H5 (overridden)": (
            parameter_generators.CartesianProduct({"parameter_1": [1, 2]}, output_file=pathlib.Path("output.h5")),
            {"output_file_type": "yaml"},
            None,
            None,
            ["parameter_set0:\n  parameter_1: 2\nparameter_set1:\n  parameter_1: 1\n"],
            None,
            does_not_raise,
        ),
        "CartesianProduct (class init): output file, YAML": (
            parameter_generators.CartesianProduct(
                {"parameter_1": [1, 2]}, output_file=pathlib.Path("output.yaml"), output_file_type="yaml"
            ),
            {},
            None,
            None,
            ["parameter_set0:\n  parameter_1: 2\nparameter_set1:\n  parameter_1: 1\n"],
            None,
            does_not_raise,
        ),
        "CartesianProduct (class init): output file, YAML, dry run": (
            parameter_generators.CartesianProduct(
                {"parameter_1": [1, 2]}, output_file=pathlib.Path("output.yaml"), output_file_type="yaml"
            ),
            {"dry_run": True},
            [f"{pathlib.Path('output.yaml')}\nparameter_set0:\n  parameter_1: 2\nparameter_set1:\n  parameter_1: 1\n"],
            None,
            None,
            None,
            does_not_raise,
        ),
        "CartesianProduct (class init): output file (overridden), YAML, dry run": (
            parameter_generators.CartesianProduct(
                {"parameter_1": [1, 2]}, output_file=pathlib.Path("output.yaml"), output_file_type="yaml"
            ),
            {"output_file": pathlib.Path("different.yaml"), "dry_run": True},
            [
                f"{pathlib.Path('different.yaml')}\n"
                "parameter_set0:\n  parameter_1: 2\nparameter_set1:\n  parameter_1: 1\n"
            ],
            None,
            None,
            None,
            does_not_raise,
        ),
        "CartesianProduct (class init): output file, YAML (overridden)": (
            parameter_generators.CartesianProduct(
                {"parameter_1": [1, 2]}, output_file=pathlib.Path("output.yaml"), output_file_type="yaml"
            ),
            {"output_file_type": "h5"},
            None,
            [
                xarray.Dataset(
                    {
                        "parameter_1": xarray.DataArray(
                            [2, 1],
                            coords={
                                "set_name": xarray.DataArray(
                                    ["parameter_set0", "parameter_set1"],
                                    dims=["set_name"],
                                )
                            },
                        ),
                        "set_hash": xarray.DataArray(
                            ["0b588b6a82c1d3d3d19fda304f940342", "1661dcd0bf4761d25471c1cf5514ceae"],
                            dims="set_name",
                        ),
                    },
                ).set_coords("set_hash"),
            ],
            None,
            None,
            does_not_raise,
        ),
    }
)


@pytest.mark.parametrize(
    (
        "generator",
        "kwargs",
        "expected_stdout",
        "expected_to_netcdf",
        "expected_write",
        "expected_write_meta_file_contents",
        "outcome",
    ),
    test_class_write_cases.values(),
    ids=test_class_write_cases.keys(),
)
def test_class_write(
    generator: parameter_generators.ParameterGenerator,
    kwargs: dict,
    expected_stdout: list[str] | None,
    expected_to_netcdf: list[xarray.Dataset] | None,
    expected_write: list[str] | None,
    expected_write_meta_file_contents: str | None,
    outcome: contextlib.nullcontext | pytest.RaisesExc,
) -> None:
    if sum([thing is not None for thing in (expected_stdout, expected_to_netcdf, expected_write)]) > 1:
        raise ValueError("Do not pass more than one expected output")
    with (
        outcome,
        patch("sys.stdout.write") as mock_stdout,
        patch("xarray.Dataset.to_netcdf") as mock_to_netcdf,
        patch("pathlib.Path.is_file", return_value=False),
        patch("pathlib.Path.open", mock_open()) as mock_file,
        patch("waves.parameter_generators._write_parameter_study_meta_file") as mock_write_meta_file,
        patch("pathlib.Path.mkdir"),
    ):
        generator.write(**kwargs)
        if expected_stdout is None:
            mock_stdout.assert_not_called()
        else:
            assert mock_stdout.call_count == len(expected_stdout)
            mock_stdout.assert_has_calls([call(item) for item in expected_stdout])
        if expected_to_netcdf is None:
            mock_to_netcdf.assert_not_called()
        else:
            # TODO: figure out how to assert the dataset/output association
            assert mock_to_netcdf.call_count == len(expected_to_netcdf)
        if expected_write is None:
            mock_file().assert_not_called()
        else:
            assert mock_file().write.call_count == len(expected_write)
            mock_file().write.assert_has_calls([call(item) for item in expected_write])
        if expected_write_meta_file_contents is None:
            mock_write_meta_file.assert_not_called()
        else:
            mock_write_meta_file.assert_called_once()
            assert mock_write_meta_file.call_args[0][1] == expected_write_meta_file_contents
