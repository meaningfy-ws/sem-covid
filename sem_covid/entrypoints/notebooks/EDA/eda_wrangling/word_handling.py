
import re

import spacy
from cleantext import clean
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

nlp = spacy.load("en_core_web_sm", exclude=["lemmatizer"])


def get_nlp_docs(data: pd.Series) -> list:
    """
    Function to get spaCy NLP doc for each row from series of strings
    """
    return [nlp(row) for row in data]


def get_entity_words(data: pd.Series, entity_name: str = 'ORG', docs: list = None) -> pd.Series:
    """
    Function to get list of words labeled with entity_name
    """
    if docs is None:
        docs = get_nlp_docs(data)
    result = [e.text for doc in docs for e in doc.ents if e.label_ == entity_name]

    return pd.Series(result, dtype=str)


def get_named_entities(data: pd.Series, docs: list = None) -> pd.Series:
    """
    Function to get entity names from series of strings
    """
    if docs is None:
        docs = get_nlp_docs(data)
    result = [e.label_ for doc in docs for e in doc.ents]

    return pd.Series(result, dtype=str)


def remove_stopwords(data: pd.Series) -> pd.Series:
    """
    Function which remove stop words from series of strings
    """
    stop_words = nlp.Defaults.stop_words
    result = []
    for row in data:
        result.append(" ".join([word for word in row.split() if word not in stop_words]))

    return pd.Series(result, dtype=str)


def calculate_tf_idf(data: pd.Series, title: str) -> pd.DataFrame:
    """
    Function to get TF-IDF for series of strings
    """
    vectorizer = TfidfVectorizer()
    documents = remove_stopwords(data)
    vectors = vectorizer.fit_transform(documents)
    feature_names = vectorizer.get_feature_names()
    dense = vectors.todense()
    dense_list = dense.tolist()
    tmp_df = pd.DataFrame(dense_list, columns=feature_names)
    tmp_df = tmp_df.max().sort_values(ascending=False).reset_index()
    tmp_df.columns = [title, "TF-IDF"]

    return tmp_df


def get_ngrams(data: pd.Series, n: int, stopwords: bool = True) -> pd.Series:
    """
    Function to get N grams from series of strings
    """
    if not stopwords:
        data = remove_stopwords(data)
    result = [" ".join(text[i : i + n])
    for text in data.str.split()
    for i in range(len(text) - n + 1)]

    return pd.Series(result, dtype=str)


def get_noun_phrases(data: pd.Series, docs: list = None) -> pd.Series:
    """
    Function to get list of noun phrases
    """
    if docs is None:
        docs = get_nlp_docs(data)
    result = [str(n) for doc in docs for n in doc.noun_chunks]

    return pd.Series(result, dtype=str)


def get_words(data: pd.Series) -> pd.Series:
    """
    Function to get list of words without stop words
    """
    text = " ".join(data)
    stop_words = nlp.Defaults.stop_words
    result = [word for word in text.split() if word not in stop_words]

    return pd.Series(result, dtype=str)


def delete_punctuation(text: str) -> str:
    """
    Function to delete punctuation from text
    """
    regex_filter = r'[,;:\*`#\"^&~@=+_.()?\[\]!\s]\s*'
    text = " ".join(list(filter(None, re.split(regex_filter, text))))
    text = text.replace("-", "")

    return text


def prepare_text_data(data: pd.Series) -> pd.Series:
    """
    Function to clear textual data
    :param data:
    :return:
    """
    data = data.dropna().explode()
    result = [delete_punctuation(
        clean(text, no_urls=True, no_emails=True, no_phone_numbers=True))
        for text in data]

    return pd.Series(result, dtype=str)
