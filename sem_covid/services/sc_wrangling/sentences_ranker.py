#!/usr/bin/python3

# sentences_ranker.py
# Date:  07.09.2021
# Author: Stratulat Ștefan
# Email: stefan.stratulat1997@gmail.com
from typing import List

from numpy import mean
from sklearn.feature_extraction.text import TfidfVectorizer

vectorizer = TfidfVectorizer(lowercase=True, stop_words='english')


def top_k_mean(data: list, top_k: int):
    """
        This function calculates the arithmetic mean of the first K terms in descending order.
        If K is greater than the N number of terms, the remaining terms will be filled in with zero.
    :param data: a list of numerical terms
    :param top_k: the number of terms that will participate in the average
    :return: the arithmetic mean of the top K terms.
    """
    tmp_data = data.copy()
    tmp_data.sort(reverse=True)
    return mean(tmp_data[:top_k] + [0] * (top_k - len(data)))


def textual_tfidf_ranker(textual_chunks: List[str], top_k: int) -> list:
    """
        This function weights the texts in the input list based on the Tf-Idf metrics.
    :param textual_chunks: a list of text sequences
    :param top_k: the number of terms that will participate in the calculation of the Top-K-Mean average
    :return: a list of weights, where one weight for each text sequence in the input list.
    """
    vectors = vectorizer.fit_transform(textual_chunks).todense().tolist()
    return [top_k_mean(vec, top_k=top_k) for vec in vectors]
