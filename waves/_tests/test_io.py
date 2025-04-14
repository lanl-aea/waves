import inspect
import pathlib
import tempfile

import pytest
import xarray

from waves import _utilities
from waves import parameter_generators


test_previous_parameter_study_cases = {
    "int": {"int": [1]},
    "float": {"float": [1.0]},
    "str": {"str": ["a"]},
    "bool": {"bool": [True]},
    "int and float": {"int": [1], "float": [1.0]},
    "int and str": {"int": [1], "str": ["a"]},
    "int and bool": {"int": [1], "bool": [True]},
    "float and str": {"float": [1.0], "str": ["a"]},
    "float and bool": {"float": [1.0], "bool": [True]},
    "str and bool": {"str": ["a"], "bool": [True]},
    "int, float, str, bool": {"int": [1], "float": [1.0], "str": ["a"], "bool": [True]},
}


@pytest.mark.systemtest
@pytest.mark.parametrize(
    "schema",
    test_previous_parameter_study_cases.values(),
    ids=test_previous_parameter_study_cases.keys(),
)
def test_previous_parameter_study(
    system_test_directory,
    request,
    schema,
) -> None:
    """Run real system I/O from the waves.parameter_generators API and check parameter study merge behaviors

    Test directory name is constructed from test ID string, with character replacements to create a valid Python
    identifier as a conservative estimate of a valid directory name. Failed tests persist on disk.

    :param system_test_directory: custom pytest decorator defined in conftest.py
    :param request: pytest decorator with test case meta data
    :param schema: waves.parameter_generators.CartesianProduct schema
    """
    module_name = pathlib.Path(__file__).stem
    test_id = request.node.callspec.id
    test_prefix = _utilities.create_valid_identifier(test_id)
    test_prefix = f"{module_name}.test_previous_parameter_study.{test_prefix}."
    if system_test_directory is not None:
        system_test_directory.mkdir(parents=True, exist_ok=True)

    # TODO: Move to common test utility VVV
    kwargs = {}
    temporary_directory_arguments = inspect.getfullargspec(tempfile.TemporaryDirectory).args
    if "ignore_cleanup_errors" in temporary_directory_arguments and system_test_directory is not None:
        kwargs.update({"ignore_cleanup_errors": True})
    temp_directory = tempfile.TemporaryDirectory(dir=system_test_directory, prefix=test_prefix, **kwargs)
    temp_path = pathlib.Path(temp_directory.name)
    temp_path.mkdir(parents=True, exist_ok=True)
    # Move to common test utility ^^^

    parameter_study_file = temp_path / "parameter_study.h5"
    parameter_generator = parameter_generators.CartesianProduct(
        schema,
        output_file=parameter_study_file,
        output_file_type="h5",
    )
    parameter_generator.write()

    # Check that xarray thinks the datasets are identical as a sanity check
    disk = xarray.open_dataset(parameter_study_file)
    assert disk.identical(parameter_generator.parameter_study)

    # Check that the verify function does not raise an exception
    parameter_generators._verify_parameter_study(disk)
    disk.close()

    # Check that the open function does not raise an exception
    disk_waves = parameter_generators._open_parameter_study(parameter_study_file)
    assert disk_waves.identical(parameter_generator.parameter_study)
    disk_waves.close()

    # Check that opening as a previous parameter study does not raise an exception
    parameter_generator = parameter_generators.CartesianProduct(
        schema,
        output_file=parameter_study_file,
        output_file_type="h5",
        previous_parameter_study=parameter_study_file,
    )
