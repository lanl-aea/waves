#! /usr/bin/env python

import pandas as pd

from waves.tutorials.eabm_package.python import post_processing


def test_regression_test():
    data = {
        'DummyLine': [1, 2, 3],
        'SecondDummyLine': [4, 5, 6]
    }
    # Control DataFrame
    control = pd.DataFrame(data)

    # Identical DataFrame
    identical_copy = control.copy()

    # Different DataFrame
    different = control.copy()
    different.loc[0, 'DummyLine'] = 999

    # Assert that the function returns "1" when the DataFrames differ
    assert post_processing.regression_test(control, different) == 1

    # Assert that the function returns None when the DataFrames are identical
    assert post_processing.regression_test(control, identical_copy) is None
