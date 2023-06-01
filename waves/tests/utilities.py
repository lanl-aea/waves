import pytest
from contextlib import nullcontext as does_not_raise


def get_salib_sampler_tuple(method, schema=None, n=None, problem=None, num_vars=None, names=None, bounds=None,
                            error=False, missing_problem=False):
    """

    """
    salib_raises = pytest.raises(error) if error else does_not_raise()
    if schema:
        salib_tuple = (method, schema, salib_raises)
    else:
        schema_dict = dict()
        if n:
            schema_dict["N"] = n
        if problem:
            schema_dict["problem"] = problem
        elif missing_problem:
            pass
        else:
            problem_dict = dict()
            if num_vars:
                problem_dict["num_vars"] = num_vars
            if names:
                problem_dict["names"] = names
            if bounds:
                problem_dict["bounds"] = bounds
            schema_dict["problem"] = problem_dict
        salib_tuple = (method, schema_dict, salib_raises)
    return salib_tuple
