#! /usr/bin/env python

import pandas as pd

from waves.tutorials.eabm_package.python import post_processing


def test_csv_files_match():
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

    # Assert that the function returns False when the DataFrames differ
    assert post_processing.csv_files_match(control, different) is False

    # Assert that the function returns True when the DataFrames are identical
    assert post_processing.csv_files_match(control, identical_copy) is True
