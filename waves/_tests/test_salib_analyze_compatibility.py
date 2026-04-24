import contextlib

import numpy
import pytest
import SALib.analyze.delta
import SALib.analyze.dgsm
import SALib.analyze.discrepancy
import SALib.analyze.fast
import SALib.analyze.hdmr
import SALib.analyze.morris
import SALib.analyze.pawn
import SALib.analyze.rbd_fast
import SALib.analyze.rsa
import SALib.analyze.sobol
import SALib.sample.fast_sampler
import SALib.sample.finite_diff
import SALib.sample.latin
import SALib.sample.morris
import SALib.sample.sobol
import SALib.test_functions.Ishigami

import waves

does_not_raise = contextlib.nullcontext()


def column_sort(array: numpy.ndarray) -> numpy.ndarray:
    if array.ndim == 2:
        indices = numpy.lexsort([array[:, column] for column in reversed(range(array.shape[1]))])
        return array[indices]
    else:
        raise RuntimeError(f"Can only sort 2D arrays. Found '{array.ndim}' dimensions.")


@pytest.mark.parametrize(
    ("array", "expected", "outcome"),
    [
        (
            numpy.array(
                [
                    [3, 1, 1],
                    [2, 1, 1],
                    [1, 3, 1],
                    [1, 2, 1],
                    [1, 1, 3],
                    [1, 1, 2],
                    [1, 1, 1],
                ],
            ),
            numpy.array(
                [
                    [1, 1, 1],
                    [1, 1, 2],
                    [1, 1, 3],
                    [1, 2, 1],
                    [1, 3, 1],
                    [2, 1, 1],
                    [3, 1, 1],
                ],
            ),
            does_not_raise,
        ),
        (
            numpy.array([1, 2, 3]),
            None,
            pytest.raises(RuntimeError, match=r"Can only sort 2D arrays\. Found '1' dimensions\."),
        ),
        (
            numpy.array([[[1, 2, 3]]]),
            None,
            pytest.raises(RuntimeError, match=r"Can only sort 2D arrays\. Found '3' dimensions\."),
        ),
    ],
)
def test_column_sort(
    array: numpy.ndarray,
    expected: numpy.ndarray,
    outcome: contextlib.nullcontext | pytest.RaisesExc,
) -> None:
    with outcome:
        sorted_array = column_sort(array)
        numpy.testing.assert_allclose(sorted_array, expected)


universal_analyze_methods = [
    "delta",
    "discrepancy",
    "hdmr",
    "pawn",
    "rbd_fast",
    "rsa",
]
skip_salib_analyze_incompatibility = (
    "Known WAVES-SALib analyze incompatibility. Remove skip when WAVES enables"
    " re-sorting to original SALib index order or when SALib enables user-input order handling."
)


@pytest.mark.parametrize(
    ("sample_method", "analyze_method", "original_index"),
    [
        # Confirmed sample-analyze compatibility after WAVES re-shuffle
        ("fast_sampler", "discrepancy", False),
        ("fast_sampler", "pawn", False),
        ("fast_sampler", "rsa", False),
        ("finite_diff", "discrepancy", False),
        ("finite_diff", "pawn", False),
        ("finite_diff", "rsa", False),
        ("latin", "discrepancy", False),
        ("latin", "pawn", False),
        ("latin", "rsa", False),
        ("sobol", "discrepancy", False),
        ("sobol", "pawn", False),
        ("sobol", "rsa", False),
        # Check sample-analyze compatibility when sorted by original SALib index
        ("fast_sampler", "discrepancy", True),
        ("fast_sampler", "pawn", True),
        ("fast_sampler", "rsa", True),
        ("finite_diff", "discrepancy", True),
        ("finite_diff", "pawn", True),
        ("finite_diff", "rsa", True),
        ("latin", "discrepancy", True),
        ("latin", "pawn", True),
        ("latin", "rsa", True),
        ("sobol", "discrepancy", True),
        ("sobol", "pawn", True),
        ("sobol", "rsa", True),
        # SALib documented single combination sample-analyze compatibilities
        pytest.param("fast_sampler", "fast", True),
        pytest.param("finite_diff", "dgsm", True),
        pytest.param("sobol", "sobol", True),
        pytest.param("morris", "morris", True, marks=[pytest.mark.skip(reason=skip_salib_analyze_incompatibility)]),
        # SALib full-factorial of analyze methods documented as "compatible with: all samplers"
        pytest.param("fast_sampler", "delta", True),
        pytest.param("fast_sampler", "hdmr", True, marks=[pytest.mark.skip(reason=skip_salib_analyze_incompatibility)]),
        pytest.param("fast_sampler", "rbd_fast", True),
        pytest.param("finite_diff", "delta", True),
        pytest.param("finite_diff", "hdmr", True, marks=[pytest.mark.skip(reason=skip_salib_analyze_incompatibility)]),
        pytest.param("finite_diff", "rbd_fast", True),
        pytest.param("latin", "delta", True),
        pytest.param("latin", "hdmr", True, marks=[pytest.mark.skip(reason=skip_salib_analyze_incompatibility)]),
        pytest.param("latin", "rbd_fast", True),
        pytest.param("morris", "delta", True, marks=[pytest.mark.skip(reason=skip_salib_analyze_incompatibility)]),
        pytest.param(
            "morris", "discrepancy", True, marks=[pytest.mark.skip(reason=skip_salib_analyze_incompatibility)]
        ),
        pytest.param("morris", "hdmr", True, marks=[pytest.mark.skip(reason=skip_salib_analyze_incompatibility)]),
        pytest.param("morris", "pawn", True, marks=[pytest.mark.skip(reason=skip_salib_analyze_incompatibility)]),
        pytest.param("morris", "rbd_fast", True, marks=[pytest.mark.skip(reason=skip_salib_analyze_incompatibility)]),
        pytest.param("morris", "rsa", True, marks=[pytest.mark.skip(reason=skip_salib_analyze_incompatibility)]),
        pytest.param("sobol", "delta", True),
        pytest.param("sobol", "hdmr", True, marks=[pytest.mark.skip(reason=skip_salib_analyze_incompatibility)]),
        pytest.param("sobol", "rbd_fast", True),
    ],
)
def test_salib_analyze(sample_method: str, analyze_method: str, original_index: bool) -> None:
    # Setup
    sample_function = getattr(SALib.sample, sample_method)
    analyze_function = getattr(SALib.analyze, analyze_method)

    # Problem
    seed = 42
    problem = {
        "num_vars": 3,
        "names": ["x1", "x2", "x3"],
        "bounds": [[-numpy.pi, numpy.pi]] * 3,
        "seed": seed,
    }
    sample_count = 1024

    # Samples and dependent calculation: SALib
    salib_parameters = sample_function.sample(problem, sample_count, seed=seed)
    salib_dependent = SALib.test_functions.Ishigami.evaluate(salib_parameters)

    # Samples and dependent calculation: WAVES+SALib
    generator = waves.parameter_generators.SALibSampler(
        sample_method,
        {"problem": problem, "N": sample_count},
        seed=seed,
        original_index=original_index,
    )
    if original_index:
        waves_parameters = (
            generator.parameter_study.sortby("original_index")
            .to_dataframe()
            .drop(columns=["set_hash", "original_index"])
            .to_numpy()
        )
        numpy.testing.assert_allclose(salib_parameters, waves_parameters)
    else:
        waves_parameters = generator.parameter_study.to_dataframe().drop(columns=["set_hash"]).to_numpy()
    waves_dependent = SALib.test_functions.Ishigami.evaluate(waves_parameters)

    # Verify that the input is only out-of-order and not different
    numpy.testing.assert_allclose(column_sort(salib_parameters), column_sort(waves_parameters))
    numpy.testing.assert_allclose(numpy.sort(salib_dependent), numpy.sort(waves_dependent))

    # Analysis: handling API differences
    if analyze_method in ["sobol", "fast"]:
        salib_sensitivity_indices = analyze_function.analyze(problem, salib_dependent, seed=seed)
        waves_sensitivity_indices = analyze_function.analyze(problem, waves_dependent, seed=seed)
    elif analyze_method in [*universal_analyze_methods, "dgsm", "morris"]:
        salib_sensitivity_indices = analyze_function.analyze(problem, salib_parameters, salib_dependent, seed=seed)
        waves_sensitivity_indices = analyze_function.analyze(problem, waves_parameters, waves_dependent, seed=seed)
    else:
        raise RuntimeError(f"Unhandled analyze method '{analyze_method}'")

    # Test assertions
    assert salib_sensitivity_indices.keys() == waves_sensitivity_indices.keys()
    for key, expected in salib_sensitivity_indices.items():
        expected_array = numpy.array(expected)
        if numpy.issubdtype(expected_array.dtype, numpy.dtype("U")):
            assert waves_sensitivity_indices[key] == expected
        else:
            numpy.testing.assert_allclose(waves_sensitivity_indices[key], expected)
