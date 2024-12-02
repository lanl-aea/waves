"""Test odb extract
Test odb_extract.py

.. moduleauthor:: Prabhu S. Khalsa <pkhalsa@lanl.gov>
"""

from pathlib import Path

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
        patch("waves._abaqus.odb_extract.which", return_value="abaqus"),
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
        patch("waves._abaqus.odb_extract.which", return_value="abaqus"),
        patch("select.select", return_value=[None, None, None]),
        patch("waves._abaqus.abaqus_file_parser.OdbReportFileParser"),
        patch("waves._abaqus.odb_extract.print_warning") as mock_print,
        patch("pathlib.Path.exists", return_value=True),
    ):  # Test warning after second critical error
        odb_extract.odb_extract(["sample"], None)
    assert err.value.code != 0
    assert "sample.odb does not exist." in str(err.value.args)

    with (
        patch("yaml.safe_dump"),
        patch("builtins.open", mock_open(read_data="data")),
        patch("waves._abaqus.odb_extract.which", return_value="abaqus"),
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
        patch("waves._abaqus.odb_extract.which", return_value="abaqus"),
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
        patch("waves._abaqus.odb_extract.which", return_value="abaqus"),
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
        patch("waves._abaqus.odb_extract.which", return_value="abaqus"),
        patch("select.select", return_value=["y", None, None]),
        patch("sys.stdin", return_value="y"),
        patch("waves._abaqus.abaqus_file_parser.OdbReportFileParser") as mock_abaqus_file_parser,
        patch("waves._abaqus.odb_extract.run_external", return_value=[0, b"", b"valid command."]) as mock_run_external,
    ):
        # Test case where report args need to be adjusted and abaqus file parser is called
        odb_extract.odb_extract(["sample.odb"], None, odb_report_args="job=job_name odb=odb_filea ll")
        mock_abaqus_file_parser.assert_called()
        mock_run_external.assert_called_with("abaqus odbreport job=sample odb=sample.odb all mode=CSV blocked")

    with (
        patch("pathlib.Path.exists", return_value=True),
        patch("builtins.open", mock_open(read_data="data")),
        patch("yaml.safe_dump") as mock_safe_dump,
        patch("waves._abaqus.odb_extract.which", return_value="abaqus"),
        patch("select.select", return_value=["y", None, None]),
        patch("sys.stdin", return_value="y"),
        patch("waves._abaqus.abaqus_file_parser.OdbReportFileParser"),
        patch("waves._abaqus.odb_extract.run_external", return_value=[0, b"", b"valid command."]) as mock_run_external,
    ):
        # Test case where output name doesn't match odb name
        odb_extract.odb_extract(["sample.odb"], "new_name.h5", odb_report_args="odbreport all")
        mock_run_external.assert_called_with("abaqus odbreport job=new_name odb=sample.odb all blocked mode=CSV")

    with (
        patch("pathlib.Path.exists", return_value=True),
        patch("builtins.open", mock_open(read_data="data")),
        patch("yaml.safe_dump") as mock_safe_dump,
        patch("waves._abaqus.odb_extract.which", return_value="abaqus"),
        patch("select.select", return_value=["y", None, None]),
        patch("sys.stdin", return_value="y"),
        patch("waves._abaqus.abaqus_file_parser.OdbReportFileParser"),
        patch("waves._abaqus.odb_extract.run", return_value=FakeProcess) as mock_run,
    ):
        # Test case where yaml dump is called
        odb_extract.odb_extract(["sample.odb"], None, odb_report_args="odbreport all", output_type="yaml")
        mock_safe_dump.assert_called()
        mock_run.assert_called_with(
            ["abaqus", "odbreport", "job=sample", "odb=sample.odb", "all", "blocked", "mode=CSV"], capture_output=True
        )

    with (
        patch("pathlib.Path.exists", return_value=True),
        patch("builtins.open", mock_open(read_data="data")),
        patch("select.select", return_value=[None, None, None]),
        patch("waves._abaqus.odb_extract.which", return_value=""),
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
        patch("waves._abaqus.odb_extract.which", return_value="abaqus"),
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
        patch("waves._abaqus.odb_extract.which", return_value="abaqus"),
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
odb_report_arguments = { #odb_report_args,                      input_file,        job_name  # noqa: E261,E262
    "1 spaces":             (        None,    "/some/path with/spaces.txt", "/no/spaces.csv"),  # noqa: E241,E201
    "2 spaces":             (        None,    "/some/path with/spaces.txt", "/some more/spaces.csv"),  # noqa: E241,E201
    "no spaces":            (        None, "/some/path/without/spaces.txt", "/no/spaces.csv"),         # noqa: E241,E201
    "Exists 1 spaces":      ( "arg1=val1",    "/some/path with/spaces.txt", "/no/spaces.csv"),         # noqa: E241,E201
    "Exists 2 spaces":      ( "arg1=val1",    "/some/path with/spaces.txt", "/some more/spaces.csv"),  # noqa: E241,E201
    "Exists no spaces":     ( "arg1=val1", "/some/path/without/spaces.txt", "/no/spaces.csv"),         # noqa: E241,E201
    "Exists 1 spaces odb":  (  "odb=val1",    "/some/path with/spaces.txt", "/no/spaces.csv"),         # noqa: E241,E201
    "Exists 2 spaces odb":  (  "odb=val1",    "/some/path with/spaces.txt", "/some more/spaces.csv"),  # noqa: E241,E201
    "Exists no spaces odb": (  "odb=val1", "/some/path/without/spaces.txt", "/no/spaces.csv"),         # noqa: E241,E201
}
# fmt: on


@pytest.mark.parametrize(
    "odb_report_args, input_file, job_name", odb_report_arguments.values(), ids=odb_report_arguments.keys()
)
def test_abaqus_journal(odb_report_args, input_file, job_name):
    new_odb_report_args = odb_extract.get_odb_report_args(odb_report_args, Path(input_file), Path(job_name), True)
    expected_odb = new_odb_report_args.split("odb=")[-1].split("arg1=")[0].split("all")[0].strip()
    assert Path(expected_odb) == _quote_spaces_in_path(input_file)
    expected_job_name = new_odb_report_args.split("job=")[-1].split("odb=")[0].strip()
    assert Path(expected_job_name) == _quote_spaces_in_path(Path(job_name).with_suffix(""))
