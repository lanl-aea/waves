"""System test API calls with real file I/O"""

import sys
import shutil
import typing
import inspect
import pathlib
import tempfile

import pytest
import xarray

import waves


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
    system_test_directory: typing.Optional[pathlib.Path],
    keep_system_tests: bool,
    request: pytest.FixtureRequest,
    schema: dict,
) -> None:
    """Run real system I/O from the waves.parameter_generators API and check parameter study merge behaviors

    Test directory name is constructed from test ID string, with character replacements to create a valid Python
    identifier as a conservative estimate of a valid directory name. Failed tests persist on disk.

    :param system_test_directory: custom pytest decorator defined in conftest.py
    :param keep_system_tests: custom pytest decorator defined in conftest.py
    :param request: pytest decorator with test case meta data
    :param schema: waves.parameter_generators.CartesianProduct schema
    """
    module_name = pathlib.Path(__file__).stem
    test_id = request.node.callspec.id
    test_prefix = waves._utilities.create_valid_identifier(test_id)
    test_prefix = f"{module_name}.test_previous_parameter_study.{test_prefix}."
    if system_test_directory is not None:
        system_test_directory.mkdir(parents=True, exist_ok=True)

    # TODO: Move to common test utility VVV
    kwargs = {}
    temporary_directory_inspection = inspect.getfullargspec(tempfile.TemporaryDirectory)
    temporary_directory_arguments = temporary_directory_inspection.args + temporary_directory_inspection.kwonlyargs
    if "ignore_cleanup_errors" in temporary_directory_arguments and system_test_directory is not None:
        kwargs.update({"ignore_cleanup_errors": True})
    if keep_system_tests:
        if "delete" in temporary_directory_arguments:
            kwargs.update({"delete": False})
        else:
            print(
                "``--keep-system-tests`` requested, but Python version does not support ``delete=False`` in"
                " tempfile.TemporaryDirectory. System test directories will be deleted on cleanup.",
                file=sys.stderr,
            )
    temp_directory = tempfile.TemporaryDirectory(dir=system_test_directory, prefix=test_prefix, **kwargs)
    temp_path = pathlib.Path(temp_directory.name)
    temp_path.mkdir(parents=True, exist_ok=True)
    # Move to common test utility ^^^

    parameter_study_file = temp_path / "parameter_study.h5"
    parameter_generator = waves.parameter_generators.CartesianProduct(
        schema,
        output_file=parameter_study_file,
        output_file_type="h5",
    )
    parameter_generator.write()

    # Check that xarray thinks the datasets are identical as a sanity check
    disk = xarray.open_dataset(parameter_study_file, engine="h5netcdf")
    assert disk.identical(parameter_generator.parameter_study)

    # Check that the verify function does not raise an exception
    waves.parameter_generators._verify_parameter_study(disk)
    disk.close()

    # Check that the open function does not raise an exception
    disk_waves = waves.parameter_generators._open_parameter_study(parameter_study_file)
    assert disk_waves.identical(parameter_generator.parameter_study)
    disk_waves.close()

    # Check that opening as a previous parameter study does not raise an exception
    parameter_generator = waves.parameter_generators.CartesianProduct(
        schema,
        output_file=parameter_study_file,
        output_file_type="h5",
        previous_parameter_study=parameter_study_file,
    )

    if not keep_system_tests:
        temp_directory.cleanup()


@pytest.mark.systemtest
def test_qoi_example(
    system_test_directory: typing.Optional[pathlib.Path],
    keep_system_tests: bool,
) -> None:
    """Run real system I/O for the waves.qoi API

    Test directory name is constructed from test ID string, with character replacements to create a valid Python
    identifier as a conservative estimate of a valid directory name. Failed tests persist on disk.

    :param system_test_directory: custom pytest decorator defined in conftest.py
    :param keep_system_tests: custom pytest decorator defined in conftest.py
    """
    module_path = pathlib.Path(__file__).resolve()
    module_name = module_path.stem
    test_prefix = f"{module_name}.test_qoi_example."
    if system_test_directory is not None:
        system_test_directory.mkdir(parents=True, exist_ok=True)

    # TODO: Move to common test utility VVV
    kwargs = {}
    temporary_directory_inspection = inspect.getfullargspec(tempfile.TemporaryDirectory)
    temporary_directory_arguments = temporary_directory_inspection.args + temporary_directory_inspection.kwonlyargs
    if "ignore_cleanup_errors" in temporary_directory_arguments and system_test_directory is not None:
        kwargs.update({"ignore_cleanup_errors": True})
    if keep_system_tests:
        if "delete" in temporary_directory_arguments:
            kwargs.update({"delete": False})
        else:
            print(
                "``--keep-system-tests`` requested, but Python version does not support ``delete=False`` in"
                " tempfile.TemporaryDirectory. System test directories will be deleted on cleanup.",
                file=sys.stderr,
            )
    temp_directory = tempfile.TemporaryDirectory(dir=system_test_directory, prefix=test_prefix, **kwargs)
    temp_path = pathlib.Path(temp_directory.name)
    temp_path.mkdir(parents=True, exist_ok=True)
    # Move to common test utility ^^^

    # Create multiple QOIs
    load = waves.qoi.create_qoi(
        name="load",
        calculated=5.0,
        units="N",
        long_name="Axial Load",
        description="Axial load through component XYZ",
        group="Assembly ABC Preload",
        version="abcdef",
        date="2025-01-01",
    )
    gap = waves.qoi.create_qoi(
        name="gap",
        calculated=1.0,
        units="mm",
        long_name="Radial gap",
        description="Radial gap between components A and B",
        group="Assembly ABC Preload",
        version="abcdef",
        date="2025-01-01",
    )

    # Combine QOIs into calculated QOIs set
    simulation_1_qois = waves.qoi.create_qoi_set((load, gap))
    print(simulation_1_qois)
    print(simulation_1_qois["load"])

    # Save calculated QOIs to CSV
    waves.qoi.write_qoi_set_to_csv(simulation_1_qois, temp_path / "simulation_1_qois.csv")

    # Save calculated QOIs to h5
    simulation_1_qois.to_netcdf(temp_path / "simulation_1_qois.h5", engine="h5netcdf")

    # Read expected QOIs from CSV
    shutil.copy(
        module_path.parent / "simulation_1_expected_qois.csv",
        temp_path / "simulation_1_expected_qois.csv",
    )
    simulation_1_expected_qois = waves.qoi._read_qoi_set(temp_path / "simulation_1_expected_qois.csv")
    print(simulation_1_expected_qois)

    # Compare calculated to expected values
    waves.qoi._diff(
        calculated=temp_path / "simulation_1_qois.csv",
        expected=temp_path / "simulation_1_expected_qois.csv",
        output=temp_path / "simulation_1_qois_diff.csv",
    )

    # Accept new calculated values
    waves.qoi._accept(
        calculated=temp_path / "simulation_1_qois.csv", expected=temp_path / "simulation_1_expected_qois.csv"
    )

    # Create QOIs for different simulation
    load_2 = waves.qoi.create_qoi(
        name="load",
        calculated=30.0,
        units="lbf",
        long_name="Transverse load",
        description="Transverse load through component D",
        group="Assembly DEF Preload",
        version="abcdef",
        date="2025-01-01",
    )
    stress = waves.qoi.create_qoi(
        name="stress",
        calculated=100.0,
        units="MPa",
        long_name="Membrane stress",
        description="Membrane stress in component E",
        group="Assembly DEF Preload",
        version="abcdef",
        date="2025-01-01",
    )
    simulation_2_qois = waves.qoi.create_qoi_set((load_2, stress))

    # Combine QOIs into archive
    commit_1_qois = waves.qoi._create_qoi_archive((*simulation_1_qois.values(), *simulation_2_qois.values()))
    # TODO: avoid writing attributes at dataset level
    commit_1_qois["Assembly ABC Preload"]["load"]

    # Write archive to H5
    commit_1_qois.to_netcdf(temp_path / "commit_1_qois.h5", engine="h5netcdf")

    # Create tolerance report from archive
    waves.qoi._write_qoi_report(commit_1_qois, temp_path / "commit_1_report.pdf")

    # Create QOIs for different commit
    commit_2_qois = waves.qoi._create_qoi_archive(
        (
            waves.qoi.create_qoi(
                name="load",
                calculated=5.3,
                expected=4.5,
                lower_limit=3.5,
                upper_limit=5.5,
                units="N",
                long_name="Axial Load",
                description="Axial load through component XYZ",
                group="Assembly ABC Preload",
                version="ghijkl",
                date="2025-02-01",
            ),
            waves.qoi.create_qoi(
                name="gap",
                calculated=1.0,
                expected=0.95,
                lower_limit=0.85,
                upper_limit=1.05,
                units="mm",
                long_name="Radial gap",
                description="Radial gap between components A and B",
                group="Assembly ABC Preload",
                version="ghijkl",
                date="2025-02-01",
            ),
            waves.qoi.create_qoi(
                name="load",
                calculated=35.0,
                units="lbf",
                long_name="Transverse load",
                description="Transverse load through component D",
                group="Assembly DEF Preload",
                version="ghijkl",
                date="2025-02-01",
            ),
            waves.qoi.create_qoi(
                name="stress",
                calculated=110.0,
                units="MPa",
                long_name="Membrane stress",
                description="Membrane stress in component E",
                group="Assembly DEF Preload",
                version="ghijkl",
                date="2025-02-01",
            ),
        )
    )
    commit_2_qois.to_netcdf(temp_path / "commit_2_qois.h5", engine="h5netcdf")

    # Merge archives
    all_commit_qois = waves.qoi._merge_qoi_archives((commit_1_qois, commit_2_qois))
    print(all_commit_qois)

    # Create QOI history report
    waves.qoi._qoi_history_report(all_commit_qois, temp_path / "qoi_history.pdf")

    # Create QOI set with set_name attribute for parameter studies
    # Group must still be unique
    set_0_qoi = waves.qoi.create_qoi(
        name="load",
        calculated=5.0,
        units="N",
        long_name="Axial Load",
        description="Axial load through component XYZ",
        group="Assembly ABC Preload set_0",
        set_name="set_0",
        version="abcdef",
    )
    set_1_qoi = waves.qoi.create_qoi(
        name="load",
        calculated=6.0,
        units="N",
        long_name="Axial Load",
        description="Axial load through component XYZ",
        group="Assembly ABC Preload set_1",
        set_name="set_1",
        version="abcdef",
    )
    set_2_qoi = waves.qoi.create_qoi(
        name="load",
        calculated=7.0,
        units="N",
        long_name="Axial Load",
        description="Axial load through component XYZ",
        group="Assembly ABC Preload set_2",
        set_name="set_2",
        version="abcdef",
    )
    set_3_qoi = waves.qoi.create_qoi(
        name="load",
        calculated=8.0,
        units="N",
        long_name="Axial Load",
        description="Axial load through component XYZ",
        group="Assembly ABC Preload set_3",
        set_name="set_3",
        version="abcdef",
    )

    study = waves.parameter_generators.CartesianProduct(
        {"height": [1.0, 2.0], "width": [0.2, 0.4]},
        output_file="study.h5",
        set_name_template="set_@number",
    )
    print(study.parameter_study)
    qoi_study = waves.qoi._create_qoi_study((set_0_qoi, set_1_qoi, set_2_qoi, set_3_qoi), study.parameter_study)
    print(qoi_study)

    # Reindex on independent parameters
    qoi_study = qoi_study.set_index(set_name=("height", "width")).unstack("set_name")
    print(qoi_study)
    print(qoi_study.sel(height=2.0))

    if not keep_system_tests:
        temp_directory.cleanup()
