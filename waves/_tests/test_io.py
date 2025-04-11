import inspect
import pathlib
import tempfile

import pytest
import xarray

from waves import parameter_generators


test_previous_parameter_study_cases = {
    "ints": {"ints": [1]},
    "floats": {"floats": [1.]},
    "ints and floats": {"ints": [1], "floats": [1.]},
}


@pytest.mark.systemtest
@pytest.mark.parametrize(
    "schema",
    test_previous_parameter_study_cases.values(),
    ids=test_previous_parameter_study_cases.keys(),
)
def test_previous_parameter_study(
    system_test_directory,
    schema,
) -> None:

    # TODO: construct test prefix from module basename and test name
    test_prefix = f"test_io.test_open_parameter_study."
    # TODO: Move to common test utility VVV
    if system_test_directory is not None:
        system_test_directory.mkdir(parents=True, exist_ok=True)

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
