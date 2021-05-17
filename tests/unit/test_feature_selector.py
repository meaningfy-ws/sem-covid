import pandas as pd

from sem_covid.services.sc_wrangling.feature_selector import (reduce_array_column,
                                                              multi_label_column_to_binary_columns)


def test_reduce_array_column_rows_expectation():
    df = pd.DataFrame({'col1': [['hello', 'world', 'Ave', 'Maria']],
                       'col2': [['PC', 'Master', 'Race', 'Sucks']],
                       'col3': [['row1', 'row2', 'row3', 'row4']]})

    # test given with expected result
    actual_rows = reduce_array_column(df, 'col1')
    expected_rows = pd.DataFrame({'col1': ['hello, world, Ave, Maria']})

    assert len(actual_rows) == len(expected_rows)
    assert all([a == b for a, b in zip(actual_rows, expected_rows)])


def test_multi_label_column_to_binary_columns():
    df = pd.DataFrame({'col1': ['row1', 'row2'],
                       'col2': ['hello, world', 'Ave, Maria']})

    actual_columns = multi_label_column_to_binary_columns(df, 'col2')
    expected_columns = pd.DataFrame({'col1': ['row1', 'row2'], 'col2': ['hello, world', 'Ave, Maria'],
                                     'hello': [1, 0], 'world': [1, 0], 'Ave': [0, 1], 'Maria': [0, 1]})

    # compare generated columns based on rows values
    assert len(actual_columns) == len(expected_columns)
    assert all([a == b for a, b in zip(actual_columns, actual_columns)])
