
from sem_covid.entrypoints.notebooks.EDA.eda_wrangling.data_observations import (calc_freq_categorical_data,
                                                                                 calc_freq_missing_data)


def test_calc_freq_categorical_data(transformed_pwdb_dataframe):
    categorical_data = calc_freq_categorical_data(transformed_pwdb_dataframe['Category'], 'labels')

    assert categorical_data.isnull().values.any() == False
    assert "labels" in categorical_data
    assert "Absolute freq" in categorical_data
    assert len(categorical_data) == 2


def test_calc_freq_missing_data(transformed_pwdb_dataframe):
    missing_data = calc_freq_missing_data(transformed_pwdb_dataframe)

    assert len(missing_data) == 4
    assert "index" in missing_data
    assert "Absolute freq" in missing_data
