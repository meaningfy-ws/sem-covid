
import numpy as np
import pandas as pd
from gensim.models import KeyedVectors


def euclidean_similarity(vector_1: np.array, vector_2: np.array) -> np.float:
    """
        calculate euclidean distance between two vectors
    """
    return 1 / (1 + np.linalg.norm(vector_1 - vector_2))


def cosine_similarity(vector_1: np.array, vector_2: np.array) -> np.float:
    """
        calculate cosine distance between two vectors
    """
    return np.dot(vector_1, vector_2) / (np.linalg.norm(vector_1) * np.linalg.norm(vector_2))


def manhattan_similarity(vector_1: np.array, vector_2: np.array) -> np.float:
    """
        calculate manhattan distance between two vectors
    """
    return sum(abs(value_1 - value_2) for value_1, value_2 in zip(vector_1, vector_2))


def get_similarity_matrix(wv: KeyedVectors, similarity_function) -> pd.DataFrame:
    """
        creates a dataframe based on keys and vectors from pretrained gensim model
        and selected similarity function

        :param wv: the object that contains the mapping between words and embeddings
        :param similarity_function: function that helps to measure the distance between word vectors
        :return: dataframe with similarity of each word
    """
    similarity_matrix_columns = wv.index_to_key
    return pd.DataFrame([{column_index: similarity_function(wv[row_index], wv[column_index])
                          for column_index in similarity_matrix_columns}
                        for row_index in similarity_matrix_columns],
                        columns=similarity_matrix_columns, index=[similarity_matrix_columns])
