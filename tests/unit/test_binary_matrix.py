import pandas as pd

from sem_covid.entrypoints.notebooks.EDA.eda_wrangling.binary_matrix import (
    convert_to_binary_matrix, dependency_table)


def test_convert_to_binary_matrix(transformed_pwdb_dataframe):
    testing_df = transformed_pwdb_dataframe.drop('sources', axis=1)
    pwdb_binary_matrix = convert_to_binary_matrix(testing_df)

    assert len(pwdb_binary_matrix) == 2
    assert type(pwdb_binary_matrix) == pd.core.frame.DataFrame
    assert pwdb_binary_matrix.shape[0] == 2
    assert pwdb_binary_matrix.shape[1] >= 44
    assert "03/27/2020" in pwdb_binary_matrix
    assert "Employers' organisations" in pwdb_binary_matrix
    assert 0.0 in pwdb_binary_matrix["Employers' organisations"]
    assert 1.0 in pwdb_binary_matrix["Employers' organisations"]


# !!! dependency_table issue
def test_dependency_table():
    df_data = {'col1': [1, 2, 5], 'col2': [3, 4, 5], 'col3': [3, 4, 'Unknown']}
    test_data_frame = pd.DataFrame(data=df_data)
    response = dependency_table(test_data_frame)
    assert isinstance(response, pd.DataFrame)
    assert response['col1'].values[0] == 3.0
    assert response['col1'].values[1] == 3.0
