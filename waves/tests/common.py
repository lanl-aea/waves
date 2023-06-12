from waves._settings import _hash_coordinate_key, _set_coordinate_key, _supported_salib_samplers
from unittest.mock import patch


def consistent_hash_parameter_check(test_merge1, test_merge2):
    for set_name, parameter_set in test_merge1.parameter_study.groupby(_set_coordinate_key):
        assert parameter_set == test_merge2.parameter_study.sel(parameter_sets=set_name)


def self_consistency_checks(test_merge):
    assert list(test_merge._parameter_set_names.values()) == test_merge.parameter_study[
        _set_coordinate_key].values.tolist()
    assert test_merge._parameter_set_hashes == test_merge.parameter_study[_hash_coordinate_key].values.tolist()


def get_samplers(sampler_class, sampler, first_schema, second_schema, kwargs):
    test_merge1 = sampler_class(sampler, first_schema, **kwargs)
    with patch('xarray.open_dataset', return_value=test_merge1.parameter_study):
        test_merge2 = sampler_class(sampler, second_schema, previous_parameter_study='dummy_string', **kwargs)
    test_merge2._samples.astype(float)
    return test_merge1, test_merge2
