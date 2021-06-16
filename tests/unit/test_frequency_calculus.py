from sem_covid.entrypoints.notebooks.EDA.eda_wrangling.frequency_calculus import calculate_frequency


def test_frequency_calculus(transformed_pwdb_dataframe):
    frequency = calculate_frequency(transformed_pwdb_dataframe['category'], 'labels')

    assert frequency.isnull().values.any() == False
    assert "labels" in frequency
    assert "Absolute freq" in frequency
    assert len(frequency) == 2

    frequency = calculate_frequency(transformed_pwdb_dataframe['category'], 'labels', True)
    assert frequency.isnull().values.any() == False
    assert "labels" in frequency
    assert len(frequency) == 2
    assert "Relative freq" in frequency
