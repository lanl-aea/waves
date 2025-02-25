"""Test odb extract
Test odb_extract.py

.. moduleauthor:: Prabhu S. Khalsa <pkhalsa@lanl.gov>
"""

import os
import pathlib

import pytest
from unittest.mock import patch, mock_open

from waves._abaqus import odb_extract
from waves._utilities import _quote_spaces_in_path


fake_odb = {
    "rootAssembly": {
        "name": "ASSEMBLY",
        "instances": {
            "RIGID-1": {
                "name": "RIGID-1",
                "embeddedSpace": "THREE_D",
                "type": "ANALYTIC_RIGID_SURFACE",
                "nodes": [{"label": 1, "coordinates": [100.0, 20, 6.12323e-15]}],
                "tuple": (1, 2.0),
                "float": 1.0,
                "string_list": ["list", "of", "strings"],
            }
        },
    }
}


class FakeProcess:
    returncode = 0
    stdout = b""
    stderr = b"valid command."


def test_get_parser():
    with patch("sys.argv", ["odb_extract.py", "sample.odb"]):
        cmd_args = odb_extract.get_parser().parse_args()
        assert cmd_args.abaqus_command == "abq2024"


def test_odb_extract():
    with (
        patch("yaml.safe_dump"),
        patch("shutil.which", return_value="abaqus"),
        patch("select.select", return_value=[None, None, None]),
        patch("waves._abaqus.abaqus_file_parser.OdbReportFileParser"),
        patch("builtins.open", mock_open(read_data="data")),
        pytest.raises(SystemExit) as err,
    ):  # Test first critical error
        odb_extract.odb_extract(["sample.odb"], None)
    assert err.value.code != 0
    assert "sample.odb does not exist" in str(err.value.args)

    with (
        patch("yaml.safe_dump"),
        patch("builtins.open", mock_open(read_data="data")),
        patch("shutil.which", return_value="abaqus"),
        patch("select.select", return_value=[None, None, None]),
        patch("waves._abaqus.abaqus_file_parser.OdbReportFileParser"),
        patch("builtins.print") as mock_print,
        patch("pathlib.Path.exists", return_value=True),
    ):  # Test warning after second critical error
        odb_extract.odb_extract(["sample"], None)
    assert err.value.code != 0
    assert "sample.odb does not exist." in str(err.value.args)

    with (
        patch("yaml.safe_dump"),
        patch("builtins.open", mock_open(read_data="data")),
        patch("shutil.which", return_value="abaqus"),
        patch("select.select", return_value=[None, None, None]),
        patch("waves._abaqus.abaqus_file_parser.OdbReportFileParser", side_effect=IndexError("Test")),
        patch("pathlib.Path.exists", return_value=True),
        pytest.raises(SystemExit) as err,
    ):  # Test second critical error
        odb_extract.odb_extract(
            ["sample.odb"], None, odb_report_args="odbreport all invariants", output_type="yaml", verbose=True
        )
    assert err.value.code != 0
    assert "could not be parsed." in str(err.value.args)

    with (
        patch("pathlib.Path.exists", return_value=True),
        patch("builtins.open", mock_open(read_data="data")),
        patch("yaml.safe_dump"),
        patch("shutil.which", return_value="abaqus"),
        patch("select.select", return_value=["y", None, None]),
        patch("sys.stdin", return_value="y"),
        patch("waves._abaqus.odb_extract.run_external", return_value=[-1, b"", b"invalid command."]),
        pytest.raises(SystemExit) as err,
    ):
        odb_extract.odb_extract(["sample.odb"], None, odb_report_args="job=job_name odb=odb_filea ll")
    assert err.value.code != 0
    assert "Abaqus odbreport command failed to execute" in str(err.value.args)

    with (
        patch("pathlib.Path.exists", side_effect=[True, True, True, False]),
        patch("builtins.open", mock_open(read_data="data")),
        patch("yaml.safe_dump"),
        patch("shutil.which", return_value="abaqus"),
        patch("select.select", return_value=["y", None, None]),
        patch("sys.stdin", return_value="y"),
        patch("waves._abaqus.abaqus_file_parser.OdbReportFileParser") as mock_abaqus_file_parser,
        patch("waves._abaqus.odb_extract.run_external", return_value=[0, b"", b"valid command."]),
        pytest.raises(SystemExit) as err,
    ):
        odb_extract.odb_extract(["sample.odb"], None, odb_report_args="odbreport all", output_type="yaml")
    assert err.value.code != 0
    assert "does not exist" in str(err.value.args)

    with (
        patch("pathlib.Path.exists", return_value=True),
        patch("builtins.open", mock_open(read_data="data")),
        patch("yaml.safe_dump"),
        patch("shutil.which", return_value="abaqus"),
        patch("select.select", return_value=["y", None, None]),
        patch("sys.stdin", return_value="y"),
        patch("waves._abaqus.abaqus_file_parser.OdbReportFileParser") as mock_abaqus_file_parser,
        patch("waves._abaqus.odb_extract.run_external", return_value=[0, b"", b"valid command."]) as mock_run_external,
    ):
        # Test case where report args overridden by appended arguments
        odb_extract.odb_extract(["sample.odb"], None, odb_report_args="job=job_name odb=odb_file")
        mock_abaqus_file_parser.assert_called()
        mock_run_external.assert_called_with(
            "abaqus odbreport job=job_name odb=odb_file -job sample -odb sample.odb -mode CSV -blocked"
        )

    with (
        patch("pathlib.Path.exists", return_value=True),
        patch("builtins.open", mock_open(read_data="data")),
        patch("yaml.safe_dump") as mock_safe_dump,
        patch("shutil.which", return_value="abaqus"),
        patch("select.select", return_value=["y", None, None]),
        patch("sys.stdin", return_value="y"),
        patch("waves._abaqus.abaqus_file_parser.OdbReportFileParser"),
        patch("waves._abaqus.odb_extract.run_external", return_value=[0, b"", b"valid command."]) as mock_run_external,
    ):
        # Test case where output name doesn't match odb name
        odb_extract.odb_extract(["sample.odb"], "new_name.h5", odb_report_args="odbreport -all")
        mock_run_external.assert_called_with("abaqus odbreport -all -job new_name -odb sample.odb -mode CSV -blocked")

    with (
        patch("pathlib.Path.exists", return_value=True),
        patch("builtins.open", mock_open(read_data="data")),
        patch("yaml.safe_dump") as mock_safe_dump,
        patch("shutil.which", return_value="abaqus"),
        patch("select.select", return_value=["y", None, None]),
        patch("sys.stdin", return_value="y"),
        patch("waves._abaqus.abaqus_file_parser.OdbReportFileParser"),
        patch("subprocess.run", return_value=FakeProcess) as mock_run,
    ):
        # Test case where yaml dump is called
        odb_extract.odb_extract(["sample.odb"], "", odb_report_args="odbreport -all", output_type="yaml")
        mock_safe_dump.assert_called()
        mock_run.assert_called_with(
            [
                "abaqus",
                "odbreport",
                "-all",
                "-job",
                "sample",
                "-odb",
                "sample.odb",
                "-mode",
                "CSV",
                "-blocked",
            ],
            capture_output=True,
        )

    with (
        patch("pathlib.Path.exists", return_value=True),
        patch("builtins.open", mock_open(read_data="data")),
        patch("select.select", return_value=[None, None, None]),
        patch("shutil.which", return_value=""),
        patch("json.dump") as mock_safe_dump,
        patch("waves._abaqus.abaqus_file_parser.OdbReportFileParser"),
        patch("pathlib.Path.unlink") as mock_unlink,
        patch("waves._abaqus.odb_extract.run_external", return_value=[0, b"", b"valid command."]),
    ):
        # Test case where yaml dump is called
        odb_extract.odb_extract(["sample.odb"], output_file="sample.j", output_type="json", delete_report_file=True)
        mock_safe_dump.assert_called()
        mock_unlink.assert_called()

    with (
        patch("pathlib.Path.exists", return_value=True),
        patch("builtins.open", mock_open(read_data="data")),
        patch("shutil.which", return_value="abaqus"),
        patch("select.select", return_value=[None, None, None]),
        patch("waves._abaqus.abaqus_file_parser.OdbReportFileParser") as h5_parser,
        patch("waves._abaqus.odb_extract.run_external", return_value=[0, b"", b"valid command."]),
    ):
        # Test case where h5 file is created
        odb_extract.odb_extract(["sample.odb"], None, output_type="h5")
        h5_parser.assert_called()

    with (
        patch("yaml.safe_dump"),
        patch("builtins.open", mock_open(read_data="data")),
        patch("shutil.which", return_value="abaqus"),
        patch("select.select", return_value=[None, None, None]),
        patch("waves._abaqus.abaqus_file_parser.OdbReportFileParser", side_effect=IndexError("Test")),
        patch("pathlib.Path.exists", return_value=True),
        pytest.raises(SystemExit) as err,
    ):  # Test second critical error
        # Test case where h5 file is requested, but error is raised
        odb_extract.odb_extract(["sample.odb"], None, output_type="h5")
    assert err.value.code != 0
    assert "could not be parsed." in str(err.value.args)


# fmt: off
odb_report_arguments = {
    "1 spaces": (
        "",
        f"{os.path.sep}some{os.path.sep}path with{os.path.sep}spaces.txt",
        f"{os.path.sep}no{os.path.sep}spaces.csv",
        f"-all -job {os.path.sep}no{os.path.sep}spaces -odb {os.path.sep}some{os.path.sep}\"path with\"{os.path.sep}spaces.txt -mode CSV -blocked",  # noqa: E501
    ),
    "2 spaces": (
        "",
        f"{os.path.sep}some{os.path.sep}path with{os.path.sep}spaces.txt",
        f"{os.path.sep}some more{os.path.sep}spaces.csv",
        f"-all -job {os.path.sep}\"some more\"{os.path.sep}spaces -odb {os.path.sep}some{os.path.sep}\"path with\"{os.path.sep}spaces.txt -mode CSV -blocked",  # noqa: E501
    ),
    "no spaces": (
        "",
        f"{os.path.sep}some{os.path.sep}path{os.path.sep}without{os.path.sep}spaces.txt",
        f"{os.path.sep}no{os.path.sep}spaces.csv",
        f"-all -job {os.path.sep}no{os.path.sep}spaces -odb {os.path.sep}some{os.path.sep}path{os.path.sep}without{os.path.sep}spaces.txt -mode CSV -blocked",  # noqa: E501
    ),
    "provided arguments, 1 spaces": (
        "arg1=val1",
        f"{os.path.sep}some{os.path.sep}path with{os.path.sep}spaces.txt",
        f"{os.path.sep}no{os.path.sep}spaces.csv",
        f"arg1=val1 -job {os.path.sep}no{os.path.sep}spaces -odb {os.path.sep}some{os.path.sep}\"path with\"{os.path.sep}spaces.txt -mode CSV -blocked",  # noqa: E501
    ),
    "provided arguments, 2 spaces": (
        "arg1=val1",
        f"{os.path.sep}some{os.path.sep}path with{os.path.sep}spaces.txt",
        f"{os.path.sep}some more{os.path.sep}spaces.csv",
        f"arg1=val1 -job {os.path.sep}\"some more\"{os.path.sep}spaces -odb {os.path.sep}some{os.path.sep}\"path with\"{os.path.sep}spaces.txt -mode CSV -blocked",  # noqa: E501
    ),
    "provided odb, no spaces": (
        "arg1=val1",
        f"{os.path.sep}some{os.path.sep}path{os.path.sep}without{os.path.sep}spaces.txt",
        f"{os.path.sep}no{os.path.sep}spaces.csv",
        f"arg1=val1 -job {os.path.sep}no{os.path.sep}spaces -odb {os.path.sep}some{os.path.sep}path{os.path.sep}without{os.path.sep}spaces.txt -mode CSV -blocked",  # noqa: E501
    ),
    "provided odb, 1 spaces odb": (
        "odb=val1",
        f"{os.path.sep}some{os.path.sep}path with{os.path.sep}spaces.txt",
        f"{os.path.sep}no{os.path.sep}spaces.csv",
        f"odb=val1 -job {os.path.sep}no{os.path.sep}spaces -odb {os.path.sep}some{os.path.sep}\"path with\"{os.path.sep}spaces.txt -mode CSV -blocked",  # noqa: E501
    ),
    "provided odb, 2 spaces odb": (
        "odb=val1",
        f"{os.path.sep}some{os.path.sep}path with{os.path.sep}spaces.txt",
        f"{os.path.sep}some more{os.path.sep}spaces.csv",
        f"odb=val1 -job {os.path.sep}\"some more\"{os.path.sep}spaces -odb {os.path.sep}some{os.path.sep}\"path with\"{os.path.sep}spaces.txt -mode CSV -blocked",  # noqa: E501
    ),
    "provided odb, no spaces odb": (
        "odb=val1",
        f"{os.path.sep}some{os.path.sep}path{os.path.sep}without{os.path.sep}spaces.txt",
        f"{os.path.sep}no{os.path.sep}spaces.csv",
        f"odb=val1 -job {os.path.sep}no{os.path.sep}spaces -odb {os.path.sep}some{os.path.sep}path{os.path.sep}without{os.path.sep}spaces.txt -mode CSV -blocked",  # noqa: E501
    ),
}
# fmt: on


@pytest.mark.parametrize(
    "odb_report_args, input_file, job_name, expected",
    odb_report_arguments.values(),
    ids=odb_report_arguments.keys(),
)
def test_get_odb_report_args(odb_report_args, input_file, job_name, expected):
    new_odb_report_args = odb_extract.get_odb_report_args(
        odb_report_args,
        pathlib.Path(input_file),
        pathlib.Path(job_name),
    )
    assert new_odb_report_args == expected
