import platform
from unittest.mock import patch

from waves._settings import _hash_coordinate_key, _set_coordinate_key


def platform_check():
    """Check platform and set platform specific variables

    :return: tuple (root_fs, testing_windows)
    :rtype: (str, bool)
    """
    if platform.system().lower() == "windows":
        root_fs = "C:\\"
        testing_windows = True
    else:
        root_fs = "/"
        testing_windows = False
    testing_macos = False
    if platform.system().lower() == "darwin":
        testing_macos = True
    return testing_windows, root_fs, testing_macos


def consistent_hash_parameter_check(original_study, merged_study):
    """Assert that the merged parameter study data matches the original parameter study.

    :param Union[CartesianProduct, SobolSequence, ScipySampler, SALibSampler] original_study: Original sampler object
    :param Union[CartesianProduct, SobolSequence, ScipySampler, SALibSampler] merged_study: Merged sampler object
    """
    for set_name, parameters in original_study.parameter_study.groupby(_set_coordinate_key):
        assert parameters == merged_study.parameter_study.sel({_set_coordinate_key: set_name})


def self_consistency_checks(merged_study):
    """Assert that the merged parameter set data is consistent throughout the sampler object.

    :param Union[CartesianProduct, SobolSequence, ScipySampler, SALibSampler] merged_study: Sampler object
    """
    assert (
        list(merged_study._set_names.values())
        == merged_study.parameter_study[_set_coordinate_key].values.tolist()  # noqa: W503
    )
    assert merged_study._set_hashes == merged_study.parameter_study[_hash_coordinate_key].values.tolist()


def merge_samplers(sampler_class, first_schema, second_schema, kwargs, sampler=None):
    """Return sampler objects based on the provided schemas and sampler class. Second sampler contains the
    merged first sampler.

    :param Union[CartesianProduct, SobolSequence, ScipySampler, SALibSampler] sampler_class: Class of the study objects
    :param dict first_schema: Dictionary containing parameter study data
    :param dict second_schema: Dictionary containing parameter study data
    :param dict kwargs: Dictionary containing keyword arguments
    :param str sampler: Optional sampler type

    :return: original_study, merged_study
    :rtype: (Union[CartesianProduct, SobolSequence, ScipySampler, SALibSampler], Union[CartesianProduct, SobolSequence, ScipySampler, SALibSampler])
    """  # noqa: E501
    if sampler:
        original_study = sampler_class(sampler, first_schema, **kwargs)
    else:
        original_study = sampler_class(first_schema, **kwargs)
    with (
        patch("xarray.open_dataset", return_value=original_study.parameter_study),
        patch("pathlib.Path.is_file", return_value=True),
    ):
        if sampler:
            merged_study = sampler_class(sampler, second_schema, previous_parameter_study="dummy_string", **kwargs)
        else:
            merged_study = sampler_class(second_schema, previous_parameter_study="dummy_string", **kwargs)
    return original_study, merged_study
