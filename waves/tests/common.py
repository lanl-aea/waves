from waves._settings import _hash_coordinate_key, _set_coordinate_key
from unittest.mock import patch


def consistent_hash_parameter_check(test_merge1, test_merge2):
    for set_name, parameter_set in test_merge1.parameter_study.groupby(_set_coordinate_key):
        assert parameter_set == test_merge2.parameter_study.sel(parameter_sets=set_name)


def self_consistency_checks(test_merge):
    assert list(test_merge._parameter_set_names.values()) == test_merge.parameter_study[
        _set_coordinate_key].values.tolist()
    assert test_merge._parameter_set_hashes == test_merge.parameter_study[_hash_coordinate_key].values.tolist()


def merge_samplers(sampler_class, first_schema, second_schema, kwargs, sampler=None, as_float=True):
    if sampler:
        original_study = sampler_class(sampler, first_schema, **kwargs)
    else:
        original_study = sampler_class(first_schema, **kwargs)
    with patch('xarray.open_dataset', return_value=original_study.parameter_study):
        if sampler:
            merged_study = sampler_class(sampler, second_schema, previous_parameter_study='dummy_string', **kwargs)
        else:
            merged_study = sampler_class(second_schema, previous_parameter_study='dummy_string', **kwargs)
    samples_array = merged_study._samples
    if as_float:
        samples_array = samples_array.astype(float)
    return original_study, merged_study, samples_array
