
from typing import List

import spacy
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer

nlp = spacy.load("en_core_web_sm")
stopwords = nlp.Defaults.stop_words


def vectorize_documents(document: List) -> pd.DataFrame:
    """
        using sklearn library TFIDFVectorizer it will transform text data
        into numbers and vectorize them.
        :return: a dataframe with vectorized document
    """

    tfidf = TfidfVectorizer(lowercase=True, stop_words=stopwords, max_df=0.2, min_df=0.02)
    tfidf_sparse = tfidf.fit_transform(document)

    return pd.DataFrame(tfidf_sparse.toarray(), columns=tfidf.get_feature_names())
