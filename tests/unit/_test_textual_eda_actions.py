import pandas as pd

from sem_covid.entrypoints.notebooks.EDA.eda_wrangling.textual_eda_actions import eda_entity_words, eda_textual, \
    eda_tf_idf, eda_n_grams_without_stopwords, eda_n_grams, eda_noun_phrases


# TODO: where are the assertions here?
def test_eda_n_grams(transformed_pwdb_json):
    series = pd.Series(data=transformed_pwdb_json, dtype=str)
    eda_n_grams(series, 'actors', 3)


# TODO: where are the assertions here?
def test_eda_n_grams_without_stopwords(transformed_pwdb_json):
    series = pd.Series(data=transformed_pwdb_json, dtype=str)
    eda_n_grams_without_stopwords(series, 'actors', 3)


# TODO: where are the assertions here?
def test_eda_tf_idf(transformed_pwdb_json):
    series = pd.Series(data=transformed_pwdb_json, dtype=str)
    eda_tf_idf(series, 'actors')


# TODO: where are the assertions here?
def test_eda_textual(transformed_pwdb_dataframe):
    test_df = transformed_pwdb_dataframe.head(2).iloc[:, :2]
    eda_textual(test_df)
