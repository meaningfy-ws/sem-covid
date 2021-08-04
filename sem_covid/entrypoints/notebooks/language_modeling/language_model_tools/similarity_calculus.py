import numpy as np
import pandas as pd
from gensim.models import KeyedVectors
from sklearn.metrics import pairwise_distances


def euclidean_similarity(vector_1: np.array, vector_2: np.array) -> np.float:
    """
        calculate euclidean similarity between two vectors
    """
    return 1 / (1 + np.linalg.norm(vector_1 - vector_2))


def cosine_similarity(vector_1: np.array, vector_2: np.array) -> np.float:
    """
        calculate cosine similarity between two vectors
    """
    return np.dot(vector_1, vector_2) / (np.linalg.norm(vector_1) * np.linalg.norm(vector_2))


def manhattan_similarity(vector_1: np.array, vector_2: np.array) -> np.float:
    """
        calculate manhattan similarity between two vectors
    """
    return 1 / (1 + np.sum(np.abs(vector_1 - vector_2)))


def build_similarity_matrix(vector: np.ndarray, keys: list, metric: callable) -> pd.DataFrame:
    """
        creates a dataframe based on keys and vectors from pretrained gensim model
        and selected similarity function

        :param vector: the object that contains the mapping between words and embeddings
        :param keys: words indexes keys
        :metric: metric distance formula
        :return: dataframe with similarity of each word
    """
    return pd.DataFrame(pairwise_distances(vector, metric=metric), columns=keys, index=keys)
