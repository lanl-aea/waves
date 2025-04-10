from __future__ import annotations
import pathlib
import typing
import subprocess
import functools
import re
import itertools

import numpy
import xarray
import pandas
import click
import matplotlib.pyplot
from matplotlib.backends.backend_pdf import PdfPages


def extract_set_name(
    input_file: pathlib.Path,
    regex: str = r"parameter_set[0-9]+|set[0-9]+",
    index: int = -1,
) -> str:
    """Extract a set name from a file path by regular expression.

    If more than one match is found, use the index. Defaults to right most set name pattern in the file path (closest to
    basename).

    Parameters
    ----------
    input_file
        pathlib.Path object to search for a set name
    regex
        the regular expression to use when searching for a set name
    index
        the index of the preferred set name if more than one is found. Expected to be ``0`` for the first (left most)
        and ``-1`` for the last (right most). Other indices are accepted, but will result in exceptions if the provided
        path does not have a matching number of set name patterns.

    :raises RuntimeError: if no set name pattern is found
    """
    matches = re.findall(regex, str(input_file))
    if len(matches) > 0:
        return matches[index]
    else:
        raise RuntimeError(
            f"Could not extract set name from '{input_file}' with regex '{regex}'"
        )


def create_qoi(
    name: str,
    calculated: float = numpy.nan,
    expected: float = numpy.nan,
    lower_rtol: float = numpy.nan,
    upper_rtol: float = numpy.nan,
    lower_atol: float = numpy.nan,
    upper_atol: float = numpy.nan,
    lower_limit: float = numpy.nan,
    upper_limit: float = numpy.nan,
    **attrs,
) -> xarray.DataArray:
    """Create a QOI DataArray.

    If you create a QOI with calculated values, and a separate QOI with only expected values, you can combine them with
    ``xarray.merge([calculated, expected])``.

    Parameters
    ----------
    name
        QOI name
    calculated, expected
        Calculated and expected QOI values, respectively.
    lower_rtol, lower_atol, lower_limit, upper_rtol, upper_atol, upper_limit
        Tolerance values which set the acceptable range of calculated QOI values.
        Any or all of these tolerances may be specified.
        If ``lower_rtol`` or ``upper_rtol`` are specified, ``expected`` must also be specified.
        The calculated QOI value will be considered within tolerance if it is greater than or equal to
        ``max((lower_limit, expected + lower_atol, expected + abs(expected * lower_rtol))``
        and less than or equal to
        ``min((upper_limit, expected + upper_atol, expected + abs(expected * upper_rtol))``.
        Unspecified tolerances are not considered in the tolerance check.
        If no tolerances are specified, the calculated QOI will always be considered within tolerance.
    **attrs
        Attributes to associate with the QOI.
        Recommended attributes are: group, units, description, long_name, commit.
        Together ``name`` and ``attrs['group']`` should distinguish each QOI from every other QOI in the Mod/Sim
        repository.
        In other words, ``group`` should be as specific as possible, e.g., "Local Test XYZ Assembly Preload" instead of
        just "Preload".
    """
    if (
        numpy.isnan(expected)
        & numpy.isfinite([lower_rtol, upper_rtol, lower_atol, upper_atol]).any()
    ):
        raise ValueError(
            "Relative and absolute tolerances were specified without an expected value."
        )
    upper_candidates = [
        upper_limit,
        expected + upper_atol,
        expected + abs(expected * upper_rtol),
    ]
    upper = min(
        [candidate for candidate in upper_candidates if not numpy.isnan(candidate)],
        default=numpy.nan,
    )
    lower_candidates = [
        lower_limit,
        expected - lower_atol,
        expected - abs(expected * lower_rtol),
    ]
    lower = max(
        [candidate for candidate in lower_candidates if not numpy.isnan(candidate)],
        default=numpy.nan,
    )
    if lower > upper:
        raise ValueError(f"Upper limit is lower than the lower limit.")
    return xarray.DataArray(
        data=[calculated, expected, lower, upper],
        coords={"value_type": ["calculated", "expected", "lower_limit", "upper_limit"]},
        name=name,
        attrs=attrs,
    )


def create_qoi_set(qois: typing.Iterable[xarray.DataArray]) -> xarray.Dataset:
    """Create a QOI dataset containing multiple QOIs from a single simulation.

    This operation combines multiple QOIs (``xarray.DataArray``s) into a single "QOI Set" (``xarray.Dataset``) using
    ``xarray.merge()``.
    This results in an ``xarray.Dataset`` with each QOI represented as a separate data variable.
    Each QOI must have a unique name.
    If multiple QOIs share a dimension name then that dimension will be merged across QOIs.
    This can lead to sparse Datasets if the dimension's index values differ.
    To avoid this, use unique dimension names or avoid combining those QOIs into the same QOI set.
    No attributes will be set at the top-level Dataset, but QOI attributes will be preserved at the data variable
    level.

    Parameters
    ----------
    qois
        Sequence of QOIs.

    Returns
    -------
    qoi_set
        QOI Set containing each QOI as a separate data variable.
    """
    qoi_set = xarray.merge(qois, combine_attrs="drop_conflicts")
    # Keep all attributes at the data variable level
    qoi_set.attrs = dict()
    return qoi_set


def create_qoi_study(
    qois: typing.Iterable[xarray.DataArray], parameter_study: xarray.Dataset = None
) -> xarray.Dataset:
    """Create a QOI Dataset spanning multiple simulations.

    This function combines multiple QOIs (``xarray.DataArray``s) into a single "QOI Study" (``xarray.Dataset``) using
    ``xarray.merge()``.
    Each QOI must have an attribute named "group", which will be added as a new dimension to the resulting Dataset.
    QOIs with the same name will be merged into a single data variable with the added "group" dimension.
    This requires that all QOIs with the same name have the same dimensions and attributes.
    If the QOIs are collected as part of a parameter study, it is useful to associate the input parameter values with
    the parameter set names.
    To do so, include the parameter set name in the "group" attribute (e.g. "Assembly XYZ Preload parameter_set0") and
    pass the parameter study definition (an ``xarray.Dataset``) as ``parameter_study``.

    Parameters
    ----------
    qois
        Sequence of QOIs.
    parameter_study
        Parameter study definition. The indexed dimension should be "set_name". The data variables and coordinates
        should be parameter values.
    """
    # Move "group" from attribute to dimension for each DataArray, and merge
    try:
        qoi_study = xarray.merge(
            [qoi.expand_dims(group=[qoi.attrs["group"]]) for qoi in qois],
            combine_attrs="drop_conflicts",
        )
    except KeyError:
        raise RuntimeError(
            "Each DataArray in `qois` must have an attribute named 'group'."
        )
    # Merge in parameter study definition
    if parameter_study:
        # Use "group" attribute to determine set names
        try:
            set_names = [extract_set_name(group) for group in qoi_study.group]
            qoi_study = qoi_study.assign_coords(
                set_name=("group", set_names)
            ).swap_dims(group="set_name")
        except RuntimeError:
            # Groups may not be valid set names.
            raise RuntimeError(
                "Could not determine a set name based on the QOI's 'group' attribute."
                "Unable to merge with parameter study."
            )
        # Convert parameter study variables to coordinates
        parameter_study = parameter_study.set_coords(parameter_study)
        qoi_study = xarray.merge(
            (qoi_study, parameter_study), combine_attrs="drop_conflicts"
        )
    return qoi_study


def _qoi_group(qoi):
    """Function for sorting and grouping QOIs."""
    return qoi.attrs["group"]


def create_qoi_archive(qois: typing.Iterable[xarray.DataArray]) -> xarray.DataTree:
    """Create a QOI DataTree spanning multiple simulations and git commits.

    Parameters
    ----------
    qois
        Sequence of QOIs. Each QOI must have a "commit" and "group" attribute.

    Returns
    -------
    qoi_archive
        xarray.DataTree
    """
    dt = xarray.DataTree()
    # Creates a group for each "group" attribute
    for group, qois in itertools.groupby(sorted(qois, key=_qoi_group), key=_qoi_group):
        # Move "commit" from attribute to dimension for each DataArray and merge to Dataset
        ds = xarray.merge((qoi.expand_dims(commit=[qoi.attrs["commit"]]) for qoi in qois), combine_attrs="drop_conflicts")
        # Add dataset as a node in the DataTree
        dt[group] = ds
    return dt


def merge_qoi_archives(qoi_archives: typing.Iterable[xarray.DataTree]) -> xarray.DataTree:
    """Merge QOI archives by concatenating leaf datasets along the "commit" dimension.

    Parameters
    ----------
    qoi_archives
        QOI archives. Each leaf dataset must have a "commit" dimension.

    Returns
    -------
    merged_archive
        Merged QOI archive.

    Note
    ----
    Technically this does not preserve the original DataTree structure. It creates a new structure based on the "group"
    attribute of each QOI.
    """
    leaves = [qoi.ds for archive in qoi_archives for qoi in archive.leaves]
    dt = xarray.DataTree()
    # Create a group for each "group" attribute
    for group, qois in itertools.groupby(sorted(leaves, key=_qoi_group), key=_qoi_group):
        # Merge dataset as a node in the DataTree
        dt[group] = xarray.merge(qois)
    return dt


def read_qoi_set(from_file: pathlib.Path) -> xarray.Dataset:
    """Create a QOI Dataset from a CSV or H5 file.

    Parameters
    ----------
    from_file
        File containing QOIs. Either a ``.csv`` or ``.h5`` file.

        ``.h5`` files will be read with ``xarray.open_dataset(from_file)``.

        ``.csv`` files will be read using ``pandas.read_csv(from_file)``.

        A QOI will be created for each row in the file using ``create_qoi(**kwargs)``.
        ``kwargs`` keys are column names and ``kwargs`` values are the row entries.
        Empty entries (or anything read as ``nan``) will not be included in ``kwargs``.
        All QOIs will be merged into a single ``xarray.Dataset`` using ``create_qoi_set()``.
    """
    if not isinstance(from_file, pathlib.Path):
        from_file = pathlib.Path(from_file)
    if from_file.suffix.lower() == ".csv":
        df = pandas.read_csv(from_file)
        # Empty entries in the CSV end up as NaN in the DataFrame.
        # Drop NaNs so they aren't passed as kwargs to `create_qoi()`
        qoi_kwargs = [row.dropna().to_dict() for idx, row in df.iterrows()]
        return create_qoi_set([create_qoi(**kwargs) for kwargs in qoi_kwargs])
    if from_file.suffix.lower() == ".h5":
        return xarray.open_dataset(from_file)


def add_tolerance_attribute(qoi_set: xarray.Dataset) -> None:
    """Adds a "within_tolerance" attribute to each QOI in a QOI Dataset in place."""
    for qoi in qoi_set.data_vars.values():
        lower_limit = qoi.sel(value_type="lower_limit").fillna(-numpy.inf)
        upper_limit = qoi.sel(value_type="upper_limit").fillna(numpy.inf)
        calculated = qoi.sel(value_type="calculated")
        # netcdf4 doesn't support bool, so make it an int
        qoi.attrs["within_tolerance"] = int(
            ((calculated >= lower_limit) & (calculated <= upper_limit)).all().item()
        )


def write_qoi_set_to_csv(qoi_set: xarray.Dataset, output: pathlib.Path) -> None:
    """Writes a QOI Dataset to a CSV file.

    Parameters
    ----------
    qoi_set
        QOI set.
    output
        Output CSV file.
    """
    df = qoi_set.to_dataarray("name").to_pandas()
    # Convert attributes to data variables so they end up as columns in the CSV
    attrs = pandas.DataFrame.from_dict(
        {qoi: qoi_set[qoi].attrs for qoi in qoi_set}, orient="index"
    )
    attrs.index.name = "name"
    pandas.concat((df, attrs), axis="columns").to_csv(output)


def plot_qoi_tolerance_check(qoi, ax):
    """Plot QOI tolerance check."""
    if "value_type" not in qoi.dims:
        ax.clear()
        ax.annotate(f"Incorrect QOI format for {qoi.name}.", (0.0, 0.0))
        ax.axis("off")
        return
    qoi_dim = len(qoi.squeeze().dims)  # Count includes the "value_type" dim
    if qoi_dim == 1:  # Scalar QOI
        try:
            calculated = qoi.sel(value_type="calculated").item()
        except KeyError:
            calculated = numpy.nan
        try:
            within_tolerance = qoi.attrs["within_tolerance"]
        except KeyError:
            within_tolerance = 1
        try:
            lower_limit = qoi.sel(value_type="lower_limit").item()
        except KeyError:
            lower_limit = -numpy.inf
        try:
            upper_limit = qoi.sel(value_type="upper_limit").item()
        except KeyError:
            upper_limit = numpy.inf
        try:
            expected = qoi.sel(value_type="expected").item()
        except KeyError:
            expected = numpy.nan
        name = _get_plotting_name(qoi)
        plot_scalar_tolerance_check(
            name, calculated, expected, lower_limit, upper_limit, within_tolerance, ax
        )


def plot_scalar_tolerance_check(
    name, calculated, expected, lower_limit, upper_limit, within_tolerance, ax
):
    """Plots a tolerance check for a scalar QOI DataArray."""
    # TODO: draw arrow if bar is clipped by xmin, xmax
    try:
        # Bar color is always green if within tolerance, red otherwise
        bar_color = "green" if within_tolerance else "red"
        # If tolerance on both sides, within_tolerance is good, out of tolerance is bad
        if numpy.isfinite([lower_limit, upper_limit]).all():
            lower_line = lower_limit
            upper_line = upper_limit
            colors = ["black", "black"]
        # If unbounded upper, assume convergence to 0 is good
        elif not numpy.isfinite(upper_limit):
            lower_line = lower_limit
            upper_line = 0.0
            colors = ["black", "blue"]
        # If unbounded lower, assume convergence to 0 is good
        elif not numpy.isfinite(lower_limit):
            lower_line = 0.0
            upper_line = upper_limit
            colors = ["blue", "black"]

        # Draw vertical lines at lower and upper tolerance limits
        container = ax.barh(
            0.0, width=(calculated - expected), left=expected, color=bar_color
        )
        ax.vlines([lower_line, upper_line], *ax.get_ylim(), colors=colors)
        ax.vlines([expected], *ax.get_ylim(), colors="black", linestyle="dashed")

        # Turn ticks and labels off, except for tolerances and expected value
        ax.tick_params(axis="x", bottom=False, pad=-1, labelsize=8)
        ax.tick_params(axis="y", left=False, labelleft=False)
        ax.set_xticks([lower_line, expected, upper_line])

        # Turn off plot borders
        ax.spines["bottom"].set_visible(False)
        ax.spines["top"].set_visible(False)
        ax.spines["left"].set_visible(False)
        ax.spines["right"].set_visible(False)

        # Extend plot past upper and lower tolerances
        tolerance_width = upper_line - lower_line
        xmin = lower_line - 0.25 * tolerance_width
        xmax = upper_line + 0.25 * tolerance_width
        ax.set_xlim([xmin, xmax])

        # Add calculated value as annotation above bar
        ax.annotate(
            f"{calculated:.3e}",
            xy=(calculated, 0.555),
            xytext=(numpy.clip(calculated, xmin, xmax), 0.55),
            annotation_clip=False,
            ha="center",
            fontsize=8,
        )

    # ValueError could mean calculated value is inf
    except ValueError:
        ax.clear()
        ax.annotate("Failed to plot.", (0.0, 0.0))
        ax.axis("off")

    # Add QOI name and values to left of plot
    if not within_tolerance:
        color = "red"
        fontweight = "bold"
    else:
        color = "black"
        fontweight = "normal"
    ax.annotate(
        text=(
            f"{name}\n"
            f" min: {lower_limit:.2e},"
            f" max: {upper_limit:.2e},"
            f" exp: {expected:.2e},"
            f" calc: {calculated:.2e}"
        ),
        xy=(-0.05, 0.5),
        textcoords="axes fraction",
        annotation_clip=False,
        ha="right",
        va="center",
        fontweight=fontweight,
        color=color,
        fontsize=8,
    )


def write_qoi_report(qoi_archive, output, plots_per_page=16):
    """Write a QOI report to a PDF.

    QOI archive must contain QOIs with only the "value_type" dimension. Multi-dimensional QOIs and QOI values across
    multiple commits cannot be plotted using this function.
    """
    with PdfPages(output) as pdf:
        for qoi_group in qoi_archive.leaves:
            for plot_num, qoi in enumerate(qoi_group.ds.data_vars.values()):
                ax_num = (
                    plot_num % plots_per_page
                )  # ax_num goes from 0 to (plots_per_page - 1)
                if ax_num == 0:  # starting new page
                    open_figure = True
                    fig, axes = matplotlib.pyplot.subplots(  # create a new figure for a new page
                        plots_per_page,
                        figsize=(8.5, 11),
                        gridspec_kw=dict(
                            left=0.6,  # plot on right half of page because text will go on left side
                            right=0.9,  # leave margin on right edge
                            top=(
                                1.0 - 1.0 / plots_per_page
                            ),  # top margin equal to single plot height
                            bottom=(
                                0.5 / plots_per_page
                            ),  # bottom margin equal to half of single plot height
                            hspace=1.0,
                        ),
                    )
                fig.suptitle(qoi_group.name)
                plot_qoi_tolerance_check(qoi, axes[ax_num])
                if ax_num == plots_per_page - 1:  # ending a page
                    pdf.savefig()  # save current figure to a page
                    matplotlib.pyplot.close()
                    open_figure = False
            if open_figure:  # If a figure is still open (hasn't been saved to a page)
                for ax in axes[ax_num + 1 :]:  # Clear remaining empty plots on the page
                    ax.clear()
                    ax.axis("off")
                pdf.savefig()
                matplotlib.pyplot.close()


def _get_plotting_name(qoi):
    if "long_name" in qoi.attrs:
        name = qoi.attrs["long_name"]
    elif "standard_name" in qoi.attrs:
        name = qoi.attrs["standard_name"]
    else:
        name = qoi.name
    if "units" in qoi.attrs:
        name = f"{name} [{qoi.attrs['units']}]"
    return name


def plot_scalar_qoi_history(qoi, ax, date_min, date_max):
    """Plot Scalar QOI history."""
    name = _get_plotting_name(qoi)
    group = qoi.attrs["group"]
    ax.scatter(qoi.date, qoi.sel(value_type="calculated"))
    ax.plot(qoi.date, qoi.sel(value_type="lower_limit"), "--")
    ax.plot(qoi.date, qoi.sel(value_type="upper_limit"), "--")
    ax.set_xlim((date_min, date_max))
    ax.set_title(name)


def qoi_history_report(qoi_archive, output, plots_per_page=8):
    """Plot history of QOI values from QOI archive"""
    qoi_archive = qoi_archive.map_over_datasets(_add_commit_date)
    qoi_archive = qoi_archive.map_over_datasets(_sort_by_commit_date)
    open_figure = False
    date_min = min(node.ds.date.min() for node in qoi_archive.leaves)
    date_max = max(node.ds.date.max() for node in qoi_archive.leaves)
    with PdfPages(output) as pdf:
        for qoi_group in qoi_archive.leaves:
            plot_num = 0
            for qoi in qoi_group.ds.data_vars.values():
                if (
                    qoi.where(numpy.isfinite(qoi)).dropna("commit", how="all").size == 0
                ):  # Would be an empty plot
                    continue  # Don't increment plot_num
                ax_num = (
                    plot_num % plots_per_page
                )  # ax_num goes from 0 to (plots_per_page - 1)
                if ax_num == 0:  # Starting new page
                    open_figure = True
                    fig, axes = matplotlib.pyplot.subplots(  # Create a new figure for a new page
                        plots_per_page,
                        figsize=(8.5, 11),
                        gridspec_kw=dict(
                            left=0.1,  # leave margin on left edge
                            right=0.9,  # leave margin on right edge
                            top=(
                                1.0 - 0.5 / plots_per_page
                            ),  # top margin equal to half of single plot height
                            bottom=(
                                0.5 / plots_per_page
                            ),  # bottom margin equal to half of single plot height
                            hspace=1.0,
                        ),
                    )
                    fig.suptitle(qoi_group.name, fontweight="bold")
                plot_scalar_qoi_history(qoi, axes[ax_num], date_min, date_max)
                if ax_num == plots_per_page - 1:  # Ending a page
                    pdf.savefig()  # save current figure to a page
                    matplotlib.pyplot.close()
                    open_figure = False
                plot_num += 1
            if open_figure:  # If a figure is still open (hasn't been saved to a page)
                for ax in axes[ax_num + 1 :]:
                    ax.clear()
                    ax.axis("off")
                pdf.savefig()
                matplotlib.pyplot.close()


@functools.cache
def _get_commit_date(commit):
    return pandas.to_datetime(
        subprocess.run(
            ["git", "show", "--no-patch", "--no-notes", "--pretty='%cs'", commit],
            capture_output=True,
        )
        .stdout.decode()
        .strip()
    )


def _add_commit_date(ds):
    try:
        return ds.assign_coords(
            date=("commit", (_get_commit_date(commit) for commit in  ds["commit"]))
        )
    except KeyError:
        return ds


def _sort_by_commit_date(ds):
    try:
        return ds.sortby("date")
    except KeyError:
        return ds


@click.group()
def cli():
    pass


@cli.command()
@click.option(
    "--calculated",
    help="Calculated value CSV",
    type=click.Path(exists=True, path_type=pathlib.Path),
)
@click.option(
    "--expected",
    help="Expected value CSV",
    type=click.Path(exists=True, path_type=pathlib.Path),
)
def accept(calculated, expected):
    """Update expected QOI values to match the currently calculated values."""
    qoi_set = read_qoi_set(calculated)
    calculated_df = qoi_set.to_dataarray("name").to_pandas()
    # Use str data type to avoid all numerical rounding
    expected_df = pandas.read_csv(expected, header=0, index_col=0, dtype=str)
    # Add/drop expected QOIs to match calculated QOIs
    new = expected_df.reindex(calculated_df.index)
    # Update expected values
    new["expected"] = calculated_df["calculated"]
    # Case insensitive sort
    new.sort_index(key=lambda name: name.str.lower()).to_csv(expected)
    return


@cli.command()
@click.option(
    "--diff",
    help="Calculated vs expected diff CSV file",
    type=click.Path(path_type=pathlib.Path),
)
def check(diff):
    """Check results of calculated vs expected QOI comparison"""
    qoi_set = read_qoi_set(diff)
    if qoi_set.filter_by_attrs(within_tolerance=0):
        raise ValueError(f"Not all QOIs are within tolerance. See {diff}.")


@cli.command()
@click.option(
    "--expected", help="Expected values", type=click.Path(exists=True, path_type=pathlib.Path)
)
@click.option(
    "--calculated",
    help="Calculated values",
    type=click.Path(exists=True, path_type=pathlib.Path),
)
@click.option(
    "--output", help="Difference from expected values", type=click.Path(path_type=pathlib.Path)
)
def diff(calculated, expected, output):
    """Compare calculated QOIs to expected values."""
    qoi_set = xarray.merge((read_qoi_set(calculated), read_qoi_set(expected)))
    add_tolerance_attribute(qoi_set)
    write_qoi_set_to_csv(qoi_set, output)


@cli.command()
@click.option(
    "--parameter-study-file",
    help="Path to parameter study definition file",
    type=click.Path(exists=True, path_type=pathlib.Path),
)
@click.option(
    "--output-file", help="post-processing output file", type=click.Path(path_type=pathlib.Path)
)
@click.argument(
    "qoi-set-files",
    required=True,
    nargs=-1,
    type=click.Path(exists=True, path_type=pathlib.Path),
)
def aggregate(parameter_study_file, output_file, qoi_set_files):
    """Aggregate QOIs across multiple simulations, e.g. across sets in a parameter study."""
    qoi_sets = (read_qoi_set(qoi_set_file) for qoi_set_file in qoi_set_files)
    qois = (qoi for qoi_set in qoi_sets for qoi in qoi_set.values())
    parameter_study = xarray.open_dataset(parameter_study_file)
    qoi_study = create_qoi_study(qois, parameter_study=parameter_study)
    qoi_study.to_netcdf(output_file)


@cli.command()
@click.option("--output", help="Report file", type=click.Path())
@click.argument(
    "qoi-archive-h5",
    required=True,
    nargs=1,
    type=click.Path(exists=True, path_type=pathlib.Path),
)
def report(output, qoi_archive_h5):
    """Generate a QOI test report."""
    qoi_archive = xarray.open_datatree(qoi_archive_h5, engine="h5netcdf")
    write_qoi_report(qoi_archive, output)


@cli.command()
@click.option(
    "--output", help="output file", default="QOI_history.pdf", type=click.Path()
)
@click.argument(
    "qoi-archive-h5",
    required=True,
    nargs=-1,
    type=click.Path(exists=True, path_type=pathlib.Path),
)
def plot_archive(output, qoi_archive_h5):
    """Plot QOI values over the Mod/Sim history."""
    qoi_archive = merge_qoi_archives((xarray.open_datatree(f) for f in qoi_archive_h5))
    qoi_history_report(qoi_archive, output)


@cli.command()
@click.option("--output", help="Report file", type=click.Path())
@click.option(
    "--commit",
    help="override existing QOI 'commit' attributes with this commit hash.",
    type=str,
    default="",
)
@click.argument(
    "qoi-set-files",
    required=True,
    nargs=-1,
    type=click.Path(exists=True, path_type=pathlib.Path),
)
def archive(output, commit, qoi_set_files):
    """Archive QOI sets from a single commit to an H5 file."""
    qoi_sets = (read_qoi_set(qoi_set_file) for qoi_set_file in qoi_set_files)
    qois = (qoi for qoi_set in qoi_sets for qoi in qoi_set.values())
    if commit:
        qois = (qoi.assign_attrs(commit=commit) for qoi in qois)
    create_qoi_archive(qois).to_netcdf(output, engine="h5netcdf")


if __name__ == "__main__":
    cli()
