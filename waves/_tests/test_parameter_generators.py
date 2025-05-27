"""Test ParameterGenerator Abstract Base Class"""

import pathlib
from unittest.mock import patch, mock_open, Mock
from contextlib import nullcontext as does_not_raise

import pytest
import numpy
import xarray

from waves import parameter_generators
from waves.exceptions import ChoicesError, MutuallyExclusiveError, SchemaValidationError
from waves import _settings


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
    "parameter_names, samples, expected_hashes",
    set_hashes.values(),
    ids=set_hashes.keys(),
)
def test_calculate_set_hash(parameter_names, samples, expected_hashes):
    for row, expected_hash in zip(samples, expected_hashes):
        set_hash = parameter_generators._calculate_set_hash(parameter_names, row)
        assert set_hash == expected_hash

        with pytest.raises(RuntimeError):
            try:
                set_hash = parameter_generators._calculate_set_hash([], row)
            finally:
                pass


@pytest.mark.parametrize(
    "parameter_names, samples, expected_hashes",
    set_hashes.values(),
    ids=set_hashes.keys(),
)
def test_calculate_set_hashes(parameter_names, samples, expected_hashes):
    set_hashes = parameter_generators._calculate_set_hashes(
        parameter_names,
        samples,
    )
    assert set_hashes == expected_hashes


@pytest.mark.parametrize(
    "parameter_names, samples, expected_hashes",
    set_hashes.values(),
    ids=set_hashes.keys(),
)
def test_verify_parameter_study(parameter_names, samples, expected_hashes):
    # Borrow setup from class test. See :meth:`test_create_set_hashes`
    HashesParameterGenerator = DummyGenerator({})
    HashesParameterGenerator._parameter_names = parameter_names
    HashesParameterGenerator._samples = samples
    HashesParameterGenerator._create_set_hashes()
    assert HashesParameterGenerator._set_hashes == expected_hashes
    parameter_study = HashesParameterGenerator.parameter_study

    with does_not_raise():
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
        does_not_raise(),
    ),
    "CartesianProduct: different parameters": (
        parameter_generators.CartesianProduct({"parameter_1": [1]}).parameter_study,
        parameter_generators.CartesianProduct({"parameter_2": [10.0]}).parameter_study,
        {"parameter_1": numpy.int64, "parameter_2": numpy.float64},
        does_not_raise(),
    ),
    "CartesianProduct: extra parameters in second dataset": (
        parameter_generators.CartesianProduct({"parameter_1": [1]}).parameter_study,
        parameter_generators.CartesianProduct({"parameter_1": [1], "parameter_2": [10.0]}).parameter_study,
        {"parameter_1": numpy.int64, "parameter_2": numpy.float64},
        does_not_raise(),
    ),
    "CartesianProduct: extra parameters in both datasets": (
        parameter_generators.CartesianProduct({"parameter_1": [1], "parameter_3": ["a"]}).parameter_study,
        parameter_generators.CartesianProduct({"parameter_1": [1], "parameter_2": [10.0]}).parameter_study,
        {"parameter_1": numpy.int64, "parameter_2": numpy.float64, "parameter_3": numpy.dtype("U1")},
        does_not_raise(),
    ),
    "CartesianProduct: extra parameters bools": (
        parameter_generators.CartesianProduct({"parameter_1": [1], "parameter_3": ["a"]}).parameter_study,
        parameter_generators.CartesianProduct({"parameter_1": [1], "parameter_2": [True]}).parameter_study,
        {"parameter_1": numpy.int64, "parameter_2": bool, "parameter_3": numpy.dtype("U1")},
        does_not_raise(),
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
        does_not_raise(),
    ),
    "OneAtATime: different parameters": (
        parameter_generators.OneAtATime({"parameter_1": [1]}).parameter_study,
        parameter_generators.OneAtATime({"parameter_2": [10.0]}).parameter_study,
        {"parameter_1": numpy.int64, "parameter_2": numpy.float64},
        does_not_raise(),
    ),
    "OneAtATime: extra parameters in second dataset": (
        parameter_generators.OneAtATime({"parameter_1": [1]}).parameter_study,
        parameter_generators.OneAtATime({"parameter_1": [1], "parameter_2": [10.0]}).parameter_study,
        {"parameter_1": numpy.int64, "parameter_2": numpy.float64},
        does_not_raise(),
    ),
    "OneAtATime: extra parameters in both datasets": (
        parameter_generators.OneAtATime({"parameter_1": [1], "parameter_3": ["a"]}).parameter_study,
        parameter_generators.OneAtATime({"parameter_1": [1], "parameter_2": [10.0]}).parameter_study,
        {"parameter_1": numpy.int64, "parameter_2": numpy.float64, "parameter_3": numpy.dtype("U1")},
        does_not_raise(),
    ),
    "OneAtATime: extra parameters bools": (
        parameter_generators.OneAtATime({"parameter_1": [1], "parameter_3": ["a"]}).parameter_study,
        parameter_generators.OneAtATime({"parameter_1": [1], "parameter_2": [True]}).parameter_study,
        {"parameter_1": numpy.int64, "parameter_2": bool, "parameter_3": numpy.dtype("U1")},
        does_not_raise(),
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
    "dataset_1, dataset_2, expected_types, outcome",
    return_dataset_types_cases.values(),
    ids=return_dataset_types_cases.keys(),
)
def test_return_dataset_types(dataset_1, dataset_2, expected_types, outcome):
    with outcome:
        try:
            types = parameter_generators._return_dataset_types(dataset_1, dataset_2)
            assert types == expected_types
        finally:
            pass


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
    "values, name, expected_output_type, should_warn",
    coerce_values_cases.values(),
    ids=coerce_values_cases.keys(),
)
def test_coerce_values(values, name, expected_output_type, should_warn):
    with patch("warnings.warn") as mock_warn:
        values_coerced = parameter_generators._coerce_values(values, name)
        assert [type(item) for item in values_coerced] == [expected_output_type] * len(values_coerced)
        if should_warn:
            mock_warn.assert_called_once()
        else:
            mock_warn.assert_not_called()


merge_parameter_studies_cases = {
    "concatenate along one parameter: unchanged": (
        [
            parameter_generators.OneAtATime({"parameter_1": [1]}).parameter_study,
            parameter_generators.OneAtATime({"parameter_1": [1]}).parameter_study,
        ],
        numpy.array([[1]], dtype=object),
        {"parameter_1": numpy.int64},
        does_not_raise(),
    ),
    "concatenate along one parameter: int": (
        [
            parameter_generators.OneAtATime({"parameter_1": [1]}).parameter_study,
            parameter_generators.OneAtATime({"parameter_1": [2]}).parameter_study,
        ],
        numpy.array([[2], [1]], dtype=object),
        {"parameter_1": numpy.int64},
        does_not_raise(),
    ),
    "concatenate along one parameter: float": (
        [
            parameter_generators.CartesianProduct({"parameter_1": [1.0]}).parameter_study,
            parameter_generators.CartesianProduct({"parameter_1": [2.0]}).parameter_study,
        ],
        numpy.array([[1.0], [2.0]], dtype=object),
        {"parameter_1": numpy.float64},
        does_not_raise(),
    ),
    "concatenate along one parameter: bool": (
        [
            parameter_generators.OneAtATime({"parameter_1": [True]}).parameter_study,
            parameter_generators.OneAtATime({"parameter_1": [False]}).parameter_study,
        ],
        numpy.array([[False], [True]], dtype=object),
        {"parameter_1": numpy.bool_},
        does_not_raise(),
    ),
    "concatenate along one parameter: int/float": (
        [
            parameter_generators.CartesianProduct({"parameter_1": [1]}).parameter_study,
            parameter_generators.CartesianProduct({"parameter_1": [2.0]}).parameter_study,
        ],
        None,
        None,
        pytest.raises(RuntimeError),
    ),
    "concatenate along one parameter: int/bool": (
        [
            parameter_generators.CartesianProduct({"parameter_1": [1]}).parameter_study,
            parameter_generators.CartesianProduct({"parameter_1": [True]}).parameter_study,
        ],
        None,
        None,
        pytest.raises(RuntimeError),
    ),
    "concatenate along one parameter: float/bool": (
        [
            parameter_generators.OneAtATime({"parameter_1": [1.0]}).parameter_study,
            parameter_generators.OneAtATime({"parameter_1": [True]}).parameter_study,
        ],
        None,
        None,
        pytest.raises(RuntimeError),
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
        numpy.array(
            [
                [1, 3.0, "a"],
                [1, 4.0, "a"],
                [2, 3.0, "a"],
                [1, 5.0, "a"],
            ],
            dtype=object,
        ),
        {"parameter_1": numpy.int64, "parameter_2": numpy.float64, "parameter_3": numpy.dtype("U1")},
        does_not_raise(),
    ),
    "concatenate along two parameters across multiple studies: int/bool": (
        [
            parameter_generators.CartesianProduct(
                {"parameter_1": [1], "parameter_2": [3.0], "parameter_3": [True]}
            ).parameter_study,
            parameter_generators.CartesianProduct(
                {"parameter_1": [1, 2], "parameter_2": [3.0], "parameter_3": [True]}
            ).parameter_study,
            parameter_generators.CartesianProduct(
                {"parameter_1": [2], "parameter_2": [3.0], "parameter_3": [False]}
            ).parameter_study,
        ],
        numpy.array(
            [
                [2, 3.0, False],
                [2, 3.0, True],
                [1, 3.0, True],
            ],
            dtype=object,
        ),
        {"parameter_1": numpy.int64, "parameter_2": numpy.float64, "parameter_3": numpy.bool_},
        does_not_raise(),
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
        numpy.array(
            [
                [2, 3.0, False],
                [1, 3.0, False],
                [2, 3.0, True],
                [1, 3.0, True],
            ],
            dtype=object,
        ),
        {"parameter_1": numpy.int64, "parameter_2": numpy.float64, "parameter_3": numpy.bool_},
        does_not_raise(),
    ),
    "too few parameter studies input": (
        [parameter_generators.OneAtATime({"parameter_1": [1]}).parameter_study],
        numpy.array([[1]], dtype=object),
        {"parameter_1": numpy.int64},
        pytest.raises(RuntimeError),
    ),
}


@pytest.mark.parametrize(
    "studies, expected_samples, expected_types, outcome",
    merge_parameter_studies_cases.values(),
    ids=merge_parameter_studies_cases.keys(),
)
def test_merge_parameter_studies(studies, expected_samples, expected_types, outcome):
    with outcome:
        try:
            merged_study = parameter_generators._merge_parameter_studies(studies)
            for key in expected_types.keys():
                assert merged_study[key].dtype == expected_types[key]
            samples = parameter_generators._parameter_study_to_numpy(merged_study)
            assert numpy.all(samples == expected_samples)
        finally:
            pass


def test_open_parameter_study():
    mock_file = "dummy.h5"
    with (
        patch("pathlib.Path.is_file", return_value=True),
        patch("xarray.open_dataset") as mock_open_dataset,
        patch("waves.parameter_generators._verify_parameter_study"),
        does_not_raise(),
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
        try:
            parameter_generators._open_parameter_study(mock_file)
        finally:
            mock_open_dataset.assert_not_called()

    # Test verification failure
    with (
        patch("pathlib.Path.is_file", return_value=True),
        patch("xarray.open_dataset") as mock_open_dataset,
        patch("waves.parameter_generators._verify_parameter_study", side_effect=RuntimeError),
        pytest.raises(RuntimeError),
    ):
        try:
            parameter_generators._open_parameter_study(mock_file)
        finally:
            mock_open_dataset.assert_called_once_with(mock_file, engine="h5netcdf")


class TestParameterGenerator:
    """Class for testing ABC ParameterGenerator"""

    def test_output_file_conflict(self):
        with pytest.raises(MutuallyExclusiveError):
            try:
                OutputFileConflict = DummyGenerator(
                    {}, output_file_template="out@number", output_file="single_output_file"
                )
            finally:
                pass

    def test_output_file_type(self):
        with pytest.raises(ChoicesError):
            try:
                OutputTypeError = DummyGenerator({}, output_file_type="notsupported")
            finally:
                pass

    def test_missing_previous_parameter_study_file(self):
        with (
            patch("pathlib.Path.is_file", return_value=False),
            patch("waves.parameter_generators.ParameterGenerator._merge_parameter_studies") as mock_merge,
            pytest.raises(RuntimeError),
        ):
            try:
                MissingPreviousStudy = DummyGenerator(
                    {}, previous_parameter_study="doesnotexist.h5", require_previous_parameter_study=True
                )
            finally:
                mock_merge.assert_not_called()

        with (
            patch("pathlib.Path.is_file", return_value=False),
            patch("waves.parameter_generators.ParameterGenerator._merge_parameter_studies") as mock_merge,
            patch("warnings.warn") as mock_warn,
            does_not_raise(),
        ):
            try:
                MissingPreviousStudy = DummyGenerator(
                    {}, previous_parameter_study="doesnotexist.h5", require_previous_parameter_study=False
                )
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
        "env, expected_kwargs",
        scons_write_cases.values(),
        ids=scons_write_cases.keys(),
    )
    def test_scons_write(self, env, expected_kwargs):
        sconsWrite = DummyGenerator({})
        with patch("waves.parameter_generators.ParameterGenerator.write") as mock_write:
            # Fake an SCons environment with a dictionary. SCons environment object not required for unit testing
            sconsWrite._scons_write([], [], env)
        mock_write.assert_called_once_with(**expected_kwargs)

    # fmt: off
    templates = {       # schema, file_template, set_template,          expected
        "no template":   (    {},        None,         None, ["parameter_set0"]),  # noqa: E241,E201
        "file template": (    {},       "out",         None,           ["out0"]),  # noqa: E241,E201
        "file template": (    {},        None,        "out",           ["out0"]),  # noqa: E241,E201
        "file template": (    {},       "out", "overridden",           ["out0"]),  # noqa: E241,E201
    }
    # fmt: on

    def test_merge_parameter_studies_with_missing_previous_parameter_study(self):
        # Test exception on missing previous parameter study attribute
        dummyGenerator = DummyGenerator({})
        dummyGenerator.previous_parameter_study = None
        with pytest.raises(RuntimeError):
            dummyGenerator._merge_parameter_studies()

    @pytest.mark.parametrize("length", range(1, 20, 5))
    def test_parameter_study_to_dict(self, length):
        expected = {f"parameter_set{index}": {"parameter_1": float(index)} for index in range(length)}
        kwargs = {"sets": length}
        sconsIterator = DummyGenerator({}, **kwargs)
        set_samples = sconsIterator.parameter_study_to_dict()
        assert set_samples == expected
        assert all(isinstance(key, str) for key in set_samples.keys())
        for set_name in expected.keys():
            assert expected[set_name] == set_samples[set_name]
            for parameter in expected[set_name].keys():
                assert type(set_samples[set_name][parameter]) == type(expected[set_name][parameter])  # fmt:skip # noqa: 721,E501

    @pytest.mark.parametrize(
        "schema, file_template, set_template, expected",
        templates.values(),
        ids=templates.keys(),
    )
    def test_set_names(self, schema, file_template, set_template, expected):
        """Check the generated parameter set names against template arguments

        :param str schema: placeholder string standing in for the schema read from an input file
        :param str file_template: user supplied string to be used as a template for output file names
        :param str set_template: user supplied string to be used as a template for parameter names
        :param list expected: list of expected parameter name strings
        """
        kwargs = {"sets": 1}
        if not set_template:
            TemplateGenerator = DummyGenerator(schema, output_file_template=file_template, **kwargs)
        else:
            TemplateGenerator = DummyGenerator(
                schema, output_file_template=file_template, set_name_template=set_template, **kwargs
            )
        assert list(TemplateGenerator._set_names.values()) == expected
        assert list(TemplateGenerator.parameter_study[_settings._set_coordinate_key].values) == expected

    @pytest.mark.parametrize(
        "schema, file_template, set_template, expected",
        templates.values(),
        ids=templates.keys(),
    )
    def test_update_set_names(self, schema, file_template, set_template, expected):
        """Check the generated and updated parameter set names against template arguments

        :param str schema: placeholder string standing in for the schema read from an input file
        :param str file_template: user supplied string to be used as a template for output file names
        :param str set_template: user supplied string to be used as a template for parameter names
        :param list expected: list of expected parameter name strings
        """
        kwargs = {"sets": 1}
        if not set_template:
            TemplateGenerator = DummyGenerator(schema, output_file_template=file_template, **kwargs)
        else:
            TemplateGenerator = DummyGenerator(
                schema, output_file_template=file_template, set_name_template=set_template, **kwargs
            )
        assert list(TemplateGenerator._set_names.values()) == expected
        assert list(TemplateGenerator.parameter_study[_settings._set_coordinate_key].values) == expected

        # Test that the update function runs with only a single set. Check that the names don't change.
        TemplateGenerator._update_set_names()
        assert list(TemplateGenerator._set_names.values()) == expected
        assert list(TemplateGenerator.parameter_study[_settings._set_coordinate_key].values) == expected

    # fmt: off
    init_write_stdout = {# schema, template, overwrite, dry_run,         is_file,  sets, stdout_calls  # noqa: E261
        "no-template-1": (     {},     None,     False,  False,          [False],    1,            1),  # noqa: E241,E201,E501
        "no-template-2": (     {},     None,      True,  False,          [False],    1,            1),  # noqa: E241,E201,E501
        "no-template-3": (     {},     None,     False,   True,   [False, False],    2,            1),  # noqa: E241,E201,E501
        "no-template-4": (     {},     None,     False,  False,   [ True,  True],    2,            1),  # noqa: E241,E201,E501
        "dry_run-1":     (     {},    "out",     False,   True,          [False],    1,            1),  # noqa: E241,E201,E501
        "dry_run-2":     (     {},    "out",      True,   True,          [False],    1,            1),  # noqa: E241,E201,E501
        "dry_run-3":     (     {},    "out",      True,   True,   [ True, False],    2,            2),  # noqa: E241,E201,E501
        "dry_run-4":     (     {},    "out",     False,   True,   [False,  True],    1,            1),  # noqa: E241,E201,E501
    }
    # fmt: on

    @pytest.mark.parametrize(
        "schema, template, overwrite, dry_run, is_file, sets, stdout_calls",
        init_write_stdout.values(),
        ids=init_write_stdout.keys(),
    )
    def test_write_to_stdout(self, schema, template, overwrite, dry_run, is_file, sets, stdout_calls):
        """Check for conditions that should result in calls to stdout

        :param str schema: placeholder string standing in for the schema read from an input file
        :param str template: user supplied string to be used as a template for output file names
        :param bool overwrite: overwrite existing files
        :param bool dry_run: skip file write, but show file name and associated contents that would ahve been written
        :param bool is_file: test specific argument mocks output for pathlib.Path().is_file()
        :param int sets: test specific argument for the number of sets to build for the test
        :param int stdout_calls: number of calls to stdout. Should only differ from set count when no template is
            provides. Should always be 1 when no template is provided.
        """
        kwargs = {"sets": sets}
        for output_file_type in _settings._allowable_output_file_types:
            WriteParameterGenerator = DummyGenerator(
                schema,
                output_file_template=template,
                output_file_type=output_file_type,
                overwrite=overwrite,
                **kwargs,
            )
            with (
                patch("waves.parameter_generators.ParameterGenerator._write_meta"),
                patch("builtins.open", mock_open()) as mock_file,
                patch("sys.stdout.write") as stdout_write,
                patch("xarray.Dataset.to_netcdf") as xarray_to_netcdf,
                patch("pathlib.Path.is_file", side_effect=is_file),
                patch("pathlib.Path.mkdir"),
            ):
                WriteParameterGenerator.write(dry_run=dry_run)
                mock_file.assert_not_called()
                xarray_to_netcdf.assert_not_called()
                assert stdout_write.call_count == stdout_calls

    # fmt: off
    init_write_files = {# schema, template, overwrite,        is_file, sets, files  # noqa: E261,E721
        "template-1":  (      {},    "out",     False,        [False],    1,     1),  # noqa: E241,E201
        "template-2":  (      {},    "out",     False, [False, False],    2,     2),  # noqa: E241,E201
        "template-3":  (      {},    "out",     False, [ True,  True],    2,     0),  # noqa: E241,E201
        "template-4":  (      {},    "out",     False, [ True, False],    2,     1),  # noqa: E241,E201
        "overwrite-2": (      {},    "out",      True, [False, False],    2,     2),  # noqa: E241,E201
        "overwrite-3": (      {},    "out",      True, [ True,  True],    2,     2),  # noqa: E241,E201
        "overwrite-4": (      {},    "out",      True, [ True, False],    2,     2),  # noqa: E241,E201
    }
    # fmt: on

    @pytest.mark.parametrize(
        "schema, template, overwrite, is_file, sets, files",
        init_write_files.values(),
        ids=init_write_files.keys(),
    )
    def test_write_yaml(self, schema, template, overwrite, is_file, sets, files):
        """Check for conditions that should result in calls to builtins.open

        :param str schema: placeholder string standing in for the schema read from an input file
        :param str template: user supplied string to be used as a template for output file names
        :param bool overwrite: overwrite existing files
        :param list is_file: test specific argument mocks changing output for pathlib.Path().is_file() repeat calls
        :param int sets: test specific argument for the number of sets to build for the test
        :param int files: integer number of files that should be written
        """
        kwargs = {"sets": sets}
        WriteParameterGenerator = DummyGenerator(
            schema,
            output_file_template=template,
            output_file_type="yaml",
            overwrite=overwrite,
            **kwargs,
        )
        with (
            patch("waves.parameter_generators.ParameterGenerator._write_meta"),
            patch("waves.parameter_generators.ParameterGenerator._conditionally_write_yaml") as mock_write_yaml,
            patch("waves.parameter_generators.ParameterGenerator._conditionally_write_dataset") as mock_write_dataset,
            patch("sys.stdout.write") as stdout_write,
            patch("pathlib.Path.is_file", side_effect=is_file),
        ):
            WriteParameterGenerator.write()
            stdout_write.assert_not_called()
            mock_write_dataset.assert_not_called()
            assert mock_write_yaml.call_count == files

        MismatchedOutputType = DummyGenerator(
            schema,
            output_file_template=template,
            output_file_type="h5",
            overwrite=overwrite,
            **kwargs,
        )
        with (
            patch("waves.parameter_generators.ParameterGenerator._write_meta"),
            patch("waves.parameter_generators.ParameterGenerator._conditionally_write_yaml") as mock_write_yaml,
            patch("waves.parameter_generators.ParameterGenerator._conditionally_write_dataset") as mock_write_dataset,
            patch("sys.stdout.write") as stdout_write,
            patch("pathlib.Path.is_file", side_effect=is_file),
        ):
            MismatchedOutputType.write(output_file_type="yaml")
            stdout_write.assert_not_called()
            mock_write_dataset.assert_not_called()
            assert mock_write_yaml.call_count == files

    @pytest.mark.parametrize(
        "schema, template, overwrite, is_file, sets, files",
        init_write_files.values(),
        ids=init_write_files.keys(),
    )
    def test_write_dataset(self, schema, template, overwrite, is_file, sets, files):
        """Check for conditions that should result in calls to ParameterGenerator._write_netcdf

        :param str schema: placeholder string standing in for the schema read from an input file
        :param str template: user supplied string to be used as a template for output file names
        :param bool overwrite: overwrite existing files
        :param list is_file: test specific argument mocks changing output for pathlib.Path().is_file() repeat calls
        :param int sets: test specific argument for the number of sets to build for the test
        :param int files: integer number of files that should be written
        """
        kwargs = {"sets": sets}
        WriteParameterGenerator = DummyGenerator(
            schema,
            output_file_template=template,
            output_file_type="h5",
            overwrite=overwrite,
            **kwargs,
        )
        with (
            patch("waves.parameter_generators.ParameterGenerator._write_meta"),
            patch("sys.stdout.write") as stdout_write,
            patch("waves.parameter_generators.ParameterGenerator._conditionally_write_yaml") as mock_write_yaml,
            patch("waves.parameter_generators.ParameterGenerator._conditionally_write_dataset") as mock_write_dataset,
            patch("pathlib.Path.is_file", side_effect=is_file),
            patch("pathlib.Path.mkdir"),
        ):
            WriteParameterGenerator.write()
            stdout_write.assert_not_called()
            mock_write_yaml.assert_not_called()
            assert mock_write_dataset.call_count == files

        kwargs = {"sets": sets}
        MismatchedOutputType = DummyGenerator(
            schema,
            output_file_template=template,
            output_file_type="yaml",
            overwrite=overwrite,
            **kwargs,
        )
        with (
            patch("waves.parameter_generators.ParameterGenerator._write_meta"),
            patch("sys.stdout.write") as stdout_write,
            patch("waves.parameter_generators.ParameterGenerator._conditionally_write_yaml") as mock_write_yaml,
            patch("waves.parameter_generators.ParameterGenerator._conditionally_write_dataset") as mock_write_dataset,
            patch("pathlib.Path.is_file", side_effect=is_file),
            patch("pathlib.Path.mkdir"),
        ):
            MismatchedOutputType.write(output_file_type="h5")
            stdout_write.assert_not_called()
            mock_write_yaml.assert_not_called()
            assert mock_write_dataset.call_count == files

    # fmt: off
    init_write_dataset_files = {# equals, is_file, overwrite, expected_call_count  # noqa: E261
        "equal-datasets":      (    True,  [True],     False,                   0),  # noqa: E241,E201
        "equal-overwrite":     (    True,  [True],      True,                   1),  # noqa: E241,E201
        "different-datasets":  (   False,  [True],     False,                   1),  # noqa: E241,E201
        "not-file-1":          (    True, [False],     False,                   1),  # noqa: E241,E201
        "not-file-2":          (   False, [False],     False,                   1),  # noqa: E241,E201
    }
    # fmt: on

    @pytest.mark.parametrize(
        "equals, is_file, overwrite, expected_call_count",
        init_write_dataset_files.values(),
        ids=init_write_dataset_files.keys(),
    )
    def test_conditionally_write_dataset(self, equals, is_file, overwrite, expected_call_count):
        """Check for conditions that should result in calls to xarray.Dataset.to_netcdf

        :param bool equals: parameter that identifies when the xarray.Dataset objects should be equal
        :param list is_file: test specific argument mocks changing output for pathlib.Path().is_file() repeat calls
        :param bool overwrite: parameter that identifies when the file should always be overwritten
        :param int expected_call_count: amount of times that the xarray.Dataset.to_netcdf function should be called
        """
        WriteParameterGenerator = DummyGenerator({}, overwrite=overwrite)

        with (
            patch("xarray.Dataset.to_netcdf") as xarray_to_netcdf,
            patch("xarray.open_dataset", mock_open()),
            patch("xarray.Dataset.equals", return_value=equals),
            patch("pathlib.Path.is_file", side_effect=is_file),
        ):
            WriteParameterGenerator._conditionally_write_dataset(pathlib.Path("dummy_string"), xarray.Dataset())
            assert xarray_to_netcdf.call_count == expected_call_count

    @pytest.mark.parametrize(
        "equals, is_file, overwrite, expected_call_count",
        init_write_dataset_files.values(),
        ids=init_write_dataset_files.keys(),
    )
    def test_conditionally_write_yaml(self, equals, is_file, overwrite, expected_call_count):
        """Check for conditions that should result in writing out to file

        :param bool equals: parameter that identifies when the dictionaries should be equal
        :param list is_file: test specific argument mocks changing output for pathlib.Path().is_file() repeat calls
        :param bool overwrite: parameter that identifies when the file should always be overwritten
        :param int expected_call_count: amount of times that the open.write function should be called
        """
        WriteParameterGenerator = DummyGenerator({}, overwrite=overwrite)
        existing_dict = {"dummy": "dict"} if equals else {"smart": "dict"}

        with (
            patch("builtins.open", mock_open()) as write_yaml_file,
            patch("yaml.safe_load", return_value=existing_dict),
            patch("pathlib.Path.is_file", side_effect=is_file),
        ):
            WriteParameterGenerator._conditionally_write_yaml("dummy_string", {"dummy": "dict"})
            assert write_yaml_file.return_value.write.call_count == expected_call_count

    def test_write_type_override(self):
        for instantiated_type, override_type in (("yaml", "h5"), ("h5", "yaml")):
            WriteParameterGenerator = DummyGenerator({}, output_file_type=instantiated_type)
            private_write_arguments = {
                "yaml": (
                    WriteParameterGenerator.parameter_study_to_dict(),
                    WriteParameterGenerator.parameter_study_to_dict().items(),
                    WriteParameterGenerator._conditionally_write_yaml,
                ),
                "h5": (
                    WriteParameterGenerator.parameter_study,
                    WriteParameterGenerator.parameter_study.groupby(_settings._set_coordinate_key),
                    WriteParameterGenerator._conditionally_write_dataset,
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
                WriteParameterGenerator.write()
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
                WriteParameterGenerator.write(output_file_type=override_type)
                mock_private_write.assert_called_once()
                assert mock_private_write.call_args[0][0] == override_arguments[0]
                # FIXME: Can't do boolean comparisons on xarray.Dataset.GroupBy objects.
                # Prefer to refactor _write interface over complicated test
                if isinstance(override_arguments[0], dict):
                    assert mock_private_write.call_args[0][1] == override_arguments[1]
                assert mock_private_write.call_args[0][2] == override_arguments[2]

    def test_write_exception(self):
        """Calling a non-supported format string should raise an exception"""
        WriteParameterGenerator = DummyGenerator({})
        with (
            patch("waves.parameter_generators.ParameterGenerator._write_meta"),
            patch("waves.parameter_generators.ParameterGenerator._write") as mock_private_write,
            pytest.raises(ChoicesError),
        ):
            try:
                WriteParameterGenerator.write(output_file_type="unsupported")
            finally:
                mock_private_write.assert_not_called()

    def test_write_call_to_write_meta(self):
        WriteParameterGenerator = DummyGenerator({})
        WriteParameterGenerator.write_meta = True
        WriteParameterGenerator.provided_output_file_template = True
        with (
            patch("waves.parameter_generators.ParameterGenerator._write_meta") as mock_write_meta,
            patch("waves.parameter_generators.ParameterGenerator._write") as mock_private_write,
        ):
            WriteParameterGenerator.write()
            mock_write_meta.assert_called_once()

    def test_write_meta(self):
        WriteMetaParameterGenerator = DummyGenerator({})
        with (
            patch("builtins.open", mock_open()) as mock_file,
            patch("pathlib.Path.resolve", return_value=pathlib.Path("parameter_set1.h5")),
        ):
            WriteMetaParameterGenerator._write_meta()
            handle = mock_file()
            handle.write.assert_called_once_with("parameter_set1.h5\n")

        WriteMetaParameterGenerator.output_file = pathlib.Path("dummy.h5")
        with (
            patch("builtins.open", mock_open()) as mock_file,
            patch("pathlib.Path.resolve", return_value=pathlib.Path("dummy.h5")),
        ):
            WriteMetaParameterGenerator._write_meta()
            handle = mock_file()
            handle.write.assert_called_once_with("dummy.h5\n")

    @pytest.mark.parametrize(
        "parameter_names, samples, expected_hashes",
        set_hashes.values(),
        ids=set_hashes.keys(),
    )
    def test_create_set_hashes(self, parameter_names, samples, expected_hashes):
        HashesParameterGenerator = DummyGenerator({})
        HashesParameterGenerator._parameter_names = parameter_names
        HashesParameterGenerator._samples = samples
        del HashesParameterGenerator._set_hashes
        assert not hasattr(HashesParameterGenerator, "_set_hashes")
        # Check the function setting the set hashes attribute.
        HashesParameterGenerator._create_set_hashes()
        assert HashesParameterGenerator._set_hashes == expected_hashes

    def test_create_set_names(self):
        """Test the parameter set name generation"""
        SetNamesParameterGenerator = DummyGenerator({}, output_file_template="out")
        SetNamesParameterGenerator._samples = numpy.array([[1], [2]])
        SetNamesParameterGenerator._create_set_hashes()
        SetNamesParameterGenerator._create_set_names()
        assert list(SetNamesParameterGenerator._set_names.values()) == ["out0", "out1"]

    def test_parameter_study_to_numpy(self):
        """Test the self-consistency of the parameter study dataset construction and deconstruction"""
        # Setup
        DataParameterGenerator = DummyGenerator({})
        DataParameterGenerator._parameter_names = ["ints", "floats", "strings", "bools"]
        DataParameterGenerator._samples = numpy.array([[1, 10.1, "a", True], [2, 20.2, "b", False]], dtype=object)
        DataParameterGenerator._create_set_hashes()
        DataParameterGenerator._create_set_names()
        DataParameterGenerator._create_parameter_study()
        # Test class method
        returned_samples = DataParameterGenerator._parameter_study_to_numpy()
        assert numpy.all(returned_samples == DataParameterGenerator._samples)
        # Test module function
        returned_samples = parameter_generators._parameter_study_to_numpy(DataParameterGenerator.parameter_study)


class TestParameterDistributions:
    """Class for testing _ScipyGenerator ABC class common methods"""

    validate_input = {
        "good schema": (
            {"num_simulations": 1, "parameter_1": {"distribution": "norm", "kwarg1": 1}},
            does_not_raise(),
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
        "parameter_schema, outcome",
        validate_input.values(),
        ids=validate_input.keys(),
    )
    def test_validate(self, parameter_schema, outcome):
        with (
            patch("waves.parameter_generators._ScipyGenerator._generate_parameter_distributions") as mock_distros,
            outcome,
        ):
            try:
                # Validate is called in __init__. Do not need to call explicitly.
                TestValidate = ParameterDistributions(parameter_schema)
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
        "parameter_schema, expected_scipy_kwds",
        generate_input.values(),
        ids=generate_input.keys(),
    )
    def test_generate_parameter_distributions(self, parameter_schema, expected_scipy_kwds):
        TestDistributions = ParameterDistributions(parameter_schema)
        assert TestDistributions._parameter_names == list(TestDistributions.parameter_distributions.keys())
        for parameter_name, expected_kwds in zip(TestDistributions._parameter_names, expected_scipy_kwds):
            assert TestDistributions.parameter_distributions[parameter_name].kwds == expected_kwds


class DummyGenerator(parameter_generators.ParameterGenerator):

    def _validate(self):
        self._parameter_names = ["parameter_1"]

    def _generate(self, sets=1):
        """Generate float samples for all parameters. Value matches parameter set index"""
        parameter_count = len(self._parameter_names)
        self._samples = numpy.ones((sets, parameter_count))
        for row in range(sets):
            self._samples[row, :] = self._samples[row, :] * row
        super()._generate()


class ParameterDistributions(parameter_generators._ScipyGenerator):

    def _generate(self):
        pass
