
from plotly.graph_objs._figure import Figure

from sem_covid.entrypoints.notebooks.EDA.eda_wrangling.data_observations import *


def test_plot_bar_chart(transformed_pwdb_dataframe):
    text_data = transformed_pwdb_dataframe[['title', 'title_national_language']]
    plot = plot_bar_chart(text_data, "test_title")

    assert Figure == type(plot)


def test_plot_pie_chart(transformed_pwdb_dataframe):
    text_data = transformed_pwdb_dataframe[['title', 'title_national_language']]
    plot = plot_pie_chart(text_data, "test_title")

    assert Figure == type(plot)





def test_calc_freq_categorical_data(transformed_pwdb_dataframe):
    categorical_data = calc_freq_categorical_data(transformed_pwdb_dataframe['category'], 'labels')

    assert categorical_data.isnull().values.any() == False
    assert "labels" in categorical_data
    assert "Absolute freq" in categorical_data
    assert len(categorical_data) == 2


def test_calc_freq_missing_data(transformed_pwdb_dataframe):
    missing_data = calc_freq_missing_data(transformed_pwdb_dataframe)

    assert len(missing_data) == 4
    assert "index" in missing_data
    assert "Absolute freq" in missing_data
