import argparse
import pathlib

from waves import qoi


_exclude_from_namespace = set(globals().keys())


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(add_help=False)
    qoi_subparsers = parser.add_subparsers(
        title="QOI subcommands",
        metavar="{qoi_subcommand}",
        dest="qoi_subcommand",
    )
    qoi_subparsers.add_parser(
        "accept",
        help="Update expected values to match calculated values",
        parents=[get_accept_parser()],
    )
    qoi_subparsers.add_parser(
        "diff",
        help="Compare expected values to calculated values",
        parents=[get_diff_parser()],
    )
    qoi_subparsers.add_parser(
        "check",
        help="Raise error if expected values do not match calculated values",
        parents=[get_check_parser()],
    )
    qoi_subparsers.add_parser(
        "aggregate",
        help="Combine parameter study QOIs",
        parents=[get_aggregate_parser()],
    )
    qoi_subparsers.add_parser(
        "report",
        help="Generate QOI tolerance check report",
        parents=[get_report_parser()],
    )
    qoi_subparsers.add_parser(
        "archive",
        help="Combine QOIs across multiple simulations",
        parents=[get_archive_parser()],
    )
    qoi_subparsers.add_parser(
        "plot-archive",
        help="Generate QOI history report",
        parents=[get_plot_archive_parser()],
    )
    return parser


def main(args, parser) -> None:
    if args.qoi_subcommand == "accept":
        qoi._accept(args.calculated, args.expected)
    elif args.qoi_subcommand == "diff":
        qoi._diff(args.calculated, args.expected, args.output)
    elif args.qoi_subcommand == "check":
        qoi._check(args.diff)
    elif args.qoi_subcommand == "aggregate":
        qoi._aggregate(args.parameter_study_file, args.output_file, args.QOI_SET_FILE)
    elif args.qoi_subcommand == "report":
        qoi._report(args.output, args.QOI_ARCHIVE_H5)
    elif args.qoi_subcommand == "archive":
        qoi._archive(args.output, args.version, args.date, args.QOI_SET_FILE)
    elif args.qoi_subcommand == "plot-archive":
        qoi._plot_archive(args.output, args.QOI_ARCHIVE_H5)
    else:
        parser.print_help()


def get_accept_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        "--calculated",
        help="Calculated QOI file",
        type=pathlib.Path,
    )
    parser.add_argument(
        "--expected",
        help="Expected QOI file",
        type=pathlib.Path,
    )
    return parser


def get_check_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        "--diff",
        help="Calculated vs expected diff CSV file",
        type=pathlib.Path,
    )
    return parser


def get_diff_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        "--expected",
        help="Expected values",
        type=pathlib.Path,
    )
    parser.add_argument(
        "--calculated",
        help="Calculated values",
        type=pathlib.Path,
    )
    parser.add_argument(
        "--output",
        help="Difference from expected values",
        type=pathlib.Path,
    )
    return parser


def get_aggregate_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        "--parameter-study-file",
        help="Path to parameter study definition file",
        type=pathlib.Path,
    )
    parser.add_argument(
        "--output-file",
        help="post-processing output file",
        type=pathlib.Path,
    )
    parser.add_argument(
        "QOI_SET_FILE",
        nargs="+",
        type=pathlib.Path,
    )
    return parser


def get_report_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        "--output",
        help="Report file",
        type=pathlib.Path,
    )
    parser.add_argument(
        "QOI_ARCHIVE_H5",
        type=pathlib.Path,
    )
    return parser


def get_plot_archive_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        "--output",
        help="output file",
        default="QOI_history.pdf",
        type=pathlib.Path,
    )
    parser.add_argument(
        "QOI_ARCHIVE_H5",
        nargs="+",
        type=pathlib.Path,
    )
    return parser


def get_archive_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        "--output",
        help="Report file",
        type=pathlib.Path,
    )
    parser.add_argument(
        "--version",
        help="override existing QOI 'version' attributes with this text (e.g. a git commit hash).",
        type=str,
        default="",
    )
    parser.add_argument(
        "--date",
        help="override existing QOI 'date' attributes with this text (e.g. a git commit date).",
        type=str,
        default="",
    )
    parser.add_argument(
        "QOI_SET_FILE",
        nargs="+",
        type=pathlib.Path,
    )
    return parser


# Limit help() and 'from module import *' behavior to the module's public API
_module_objects = set(globals().keys()) - _exclude_from_namespace
__all__ = [name for name in _module_objects if not name.startswith("_")]
