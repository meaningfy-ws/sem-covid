import json

import pandas as pd

from sem_covid.entrypoints.notebooks.EDA.eda_wrangling.categorical_analyze import fast_categorical_analyze


def test_categorical_analyze():
    df_data = {'col1': [1, 2, 5], 'col2': [3, 4, 5], 'col3': [3, 4, 'Unknown']}
    test_data_frame = pd.DataFrame(data=df_data)
    expected_result_in_returned_dict_items = 'col3Relativefreq0333.331433.332Unknown33.33'
    response = fast_categorical_analyze(test_data_frame, ['col3'], 'Unknown')
    assert 'col3' in response
    assert str(response["col3"]).replace("\n", "").replace(" ", "") == expected_result_in_returned_dict_items

