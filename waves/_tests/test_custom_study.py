"""Test CustomStudy Class"""

from unittest.mock import patch, call, mock_open
from contextlib import nullcontext as does_not_raise

import pytest
import numpy

from waves.parameter_generators import CustomStudy
from waves._settings import _hash_coordinate_key, _set_coordinate_key
from waves.exceptions import SchemaValidationError
from waves._tests.common import merge_samplers


class TestCustomStudy:
    """Class for testing CustomStudy parameter study generator class"""

    validate_input = {
        "good schema list of lists": (
            {"parameter_names": ["a", "b"], "parameter_samples": [[1, 2.0], [3, 4.5]]},
            does_not_raise(),
        ),
        "good schema numpy array": (
            {"parameter_names": ["a", "b"], "parameter_samples": numpy.array([[1, 2.0], [3, 4.5]])},
            does_not_raise(),
        ),
        "not a dict": (
            "not a dict",
            pytest.raises(SchemaValidationError),
        ),
        "bad schema no names": (
            {"parameter_samples": numpy.array([[1, 2.0], [3, 4.5]], dtype=object)},
            pytest.raises(SchemaValidationError),
        ),
        "bad schema no values": (
            {"parameter_names": ["a", "b"]},
            pytest.raises(SchemaValidationError),
        ),
        "bad schema dimension": (
            {"parameter_names": ["a", "b"], "parameter_samples": numpy.array([1, 2.0], dtype=object)},
            pytest.raises(SchemaValidationError),
        ),
        "bad schema shape": (
            {"parameter_names": ["a", "b", "c"], "parameter_samples": numpy.array([[1, 2.0], [3, 4.5]], dtype=object)},
            pytest.raises(SchemaValidationError),
        ),
    }

    @pytest.mark.parametrize(
        "parameter_schema, outcome",
        validate_input.values(),
        ids=validate_input.keys(),
    )
    def test_validate(self, parameter_schema, outcome):
        with outcome:
            try:
                # Validate is called in __init__. Do not need to call explicitly.
                TestValidate = CustomStudy(parameter_schema)
            finally:
                pass

    generate_io = {
        "one_parameter": (
            {"parameter_names": ["a"], "parameter_samples": numpy.array([[1], [2]], dtype=object)},
            numpy.array([[1], [2]], dtype=object),
            {"a": numpy.int64},
        ),
        "two_parameter": (
            {"parameter_names": ["a", "b"], "parameter_samples": numpy.array([[1, 10.0], [2, 20.0]], dtype=object)},
            numpy.array([[1, 10.0], [2, 20.0]], dtype=object),
            {"a": numpy.int64, "b": numpy.float64},
        ),
    }

    @pytest.mark.parametrize(
        "parameter_schema, expected_array, expected_types",
        generate_io.values(),
        ids=generate_io.keys(),
    )
    def test_generate(self, parameter_schema, expected_array, expected_types):
        TestGenerate = CustomStudy(parameter_schema)
        generate_array = TestGenerate._samples
        assert numpy.all(generate_array == expected_array)
        for key in TestGenerate.parameter_study.keys():
            assert TestGenerate.parameter_study[key].dtype == expected_types[key]
        # Verify that the parameter set name creation method was called
        assert list(TestGenerate._set_names.values()) == [f"parameter_set{num}" for num in range(len(expected_array))]
        # Check that the parameter set names are correctly populated in the parameter study Xarray Dataset
        expected_set_names = [f"parameter_set{num}" for num in range(len(expected_array))]
        set_names = list(TestGenerate.parameter_study[_set_coordinate_key])
        assert numpy.all(set_names == expected_set_names)

    merge_test = {
        "single set unchanged": (
            {"parameter_names": ["ints"], "parameter_samples": numpy.array([[1]], dtype=object)},
            {"parameter_names": ["ints"], "parameter_samples": numpy.array([[1]], dtype=object)},
            # Ordered by md5 hash during Xarray merge operation. New tests must verify hash ordering.
            numpy.array([[1]], dtype=object),
            {"ints": numpy.int64},
        ),
        "single set and new set": (
            {"parameter_names": ["ints"], "parameter_samples": numpy.array([[1]], dtype=object)},
            {"parameter_names": ["ints"], "parameter_samples": numpy.array([[2]], dtype=object)},
            # Ordered by md5 hash during Xarray merge operation. New tests must verify hash ordering.
            numpy.array([[1], [2]], dtype=object),
            {"ints": numpy.int64},
        ),
        "new set": (
            {
                "parameter_names": ["ints", "floats", "strings"],
                "parameter_samples": numpy.array([[1, 10.1, "a"], [2, 20.2, "b"]], dtype=object),
            },
            {
                "parameter_names": ["ints", "floats", "strings"],
                "parameter_samples": numpy.array([[1, 10.1, "a"], [3, 30.3, "c"], [2, 20.2, "b"]], dtype=object),
            },
            # Ordered by md5 hash during Xarray merge operation. New tests must verify hash ordering.
            numpy.array(
                [
                    [3, 30.3, "c"],
                    [1, 10.1, "a"],
                    [2, 20.2, "b"],
                ],
                dtype=object,
            ),
            {"ints": numpy.int64, "floats": numpy.float64, "strings": numpy.dtype("U1")},
        ),
        "unchanged sets": (
            {
                "parameter_names": ["ints", "floats", "strings"],
                "parameter_samples": numpy.array([[1, 10.1, "a"], [2, 20.2, "b"]], dtype=object),
            },
            {
                "parameter_names": ["ints", "floats", "strings"],
                "parameter_samples": numpy.array([[1, 10.1, "a"], [2, 20.2, "b"]], dtype=object),
            },
            # Ordered by md5 hash during Xarray merge operation. New tests must verify hash ordering.
            numpy.array(
                [[1, 10.1, "a"], [2, 20.2, "b"]],
                dtype=object,
            ),
            {"ints": numpy.int64, "floats": numpy.float64, "strings": numpy.dtype("U1")},
        ),
    }

    @pytest.mark.parametrize(
        "first_schema, second_schema, expected_array, expected_types",
        merge_test.values(),
        ids=merge_test.keys(),
    )
    def test_merge(self, first_schema, second_schema, expected_array, expected_types):
        with patch("waves.parameter_generators._verify_parameter_study"):
            TestMerge1, TestMerge2 = merge_samplers(CustomStudy, first_schema, second_schema, {})
            generate_array = TestMerge2._samples
            assert numpy.all(generate_array == expected_array)
            # Check for type preservation
            for key in TestMerge2.parameter_study.keys():
                assert TestMerge2.parameter_study[key].dtype == expected_types[key]
            # Check for consistent hash-parameter set relationships
            for set_name, parameters in TestMerge1.parameter_study.groupby(_set_coordinate_key):
                assert parameters == TestMerge2.parameter_study.sel({_set_coordinate_key: set_name})
            # Self-consistency checks
            assert (
                list(TestMerge2._set_names.values())
                == TestMerge2.parameter_study[_set_coordinate_key].values.tolist()  # noqa: W503
            )
            assert TestMerge2._set_hashes == TestMerge2.parameter_study[_hash_coordinate_key].values.tolist()

    generate_io = {
        "one parameter yaml": (
            {"parameter_names": ["a"], "parameter_samples": numpy.array([[1], [2]], dtype=object)},
            "out",
            None,
            "yaml",
            2,
            [call("a: 1\n"), call("a: 2\n")],
        ),
        "two parameter yaml": (
            {"parameter_names": ["a", "b"], "parameter_samples": numpy.array([[1, 2.0], [3, 4.5]], dtype=object)},
            "out",
            None,
            "yaml",
            2,
            [call("a: 1\nb: 2.0\n"), call("a: 3\nb: 4.5\n")],
        ),
        "one parameter one file yaml": (
            {"parameter_names": ["a"], "parameter_samples": numpy.array([[1], [2]], dtype=object)},
            None,
            "parameter_study.yaml",
            "yaml",
            1,
            [call("parameter_set0:\n  a: 1\nparameter_set1:\n  a: 2\n")],
        ),
        "two parameter one file yaml": (
            {"parameter_names": ["a", "b"], "parameter_samples": numpy.array([[1, 2.0], [3, 4.5]], dtype=object)},
            None,
            "parameter_study.yaml",
            "yaml",
            1,
            [call("parameter_set0:\n  a: 1\n  b: 2.0\nparameter_set1:\n  a: 3\n  b: 4.5\n")],
        ),
    }

    @pytest.mark.parametrize(
        "parameter_schema, output_file_template, output_file, output_type, file_count, expected_calls",
        generate_io.values(),
        ids=generate_io.keys(),
    )
    def test_write_yaml(
        self, parameter_schema, output_file_template, output_file, output_type, file_count, expected_calls
    ):
        with (
            patch("waves.parameter_generators.ParameterGenerator._write_meta"),
            patch("builtins.open", mock_open()) as mock_file,
            patch("xarray.Dataset.to_netcdf") as xarray_to_netcdf,
            patch("sys.stdout.write") as stdout_write,
            patch("pathlib.Path.is_file", return_value=False),
        ):
            TestWriteYAML = CustomStudy(
                parameter_schema,
                output_file_template=output_file_template,
                output_file=output_file,
                output_file_type=output_type,
            )
            TestWriteYAML.write()
            stdout_write.assert_not_called()
            xarray_to_netcdf.assert_not_called()
            assert mock_file.call_count == file_count
            mock_file().write.assert_has_calls(expected_calls, any_order=False)
