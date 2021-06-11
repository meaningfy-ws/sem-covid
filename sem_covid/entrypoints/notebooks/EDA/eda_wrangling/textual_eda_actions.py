
from tqdm import tqdm
import pandas as pd

from sem_covid.entrypoints.notebooks.EDA.eda_wrangling.data_observations import eda_display_result
from sem_covid.entrypoints.notebooks.EDA.eda_wrangling.frequency_calculus import calculate_frequency
from sem_covid.entrypoints.notebooks.EDA.eda_wrangling.word_handling import get_entity_words, get_words, \
    get_named_entities, get_noun_phrases, get_ngrams, calculate_tf_idf, prepare_text_data, get_nlp_docs


def eda_entity_words(data: pd.Series, data_title: str, docs):
    """
    Textual EDA for words classified with the same entity name
    :param data:
    :param data_title:
    :param docs:
    :return:
    """
    result = calculate_frequency(get_entity_words(data, 'ORG', docs), data_title, True)
    return eda_display_result(result, "Entity words for " + data_title)


def eda_words_freq(data: pd.Series, data_title: str):
    """
    Textual EDA for words frequency
    :param data:
    :param data_title:
    :return:
    """
    result = calculate_frequency(get_words(data), data_title, True)
    return eda_display_result(result, "Words frequency for " + data_title)


def eda_named_entities(data: pd.Series, data_title: str, docs):
    """
    Textual EDA for entity names
    :param data:
    :param data_title:
    :param docs:
    :return:
    """
    result = calculate_frequency(get_named_entities(data, docs), data_title, True)
    return eda_display_result(result, "Named entities for " + data_title)


def eda_noun_phrases(data: pd.Series, data_title: str, docs):
    """
    Textual EDA for noun phrases
    :param data:
    :param data_title:
    :param docs:
    :return:
    """
    result = calculate_frequency(get_noun_phrases(data, docs), data_title, True)
    return eda_display_result(result, "Noun phrases for " + data_title)


def eda_n_grams(data: pd.Series, data_title: str, n_grams):
    """
    Textual EDA for N grams
    :param data:
    :param data_title:
    :param n_grams:
    :return:
    """
    result = calculate_frequency(get_ngrams(data, n_grams), data_title, True)
    return eda_display_result(result, "N grams for " + data_title)


def eda_n_grams_without_stopwords(data: pd.Series, data_title: str, n_grams):
    """
    Textual EDA for N grams without stop words
    :param data:
    :param data_title:
    :param n_grams:
    :return:
    """
    result = calculate_frequency(get_ngrams(data, n_grams, False), data_title, True)
    return eda_display_result(result, "N grams without stopwords for " + data_title)


def eda_tf_idf(data: pd.Series, data_title: str):
    """
    Textual EDA for top 10 TF-IDF from column
    :param data:
    :param data_title:
    :return:
    """
    result = calculate_tf_idf(data, data_title)
    return eda_display_result(result.head(10), "TOP 10 TF-IDF for " + data_title, pie_chart=False)


def eda_textual(data: pd.DataFrame):
    """
    Combined textual EDA
    :param data:
    :return:
    """
    p_bar = tqdm(data.columns)
    for column_name in p_bar:
        p_bar.set_description('Eda on textual data ['+column_name+']')
        column_data = prepare_text_data(data[column_name])
        docs = get_nlp_docs(column_data)
        eda_words_freq(column_data, column_name)
        eda_n_grams(column_data, column_name, 3)
        eda_n_grams_without_stopwords(column_data, column_name, 3)
        eda_noun_phrases(column_data, column_name, docs)
        eda_named_entities(column_data, column_name, docs)
        eda_entity_words(column_data, column_name, docs)
        eda_tf_idf(column_data, column_name)
