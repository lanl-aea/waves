import pathlib
import typing
import subprocess
import functools
import itertools

import numpy
import xarray
import pandas
import matplotlib.pyplot
from matplotlib.backends.backend_pdf import PdfPages


_exclude_from_namespace = set(globals().keys())


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

    :param name: QOI name
    :param calculated, expected: Calculated and expected QOI values, respectively.
    :param lower_rtol, lower_atol, lower_limit, upper_rtol, upper_atol, upper_limit: Tolerance values which set the
        acceptable range of calculated QOI values.
        Any or all of these tolerances may be specified.
        If ``lower_rtol`` or ``upper_rtol`` are specified, ``expected`` must also be specified.
        The calculated QOI value will be considered within tolerance if it is greater than or equal to
        ``max((lower_limit, expected + lower_atol, expected + abs(expected * lower_rtol))``
        and less than or equal to
        ``min((upper_limit, expected + upper_atol, expected + abs(expected * upper_rtol))``.
        Unspecified tolerances are not considered in the tolerance check.
        If no tolerances are specified, the calculated QOI will always be considered within tolerance.
    :param **attrs: Attributes to associate with the QOI.
        Recommended attributes are: group, units, description, long_name, version.
        Together ``name`` and ``attrs['group']`` should distinguish each QOI from every other QOI in the Mod/Sim
        repository.
        In other words, ``group`` should be as specific as possible, e.g., "Local Test XYZ Assembly Preload" instead of
        just "Preload".

    :returns: QOI
    """
    if numpy.isnan(expected) & numpy.isfinite([lower_rtol, upper_rtol, lower_atol, upper_atol]).any():
        raise ValueError("Relative and absolute tolerances were specified without an expected value.")
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


def create_qoi_set(qois: typing.List[xarray.DataArray]) -> xarray.Dataset:
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

    :param qois: Sequence of QOIs.

    :returns: QOI Set containing each QOI as a separate data variable.
    """
    qoi_set = xarray.merge(qois, combine_attrs="drop_conflicts")
    # Keep all attributes at the data variable level
    qoi_set.attrs = dict()
    return qoi_set


def _create_qoi_study(qois: typing.List[xarray.DataArray], parameter_study: xarray.Dataset = None) -> xarray.Dataset:
    """Create a QOI Dataset spanning multiple simulations.

    This function combines multiple QOIs (``xarray.DataArray``s) into a single "QOI Study" (``xarray.Dataset``) using
    ``xarray.merge()``.
    Each QOI must have an attribute named "set_name", which will be added as a new dimension to the resulting Dataset.
    QOIs with the same name will be merged into a single data variable with the added "set_name" dimension.
    This requires that all QOIs with the same name have the same dimensions and attributes.
    If the QOIs are collected as part of a parameter study, it is useful to associate the input parameter values with
    the parameter set names.
    To do so, pass the parameter study definition (an ``xarray.Dataset``) as ``parameter_study``.

    :param qois: Sequence of QOIs.
    :param parameter_study: Parameter study definition. The indexed dimension should be "set_name". The data variables
        and coordinates should be parameter values.

    :returns: QOI study
    """
    # Move "group" from attribute to dimension for each DataArray, and merge
    try:
        qoi_study = xarray.merge(
            [qoi.expand_dims(set_name=[qoi.attrs["set_name"]]) for qoi in qois],
            combine_attrs="drop_conflicts",
        )
    except KeyError:
        raise RuntimeError("Each DataArray in `qois` must have an attribute named 'set_name'.")
    # Merge in parameter study definition
    if parameter_study:
        # Convert parameter study variables to coordinates
        parameter_study = parameter_study.set_coords(parameter_study)
        qoi_study = xarray.merge((qoi_study, parameter_study), combine_attrs="drop_conflicts")
    return qoi_study


def _qoi_group(qoi):
    """Return "group" attribute of a QOI (xarray.Dataset)."""
    return qoi.attrs["group"]


def _create_qoi_archive(qois: typing.List[xarray.DataArray]) -> xarray.DataTree:
    """Create a QOI DataTree spanning multiple simulations and versions.

    :param qois: Sequence of QOIs. Each QOI must have a "version" and "group" attribute.

    :returns: QOI archive
    """
    dt = xarray.DataTree()
    # Creates a group for each "group" attribute
    for group, qois in itertools.groupby(sorted(qois, key=_qoi_group), key=_qoi_group):
        # Move "version" from attribute to dimension for each DataArray and merge to Dataset
        qois = [qoi.expand_dims(version=[qoi.attrs["version"]]) for qoi in qois]
        # Try to add date as a coordinate if available
        try:
            qois = [qoi.assign_coords(date=("version", [qoi.attrs["date"]])) for qoi in qois]
        except KeyError:
            pass  # date coordinate is not needed
        ds = xarray.merge(qois, combine_attrs="drop_conflicts")
        # Add dataset as a node in the DataTree
        dt[group] = ds
    return dt


def _merge_qoi_archives(qoi_archives: typing.List[xarray.DataTree]) -> xarray.DataTree:
    """Merge QOI archives by concatenating leaf datasets along the "version" dimension.

    :param qoi_archives: QOI archives. Each leaf dataset must have a "version" dimension.
    :returns: Merged QOI archive.

    .. note::

        Technically this does not preserve the original DataTree structure. It creates a new structure based on the
        "group" attribute of each QOI.
    """
    leaves = [qoi.ds for archive in qoi_archives for qoi in archive.leaves]
    dt = xarray.DataTree()
    # Create a group for each "group" attribute
    for group, qois in itertools.groupby(sorted(leaves, key=_qoi_group), key=_qoi_group):
        # Merge dataset as a node in the DataTree
        dt[group] = xarray.merge(qois)
    return dt


def _read_qoi_set(from_file: pathlib.Path) -> xarray.Dataset:
    """Create a QOI Dataset from a CSV or H5 file.

    :param from_file: File containing QOIs. Either a ``.csv`` or ``.h5`` file.

        ``.h5`` files will be read with ``xarray.open_dataset(from_file)``.

        ``.csv`` files will be read using ``pandas.read_csv(from_file)``.

        A QOI will be created for each row in the file using ``create_qoi(**kwargs)``.
        ``kwargs`` keys are column names and ``kwargs`` values are the row entries.
        Empty entries (or anything read as ``nan``) will not be included in ``kwargs``.
        All QOIs will be merged into a single ``xarray.Dataset`` using ``create_qoi_set()``.

    :returns: QOI set
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


def _add_tolerance_attribute(qoi_set: xarray.Dataset) -> None:
    """Adds a "within_tolerance" attribute to each QOI in a QOI Dataset in place.

    :param qoi_set: QOI set.
    """
    for qoi in qoi_set.data_vars.values():
        lower_limit = qoi.sel(value_type="lower_limit").fillna(-numpy.inf)
        upper_limit = qoi.sel(value_type="upper_limit").fillna(numpy.inf)
        calculated = qoi.sel(value_type="calculated")
        # netcdf4 doesn't support bool, so make it an int
        qoi.attrs["within_tolerance"] = int(((calculated >= lower_limit) & (calculated <= upper_limit)).all().item())


def _write_qoi_set_to_csv(qoi_set: xarray.Dataset, output: pathlib.Path) -> None:
    """Writes a QOI Dataset to a CSV file.

    :param qoi_set: QOI set.
    :param output: Output CSV file.
    """
    df = qoi_set.to_dataarray("name").to_pandas()
    # Convert attributes to data variables so they end up as columns in the CSV
    attrs = pandas.DataFrame.from_dict({qoi: qoi_set[qoi].attrs for qoi in qoi_set}, orient="index")
    attrs.index.name = "name"
    pandas.concat((df, attrs), axis="columns").to_csv(output)


def _plot_qoi_tolerance_check(qoi, ax):
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
        _plot_scalar_tolerance_check(name, calculated, expected, lower_limit, upper_limit, within_tolerance, ax)


def _plot_scalar_tolerance_check(name, calculated, expected, lower_limit, upper_limit, within_tolerance, ax):
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
        container = ax.barh(0.0, width=(calculated - expected), left=expected, color=bar_color)
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


def _write_qoi_report(qoi_archive, output, plots_per_page=16):
    """Write a QOI report to a PDF.

    QOI archive must contain QOIs with only the "value_type" dimension. Multi-dimensional QOIs and QOI values across
    multiple versions cannot be plotted using this function.
    """
    with PdfPages(output) as pdf:
        for qoi_group in qoi_archive.leaves:
            for plot_num, qoi in enumerate(qoi_group.ds.data_vars.values()):
                ax_num = plot_num % plots_per_page  # ax_num goes from 0 to (plots_per_page - 1)
                if ax_num == 0:  # starting new page
                    open_figure = True
                    fig, axes = matplotlib.pyplot.subplots(  # create a new figure for a new page
                        plots_per_page,
                        figsize=(8.5, 11),
                        gridspec_kw=dict(
                            left=0.6,  # plot on right half of page because text will go on left side
                            right=0.9,  # leave margin on right edge
                            top=(1.0 - 1.0 / plots_per_page),  # top margin equal to single plot height
                            bottom=(0.5 / plots_per_page),  # bottom margin equal to half of single plot height
                            hspace=1.0,
                        ),
                    )
                fig.suptitle(qoi_group.name)
                _plot_qoi_tolerance_check(qoi, axes[ax_num])
                if ax_num == plots_per_page - 1:  # ending a page
                    pdf.savefig()  # save current figure to a page
                    matplotlib.pyplot.close()
                    open_figure = False
            if open_figure:  # If a figure is still open (hasn't been saved to a page)
                for ax in axes[ax_num + 1:]:  # Clear remaining empty plots on the page
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


def _plot_scalar_qoi_history(qoi, ax, date_min, date_max):
    """Plot Scalar QOI history."""
    name = _get_plotting_name(qoi)
    group = qoi.attrs["group"]
    ax.scatter(qoi.date, qoi.sel(value_type="calculated"))
    ax.plot(qoi.date, qoi.sel(value_type="lower_limit"), "--")
    ax.plot(qoi.date, qoi.sel(value_type="upper_limit"), "--")
    ax.set_xlim((date_min, date_max))
    ax.set_title(name)


def _qoi_history_report(qoi_archive, output, plots_per_page=8, add_git_commit_date=False):
    """Plot history of QOI values from QOI archive."""
    if add_git_commit_date:
        qoi_archive = qoi_archive.map_over_datasets(_add_commit_date)
    qoi_archive = qoi_archive.map_over_datasets(_sort_by_date)
    open_figure = False
    date_min = min(node.ds.date.min() for node in qoi_archive.leaves)
    date_max = max(node.ds.date.max() for node in qoi_archive.leaves)
    with PdfPages(output) as pdf:
        for qoi_group in qoi_archive.leaves:
            plot_num = 0
            for qoi in qoi_group.ds.data_vars.values():
                if qoi.where(numpy.isfinite(qoi)).dropna("version", how="all").size == 0:  # Would be an empty plot
                    continue  # Don't increment plot_num
                ax_num = plot_num % plots_per_page  # ax_num goes from 0 to (plots_per_page - 1)
                if ax_num == 0:  # Starting new page
                    open_figure = True
                    fig, axes = matplotlib.pyplot.subplots(  # Create a new figure for a new page
                        plots_per_page,
                        figsize=(8.5, 11),
                        gridspec_kw=dict(
                            left=0.1,  # leave margin on left edge
                            right=0.9,  # leave margin on right edge
                            top=(1.0 - 0.5 / plots_per_page),  # top margin equal to half of single plot height
                            bottom=(0.5 / plots_per_page),  # bottom margin equal to half of single plot height
                            hspace=1.0,
                        ),
                    )
                    fig.suptitle(qoi_group.name, fontweight="bold")
                _plot_scalar_qoi_history(qoi, axes[ax_num], date_min, date_max)
                if ax_num == plots_per_page - 1:  # Ending a page
                    pdf.savefig()  # save current figure to a page
                    matplotlib.pyplot.close()
                    open_figure = False
                plot_num += 1
            if open_figure:  # If a figure is still open (hasn't been saved to a page)
                for ax in axes[ax_num + 1:]:
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
        return ds.assign_coords(date=("version", (_get_commit_date(commit) for commit in ds["version"])))
    except KeyError:
        return ds


def _sort_by_date(ds):
    try:
        return ds.sortby("date")
    except KeyError:
        return ds


def _accept(calculated, expected):
    """Update expected QOI values to match the currently calculated values."""
    qoi_set = _read_qoi_set(calculated)
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


def _check(diff):
    """Check results of calculated vs expected QOI comparison"""
    qoi_set = _read_qoi_set(diff)
    if qoi_set.filter_by_attrs(within_tolerance=0):
        raise ValueError(f"Not all QOIs are within tolerance. See {diff}.")


def _diff(calculated, expected, output):
    """Compare calculated QOIs to expected values."""
    qoi_set = xarray.merge((_read_qoi_set(calculated), _read_qoi_set(expected)))
    _add_tolerance_attribute(qoi_set)
    _write_qoi_set_to_csv(qoi_set, output)


def _aggregate(parameter_study_file, output_file, qoi_set_files):
    """Aggregate QOIs across multiple simulations, e.g. across sets in a parameter study."""
    qoi_sets = (_read_qoi_set(qoi_set_file) for qoi_set_file in qoi_set_files)
    qois = (qoi for qoi_set in qoi_sets for qoi in qoi_set.values())
    parameter_study = xarray.open_dataset(parameter_study_file)
    qoi_study = _create_qoi_study(qois, parameter_study=parameter_study)
    qoi_study.to_netcdf(output_file)


def _report(output, qoi_archive_h5):
    """Generate a QOI test report."""
    qoi_archive = xarray.open_datatree(qoi_archive_h5, engine="h5netcdf")
    _write_qoi_report(qoi_archive, output)


def _plot_archive(output, qoi_archive_h5):
    """Plot QOI values over the Mod/Sim history."""
    qoi_archive = _merge_qoi_archives((xarray.open_datatree(f) for f in qoi_archive_h5))
    _qoi_history_report(qoi_archive, output)


def _archive(output, version, qoi_set_files):
    """Archive QOI sets from a single version to an H5 file."""
    qoi_sets = (_read_qoi_set(qoi_set_file) for qoi_set_file in qoi_set_files)
    qois = (qoi for qoi_set in qoi_sets for qoi in qoi_set.values())
    if version:
        qois = (qoi.assign_attrs(version=version) for qoi in qois)
    _create_qoi_archive(qois).to_netcdf(output, engine="h5netcdf")


# Limit help() and 'from module import *' behavior to the module's public API
_module_objects = set(globals().keys()) - _exclude_from_namespace
__all__ = [name for name in _module_objects if not name.startswith("_")]
