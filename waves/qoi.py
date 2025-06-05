"""Quantity of Interest (QOI) tools

.. warning::

   This module is considered experimental pending early adopter end user trial and feedback.

   The QOI xarray data array and dataset handling of :meth:`create_qoi` and :meth:`create_qoi_set` should be stable, but
   the output plotting and reporting formatting is subject to change.
"""

import pathlib
import typing
import collections.abc
import itertools

import numpy
import xarray
import pandas
import matplotlib.pyplot
from matplotlib.backends.backend_pdf import PdfPages

from waves import _settings


_exclude_from_namespace = set(globals().keys())

_version_key = "version"


def _propagate_identical_attrs(all_attrs, context):
    first_attrs = all_attrs[0]
    identical_pairs = {}

    for key, value in first_attrs.items():
        if all(key in attrs and attrs[key] == value and type(attrs[key]) is type(value) for attrs in all_attrs[1:]):
            identical_pairs[key] = value

    return identical_pairs


_merge_constants = {"combine_attrs": _propagate_identical_attrs}


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
    :param attrs: Attributes to associate with the QOI.
        Recommended attributes are: group, units, description, long_name, version.
        Together ``name`` and ``attrs['group']`` should distinguish each QOI from every other QOI in the Mod/Sim
        repository.
        In other words, ``group`` should be as specific as possible, e.g., "Local Test XYZ Assembly Preload" instead of
        just "Preload".

    :returns: QOI

    Example

    .. code-block::

        >>> load = waves.qoi.create_qoi(
        ...     name="load",
        ...     calculated=5.0,
        ...     units="N",
        ...     long_name="Axial Load",
        ...     description="Axial load through component XYZ",
        ...     group="Assembly ABC Preload",
        ...     version="abcdef",
        ...     date="2025-01-01",
        ... )
        >>> load
        <xarray.DataArray 'load' (value_type: 4)> Size: 32B
        array([ 5., nan, nan, nan])
        Coordinates:
          * value_type  (value_type) <U11 176B 'calculated' 'expected' ... 'upper_limit'
        Attributes:
            units:        N
            long_name:    Axial Load
            description:  Axial load through component XYZ
            group:        Assembly ABC Preload
            version:      abcdef
            date:         2025-01-01
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

    :param qois: Sequence of QOIs.

    :returns: QOI Set containing each QOI as a separate data variable.

    Example

    .. code-block::

        >>> load = waves.qoi.create_qoi(
        ...     name="load",
        ...     calculated=5.0,
        ...     units="N",
        ...     long_name="Axial Load",
        ...     description="Axial load through component XYZ",
        ...     group="Assembly ABC Preload",
        ...     version="abcdef",
        ...     date="2025-01-01",
        ... )
        ... gap = waves.qoi.create_qoi(
        ...     name="gap",
        ...     calculated=1.0,
        ...     units="mm",
        ...     long_name="Radial gap",
        ...     description="Radial gap between components A and B",
        ...     group="Assembly ABC Preload",
        ...     version="abcdef",
        ...     date="2025-01-01",
        ... )
        ...
        ... # Combine QOIs into calculated QOIs set
        ... simulation_1_qois = waves.qoi.create_qoi_set((load, gap))
        ... simulation_1_qois
        <xarray.Dataset> Size: 240B
        Dimensions:     (value_type: 4)
        Coordinates:
          * value_type  (value_type) <U11 176B 'calculated' 'expected' ... 'upper_limit'
        Data variables:
            load        (value_type) float64 32B 5.0 nan nan nan
            gap         (value_type) float64 32B 1.0 nan nan nan
        >>> simulation_1_qois["load"]
        <xarray.DataArray 'load' (value_type: 4)> Size: 32B
        array([ 5., nan, nan, nan])
        Coordinates:
          * value_type  (value_type) <U11 176B 'calculated' 'expected' ... 'upper_limit'
        Attributes:
            units:        N
            long_name:    Axial Load
            description:  Axial load through component XYZ
            group:        Assembly ABC Preload
            version:      abcdef
            date:         2025-01-01
    """
    qoi_set = xarray.merge(qois, **_merge_constants)
    # Keep all attributes at the data variable level
    qoi_set.attrs = dict()
    return qoi_set


def _create_qoi_study(
    qois: typing.Iterable[xarray.DataArray],
    parameter_study: xarray.Dataset = None,
) -> xarray.Dataset:
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

    Example

    .. code-block::

        >>> set_0_qoi = waves.qoi.create_qoi(
        ...     name="load",
        ...     calculated=5.0,
        ...     units="N",
        ...     long_name="Axial Load",
        ...     description="Axial load through component XYZ",
        ...     group="Assembly ABC Preload set_0",
        ...     set_name="set_0",
        ...     version="abcdef",
        ... )
        ... set_1_qoi = waves.qoi.create_qoi(
        ...     name="load",
        ...     calculated=6.0,
        ...     units="N",
        ...     long_name="Axial Load",
        ...     description="Axial load through component XYZ",
        ...     group="Assembly ABC Preload set_1",
        ...     set_name="set_1",
        ...     version="abcdef",
        ... )
        ... set_2_qoi = waves.qoi.create_qoi(
        ...     name="load",
        ...     calculated=7.0,
        ...     units="N",
        ...     long_name="Axial Load",
        ...     description="Axial load through component XYZ",
        ...     group="Assembly ABC Preload set_2",
        ...     set_name="set_2",
        ...     version="abcdef",
        ... )
        ... set_3_qoi = waves.qoi.create_qoi(
        ...     name="load",
        ...     calculated=8.0,
        ...     units="N",
        ...     long_name="Axial Load",
        ...     description="Axial load through component XYZ",
        ...     group="Assembly ABC Preload set_3",
        ...     set_name="set_3",
        ...     version="abcdef",
        ... )
        ...
        ... study = waves.parameter_generators.CartesianProduct(
        ...     {"height": [1.0, 2.0], "width": [0.2, 0.4]},
        ...     output_file="study.h5",
        ...     set_name_template="set_@number",
        ... )
        ... study.parameter_study
        <xarray.Dataset> Size: 736B
        Dimensions:         (set_name: 4)
        Coordinates:
            set_hash        (set_name) <U32 512B '8f1f75de634dfa73a8f2a3feaa4562c3' ....
          * set_name        (set_name) <U5 80B 'set_0' 'set_1' 'set_2' 'set_3'
            parameter_sets  (set_name) <U5 80B 'set_0' 'set_1' 'set_2' 'set_3'
        Data variables:
            height          (set_name) float64 32B 1.0 1.0 2.0 2.0
            width           (set_name) float64 32B 0.2 0.4 0.2 0.4
        >>> qoi_study = waves.qoi._create_qoi_study((set_0_qoi, set_1_qoi, set_2_qoi, set_3_qoi), study.parameter_study)
        >>> qoi_study
        <xarray.Dataset> Size: 992B
        Dimensions:         (value_type: 4, set_name: 4)
        Coordinates:
          * value_type      (value_type) <U11 176B 'calculated' ... 'upper_limit'
          * set_name        (set_name) object 32B 'set_0' 'set_1' 'set_2' 'set_3'
            set_hash        (set_name) <U32 512B '8f1f75de634dfa73a8f2a3feaa4562c3' ....
            height          (set_name) float64 32B 1.0 1.0 2.0 2.0
            width           (set_name) float64 32B 0.2 0.4 0.2 0.4
            parameter_sets  (set_name) <U5 80B 'set_0' 'set_1' 'set_2' 'set_3'
        Data variables:
            load            (set_name, value_type) float64 128B 5.0 nan nan ... nan nan
    """
    # Move "group" from attribute to dimension for each DataArray, and merge
    try:
        qoi_study = xarray.merge(
            [qoi.expand_dims(set_name=[qoi.attrs[_settings._set_coordinate_key]]) for qoi in qois],
            **_merge_constants,
        )
    except KeyError:
        raise RuntimeError(
            f"Each DataArray in ``qois`` must have an attribute named '{_settings._set_coordinate_key}'."
        )
    # Keep all attributes at the data variable level
    qoi_study.attrs = dict()
    # Merge in parameter study definition
    if parameter_study:
        # Convert parameter study variables to coordinates
        parameter_study = parameter_study.set_coords(parameter_study)
        qoi_study = xarray.merge((qoi_study, parameter_study), **_merge_constants)
    return qoi_study


def _node_path(node: xarray.DataTree) -> str:
    """Return ``"path"`` of a QOI node (xarray.DataTree)."""
    return node.path


def _qoi_group(qoi: xarray.Dataset) -> str:
    """Return ``"group"`` attribute of a QOI (xarray.Dataset)."""
    return qoi.attrs["group"]


def _create_qoi_archive(qois: typing.Iterable[xarray.DataArray]) -> xarray.DataTree:
    """Create a QOI DataTree spanning multiple simulations and versions.

    :param qois: Sequence of QOIs. Each QOI must have a "version" and "group" attribute.

    :returns: QOI archive

    Example

    .. code-block::

        >>> archive = waves.qoi._create_qoi_archive(
        ...     (
        ...         waves.qoi.create_qoi(
        ...             name="load",
        ...             calculated=5.3,
        ...             expected=4.5,
        ...             lower_limit=3.5,
        ...             upper_limit=5.5,
        ...             units="N",
        ...             long_name="Axial Load",
        ...             description="Axial load through component XYZ",
        ...             group="Assembly ABC Preload",
        ...             version="ghijkl",
        ...             date="2025-02-01",
        ...         ),
        ...         waves.qoi.create_qoi(
        ...             name="gap",
        ...             calculated=1.0,
        ...             expected=0.95,
        ...             lower_limit=0.85,
        ...             upper_limit=1.05,
        ...             units="mm",
        ...             long_name="Radial gap",
        ...             description="Radial gap between components A and B",
        ...             group="Assembly ABC Preload",
        ...             version="ghijkl",
        ...             date="2025-02-01",
        ...         ),
        ...         waves.qoi.create_qoi(
        ...             name="load",
        ...             calculated=35.0,
        ...             units="lbf",
        ...             long_name="Transverse load",
        ...             description="Transverse load through component D",
        ...             group="Assembly DEF Preload",
        ...             version="ghijkl",
        ...             date="2025-02-01",
        ...         ),
        ...         waves.qoi.create_qoi(
        ...             name="stress",
        ...             calculated=110.0,
        ...             units="MPa",
        ...             long_name="Membrane stress",
        ...             description="Membrane stress in component E",
        ...             group="Assembly DEF Preload",
        ...             version="ghijkl",
        ...             date="2025-02-01",
        ...         ),
        ...     )
        ... )
        ... archive
        <xarray.DataTree>
        Group: /
        ├── Group: /Assembly ABC Preload
        │       Dimensions:     (version: 1, value_type: 4)
        │       Coordinates:
        │         * version     (version) object 8B 'ghijkl'
        │         * value_type  (value_type) <U11 176B 'calculated' 'expected' ... 'upper_limit'
        │           date        (version) <U10 40B '2025-02-01'
        │       Data variables:
        │           load        (version, value_type) float64 32B 5.3 4.5 3.5 5.5
        │           gap         (version, value_type) float64 32B 1.0 0.95 0.85 1.05
        └── Group: /Assembly DEF Preload
                Dimensions:     (version: 1, value_type: 4)
                Coordinates:
                  * version     (version) object 8B 'ghijkl'
                  * value_type  (value_type) <U11 176B 'calculated' 'expected' ... 'upper_limit'
                    date        (version) <U10 40B '2025-02-01'
                Data variables:
                    load        (version, value_type) float64 32B 35.0 nan nan nan
                    stress      (version, value_type) float64 32B 110.0 nan nan nan
    """
    archive = xarray.DataTree()
    # Creates a group for each "group" attribute
    for group, qois in itertools.groupby(sorted(qois, key=_qoi_group), key=_qoi_group):
        # Move "version" from attribute to dimension for each DataArray and merge to Dataset
        qois = [qoi.expand_dims(version=[qoi.attrs[_version_key]]) for qoi in qois]
        # Try to add date as a coordinate if available
        try:
            qois = [qoi.assign_coords(date=(_version_key, [qoi.attrs["date"]])) for qoi in qois]
        except KeyError:
            pass  # date coordinate is not needed
        qoi_set = create_qoi_set(qois)
        # Add dataset as a node in the DataTree
        archive[group] = qoi_set
    return archive


def _merge_qoi_archives(qoi_archives: typing.Iterable[xarray.DataTree]) -> xarray.DataTree:
    """Merge QOI archives by concatenating leaf datasets along the "version" dimension.

    :param qoi_archives: QOI archives. Each leaf dataset must have a "version" dimension.
    :returns: Merged QOI archive.
    """
    # FIXME: The "version" attribute of the merged datasets incorrectly keeps the original dataset's value
    # https://re-git.lanl.gov/aea/python-projects/waves/-/issues/927
    leaves = [qoi for archive in qoi_archives for qoi in archive.leaves]
    merged_archive = xarray.DataTree()
    # Group by datatree node path, i.e. the QOI group
    for group, qois in itertools.groupby(sorted(leaves, key=_node_path), key=_node_path):
        # Merge dataset as a node in the DataTree
        merged_archive[group] = xarray.merge((node.ds for node in qois), **_merge_constants)
    return merged_archive


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

    Example

    .. csv-table::
        :header-rows: 1

        name,expected,lower_atol,upper_atol
        load,4.5,1.0,1.0
        gap,0.8,0.1,0.1

    .. code-block::

        >>> waves.qoi._read_qoi_set(pathlib.Path("simulation_1_expected_qois.csv"))
        <xarray.Dataset> Size: 240B
        Dimensions:     (value_type: 4)
        Coordinates:
          * value_type  (value_type) <U11 176B 'calculated' 'expected' ... 'upper_limit'
        Data variables:
            load        (value_type) float64 32B nan 4.5 3.5 5.5
            gap         (value_type) float64 32B nan 0.8 0.7 0.9
    """
    suffix = from_file.suffix.lower()
    if suffix == ".csv":
        df = pandas.read_csv(from_file)
        # Empty entries in the CSV end up as NaN in the DataFrame.
        # Drop NaNs so they aren't passed as kwargs to `create_qoi()`
        qoi_kwargs = [row.dropna().to_dict() for idx, row in df.iterrows()]
        return create_qoi_set([create_qoi(**kwargs) for kwargs in qoi_kwargs])
    elif suffix == ".h5":
        return xarray.open_dataset(from_file, engine="h5netcdf")
    else:
        raise RuntimeError(f"Unknown file suffix '{suffix}'")


def _add_tolerance_attribute(qoi_set: xarray.Dataset) -> None:
    """Adds a ``"within_tolerance"`` attribute to each QOI in a QOI Dataset in place.

    :param qoi_set: QOI set.
    """
    for qoi in qoi_set.data_vars.values():
        lower_limit = qoi.sel(value_type="lower_limit").fillna(-numpy.inf)
        upper_limit = qoi.sel(value_type="upper_limit").fillna(numpy.inf)
        calculated = qoi.sel(value_type="calculated")
        # netcdf4 doesn't support bool, so make it an int
        qoi.attrs["within_tolerance"] = int(((calculated >= lower_limit) & (calculated <= upper_limit)).all().item())


def write_qoi_set_to_csv(qoi_set: xarray.Dataset, output: pathlib.Path) -> None:
    """Writes a QOI Dataset to a CSV file.

    :param qoi_set: QOI set.
    :param output: Output CSV file.

    Example

    .. code-block::

        >>> simulation_1_qois
        <xarray.Dataset> Size: 240B
        Dimensions:     (value_type: 4)
        Coordinates:
          * value_type  (value_type) <U11 176B 'calculated' 'expected' ... 'upper_limit'
        Data variables:
            load        (value_type) float64 32B 5.0 4.5 3.5 5.5
            gap         (value_type) float64 32B 1.0 0.8 0.7 0.9
        >>> waves.qoi.write_qoi_set_to_csv(simulation_1_qois, "simulation_1_qois.csv")

    .. csv-table::
        :header-rows: 1

        name,calculated,expected,lower_limit,upper_limit,units,long_name,description,group,version,date
        load,5.0,4.5,3.5,5.5,N,Axial Load,Axial load through component XYZ,Assembly ABC Preload,abcdef,2025-01-01
        gap,1.0,0.8,0.7000000000000001,0.9,mm,Radial gap,Radial gap between components A and B,Assembly ABC Preload,abcdef,2025-01-01
    """  # noqa: E501
    df = qoi_set.to_dataarray("name").to_pandas()
    # Convert attributes to data variables so they end up as columns in the CSV
    attrs = pandas.DataFrame.from_dict({qoi: qoi_set[qoi].attrs for qoi in qoi_set}, orient="index")
    attrs.index.name = "name"
    pandas.concat((df, attrs), axis="columns").to_csv(output)


def _plot_qoi_tolerance_check(qoi: xarray.DataArray, axes: matplotlib.axes.Axes) -> None:
    """Plot QOI tolerance check.

    Handle differences in scalar and vector (not yet implemented) QOI tolerance plots. Handle missing required
    attributes and dimensions.

    :param qoi: Quantity of interest data array as built by :meth:`create_qoi`
    :param axes: Matplotlib axes for plotting
    """
    qoi_dim = len(qoi.squeeze().dims)  # Count includes the "value_type" dim
    if qoi_dim == 1:  # Scalar QOI
        _plot_scalar_tolerance_check(qoi, axes)


def _can_plot_qoi_tolerance_check(qoi: xarray.DataArray) -> bool:
    """Checks if a QOI meets requirements to be plotted by `_plot_qoi_tolerance_check()`.

    Requires the following:
        1. "value_type" is a dimension
        2. "within_tolerance" is an attribute
        3. The QOI is scalar
        4. No values (e.g. calculated, expected, lower_limit, upper_limit) are null

    :param qoi: Quantity of interest data array as built by :meth:`create_qoi`
    """
    if "value_type" not in qoi.dims:
        return False
    if "within_tolerance" not in qoi.attrs:
        return False
    qoi_dim = len(qoi.squeeze().dims)  # Count includes the "value_type" dim
    if qoi_dim == 1:  # Scalar QOI
        if qoi.isnull().any():
            return False
    else:
        return False
    return True


def _plot_scalar_tolerance_check(
    qoi: xarray.DataArray,
    axes: matplotlib.axes.Axes,
) -> None:
    """Plots a tolerance check for a scalar QOI DataArray.

    :param qoi: Quantity of interest data array as built by :meth:`create_qoi`
    :param axes: Matplotlib axes for plotting
    """
    name = _get_plotting_name(qoi)
    calculated = qoi.sel(value_type="calculated").item()
    expected = qoi.sel(value_type="expected").item()
    lower_limit = qoi.sel(value_type="lower_limit").item()
    upper_limit = qoi.sel(value_type="upper_limit").item()
    within_tolerance = qoi.attrs["within_tolerance"]
    # TODO: draw arrow if bar is clipped by xmin, xmax

    # Bar color is always green if within tolerance, red otherwise
    bar_color = "green" if within_tolerance else "red"
    # If tolerance on both sides, within_tolerance is good, out of tolerance is bad
    lower_line = lower_limit
    upper_line = upper_limit
    colors = ["black", "black"]

    # Draw vertical lines at lower and upper tolerance limits
    container = axes.barh(0.0, width=(calculated - expected), left=expected, color=bar_color)
    axes.vlines([lower_line, upper_line], *axes.get_ylim(), colors=colors)
    axes.vlines([expected], *axes.get_ylim(), colors="black", linestyle="dashed")

    # Turn ticks and labels off, except for tolerances and expected value
    axes.tick_params(axis="x", bottom=False, pad=-1, labelsize=8)
    axes.tick_params(axis="y", left=False, labelleft=False)
    axes.set_xticks([lower_line, expected, upper_line])

    # Turn off plot borders
    axes.spines["bottom"].set_visible(False)
    axes.spines["top"].set_visible(False)
    axes.spines["left"].set_visible(False)
    axes.spines["right"].set_visible(False)

    # Extend plot past upper and lower tolerances
    tolerance_width = upper_line - lower_line
    xmin = lower_line - 0.25 * tolerance_width
    xmax = upper_line + 0.25 * tolerance_width
    axes.set_xlim((xmin, xmax))

    # Add calculated value as annotation above bar
    axes.annotate(
        f"{calculated:.3e}",
        xy=(calculated, 0.555),
        xytext=(numpy.clip(calculated, xmin, xmax), 0.55),
        annotation_clip=False,
        ha="center",
        fontsize=8,
    )

    # Add QOI name and values to left of plot
    if not within_tolerance:
        color = "red"
        fontweight = "bold"
    else:
        color = "black"
        fontweight = "normal"
    axes.annotate(
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


def _write_qoi_report(qoi_archive: xarray.DataTree, output: pathlib.Path, plots_per_page: int = 16) -> None:
    """Write a QOI report to a PDF.

    QOI archive must contain QOIs with only the "value_type" dimension. Multi-dimensional QOIs and QOI values across
    multiple versions cannot be plotted using this function.

    :param qoi_archive: collection of QOI datasets stored as a datatree
    :param output: history report output path
    :param plots_per_page: the number of plots on each page of the output
    """
    qois = [
        qoi for leaf in qoi_archive.leaves for qoi in leaf.ds.data_vars.values() if _can_plot_qoi_tolerance_check(qoi)
    ]
    page_margins = dict(
        left=0.6,  # plot on right half of page because text will go on left side
        right=0.9,  # leave margin on right edge
        top=(1.0 - 1.0 / plots_per_page),  # top margin equal to single plot height
        bottom=(0.5 / plots_per_page),  # bottom margin equal to half of single plot height
        hspace=1.0,
    )
    _pdf_report(qois, output, page_margins, plots_per_page, _plot_qoi_tolerance_check, {})


def _get_plotting_name(qoi: xarray.DataArray) -> str:
    """Return a QOI label with optional units as ``name`` or ``name [units]``

    Construct a QOI label from the following preference ordered list of attributes. The ``name`` attribute _must_ exist
    if the other attributes do not exist.

    1. ``long_name``
    2. ``standard_name``
    3. ``name``

    Always append the value of the ``units`` attribute if it exists.

    :param qoi: Quantity of interest data array as built by :meth:`create_qoi`

    :returns: plotting QOI label as either ``name`` or ``name [units]``
    """
    if "long_name" in qoi.attrs:
        name = qoi.attrs["long_name"]
    elif "standard_name" in qoi.attrs:
        name = qoi.attrs["standard_name"]
    else:
        name = qoi.name
    if "units" in qoi.attrs:
        name = f"{name} [{qoi.attrs['units']}]"
    return name


def _plot_scalar_qoi_history(
    qoi: xarray.DataArray,
    axes: matplotlib.axes.Axes,
    date_min,
    date_max,
) -> None:
    """Plot Scalar QOI history.

    The QOI data array must have the attributes and dimensions created by :meth:`create_qoi`. Must contain the
    coordinate ``value_type`` with values ``calculated``, ``lower_limit``, ``upper_limit`` and the attribute ``group``.

    :param qoi: Quantity of interest data array as generated by :meth:`create_qoi`.
    :param axes: Matplotlib axes for plotting
    :param date_min: minimum date to include on the x-axes
    :param date_max: maximum date to include on the x-axes
    """
    name = _get_plotting_name(qoi)
    axes.scatter(qoi.date, qoi.sel(value_type="calculated"))
    axes.plot(qoi.date, qoi.sel(value_type="lower_limit"), "--")
    axes.plot(qoi.date, qoi.sel(value_type="upper_limit"), "--")
    axes.set_xlim((date_min, date_max))
    axes.set_title(name)


def _qoi_history_report(
    qoi_archive: xarray.DataTree,
    output: pathlib.Path,
    plots_per_page: int = 8,
) -> None:
    """Plot history of QOI values from QOI archive.

    :param qoi_archive: collection of QOI datasets stored as a datatree
    :param output: history report output path
    :param plots_per_page: the number of plots on each page of the output
    """
    qois = [
        qoi.sortby("date")
        for leaf in qoi_archive.leaves
        for qoi in leaf.ds.data_vars.values()
        if _can_plot_scalar_qoi_history(qoi)
    ]
    plotting_kwargs = dict(date_min=min(qoi.date.min() for qoi in qois), date_max=max(qoi.date.max() for qoi in qois))
    page_margins = dict(
        left=0.1,  # leave margin on left edge
        right=0.9,  # leave margin on right edge
        top=(1.0 - 0.5 / plots_per_page),  # top margin equal to half of single plot height
        bottom=(0.5 / plots_per_page),  # bottom margin equal to half of single plot height
        hspace=1.0,
    )
    _pdf_report(qois, output, page_margins, plots_per_page, _plot_scalar_qoi_history, plotting_kwargs)


def _can_plot_scalar_qoi_history(qoi: xarray.DataArray) -> bool:
    """Checks if a QOI meets requirements to be plotted by :meth:`_plot_scalar_qoi_history`.

    Requires the following:
        1. The QOI contains at least 1 finite value
        2. The QOI contains a dimension named "version"

    :param qoi: Quantity of interest data array as built by :meth:`create_qoi`
    """
    if _version_key not in qoi.dims:
        return False
    if qoi.where(numpy.isfinite(qoi)).dropna(_version_key, how="all").size == 0:  # Avoid empty plots
        return False
    return True


def _pdf_report(
    qois: typing.Iterable[xarray.DataArray],
    output_pdf: pathlib.Path,
    page_margins: typing.Dict[str, float],
    plots_per_page: int,
    plotting_method: collections.abc.Callable,
    plotting_kwargs: typing.Dict,
    groupby: collections.abc.Callable = _qoi_group,
) -> None:
    """Generate a multi-page PDF report of QOI plots.

    :param qois: Sequence of QOIs.
    :param output_pdf: PDF report output path
    :param page_margins: Dictionary of kwargs passed as `gridspec_kw` to `matplotlib.pyplot.subplots()`
    :param plots_per_page: the number of plots on each page of the output
    :param plotting_method: plotting function which takes a QOI and a plotting axis as the first and second args
    :param plotting_kwargs: additional kwargs to pass to `plotting_method`
    :param groupby: Function which takes a QOI as the only positional argument and returns a string.
        The returned string will be used to group the QOIs and as a PDF page header.
    """
    open_figure = False
    with PdfPages(output_pdf) as pdf:
        for group, qois in itertools.groupby(sorted(qois, key=groupby), key=groupby):
            for plot_num, qoi in enumerate(qois):
                ax_num = plot_num % plots_per_page  # ax_num goes from 0 to (plots_per_page - 1)
                if ax_num == 0:  # Starting new page
                    open_figure = True
                    fig, axes = matplotlib.pyplot.subplots(  # Create a new figure for a new page
                        plots_per_page,
                        figsize=(8.5, 11),
                        gridspec_kw=page_margins,
                    )
                    fig.suptitle(group, fontweight="bold")
                plotting_method(qoi, axes[ax_num], **plotting_kwargs)
                if ax_num == plots_per_page - 1:  # Ending a page
                    pdf.savefig()  # save current figure to a page
                    matplotlib.pyplot.close()
                    open_figure = False
            if open_figure:  # If a figure is still open (hasn't been saved to a page)
                for ax in axes[ax_num + 1 :]:  # noqa: E203
                    ax.clear()
                    ax.axis("off")
                pdf.savefig()
                matplotlib.pyplot.close()


def _accept(calculated: pathlib.Path, expected: pathlib.Path) -> None:
    """Update expected QOI values to match the currently calculated values.

    :param calculated: path to source file containing calculated QOI values
    :param expected: path to source file containing expected QOI values
    """
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


def _check(diff: pathlib.Path) -> None:
    """Check results of calculated vs expected QOI comparison

    :param diff: path for differences between calculated and expected QOI values

    :raises ValueError: If any QOIs are out of specified tolerance in the diff file
    """
    qoi_set = _read_qoi_set(diff)
    if qoi_set.filter_by_attrs(within_tolerance=0):
        raise ValueError(f"Not all QOIs are within tolerance. See {diff}.")


def _diff(calculated: pathlib.Path, expected: pathlib.Path, output: pathlib.Path):
    """Compare calculated QOIs to expected values.

    :param calculated: path to source file containing calculated QOI values
    :param expected: path to source file containing expected QOI values
    :param output: output path for differences between calculated and expected QOI values
    """
    qoi_set = xarray.merge((_read_qoi_set(calculated), _read_qoi_set(expected)))
    _add_tolerance_attribute(qoi_set)
    write_qoi_set_to_csv(qoi_set, output)


def _aggregate(
    parameter_study_file: pathlib.Path,
    output_file: pathlib.Path,
    qoi_set_files: typing.Iterable[pathlib.Path],
) -> None:
    """Aggregate QOIs across multiple simulations, e.g. across sets in a parameter study.

    :param parameter_study_file: WAVES parameter study H5 file
    :param output_file: post-processing output file
    :param qoi_set_files: QOI file paths
    """
    qoi_sets = (_read_qoi_set(qoi_set_file) for qoi_set_file in qoi_set_files)
    qois = (qoi for qoi_set in qoi_sets for qoi in qoi_set.values())
    parameter_study = xarray.open_dataset(parameter_study_file, engine="h5netcdf")
    qoi_study = _create_qoi_study(qois, parameter_study=parameter_study)
    qoi_study.to_netcdf(output_file, engine="h5netcdf")


def _report(output: pathlib.Path, qoi_archive_h5: pathlib.Path) -> None:
    """Generate a QOI test report.

    :param output: report output file path
    :param qoi_archive_h5: QOI archive file
    """
    qoi_archive = xarray.open_datatree(qoi_archive_h5, engine="h5netcdf")
    _write_qoi_report(qoi_archive, output)


def _plot_archive(output: pathlib.Path, qoi_archive_h5: typing.Iterable[pathlib.Path]) -> None:
    """Plot QOI values over the Mod/Sim history.

    :param output: report output file path
    :param qoi_archive_h5: QOI archive file(s)
    """
    qoi_archive = _merge_qoi_archives((xarray.open_datatree(archive, engine="h5netcdf") for archive in qoi_archive_h5))
    _qoi_history_report(qoi_archive, output)


def _archive(output: pathlib.Path, version: str, date: str, qoi_set_files: typing.Iterable[pathlib.Path]) -> None:
    """Archive QOI sets from a single version to an H5 file.

    :param output: report output file path
    :param version: version string to override existing QOI version attribute
    :param date: date string to override existing QOI date attribute
    :param qoi_set_files: QOI file paths
    """
    qoi_sets = (_read_qoi_set(qoi_set_file) for qoi_set_file in qoi_set_files)
    qois = (qoi for qoi_set in qoi_sets for qoi in qoi_set.values())
    if version:
        qois = (qoi.assign_attrs(version=version) for qoi in qois)
    if date:
        qois = (qoi.assign_attrs(date=date) for qoi in qois)
    _create_qoi_archive(qois).to_netcdf(output, engine="h5netcdf")


# Limit help() and 'from module import *' behavior to the module's public API
_module_objects = set(globals().keys()) - _exclude_from_namespace
__all__ = [name for name in _module_objects if not name.startswith("_")]
