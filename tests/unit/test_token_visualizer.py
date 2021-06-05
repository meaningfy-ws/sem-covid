import pandas as pd

from sem_covid.entrypoints.notebooks.topic_modeling.topic_modeling_wrangling.token_management import *


def test_filter_stop_words(tokenized_textual_pwdb_series):
    corpus_without_stopwords = tokenized_textual_pwdb_series.apply(filter_stop_words, spacy_stop_words)

    assert pd.Series == type(corpus_without_stopwords)


def test_filter_pos(tokenized_textual_pwdb_series):
    document = tokenized_textual_pwdb_series.apply(filter_pos, pos="PUNCT")

    assert pd.Series == type(document)


def test_select_pos(tokenized_textual_pwdb_series):
    pass


def test_filter_stop_words_on_a_span_list(tokenized_textual_pwdb_series):
    pass
